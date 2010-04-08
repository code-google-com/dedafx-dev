from distutils.core import setup
import py2exe

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "1.0.0"
        self.company_name = "DedaFX"
        self.copyright = "copyright 2010"
        self.name = "Vinyard Renderfarm"

vinyardService = Target(
    description = "Vinyard renderfarm worker node service",
    modules=["WorkerNodeService"],
    cmdline_style='pywin32',
    )

setup(service=[vinyardService],
      options={"py2exe" : {
          #"includes": ["sip", "PyQt4.QtSql"],
          "packages": ["sqlalchemy.databases", "sqlalchemy.dialects.sqlite"]
      }})
