from distutils.core import setup
import py2exe

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "1.0.0"
        self.company_name = "DedaFX"
        self.copyright = "copyright 2010"
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
          "packages": ["sqlalchemy.databases", "sqlalchemy.dialects.sqlite"]
      }},
      windows=[
          {"script":"FarmManager.py",
          "icon_resources": [(1, "res/vineyard.ico")]
      }]
      )
