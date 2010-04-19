#!/usr/bin/python

import ConfigParser, os
import vineyard

def create():
    config = ConfigParser.ConfigParser()
    
    config.add_section('Global')
    config.set('Global', 'autodiscovery', vineyard.AUTODISCOVERY_ON)
    
    config.add_section('Manager')
    config.set('Manager', 'status_update_period', vineyard.STATUS_UPDATE_PERIOD)
    
    #config.add_section('Database')
    #config.set('Database', 'server', 'localhost')
    
    config.add_section('Ports')
    config.set('Ports', 'autodiscovery_port', str(vineyard.AUTODISCOVERY_PORT))
    config.set('Ports', 'status_port', str(vineyard.STATUS_PORT))
    
    with open('vineyard.cfg', 'wb') as configfile:
        config.write(configfile)

    
def load():    
    if os.path.exists('vineyard.cfg'):
        config = ConfigParser.ConfigParser()
        config.read('vineyard.cfg')
        
        vineyard.AUTODISCOVERY_ON = config.getboolean('Global', 'autodiscovery')
        
        vineyard.STATUS_UPDATE_PERIOD = config.getint('Manager', 'status_update_period')
        
        vineyard.AUTODISCOVERY_PORT = config.getint('Ports', 'autodiscovery_port')
        vineyard.STATUS_PORT = config.getint('Ports', 'status_port')
        
        return True
    else:
        create()
        return False

if __name__ == '__main__':
    create()