import threading, time, socket, struct, os, sys, collections, platform
from vineyard.models import Session, WorkerNode, metadata, engine
from Queue import Queue
import cherrypy, simplejson, urllib
from vineyard import __version__, AUTODISCOVERY_PORT, STATUS_PORT, FarmConfig
import vineyard
import vineyard.engines
from vineyard.engines.BaseEngines import EngineRegistry
if os.name == 'nt':
    try:
        from _winreg import *
    except:
        pass

# this is an ugly global, but useful when the domain of the subnet is outside the control of the user
# when the worker node tries to get it's ip address, this global means that the node will use the socket.getfqdn() in retrieving the ip
# otherwise it will use, and continue to use socket.gethostname() in ip retrieval
__useFullyQualifiedDomainName__ = True

# default to a short timeout on the status polling
#(TODO) set this with a configuration setting
socket.setdefaulttimeout(1.0)

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
            self._stop.wait(1.0)

    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()
    
class JobQueueThread(threading.Thread):
    """Watch and process jobs in the job queue"""
    
    def __init__(self):
        super(JobQueueThread, self).__init__()
        self._stop = threading.Event()  
        self._working = threading.Event()
        self.input_queue = Queue()    
        session = Session()
        metadata.create_all(engine)
    
    def run(self):       
        while not self.isStopped(): 
            if not self.input_queue.empty():
                self._working.set()
                
                # do something with the job
                job = self.input_queue.get()
                
                try:
                    print "job received, processing", job["job"]
                    eng = EngineRegistry.getEngineByName(job["job"])
                except KeyError, e:
                    print "Key Error", e
                    
                if eng:
                    try:
                        proc = eng.run(job)
                        while proc.returncode == None:
                            time.sleep(1)
                        print 'process returncode:', proc.returncode
                    except Exception, e:
                        print "<ERROR>", e
                
                self._working.clear()
            
            self._stop.wait(5.0)

    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()
    
    # job is a dict {"job":"engine name", **kwargs}
    def addJob(self, job):
        self.input_queue.put(job)
        
    def isWorking(self):
        return self._working.isSet()
              
            
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
        while not self.isStopped():
            try:
                data, addr = s.recvfrom(1024)
                if data == 'DEDAFX-NODE':
                    # filter out known addresses
                    if addr in self.known_addrs:
                        continue
                    else:
                        self.queue.put(addr)
                    
                time.sleep(1)
                self.updateKnownAddrs()
            except:
                pass # probably just a socket timeout
            
            self._stop.wait(3.0)
                    
                    
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
        while not self.isStopped():
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
                    ret = urllib.urlopen(url)
                    #print ret.info()
                    #print "ret=",  ret
                    result = simplejson.load(ret)
                    
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
                        
                        try:
                            session.commit()
                        except IntegrityError, e:
                            print e
                            pass
                    else:
                        #print 'error with status-info from wroker node', addr, result['name'], result['mac_address'], result
                        print type(result)
                        nme = u'name'
                        print "result[nme]", result[nme]
                        for i in result:
                            print result.i, type(result[i])
                            if i == 'name':
                                print result[i]
            
            self._stop.wait(1.0)
        
    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()
    
def loadPlugins():
    if os.path.exists("./plugins"):
        p = os.path.abspath("./plugins")
    else:
        if os.name == 'nt':
            # we might be running as a service. 
            # check the windows registry for the install directory and pre-pend the plugin path with the install path
            try:
                #from _winreg import *
                aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
                aKey = OpenKey(aReg, r"SOFTWARE\DedaFX\Vineyard") 
                val = EnumValue(aKey, 0)
                pf = str(val[1])
                if val[0] == 'InstallDir' and os.path.exists(os.path.abspath(os.path.join(pf, "plugins"))):
                    p = os.path.abspath(os.path.join(pf, "plugins"))
                else:
                    return False
            except:
                return False
        else:
            return False
        
    #print p
    sys.path.append(p)
    pa = os.listdir(p)
    paa = []
    def fn2mod(f): 
        if (os.path.splitext(f)[1][:3].lower() == '.py') : 
            return os.path.splitext(f)[0] 
    for i in pa:
        if i[0] != '.':
            n = fn2mod(i)
            if n and not n in paa:
                paa.append(n)
    #print paa
    for plugin in paa:
        try:
            print 'loading', plugin
            __import__(plugin)
        except Exception, e:
            print '<error>', e, plugin
            raise
                
