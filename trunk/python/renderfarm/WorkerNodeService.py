import win32serviceutil
import win32service
import win32event
import win32api

from renderfarm.FarmManager import WorkerNodeDaemon
import cherrypy

class WorkerNodeService(win32serviceutil.ServiceFramework):
	_svc_name_ = 'VineyardWorkerNodeService'
	_svc_display_name_ = 'Vineyard WorkerNode Service'
	
	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		# self.stop_event = win32event.CreateEvent(None, 0, 0, None)
		self.daemon = WorkerNodeDaemon()

	def SvcDoRun(self):
		self.daemon.start()
		
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.daemon.stop()
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)



def instart(cls, name, display_name=None, stay_alive=True):
	'''
        Install and  Start (auto) a Service
            
            cls : the class (derived from Service) that implement the Service
            name : Service name
            display_name : the name displayed in the service manager
            stay_alive : Service will stop on logout if False
	'''
	cls._svc_name_ = name
	cls._svc_display_name_ = display_name or name
	try:
		module_path=modules[cls.__module__].__file__
	except AttributeError:
		# maybe py2exe went by
		from sys import executable
		module_path=executable
	module_file=splitext(abspath(module_path))[0]
	cls._svc_reg_class_ = '%s.%s' % (module_file, cls.__name__)
	if stay_alive: win32api.SetConsoleCtrlHandler(lambda x: True, True)
	try:
		win32serviceutil.InstallService(
			cls._svc_reg_class_,
			cls._svc_name_,
			cls._svc_display_name_,
			startType=win32service.SERVICE_AUTO_START
		)
		print 'Install ok'
		win32serviceutil.StartService(
			cls._svc_name_
                )
		print 'Start ok'
	except Exception, x:
		print str(x)

    
if __name__ == '__main__':
	win32serviceutil.HandleCommandLine(WorkerNodeService)
