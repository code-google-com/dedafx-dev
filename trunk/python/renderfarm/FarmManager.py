import threading, time, socket, struct
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
    """Broadcast a heartbeat packet on specified port"""
    
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

            n += 1
            if n > 5:
                running = False
                
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
        known_addresses = [] # should be filled from info in the db, if available
        while 1:
            data, addr = s.recvfrom(1024)
            if data == 'DEDAFX-NODE':
                # filter out known addresses
                if addr in known_addresses:
                    continue
                else:
                    print addr, ' ', data
                    known_addresses.append(addr)
                    __nodeQueue.put(addr)
            
class NodeQueueProcessingThread(threading.Thread):
    
    def run(self):
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
            for instance in self.session.query(WorkerNode).order_by(WorkerNode.id): 
                print instance.name, instance.fullname
        except Exception, e:
            pass
        
        
        self.initializeLocalNodeCache()

    
    def initializeLocalNodeCache(self):
        """Broadcast magic packet and wait for responses from all the nodes running on the network.
        Use the recieved packets to get address information that can be used to inquire more detail about the node.
        
        Store the node information in the local sqlite database."""        
        
        # broadcast magic packet on AUTODISCOVERY_PORT
        # get all responses over a few seconds (3s or less), store in local array
        # query each node for their node cache and store/verify local cache        
        
        pass


if __name__ == '__main__':
    machine = ''
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
    