class NodeCache(object): 
    
    def __init__(self):
        """check for a local db, otherwise initialize it
        or, get the network db node cache, raise on fail"""
        
        # load plugins
        # these are ususally additional render engines or background processing threads
        loadPlugins()
                               
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
        try:
            self.nq.stop()
        except:
            pass
        
        try:
            self.autodisc.stop()
        except:
            pass
        
        try:
            self.statusupdate.stop()
        except:
            pass
        
    def restart(self):
        try:
            self.autodisc.stop()
        except: 
            pass
        self.autodiscover()
        
        # restart the status update thread
        self.statusupdate.stop()
        time.sleep(5)
        self.statusupdate.start()
        
    def autodiscover(self):
        if vineyard.AUTODISCOVERY_ON:
            self.autodisc.start()
        else:
            try:
                self.autodisc.stop()
            except: pass    
            
    def submitJob(self, job, **kwargs):
        # get the local file of the engine def
        led = EngineRegistry.getLocalEngineDef(job.engine)
        if led:
            pass
        # create a Job and Task entry in the local database, status is 'submitted'
        # get all nodes with the correct engine, the correct pool, and sorted by priority from the local db
        # iterate, trying to submit to each, continue on fail
        # if all fail, report queue failure, else log job status as 'queued', and set the job's 
        # upload the local engine file, verify it's the same as the one on the target machine (as it could be a different version)
        # send the **kargs to the target machine
        
        # 
        pass
        
            
    def update(self):
        """This updates the memory array with the data from the database"""
        self.nodes = []
        for i in self.session.query(WorkerNode).all(): 
            engines = ""
            if type(i.engines) == list:
                for e in range(len(i.engines)):
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
    """This thread is used by the Vineyard Manager to keep the local database up to date with the system.
    It only runs while the manager gui is running, either full window or in the taskbar."""
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.session = Session()
        metadata.create_all(engine)
        self._stop = threading.Event()
    
    def run(self):
        while not self.isStopped():
            try:
                self.__updateAllNodes()
            except: pass
            time.sleep(vineyard.STATUS_UPDATE_PERIOD)
            self._stop.wait(1.0)
        print 'status update thread stopping.'
            
    def __updateAllNodes(self):
        starttime = time.clock()
        for node in self.session.query(WorkerNode).all(): 
            node.status = self.__update(node)
        self.session.commit()
        print 'status update timer:', time.clock()-starttime
            
            
    def __update(self, node):
        try:
            url = "http://"+str(node.ip_address)+":"+str(vineyard.STATUS_PORT)
            result = simplejson.load(urllib.urlopen(url))
            
            if result['name']: 
                node.name = str(result['name'])
            if result['mac_address']: 
                node.mac_address = str(result['mac_address'])
            if result['ip_address']:
                node.ip_address = str(result['ip_address'])
            if result['platform']:
                node.platform = str(result['platform'])
            if result['pools']:
                node.pools = str(result['pools'])
            if result['version']:
                node.version = str(result['version'])
            if result['cpus']:
                node.cpus = int(result['cpus'])
            if result['priority']:
                node.priority = int(result['priority'])
            
            engines = ""
            if result['engines']:
                if type(result['engines']) == list:
                    for e in range(len(result['engines'])):
                        engines += str(result['engines'][e])
                        if e < len(result['engines'])-1:
                            engines += ", "
                else:
                    engines = str(result['engines'])
            node.engines = engines
                        
            if result['status']:
                return result['status']
            else:
                return 'offline'
        except Exception, e:
            return 'offline'
        
    def stop(self):
        self._stop.set()
        
    def isStopped(self):
        return self._stop.isSet()

                
class WorkerNodeConfigurationServer(object):
    """used to set configuration settings for a worker node
    
    (TODO:) Can only be run locally by anyone, or remotely by an administrator."""
    
    def index(self):
        return ""
    index.exposed = True
    
    
