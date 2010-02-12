from struct import *


# OPCODES!
HEADER_OPCODE = 1
GROUP_OPCODE = 2
OBJECT_OPCODE = 4
FACE_OPCODE = 5
PUSH_LEVEL_OPCODE = 10
POP_LEVEL_OPCODE = 11
DOF_OPCODE = 14
PUSH_SUBFACE_OPCODE = 19
POP_SUBFACE_OPCODE = 20
PUSH_EXTENSION_OPCODE = 19
POP_EXTENSION_OPCODE = 20
CONTINUATION_OPCODE = 23
COMMENT_OPCODE = 31
COLOR_PALETTE_OPCODE = 32
LONG_ID_OPCODE = 33
MATRIX_OPCODE = 49
VECTOR_OPCODE = 50
MULTITEXTURE_OPCODE = 52
UV_LIST_OPCODE = 53
BSP_OPCODE = 55
REPLICATE_OPCODE = 60
INSTANCE_REFERENCE_OPCODE = 61
INSTANCE_DEFINITION_OPCODE = 62
XREF_OPCODE = 63
TEXTURE_PALETTE_OPCODE = 64
VERTEX_PALETTE_OPCODE = 67
VERTEX_COLOR_OPCODE = 68
VERTEX_COLOR_NORMAL_OPCODE = 69
VERTEX_COLOR_NORMAL_UV_OPCODE = 70
VERTEX_COLOR_UV_OPCODE = 71
VERTEX_LIST_OPCODE = 72
LOD_OPCODE = 73
BOUNDING_BOX_OPCODE = 74
ROTATE_ABOUT_EDGE_OPCODE = 76
TRANSLATE_OPCODE = 78
SCALE_OPCODE = 79
ROTATE_ABOUT_POINT_OPCODE = 80
ROTATE_SCALE_TO_POINT_OPCODE = 81
PUT_OPCODE = 82
EYEPOINT_TRACKPLANE_PALETTE_OPCODE = 83
MESH_OPCODE = 84
LOCAL_VERTEX_POOL_OPCODE = 85
MESH_PRIMITIVE_OPCODE = 86
ROAD_SEGMENT_OPCODE = 87
ROAD_ZONE_OPCODE = 88
MORPH_VERTEX_LIST_OPCODE = 89
LINKAGE_PALETTE_OPCODE = 90
SOUND_OPCODE = 91
ROAD_PATH_OPCODE = 92
SOUND_PALETTE_OPCODE = 93
GENERAL_MATRIX_OPCODE = 94
TEXT_OPCODE = 95
SWITCH_OPCODE = 96
LINE_STYLE_PALETTE_OPCODE = 97
CLIP_REGION_OPCODE = 98
EXTENSION_OPCODE = 100
LIGHT_SOURCE_OPCODE = 101
LIGHT_SOURCE_PALETTE_OPCODE = 102
RESERVED103_OPCODE = 103
RESERVED104_OPCODE = 104
BOUNDING_SPHERE_OPCODE = 105
BOUNDING_CYLINDER_OPCODE = 106
BOUNDING_CONVEX_HULL_OPCODE = 107
BOUNDING_VOLUME_CENTER_OPCODE = 108
BOUNDING_VOLUME_ORIENTATION_OPCODE = 109
RESERVED110_OPCODE = 110
LIGHT_POINT_OPCODE = 111
TEXTURE_MAPPING_PALETTE_OPCODE = 112
MATERIAL_PALETTE_OPCODE = 113
NAME_TABLE_OPCODE = 114
CAT_OPCODE = 115
CAT_DATA_OPCODE = 116
RESERVED117_OPCODE = 117
RESERVED118_OPCODE = 118
BOUNDING_HISTOGRAM_OPCODE = 119
RESERVED120_OPCODE = 120
RESERVED121_OPCODE = 121
PUSH_ATTRIBUTE_OPCODE = 122
POP_ATTRIBUTE_OPCODE = 123
RESERVED124_OPCODE = 124
RESERVED125_OPCODE = 125
CURVE_OPCODE = 126
ROAD_CONSTRUCTION_OPCODE = 127
LIGHT_POINT_APPEARANCE_PALETTE_OPCODE = 128
LIGHT_POINT_ANIMATION_PALETTE_OPCODE = 129
INDEXED_LIGHT_POINT_OPCODE = 130
LIGHT_POINT_SYSTEM_OPCODE = 131
INDEXED_STRING_OPCODE = 132
SHADER_PALETTE_OPCODE = 133
RESERVED134_OPCODE = 134
EXTENDED_MATERIAL_HEADER_OPCODE = 135
EXTENDED_MATERIAL_AMBIENT_OPCODE = 136
EXTENDED_MATERIAL_DIFFUSE_OPCODE = 137
EXTENDED_MATERIAL_SPECULAR_OPCODE = 138
EXTENDED_MATERIAL_EMISSIVE_OPCODE = 139
EXTENDED_MATERIAL_ALPHA_OPCODE = 140
EXTENDED_MATERIAL_LIGHTMAP_OPCODE = 141
EXTENDED_MATERIAL_NORMALMAP_OPCODE = 142
EXTENDED_MATERIAL_BUMPMAP_OPCODE = 143
RESERVED144_OPCODE = 144
EXTENDED_MATERIAL_SHADOWMAP_OPCODE = 145
RESERVED146_OPCODE = 146
EXTENDED_MATERIAL_REFLECTION_OPCODE = 147


