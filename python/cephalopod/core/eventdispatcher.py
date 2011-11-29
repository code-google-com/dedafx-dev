#!/usr/bin/env python
#coding:utf-8
################################################################################
##
##    Creator:   Ben Deda
##    Created:   11/28/2011
##    Project:   Cephalopod
##    Copyright (c) DedaFX 2011
##

"""
The EventDispatcher class definition
"""

import socket, time, uuid
import unittest

import zmq
from threading import Thread
from Queue import Queue, Empty


#-------------------------------------------------------------------------------
def CanBindToAddr(sock, addr, port):
    """Test to see if we can bind to the address with the given zmq socket"""
    try:
        sock.bind('%s:%i'%(addr, port))
        sock.close()           
        return True
    except zmq.ZMQError:
        return False
    
#-------------------------------------------------------------------------------
def CanPublishToAddr(addr, port):
    """
    Simple check used to find an open port that can be published to
    """
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUB)
    return CanBindToAddr(s, addr, port)              

#===============================================================================
class Messenger(Thread):
    """
    Worker thread for polling messages and handling 
    incoming and outgoing message queues.
    """
    
    #---------------------------------------------------------------------------
    def __init__(self, qIn, qOut, inType=zmq.SUB, outType=zmq.PUB):
        super(Messenger, self).__init__()

        self._in_binds = list()
        self._in_connects = list()
        self._in_sockopts = list()
        self._out_binds = list()
        self._out_connects = list()
        self._out_sockopts = list()
        self.daemon = True
        
        # queues exist in the main thread and need to be shared with this thread
        self._qIn = qIn
        self._qOut = qOut
        self._inType = inType
        self._outType = outType
        self._stop = False
        self._context = None
        
    #--------------------------------------------------------------------------
    def AddOutAddr(self, addr, port):
        """
        Add an output address and port to the bind list.
        """
        self._out_binds.append('%s:%i'%(addr, port))
    
    #--------------------------------------------------------------------------
    def AddInAddr(self, addr, port):
        """
        Add input address and port to the connect list.
        """
        self._in_connects.append('%s:%i'%(addr, port))
            
    #--------------------------------------------------------------------------
    def AddSockOpt(self, opt, inOpt=True):
        """
        Add a tuple of socket options to either the input or output sockets
        """
        if inOpt:
            self._in_sockopts.append(opt)
        else:
            self._out_sockopts.append(opt)
        
    #--------------------------------------------------------------------------
    def _setup_sockets(self):
        """Set up the sockets for the zeromq interface"""
        
        self._context = zmq.Context()
        
        # create the sockets
        ins = self._context.socket(self._inType)
        outs = self._context.socket(self._outType)
        
        # set sockopts (must be done first, in case of zmq.IDENTITY)
        for opt, value in self._in_sockopts:
            ins.setsockopt(opt, value)
        for opt, value in self._out_sockopts:
            outs.setsockopt(opt, value)
        
        for addr in self._in_binds:
            ins.bind(addr)
        for addr in self._out_binds:
            outs.bind(addr)
        
        for addr in self._in_connects:
            ins.connect(addr)
        for addr in self._out_connects:
            outs.connect(addr)
        
        return ins, outs

    #--------------------------------------------------------------------------
    def run(self):   
        """Run the messaging loop to handle socket communications"""
       
        ins, outs = self._setup_sockets()
        poller = zmq.Poller()
        
        poller.register( ins, zmq.POLLIN )
        poller.register( outs, zmq.POLLOUT )
                
        while not self._stop:
            
            socks = dict(poller.poll())
            
            if socks.get(ins) == zmq.POLLIN:
                try:
                    e = ins.recv_json()
                    if not self._qIn.full():
                        self._qIn.put_nowait(e)  
                except ValueError: 
                    # Probably not a JSON formatted packet
                    pass
                    
            if socks.get(outs) == zmq.POLLOUT:
                # take events from the outgoing queue and publish them
                if not self._qOut.empty():
                    try:
                        while not self._qOut.empty():
                            e = self._qOut.get_nowait()
                            outs.send_json(e)
                    finally: pass
                else:
                    time.sleep(0.01)
              
    #--------------------------------------------------------------------------
    def stop(self):
        """Stop the messenger"""
        self._stop = True
        
    #--------------------------------------------------------------------------
    @property
    def isRunning(self):
        """Return true or false if the messenger is running"""
        return self._stop == False
        
            
