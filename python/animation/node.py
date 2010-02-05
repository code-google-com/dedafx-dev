from euclid import * # this is all of the geometric classes        
        
       
class BaseRenderable:
    """Base class of all renderable objects"""
    def __init__(self):
        self.verts = []
        self.polygons = []
        self.edges = []
        
    def draw(self):
        raise NotImplemented
        
class Scene:
    """Base scene graph"""
    def __init__(self):
        self.nodes = []
        
    def _update(self):
        for i in self.nodes:
            i._update()
            
class Node:
    """Base Node class
    
        >>> n = Node("something") 
        >>> isinstance(n, Node)
        True
        >>> print n.name
        something
        >>> n._update()
    """
    
    def __init__(self, name):
        self.position = Point3()
        self.orientation = Quaternion()
        self.scale = Point3()
        
        self.global_position = Point3()
        self.global_orientation = Quaternion()
        self.global_scale = Point3()
        
        self.children = []
        self.parent = None # root is parent when this is none!
        
        self.name = name
        self.geometry = None # this is the renderable geometry for this object, derived objects must set this
        self.bRender = False # render flag

        
    def _update(self):
        """Update self, then all of the children
            M is the parent xform matrix"""
            
        if self.parent and isinstance(self.parent, Node):
            gp = self.position + self.parent.position
            go = self.orientation + self.parent.orientation
            gs = self.scale + self.parent.scale
            
        for child in self.children:
            if isinstance(child, Node):
                child.update()


    def getXform(self):
        M = self.orientation.get_matrix()
        M = M.translate( self.position.x, self.position.y, self.position.z )
        M = M.scale( self.scale.x, self.scale.y, self.scale.z )
        return M
        
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()