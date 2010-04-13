import threading, time, socket, struct, os, sys, collections
from vineyard.models import Session, WorkerNode, metadata, engine
from Queue import Queue
import cherrypy, simplejson, urllib
from vineyard import __version__, AUTODISCOVERY_PORT, STATUS_PORT, FarmConfig
import vineyard.engines
from vineyard.engines.BaseEngines import EngineRegistry

#__version__ = "1.0.0"

# default ports
# port to use for autodiscovery
#AUTODISCOVERY_PORT = 13331
# port to use to query a node for its data as a json string
#STATUS_PORT = 18088 

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
            time.sleep(3) 

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
        self.known_addrs = []
        self.updateKnownAddrs()
        while 1:
            data, addr = s.recvfrom(1024)
            if data == 'DEDAFX-NODE':
                # filter out known addresses
                if addr in self.known_addrs:
                    continue
                else:
                    self.queue.put(addr)
                    
            time.sleep(1)
            self.updateKnownAddrs()
                    
                    
    def updateKnownAddrs(self):
        session = Session()
        metadata.create_all(engine)
        try:
            for node in session.query(WorkerNode).all():
                if node in self.known_addrs:
                    continue
                else:
                    self.known_addrs.append(node.ip_address)
        except:
            pass
            
                
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
        metadata.create_all(engine)
        while 1:
            if not self.queue.empty():
                (addr, port) = self.queue.get()
                session = Session()
                nodes = session.query(WorkerNode).all()
                bNewNode = True
                for n in nodes:
                    if n.ip_address == addr:
                        bNewNode = False
                        break
                if bNewNode:
                    newNode = WorkerNode()
                    newNode.ip_address = addr
                    
                    url = "http://"+str(addr)+":"+str(STATUS_PORT)
                    result = simplejson.load(urllib.urlopen(url))
                    
                    if result['name']:
                        newNode.name = result['name']
                        newNode.mac_address = '---' #result['mac_address'] 
                        newNode.status = result['status']
                        
                        engines = ""
                        if type(result['engines']) == list:
                            for e in range(len(result['engines'])):
                                engines += str(result['engines'][e])
                                if e < len(result['engines'])-1:
                                    engines += ", "
                        else:
                            engines = str(result['engines'])
                        
                        newNode.engines = engines
                        #'autodiscovery-on'
                        newNode.cpus = result['cpus']
                        newNode.priority = result['priority']
                        newNode.platform = result['platform']
                        newNode.version = result['version']
                        newNode.pools = result['pools']
                        
                        session.add(newNode)
                        session.commit()
                    else:
                        print 'error with status infor from wroker node', addr, result['name'], result['mac_address']
                    
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
        metadata.create_all(engine)

        for i in self.session.query(WorkerNode).all(): 
            i.status = 'initializing' # until we verify that it is online
            self.nodes.append([i.name, 
                               i.mac_address, 
                               i.ip_address, 
                               i.status, 
                               i.platform, 
                               i.pools, 
                               i.version, 
                               i.cpus, 
                               i.priority, 
                               i.engines])
        self.session.commit() # status changes to offline
             
        self.nodeQueue = Queue()
        self.initializeLocalNodeCache()
        
        
    def __del__(self):
        self.nq.stop()
        self.autodisc.stop()
        self.statusupdate.stop()
        
    def autodiscover(self, on=True):
        if on:
            self.autodisc.start()
        else:
            self.autodisc.stop()
            
    def update(self):
        self.nodes = []
        for i in self.session.query(WorkerNode).all(): 
            engines = ""
            if type(i.engines) == list:
                for e in len(i.engines):
                    engines += str(i.engines[e])
                    if e < len(i.engines)-1:
                        engines += ", "
            else:
                engines = str(i.engines)
            
                    
            self.nodes.append([i.name, 
                               i.mac_address, 
                               i.ip_address, 
                               i.status, 
                               i.platform, 
                               i.pools, 
                               i.version, 
                               i.cpus, 
                               i.priority, 
                               engines])

    
    def initializeLocalNodeCache(self):
        """Broadcast magic packet and wait for responses from all the nodes running on the network.
        Use the recieved packets to get address information that can be used to inquire more detail about the node.
        
        Store the node information in the local sqlite database."""        
        
        # start the autodiscover and node queue update threads
        self.nq = NodeQueueProcessingThread(self.nodeQueue)
        self.nq.setName('Vineyard_nodeQueueProcessing') 
        self.nq.start()
        
        self.autodisc = AutodiscoveryServerThread(self.nodeQueue)
        self.autodisc.setName('Vineyard_autodiscoveryClient')        
        self.autodiscover()
        
        self.statusupdate = StatusUpdateThread()
        self.statusupdate.setName('Vineyard_StatusUpdateThread')
        self.statusupdate.start()
        
    def removeMachine(self, macAddress):
        """ remove a single machine from the memory array and the db """
        for i in range(len(self.nodes)):
            if macAddress in self.nodes[i]:
                n = self.nodes[i]
                
                dbn = self.session.query(WorkerNode).filter_by(mac_address=macAddress).first()
                print dbn, 'removed'
                
                self.session.delete( dbn )
                self.session.commit()
                
                self.nodes.remove(n)                
                return
            
class StatusUpdateThread(threading.Thread):
    
    def __init__(self, period=5):
        threading.Thread.__init__(self)
        self.session = Session()
        metadata.create_all(engine)
        self.period = period
        self._stop = threading.Event()
    
    def run(self):
        while not self.isStopped():
            try:
                self.__updateAllNodes()
            except: pass
            time.sleep(self.period)
            
    def __updateAllNodes(self):
        for node in self.session.query(WorkerNode).all(): 
            node.status = self.__updateStatus(node)
        self.session.commit()
            
            
    def __updateStatus(self, node):
        try:
            url = "http://"+str(node.ip_address)+":"+str(STATUS_PORT)
            result = simplejson.load(urllib.urlopen(url))
                        
            if result['status']:
                return result['status']
            else:
                return 'offline'
        except:
            return 'offline'
        
    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()

                
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
                                 "engines":EngineRegistry.getEngineNames(),
                                 "autodiscovery-on":(not __HEARTBEAT__.isStopped())
                                 })
    index.exposed = True
    
    def status(self):
        return simplejson.dumps({"status":"waiting"})
    status.exposed = True
    

    
__HEARTBEAT__ = HeartbeatThread()

class WorkerNodeDaemon(object):
    """the main worker node daemon class
    
    This can be run as a daemonized process or in a windows service"""
    
    def __init__(self, autodiscover=True):
        if not FarmConfig.load():
            FarmConfig.create()
        self.autodiscover = autodiscover
        self.heartbeat = __HEARTBEAT__
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
    
    print EngineRegistry.getEngineNames()
    
    if not FarmConfig.load():
        FarmConfig.create()
    
    import vineyard.gui.MainWindow as farmmgr
    farmmgr.run(sys.argv[1:])
       
        
    