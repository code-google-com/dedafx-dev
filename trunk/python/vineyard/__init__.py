__all__ = ["FarmManager", "models", "WakeOnLan"]

__version__ = "1.0.0"
__VERSION__ = __version__

# globals
AUTODISCOVERY_ON = True

#manager
STATUS_UPDATE_PERIOD = 5

# default ports
# port to use for autodiscovery
AUTODISCOVERY_PORT = 13331
# port to use to query a node for its data as a json string
STATUS_PORT = 18088 