class Record:
    def __init__(self, data):
        self.data = data
        assert len(data) >= 4
        (self.opcode,) = unpack_from(">h",data, offset=0)
        (self.length,) = unpack_from(">H",data, offset=2)
        if self.length <= 0: # prevent endless loops with bad data
            raise Exception
        self.id = ''
        if len(data) >= 12:
            (self.id,) = unpack_from(">8s",data, offset=4)
            self.id = self.id.replace('\x00',' ').strip()
        self.parent = None
        self.children = []
        

class Header(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == HEADER_OPCODE
        self.__load()
        
    def __load(self):
    
        (self.format_revision,) = unpack_from(">i",self.data, offset=12)
        (self.edit_revision,) = unpack_from(">i",self.data, offset=16)
        (self.last_revision,) = unpack_from(">32s",self.data, offset=20)
        self.last_revision = self.last_revision.replace('\x00',' ').strip()
        (self.next_group_id,) = unpack_from(">h",self.data, offset=52)
        (self.next_lod_id,) = unpack_from(">h",self.data, offset=54)
        (self.next_object_id,) = unpack_from(">h",self.data, offset=56)
        (self.next_face_id,) = unpack_from(">h",self.data, offset=58)
        (self.unit_multiplier,) = unpack_from(">h",self.data, offset=60)
        
        # 0 = Meters
        # 1 = Kilometers
        # 4 = Feet
        # 5 = Inches
        # 8 = Nautical miles
        (self.coordinate_units,) = unpack_from(">b",self.data, offset=62)
        (self.texwhite,) = unpack_from(">b",self.data, offset=63)
        
        # Flags (bits, from left to right)
        # 0 = Save vertex normals
        # 1 = Packed Color mode
        # 2 = CAD View mode
        # 3-31 = Spare
        (self.flags,) = unpack_from(">cxxx",self.data, offset=64)
        
        # 24 bytes are reserved
        # self.reserved = data[68:92]
        
        # Projection type
        # 0 = Flat earth
        # 1 = Trapezoidal
        # 2 = Round earth
        # 3 = Lambert
        # 4 = UTM
        # 5 = Geodetic
        # 6 = Geocentric
        (self.projection_type,) = unpack_from(">i",self.data, offset=92)
        
        # 28 bytes are reserved
        # self.reserved = data[96:124]
        
        (self.next_dof_id,) = unpack_from(">h",self.data, offset=124)
        (self.use_doubles,) = unpack_from(">h",self.data, offset=126)
        
class Group(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == GROUP_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class Object(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == OBJECT_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class Face(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == FACE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class ColorPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == COLOR_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class VertexPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == VERTEX_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass

class Vertex(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == VERTEX_COLOR_NORMAL_UV_OPCODE
        self.__load()
        
    def __load(self):
        (self.color_name_index,) = unpack_from('>H', self.data, offset=4)
        (self.flags,) = unpack_from('>h', self.data, offset=6)
        (self.x,) = unpack_from('>d', self.data, offset=8)
        (self.y,) = unpack_from('>d', self.data, offset=16)
        (self.z,) = unpack_from('>d', self.data, offset=24)
        (self.i,) = unpack_from('>f', self.data, offset=32)
        (self.j,) = unpack_from('>f', self.data, offset=36)
        (self.k,) = unpack_from('>f', self.data, offset=40)
        (self.u,) = unpack_from('>f', self.data, offset=44)
        (self.v,) = unpack_from('>f', self.data, offset=48)
        (self.abgr,) = unpack_from('>i', self.data, offset=52)
        (self.color_index,) = unpack_from('>i', self.data, offset=56)
        
        
class Mesh(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class LightPoint(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class DOF(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class BSP(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class Xref(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class LOD(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class Sound(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class LightSource(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class RoadSegment(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class RoadConstruction(Record):
    def __init__(self, data):
        Record.__init__(self, data)

class RoadPath(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class ClipRegion(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class Text(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class Switch(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class CAT(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class Extension(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
class Curve(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        
def createRecord(opcode, data):
    if opcode == HEADER_OPCODE:
        return Header(data)
    elif opcode == COLOR_PALETTE_OPCODE:
        return ColorPalette(data)
    elif opcode == VERTEX_PALETTE_OPCODE:
        return VertexPalette(data)
    elif opcode == VERTEX_COLOR_NORMAL_UV_OPCODE:
        return Vertex(data)
        
class OpenFlightFile:
    """4 byte opcode for each record, 4 byte multiple padding, big endian
    
    matricies:
    row0col0, row0col1, row0col2, row0col3,
    row1col0, row1col1, row1col2, row1col3,
    row2col0, row2col1, row2col2, row2col3,
    row3col0, row3col1, row3col2, row3col3
    
    max children = 65534
    
    >>> ofile = OpenFlightFile("C:/alienbrainWork/CGI_Archive/DATA/VisualDB/models/3d/lav25/lav25.flt")
    >>> ofile.header.opcode 
    1
    >>> ofile.header.length
    308
    >>> ofile.header.id
    'db'
    >>> ofile.header.format_revision
    1570
    >>> ofile.header.edit_revision
    4
    >>> ofile.header.last_revision
    'Mon Mar 28 14:22:55 2005'
    >>> ofile.header.next_group_id
    95
    >>> ofile.header.next_lod_id
    155
    >>> ofile.header.next_object_id
    333
    >>> ofile.header.next_face_id
    14521
    >>> ofile.header.unit_multiplier
    1
    >>> ofile.header.coordinate_units
    0
    >>> ofile.header.texwhite
    1
    >>> ofile.header.flags
    '\\x82'
    >>> ofile.version()
    1570
    >>> ofile.header.projection_type
    0
    
    """

    def __init__(self, filename):
        self.data = ''
        self.index = 0 # byte offset of data pointer
        self.filename = filename
        _f = open(filename,'r')
        # cache the file contents and close
        _f.seek(0,2)
        _pos = _f.tell()
        _f.seek(0,0) #back to the beginning
        #self.data = _f.read(_pos)
        self.recs = []
        
        # serialize the data into something more meaningful
        print '_pos:',_pos
        while _f.tell() < _pos-4:
            #try:
            rec = Record(_f.read(4))
            _f.seek(-4,1)
            data = None
            if rec.opcode <= 147 and rec.opcode > 0:
                data = _f.read(rec.length) 
            else:
                _f.seek(4,1)
            print 'opcode:', rec.opcode, 'length:',rec.length, '_f.tell():', _f.tell()                
            if data:
                r = createRecord(rec.opcode, data)
                if r:
                    self.recs.append(r)
            del rec
            #except:
            #    print 'exception'
            #    _f.seek(4,1)
        _f.close()
        
    def next(self):
        """return the next record as a byte stream"""
        raise StopIteration
        
    def version(self):
        return self.header.format_revision
        
def _test():
    import doctest
    doctest.testmod()
    
if __name__=='__main__':
    #_test()
    ofile = OpenFlightFile("C:/box1.flt")