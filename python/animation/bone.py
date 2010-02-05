from node import Node, Scene, BaseRenderable
from euclid import * # this is all of the geometric classes

class Bone(Node):
    """Base Bone class
    
        >>> b = Bone("MyBone")         
        >>> b.name        
        'MyBone'
        >>> b.position.x = 10.0
        >>> b.bind_position
        Point3(0.00, 0.00, 0.00)
        >>> b.position
        Point3(10.00, 0.00, 0.00)
        >>> b.reset()
        >>> b.position
        Point3(0.00, 0.00, 0.00)
    """
    
    def __init__(self, name):
        Node.__init__(self, name)
        self.bind_position = Point3(self.position.x, self.position.y, self.position.z)
        self.bind_orientation = Quaternion(self.orientation.w, self.orientation.x, self.orientation.y, self.orientation.z)
        self.bind_scale = Point3(self.scale.x, self.scale.y, self.scale.z)
        
    def reset(self):
        self.position.x = self.bind_position.x
        self.position.y = self.bind_position.y
        self.position.z = self.bind_position.z
        
        self.orientation.w = self.bind_orientation.w
        self.orientation.x = self.bind_orientation.x
        self.orientation.y = self.bind_orientation.y
        self.orientation.z = self.bind_orientation.z
        
        self.scale.x = self.bind_scale.x 
        self.scale.y = self.bind_scale.y
        self.scale.z = self.bind_scale.z
        
    
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()