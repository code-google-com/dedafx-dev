#!/usr/bin/python

import ConfigParser, os
import vineyard

config = ConfigParser.ConfigParser()

def create():
  
    if not config.has_section('Global'):
        config.add_section('Global')
    config.set('Global', 'autodiscovery', vineyard.AUTODISCOVERY_ON)
    
    if not config.has_section('Manager'):
        config.add_section('Manager')
    config.set('Manager', 'status_update_period', vineyard.STATUS_UPDATE_PERIOD)
    
    #config.add_section('Database')
    #config.set('Database', 'server', 'localhost')
    
    if not config.has_section('Ports'):
        config.add_section('Ports')
    config.set('Ports', 'autodiscovery_port', str(vineyard.AUTODISCOVERY_PORT))
    config.set('Ports', 'status_port', str(vineyard.STATUS_PORT))
    
    with open('vineyard.cfg', 'wb') as configfile:
        config.write(configfile)

    
def load():    
    if os.path.exists('vineyard.cfg'):
        config.read('vineyard.cfg')
        
        if config.has_section('Global'):
            vineyard.AUTODISCOVERY_ON = config.getboolean('Global', 'autodiscovery')
        else:
            config.add_section('Global')
            config.set('Global', 'autodiscovery', vineyard.AUTODISCOVERY_ON)
        
        if config.has_section('Manager'):
            vineyard.STATUS_UPDATE_PERIOD = config.getint('Manager', 'status_update_period')
        else:
            config.add_section('Manager')
            config.set('Manager', 'status_update_period', vineyard.STATUS_UPDATE_PERIOD)
        
        if config.has_section('Ports'):
            vineyard.AUTODISCOVERY_PORT = config.getint('Ports', 'autodiscovery_port')
            vineyard.STATUS_PORT = config.getint('Ports', 'status_port')
        else:
            config.add_section('Ports')
            config.set('Ports', 'autodiscovery_port', str(vineyard.AUTODISCOVERY_PORT))
            config.set('Ports', 'status_port', str(vineyard.STATUS_PORT))

        # re-create just to make sure missing config options are added as defaults
        with open('vineyard.cfg', 'wb') as configfile:
            config.write(configfile)           
        return True
    else:
        create()
        return False
    
def setEngineData(engineName, data):
    if os.path.exists('vineyard.cfg'):
        config.read('vineyard.cfg')
    if not config.has_section(engineName):
        config.add_section(engineName)
    for (name, val) in data:
        config.set(engineName, name, val)
    with open('vineyard.cfg', 'wb') as configfile:
        config.write(configfile)
    
def getEngineData(engineName):
    _data = []
    if os.path.exists('vineyard.cfg'):
        config.read('vineyard.cfg')        
    if config.has_section(engineName):
        _data = config.items(engineName)            
    return _data

if __name__ == '__main__':
    create()