class WorkerNodeHttpServer(object):
    def index(self):
        starttime = time.clock()
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if os.name == 'nt':
            nm = os.getenv('COMPUTERNAME')
            if not nm or nm.strip() == '':
                nm = platform.node()
            procs = os.getenv('NUMBER_OF_PROCESSORS')
        else:
            nm = os.getenv('HOSTNAME')
            if not nm or nm.strip() == '':
                nm = platform.node()
            import multiprocessing            
            procs = multiprocessing.cpu_count()
        status = "waiting"
        if __JOBQUEUE_THREAD__.isWorking():
            status = "busy"
        pluginFolder = ""
        if os.path.exists("./plugins"):
            pluginFolder = os.path.abspath("./plugins")
        else:
            if os.name == 'nt':
                # we might be running as a service. 
                # check the windows registry for the install directory and pre-pend the plugin path with the install path
                try:
                    #from _winreg import *
                    aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
                    aKey = OpenKey(aReg, "SOFTWARE\\DedaFX\\Vineyard") 
                    val = EnumValue(aKey, 0)
                    pf = str(val[1])
                    if val[0] == 'InstallDir' and os.path.exists(os.path.abspath(os.path.join(pf, "plugins"))):
                        pluginFolder = os.path.abspath(os.path.join(pf, "plugins"))
                except Exception, e:
                    pluginFolder = e
        ip = ''
        
        global __useFullyQualifiedDomainName__
        try:
            if __useFullyQualifiedDomainName__:
                ip = str(socket.gethostbyname(socket.getfqdn()))
                __useFullyQualifiedDomainName__ = True
        except: 
            __useFullyQualifiedDomainName__ = False
            try:
                ip = str(socket.gethostbyname(socket.gethostname()))
            except: pass
                    
        ret = simplejson.dumps({"name":nm, 
                                 "status":status, 
                                 "ip_address":ip,
                                 "mac_address":"",
                                 "platform":sys.platform,
                                 "pools":"",
                                 "version":__version__,
                                 "cpus":procs,
                                 "priority":1,
                                 "engines":EngineRegistry.getEngineNames(enabled_only=True),
                                 "autodiscovery-on":(not __HEARTBEAT__.isStopped()),
                                 "debug":{"calltime":(time.clock()-starttime), 
                                          "plugin_folder":pluginFolder,
                                          "current_dir":os.getcwd()}
                                 })
        return ret
    index.exposed = True
    
    def status(self):
        return simplejson.dumps({"status":"waiting"})
    status.exposed = True
    
    ## some helper functions
    # all of these will be in the servers db file.
    # when the server boots, it should check for unfinished jobs, and try to resume them
    def getFinishedJobs(self, max_count=100):
        finishedJobs = []
        return finishedJobs
    
    def getQueuedJobs(self):
        queuedJobs = []
        return queuedJobs
    
    def getActiveJobs(self):
        activeJobs = []
        return activeJobs
    
    def jobs(self, maxFinishedJobs=100, finished=True, active=True, queued=True):
        """
        
        these are only jobs that this node has committed to manage. 
        not all tasks need to run on this node, but could.
        jobs must have at least one task, since a task is the real work involved with the job. job is just a grouping container.
        
        a job must be managed by one node, who delegates responsibility of each of the tasks of the job.
        
        """
        cherrypy.response.headers['Content-Type'] = 'application/json'
        finishedJobs = self.getFinishedJobs(maxFinishedJobs)
        activeJobs = self.getActiveJobs()
        queuedJobs = self.getQueuedJobs()
        return simplejson.dumps({"jobs":{"finished":finishedJobs, "active":activeJobs, "queued":queuedJobs}})
    jobs.exposed = True
    
    def submit(self, job=None, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if job:
            eng = EngineRegistry.getEngineByName(job)
            print job, eng
            if eng:
                try:
                    params = {"job":job}
                    params = dict(params, **kwargs)
                    print params
                    __JOBQUEUE_THREAD__.addJob(params)
                    return simplejson.dumps({'status':"success", 'description':"job submitted", 'kwargs':kwargs})
                except Exception, e:
                    return simplejson.dumps({'status':"failed", 'description':"Exception thrown during submittal. " + str(e), 'kwargs':kwargs})
            else:
                return simplejson.dumps({'status':"failed", 'description':"Engine not supported for this job type.", 'kwargs':kwargs})
        return simplejson.dumps({'status':"failed", 'description':"job is None! I cannot process a null job!", 'kwargs':kwargs})
    submit.exposed = True
    
    def lastResult(self):
        return "TODO: This will return the log if the render failed, or the image/movie that resulted from the last job performed"
    lastResult.exposed = True
    
__HEARTBEAT__ = HeartbeatThread()
__JOBQUEUE_THREAD__ = JobQueueThread()

class WorkerNodeDaemon(object):
    """the main worker node daemon class
    
    This can be run as a daemonized process or in a windows service"""
    
    def __init__(self):
        # load plugins
        loadPlugins()
                
        if not FarmConfig.load():
            FarmConfig.create()
        
        self.heartbeat = __HEARTBEAT__
        self.heartbeat.setName('Vineyard_heartbeat')  
        
        self.worker = __JOBQUEUE_THREAD__
    
    def __del__(self):
        try:
            self.stop()
        except: 
            pass
    
    def start(self):
        if vineyard.AUTODISCOVERY_ON:
            self.heartbeat.start()
        self.worker.start()
        
        cherrypy.tree.mount(WorkerNodeHttpServer(), '/')
        if cherrypy.__version__[0] == '2':
            #print cherrypy.root
            cherrypy.server.start()
        elif cherrypy.__version__[:3] == '3.0':
            cherrypy.server.quickstart()
            cherrypy.engine.start(blocking=False)
        elif cherrypy.__version__[:3] == '3.1':
            cherrypy.engine.start()
            cherrypy.engine.block()
        else:
            raise exception, "Unhandled cherrypy version! I need version 2 or version 3!"
        
    def stop(self):
        if cherrypy.__version__[:3] == '3.1':
            cherrypy.engine.exit()            
        else:
            cherrypy.server.stop()
        if not self.heartbeat.isStopped():
            self.heartbeat.stop()
        self.worker.stop()
    
            
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
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
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
    arg = ["-d"]
        
    #print EngineRegistry.getEngineNames(enabled_only=True)
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-d", "--daemon", dest="daemonize", help="daemonize a server process", action="store_true", default=False)
    (opts, args) = parser.parse_args()

    
    if not FarmConfig.load():
        FarmConfig.create()
    
    if opts.daemonize:
        daemon = WorkerNodeDaemon()
        daemon.start()
    else:
        import vineyard.gui.MainWindow as farmmgr
        
        farmmgr.run(sys.argv[1:])
       
        
    
