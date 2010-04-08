import threading, time, socket, struct, os, sys
from vineyard.models import Session, WorkerNode
from Queue import Queue
import cherrypy, simplejson

__version__ = "1.0.0"

# default ports
# port to use for autodiscovery
AUTODISCOVERY_PORT = 13331
# port to use to query a node for its data as a json string
STATUS_PORT = 18088 

cherrypy.config.update({'global':{
    'engine.autoreload.on': False,
    'log.screen': False,
    'engine.SIGHUP': None,
    'engine.SIGTERM': None,
    'server.socket_host': '0.0.0.0', 
    'server.socket_port': STATUS_PORT
    }})


class HeartbeatThread(threading.Thread):
    """Broadcast a heartbeat packet on specified port.
    
    This is used by the windows service or daemon process, and is used to autodiscover running nodes."""
    
    def __init__(self):
        super(HeartbeatThread, self).__init__()
        self._stop = threading.Event()
    
    def run(self):
        n = 1        
        #host = "localhost"
        host = '<broadcast>'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", 0))
            
        while not self.isStopped():                       
            # broadcast magic packet on port            
            s.sendto("DEDAFX-NODE", (host, AUTODISCOVERY_PORT))
            time.sleep(5) 

    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()
      
            
class AutodiscoveryServerThread(threading.Thread):
    """Server thread to listen for other nodes"""
    
    def __init__(self, node_queue):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.queue = node_queue
    
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", AUTODISCOVERY_PORT))
        print "autodiscovery waiting on port:", AUTODISCOVERY_PORT
        self.known_addrs = []
        self.updateKnownAddrs()
        while 1:
            data, addr = s.recvfrom(1024)
            if data == 'DEDAFX-NODE':
                # filter out known addresses
                if addr in self.known_addrs:
                    continue
                else:
                    #print 'packet recieved in autodiscover thread:', addr, ' ', data
                    self.queue.put(addr)
                    
            time.sleep(1)
            self.updateKnownAddrs()
                    
                    
    def updateKnownAddrs(self):
        session = Session()
        for node in session.query(WorkerNode):
            if node in self.known_addrs:
                continue
            else:
                self.known_addrs.append(node.ip_address)
                
    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()
            
class NodeQueueProcessingThread(threading.Thread):
    
    def __init__(self, node_queue):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.queue = node_queue
    
    def run(self):
        """process the queue, if it has any items in it"""
        session = Session()
        while 1:
            if not self.queue.empty():
                (addr, port) = self.queue.get()
                #print 'NodeQueueProcessingThread addr:', addr
                if session.query(WorkerNode).filter_by(ip_address=addr).first() != None:
                    newNode = WorkerNode()
                    newNode.ip_address = addr
                        
                    session.add(addr)
                    session.commit()
                    
    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()
                
class NodeCache(object): 
    
    def __init__(self):
        """check for a local db, otherwise initialize it
        or, get the network db node cache, raise on fail"""
        
        self.session = None
        self.nodes = []
        
        self.session = Session()
        
        try:
            for i in self.session.query(WorkerNode).order_by(WorkerNode.id): 
                i.status = 'offline' # until we verify that it is online
                self.nodes.append([i.id, i.name, i.mac_address, i.ip_address, i.status, i.platform, i.pools, i.version, i.cpus, i.priority, i.engines])
            self.session.commit() # status changes to offline
        except Exception, e:
            print e
        
        self.nodeQueue = Queue()
        self.initializeLocalNodeCache()

    
    def initializeLocalNodeCache(self):
        """Broadcast magic packet and wait for responses from all the nodes running on the network.
        Use the recieved packets to get address information that can be used to inquire more detail about the node.
        
        Store the node information in the local sqlite database."""        
        
        # start the autodiscover and node queue update threads
        nq = NodeQueueProcessingThread(self.nodeQueue)
        nq.setName('Vineyard_nodeQueueProcessing') 
        nq.start()
        
        autodisc = AutodiscoveryServerThread(self.nodeQueue)
        autodisc.setName('Vineyard_autodiscoveryClient')        
        autodisc.start()
        
    def removeMachine(self, macAddress):
        """ remove a single machine from the memory array and the db """
        for i in range(len(self.nodes)):
            if macAddress in self.nodes[i]:
                n = self.nodes[i]
                
                dbn = self.session.query(WorkerNode).filter_by(mac_address=macAddress).first()
                print dbn
                
                self.session.delete( dbn )
                self.session.commit()
                
                self.nodes.remove(n)                
                return
                
class WorkerNodeConfigurationServer(object):
    """used to set configuration settings for a worker node
    
    Can only be run locally by anyone, or remotely by an administrator."""
    
    def index(self):
        return ""
    index.exposed = True
    
    
class WorkerNodeHttpServer(object):
    def index(self):
        if os.name == 'nt':
            nm = os.getenv('COMPUTERNAME')
            procs = os.getenv('NUMBER_OF_PROCESSORS')
        else:
            nm = os.getenv('HOSTNAME')
            procs = 1
        return simplejson.dumps({"name":nm, 
                                 "status":"waiting", 
                                 "ip_address":str(socket.gethostbyname(socket.getfqdn())),
                                 "mac_address":"",
                                 "platform":sys.platform,
                                 "pools":"",
                                 "version":__version__,
                                 "cpus":procs,
                                 "priority":1,
                                 "engines":""
                                 })
    index.exposed = True
    
    def status(self):
        return simplejson.dumps({"status":"waiting"})
    status.exposed = True
    

class WorkerNodeDaemon(object):
    """the main worker node daemon class
    
    This can be run as a daemonized process or in a windows service"""
    
    def __init__(self, autodiscover=True):
        self.heartbeat = HeartbeatThread()
        self.heartbeat.setName('Vineyard_heartbeat')        
    
    def __del__(self):
        try:
            self.stop()
        except: 
            pass
    
    def start(self):
        self.heartbeat.start()
        
        cherrypy.tree.mount(WorkerNodeHttpServer(), '/')
        cherrypy.engine.start()
        cherrypy.engine.block()
        
    def stop(self):
        cherrypy.engine.exit()
        self.heartbeat.stop()
    
            
def daemonizeThisProcess(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    if os.name != 'posix':
        print "this only works in nix environments!"
        sys.exit(-1)
    
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) # Exit first parent.
    except OSError, e:
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror)    )
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) # Exit second parent.
    except OSError, e:
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror)    )
        sys.exit(1)

    # Now I am a daemon!

    # Redirect standard file descriptors.
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


if __name__ == '__main__':
    
    # instead of starting the daemons here, this should start the gui!
    # another python file should start the daemon process on linux
    
    #daemon = WorkerNodeDaemon()
    
    if os.name == 'posix':
        #daemonizeThisProcess('/dev/null','/tmp/daemon.log','/tmp/daemon.log')
        # do the main loop for the worker node
        #daemon.start()
        pass
    elif os.name == 'nt':
        #daemon.start()
        import vineyard.gui.MainWindow as farmmgr
        farmmgr.run(sys.argv)
        
        
    