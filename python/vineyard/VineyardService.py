import win32serviceutil
import win32service

from vineyard.FarmManager import WorkerNodeDaemon

class VinyardService(win32serviceutil.ServiceFramework):
	_svc_name_ = 'VineyardService'
	_svc_display_name_ = 'Vineyard Service'
	
	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.daemon = WorkerNodeDaemon()

	def SvcDoRun(self):
		self.daemon.start()
		
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.daemon.stop()
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
    
if __name__ == '__main__':
	win32serviceutil.HandleCommandLine(VinyardService)