#==============================================================================
class Heartbeat(Thread):
    """
    This is the UDP heartbeat for discovering other 
    remote systems that we can communicate with.
    """
    
    KEY = 'CFHEARTBEAT'
    DEAD = 666
    
    #--------------------------------------------------------------------------
    def __init__(self, nodesDict, port=8383, interval=1.0):
        """Constructor"""
        
        super(Heartbeat, self).__init__()
        self.daemon = True
        self._stop = False
        self.interval = max(0.1, float(interval)) # lets be realistic...
        
        self.nodes = nodesDict # tracking of nodes. dicts are threadsafe        
        self.localIp = socket.gethostbyname(socket.gethostname())
        
        self.host = '<broadcast>'
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.settimeout(self.interval)
        self.socket.bind(('', self.port))
        
    #--------------------------------------------------------------------------
    def run(self):
        """Run the thread"""
        
        def BeatHeart(s):
            while True:
                s.sendto( Heartbeat.KEY, (self.host, self.port) )
                time.sleep(self.interval)

        hbsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        hbsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        hbsock.settimeout(self.interval)
        
        # start a slave thread that send out a hearbeat packet every interval
        hbt = Thread(target=BeatHeart, args=(hbsock,))
        hbt.daemon = True
        hbt.start()
        
        while not self._stop:

            sTime = time.time()
            
            # recv all the beats
            while True:
                try:
                    msg, addr = self.socket.recvfrom(16)
                    ip, = addr
                    if msg.startswith(Heartbeat.KEY):
                        self.nodes[ip] = time.time()
                    t = (time.time() - sTime)
                    if t < self.interval:
                        break
                except socket.timeout:
                    break # no other heartbeats
                
            for ip in self.nodes:
                if self.nodes[ip] != Heartbeat.DEAD:
                    t = abs(self.nodes[ip]-sTime)
                    if t > 3 * self.interval:
                        self.nodes[ip] = Heartbeat.DEAD
    
    #--------------------------------------------------------------------------
    def stop(self):
        """
        Stop the heartbeat thread.
        """
        self._stop = True
        


#==============================================================================
class EventDispatcher(object):
    """
    Class definition for EventDispatcher.
    
    This class handles:
        1. event handler registration/deregistration for the local process
        2. queue events to be handled locally or dispatched 
           through the messenger
    """
    
    INPORTS = (8380, 8381, 8382, 8383, 8384, 8385, 8386, 8387, 8388, 8389, 8390)
    
    _ipAddr = socket.gethostbyname(socket.gethostname())
    _localAddr = '127.0.0.1'
    _protocol = 'tcp'
      
    #--------------------------------------------------------------------------
    def __init__(self, channel='', inports=None, outport=None):
        """
        Constructor

        When outport is None, it will find the next available port in the 
            inport list that it can bind to, and use that port.
        When outport is defined, it will try to use that port and raise 
            if it cannot bind to it.
        
        inports: a list of port numbers to use as subscriber ports, 
            or None to use the default defined in the class
        
        """
        
        super(EventDispatcher, self).__init__()
        
        inAddr = '%s://%s' % (self._protocol, self._localAddr)
        outAddr = '%s://*' % self._protocol
        
        if inports == None:
            inports = self.INPORTS
        if outport == None:
            for p in inports:
                if CanPublishToAddr(outAddr, p):
                    outport = p
                    inports = list(inports)
                    inports.remove(p)
                    break
        elif outport in inports:
            inports = list(inports)
            inports.remove(outport)
            
        if outport == None:
            raise RuntimeError('Cannot find a port in range to publish to!')
        self.outport = outport
        self.inports = inports

        self._listeners = {}
        self._uuid = str(uuid.uuid1())
        
        # The mailbox queues
        self._inEvents = Queue() # coming in from the network
        self._outEvents = Queue() # going out to local processes              
        
        self._messenger = Messenger(self._inEvents, self._outEvents)
        
        # set up the socket addresses to use
        self._messenger.AddOutAddr(outAddr, self.outport)
        
        for port in self.inports:
            self._messenger.AddInAddr(inAddr, port)
        self._messenger.AddSockOpt((zmq.SUBSCRIBE, str(channel)))
        
        self._messenger.start()
            
        
    #--------------------------------------------------------------------------
    @property
    def guid(self):
        """the guid of this node/process"""        
        return self._uuid
        
    #--------------------------------------------------------------------------
    @property
    def localAddr(self):
        """The local address of this node"""        
        return self._localAddr
    
    #--------------------------------------------------------------------------
    @property
    def ipAddr(self):
        """the ip address of this node"""        
        return self._ipAddr
    
    #--------------------------------------------------------------------------
    #@property
    #def liveNodes(self):
    #    """
    #    This is only useful when we have a heartbeat 
    #    and are listening for other nodes
    #    """
    #    
    #    return [n for n in self.nodes if self.nodes[n] != Heartbeat.DEAD]
    
    #--------------------------------------------------------------------------
    #@property
    #def deadNodes(self):
    #    """
    #    This is only useful when we have a heartbeat and 
    #    are listening for other nodes
    #    """
    #    
    #    return [n for n in self.nodes if self.nodes[n] == Heartbeat.DEAD]
            
    #--------------------------------------------------------------------------
    def Kill(self):
        """Kill the messenger"""        
        self._messenger.stop()
        
    #--------------------------------------------------------------------------
    def AddEventListener(self, eventType, callback):
        """
        Add an event listener to the internal lists. 
        These are callable functions within this process.
        """

        if not callable(callback):
            raise TypeError('callback needs to be a callable function that accepts the event as a parameter!')
        if eventType not in self._listeners:
            self._listeners[eventType] = list()
        if callback not in self._listeners[eventType]:
            self._listeners[eventType].append(callback)
            
    #--------------------------------------------------------------------------
    def HasEventListener(self, eventType):
        """Check if a listener for the event type exists"""  
        
        return eventType in self._listeners and len(self._listeners[eventType]) > 0
    
    #--------------------------------------------------------------------------
    def RemoveEventListener(self, eventType, callback):
        """Remove the event listener"""
        
        if eventType in self._listeners:
            if callback in self._listeners[eventType]:
                self._listeners[eventType].remove(callback)            
            
    #--------------------------------------------------------------------------
    def Update(self):
        """
        Update tick to pump events through.
        
        Call this within the main loop to properly dispatch events.
        """
        
        try:
            while 1:
                evt = self._inEvents.get_nowait()
                self.HandleEvent(evt)
        except Empty:
            pass
            
    #--------------------------------------------------------------------------
    def DispatchEvent(self, event, inproc=False):
        """Dispatch an event, unbiased regarding event object type."""
       
        if inproc:
            self._inEvents.put_nowait(event)
        else:
            self._outEvents.put_nowait(event)
                
    #--------------------------------------------------------------------------
    def Tell(self, event, toNodeGuid):
        """Tell a specific node of an event"""
        
        # raises a TypeError if event is not a dict-like object
        event['toNode'] = toNodeGuid
            
        if toNodeGuid == self.guid:
            self.DispatchEvent(event, True)
        else:
            self.DispatchEvent(event, False)
        
    #--------------------------------------------------------------------------
    def HandleEvent(self, event):
        """handle the events locally with the local handlers/listeners"""

        if 'toNode' in event and event['toNode'] != self.guid:                                       
            return # not an event for me! 
                    
        for key in event:
            if key in self._listeners:
                for cb in self._listeners[key]:
                    # call the callback with the event as the argument
                    cb(event) 
                        

