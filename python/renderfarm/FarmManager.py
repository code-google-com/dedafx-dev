import wmi, threading, time, socket, struct

HB_PORT = 8085

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
            
            s.sendto("DEDAFX", (host, HB_PORT))

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

    hbt = HeartbeatThread()
    hbt.setName('heartbeat')    
    ekg = EKGThread()
    ekg.setName('ekg')
    hbt.start()
    ekg.start()
    