import win32serviceutil
import win32service
import win32event

from vineyard.FarmManager import WorkerNodeDaemon
import cherrypy

class VinyardService(win32serviceutil.ServiceFramework):
	_svc_name_ = 'VineyardService'
	_svc_display_name_ = 'Vineyard Service'
	
	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.stop_event = win32event.CreateEvent(None, 0, 0, None)
		self.daemon = WorkerNodeDaemon()

	def SvcDoRun(self):
		self.daemon.start()
		if cherrypy.__version__[:3] == '3.0' or cherrypy.__version__[0] == '2':
			win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

		
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.daemon.stop()
		win32event.SetEvent(self.stop_event)
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
    
if __name__ == '__main__':
	win32serviceutil.HandleCommandLine(VinyardService)
