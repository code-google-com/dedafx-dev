#__all__ = ["AfterEffectsEngine","3DelightEngine"]

from vineyard.engines.AfterEffectsEngine import *
try:
    ae_cs4_engine = AfterEffectsCS4Engine()
except Exception, e:
    print e

from vineyard.engines.DelightEngine import *
try:
    delight_engine = DelightEngine()
except Exception, e:
    print e

def getEngineList():
    ret = []
    
    try:
        ae_cs4_engine = AfterEffectsCS4Engine(False)
        ret.append(ae_cs4_engine)
    except Exception, e:
        print e
        
    try:
        delight_engine = DelightEngine(False)
        ret.append(delight_engine)
    except Exception, e:
        print e
    
    return ret
