import threading, time, socket, struct, os, sys
from renderfarm.models import Session, WorkerNode
from Queue import Queue

HB_PORT = 8085
AUTODISCOVERY_PORT = 13331
# port to use to query a node for its data as a json string
STATUS_PORT = 18088 

# message opcodes
ACK_MSG =    0x0000
PING_MSG =   0x0001
STATUS_MSG = 0x0002
QUERY_MSG =  0x0003


def createPacket(opcode, size, data):
    pkt = ''
    
    
    return pkt


class HeartbeatThread(threading.Thread):
    """Broadcast a heartbeat packet on specified port.
    
    This is used by the windows service or daemon process, and is used to autodiscover running nodes."""
    
    def run(self):
        running = True
        n = 1
        
        #host = "localhost"
        host = '<broadcast>'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", 0))
            
        while running:
            time.sleep(5)            
            # broadcast magic packet on port            
            s.sendto("DEDAFX-NODE", (host, AUTODISCOVERY_PORT))

            #n += 1
            #if n > 5:
            #    running = False
                
        print "done!"
    
class EKGThread(threading.Thread):
    """
    Monitor heartbeats from worker nodes
    
    This thread should maintain a list of all nodes, persistent in a SQL DB, 
    but also maintained in memory available only to this thread. DB will be updated with changes in states.
    
    The purpose of the DB is for state persistance, for when additional clients connect, so the complete list
    of available nodes can be obtained. Offline nodes will not be broadcasting.
    
    SQL DB will also be the centralized source for configuration data, including ports for broadcasting.
    
    This thread decides when a node has gone offline, and updates the DB appropriately.
    """
    
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", HB_PORT))
        print "waiting on port:", HB_PORT
        while 1:
            data, addr = s.recvfrom(1024)
            print addr, ' ', data
            # process data, addr
            
# queue to receive the incoming node autodiscovery 
__nodeQueue = Queue()
            
class AutodiscoveryServerThread(threading.Thread):
    """Server thread to listen for other nodes"""
    
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
                    print addr, ' ', data
                    __nodeQueue.put(addr)
                    
            time.sleep(1)
            self.updateKnownAddrs()
                    
                    
    def updateKnownAddrs(self):
        session = Session()
        for node in session.query(WorkerNode):
            if node in self.known_addrs:
                continue
            else:
                self.known_addrs.append(node.ip_address)
            
#class NodeQueueProcessingThread(threading.Thread):
    
def processNodeQueue():
    """process the queue, if it has any items in it"""
    session = Session()
    while 1:
        if not __nodeQueue.empty():
            addr = __nodeQueue.get()
            if session.query(WorkerNode).filter_by(ip_address=addr).first() != None:
                newNode = WorkerNode()
                newNode.ip_address = addr
                    
                session.add(addr)
                session.commit()
                
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
        
        
        self.initializeLocalNodeCache()

    
    def initializeLocalNodeCache(self):
        """Broadcast magic packet and wait for responses from all the nodes running on the network.
        Use the recieved packets to get address information that can be used to inquire more detail about the node.
        
        Store the node information in the local sqlite database."""        
        
        # start the autodiscover and node queue update threads
        #nq = NodeQueueProcessingThread()
        
        #nq = threading.Thread(target=processNodeQueue)
        #nq.setName('Vinyard_nodeQueueProcessing') 
        #nq.start()
        
        #autodisc = AutodiscoveryServerThread()
        #autodisc.setName('Vinyard_autodiscoveryClient')        
        #autodisc.start()
        
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
                
            

class WorkerNodeDaemon(object):
    """the main worker node daemon class
    
    This can be run as a daemonized process or in a windows service"""
    
    def __init__(self, autodiscover=True):
        if os.name == 'posix':
            pass
        elif os.name == 'nt':
            pass
    
            
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
    
    if os.name == 'posix':
        daemonize('/dev/null','/tmp/daemon.log','/tmp/daemon.log')
        # do the main loop for the worker node
        #main()
    elif os.name == 'nt':
        import WorkerNodeService

    #c = wmi.WMI()
    
    #for disk in c.Win32_LogicalDisk (DriveType=3):
    #    print disk.Caption, "%0.2f%% free" % (100.0 * long (disk.FreeSpace) / long (disk.Size))
        
    #for share in c.Win32_Share ():
    #    print share.Name, share.Path


    #for opsys in c.Win32_OperatingSystem ():
    #    break

    #print opsys.Reboot
    #print opsys.Shutdown

    #hbt = HeartbeatThread()
    #hbt.setName('heartbeat')    
    #ekg = EKGThread()
    #ekg.setName('ekg')
    #hbt.start()
    #ekg.start()
    