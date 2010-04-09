#!/usr/bin/python

import ConfigParser, os
from vineyard import AUTODISCOVERY_PORT, STATUS_PORT

def create():
    config = ConfigParser.ConfigParser()
    config.add_section('Ports')
    config.set('Ports', 'autodiscovery_port', str(AUTODISCOVERY_PORT))
    config.set('Ports', 'status_port', str(STATUS_PORT))
    with open('vineyard.cfg', 'wb') as configfile:
        config.write(configfile)

    
def load():
    if os.path.exists('vineyard.cfg'):
        config = ConfigParser.ConfigParser()
        config.read('vineyard.cfg')
        AUTODISCOVERY_PORT = config.getint('Ports', 'autodiscovery_port')
        STATUS_PORT = config.getint('Ports', 'status_port')
        return True
    else:
        return False

if __name__ == '__main__':
    create()