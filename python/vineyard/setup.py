from distutils.core import setup
import py2exe
from vineyard import __VERSION__

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = __VERSION__
        self.company_name = "DedaFX"
        self.copyright = "Copyright 2010"
        self.name = "Vineyard Renderfarm"

vineyardService = Target(
    description = "Vineyard renderfarm worker node service",
    modules = ["VineyardService"],
    cmdline_style = 'pywin32',
    icon_resources = [(1, "res/vineyard.ico")]
    )

setup(service=[vineyardService],
      options={"py2exe" : {
          "includes": ["sip"],
          "packages": ["sqlalchemy.databases", "sqlalchemy.dialects.sqlite"],
          "zipfile":"lib.so"
      }},
      windows=[
          {"script":"FarmManager.py",
          "icon_resources": [(1, "res/vineyard.ico")]
      }]
      )