# ==========================================================================
class TestEventDispatcher(unittest.TestCase):
    """Unittest test case for the EventDispatcher class"""
        
    def test_correctDefaultPorts(self):
        ed = EventDispatcher()
        self.assertTrue(ed.outport == 8380)
        self.assertFalse(8380 in ed.inports)
        self.assertTrue(len(ed.inports) == 10)
        ed.Kill()
        time.sleep(0.2)
        del ed
        
    def test_correctCustomPorts(self):
        ed = EventDispatcher(inports=(11380, 11381, 11382), outport=11380)
        self.assertTrue(ed.outport == 11380)
        self.assertFalse(11380 in ed.inports)
        self.assertTrue(len(ed.inports) == 2)
        self.assertTrue(11381 in ed.inports)
        self.assertTrue(11382 in ed.inports)
        ed.Kill()
        time.sleep(0.2)
        del ed
    
    
# ===========================================================================
class TestMessenger(unittest.TestCase):
    """Test the messenger"""
    
    def test_threadMessenger(self):
        
        qIn = Queue()
        qOut = Queue()
        
        tm = Messenger(qIn, qOut)
        inAddr, inPort = 'tcp://127.0.0.1', 5567
        outAddr, outPort = 'tcp://127.0.0.1', 5568
        
        tm.AddOutAddr('tcp://*', outPort)        
        tm.AddInAddr(inAddr, inPort)
        tm.AddSockOpt((zmq.SUBSCRIBE, ''))
        
        tm.start()
        time.sleep(1) # give the thread time to start
    
        # test subscribing to the event messages that are going out
        ctx = zmq.Context()
        sub = ctx.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, '')
        sub.connect('%s:%i' % (outAddr, outPort))
        time.sleep(0.1) # give the sub socket time to initialize
        
        for i in range(10):
            # que up an outgoing messaage
            msg1 = {'test':'message%i'%i}
            qOut.put_nowait(msg1)
            # get the message in our "remote" socket
            msg2 = sub.recv_json()
            self.assertTrue(msg1 == msg2)
            
        # test multiple messages getting queued before checking the responses
        for i in range(10):
            # que up an outgoing messaage
            msg1 = {'test':'message%i'%i}
            qOut.put_nowait(msg1)
            
        for i in range(10):
            # get the message in our "remote" socket. 
            # this will block until a message is received
            msg2 = sub.recv_json()
            self.assertTrue(msg2['test'].startswith('message'))
             
        # now send some events in and check the qIn for them
        pub = ctx.socket(zmq.PUB)
        pub.bind('%s:%i' % (inAddr, inPort))
        time.sleep(0.2)
        
        for i in range(10):
            msg1 = {'testevent':'message%i'%i}
            pub.send_json(msg1)
            sz = qIn.qsize()
            starttime = time.time()
            while sz < 1:
                time.sleep(0.1)
                sz = qIn.qsize()
                if time.time()-starttime > 1.0:
                    break
            self.assertTrue(sz == 1)
            self.assertTrue(qIn.get_nowait() == msg1)
            
    
if __name__=='__main__':
    unittest.main()
