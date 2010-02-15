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
        (_d,_d2) = unpack_from('>HH',data,offset=0)
        #print len(data), str(_d), str(_d2)
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
    
class DOF(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == DOF_OPCODE
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
    
class Matrix(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == MATRIX_OPCODE
        self.__load()
        
    def __load(self):
        pass
    
class Vector(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == VECTOR_OPCODE
        self.__load()
        
    def __load(self):
        pass
    
class Multitexture(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == MULTITEXTURE_OPCODE
        self.__load()
        
    def __load(self):
        pass

class UVList(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == UV_LIST_OPCODE
        self.__load()
        
    def __load(self):
        pass
    
class BSP(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BSP_OPCODE
        self.__load()
        
    def __load(self):
        pass

class Xref(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == XREF_OPCODE
        self.__load()
        
    def __load(self):
        pass

class TexturePalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == TEXTURE_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
    
class VertexPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == VERTEX_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        (self.total_length, ) = unpack_from('>i', self.data, offset=4)
        
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
      
class VertexList(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == VERTEX_LIST_OPCODE
        self.__load()
        
    def __load(self):
        pass

class LOD(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LOD_OPCODE
        self.__load()
        
    def __load(self):
        pass

class BBox(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BOUNDING_BOX_OPCODE
        self.__load()
        
    def __load(self):
        pass

class EyepointTrackplanePalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EYEPOINT_TRACKPLANE_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass

class Mesh(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == MESH_OPCODE
        self.__load()
        
    def __load(self):
        pass
         
class LocalVertexPool(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LOCAL_VERTEX_POOL_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class MeshPrimitive(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == MESH_PRIMITIVE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class RoadSegment(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == ROAD_SEGMENT_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class RoadZone(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == ROAD_ZONE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class MorphVertexList(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == MORPH_VERTEX_LIST_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class LinkagePalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LINKAGE_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class Sound(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == SOUND_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class RoadPath(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == ROAD_PATH_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class SoundPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == SOUND_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class GeneralMatrix(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == GENERAL_MATRIX_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class Text(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == TEXT_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class Switch(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == SWITCH_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class LineStylePalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LINE_STYLE_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class ClipRegion(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == CLIP_REGION_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class Extension(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENSION_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class LightSource(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LIGHT_SOURCE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class LightSourcePalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LIGHT_SOURCE_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class BoundingSphere(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BOUNDING_SPHERE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class BoundingCylinder(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BOUNDING_CYLINDER_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class BoundingConvexHull(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BOUNDING_CONVEX_HULL_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class BoundingVolumeCenter(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BOUNDING_VOLUME_CENTER_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class BoundingVolumeOrientation(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BOUNDING_VOLUME_ORIENTATION_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class LightPoint(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LIGHT_POINT_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class TextureMappingPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == TEXTURE_MAPPING_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class MaterialPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == MATERIAL_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class NameTable(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == NAME_TABLE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class CAT(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == CAT_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class CatData(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == CAT_DATA_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class BoundingHistogram(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == BOUNDING_HISTOGRAM_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class Curve(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == CURVE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class RoadConstruction(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == ROAD_CONSTRUCTION_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class LightPointAppearancePalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LIGHT_POINT_APPEARANCE_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
class LightPointAnimationPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LIGHT_POINT_ANIMATION_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class IndexedLightPoint(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == INDEXED_LIGHT_POINT_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class LightPointSystem(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == LIGHT_POINT_SYSTEM_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class IndexedString(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == INDEXED_STRING_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ShaderPalette(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == SHADER_PALETTE_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialHeader(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_HEADER_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialAmbient(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_AMBIENT_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialDiffuse(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_DIFFUSE_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialSpecular(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_SPECULAR_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialEmissive(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_EMISSIVE_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialAlpha(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_ALPHA_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialLightmap(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_LIGHTMAP_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialNormalmap(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_NORMALMAP_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialBumpmap(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_BUMPMAP_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialShadowmap(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_SHADOWMAP_OPCODE
        self.__load()
        
    def __load(self):
        pass
 
class ExtendedMaterialReflection(Record):
    def __init__(self, data):
        Record.__init__(self, data)
        assert self.opcode == EXTENDED_MATERIAL_REFLECTION_OPCODE
        self.__load()
        
    def __load(self):
        pass
        
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
        _data = ''
        self.filename = filename
        _f = open(filename,'rb')
        # cache the file contents and close
        _f.seek(0,2)
        _end = _f.tell()
        _f.seek(0,0) #back to the beginning
        _data = _f.read()
        assert len(self.data) == _end
        _f.close()
        self.records = [] # these are "global" nodes (ie. vertex definitions)
        self.children = [] # this node is a special case top-level parent for the node tree
        
        # serialize the data into something more meaningful
        print '_end:',_end
        _pos = 0
        while _pos <= _end-4:
            rec = Record(_data[_pos:_pos+4])
            if _pos+rec.length > _end:
                raise Exception, 'File parse error!'
            data =  _data[_pos:_pos+rec.length]          
            if data:
                r = self.createRecord(rec.opcode, data)
                if r:
                    print 'opcode:', rec.opcode, 'length:',rec.length, r
                    self.records.append(r)
                else:
                    print 'record not created for opcode', rec.opcode
            _pos += rec.length
            del rec
            if _pos >= _end:
                break
        
    def version(self):
        return self.header.format_revision
    
    def createRecord(self, opcode, data):
        if opcode == HEADER_OPCODE:
            return Header(data)
        elif opcode == GROUP_OPCODE:
            return Group(data)
        elif opcode == OBJECT_OPCODE:
            return Object(data)
        elif opcode == FACE_OPCODE :
            return Face(data)
        #elif opcode == PUSH_LEVEL_OPCODE = 10
        #elif opcode == POP_LEVEL_OPCODE = 11
        elif opcode == DOF_OPCODE:
            return DOF(data)
        #elif opcode == PUSH_SUBFACE_OPCODE = 19
        #elif opcode == POP_SUBFACE_OPCODE = 20
        #elif opcode == PUSH_EXTENSION_OPCODE = 19
        #elif opcode == POP_EXTENSION_OPCODE = 20
        #elif opcode == CONTINUATION_OPCODE = 23
        #elif opcode == COMMENT_OPCODE = 31
        elif opcode == COLOR_PALETTE_OPCODE:
            return ColorPalette(data)
        #elif opcode == LONG_ID_OPCODE = 33
        elif opcode == MATRIX_OPCODE:
            return Matrix(data)
        elif opcode == VECTOR_OPCODE:
            return Vector(data)
        elif opcode == MULTITEXTURE_OPCODE:
            return Multitexture(data)
        elif opcode == UV_LIST_OPCODE:
            return UvList(data)
        elif opcode == BSP_OPCODE:
            return BSP(data)
        #elif opcode == REPLICATE_OPCODE = 60
        #elif opcode == INSTANCE_REFERENCE_OPCODE = 61
        #elif opcode == INSTANCE_DEFINITION_OPCODE = 62
        elif opcode == XREF_OPCODE:
            return Xref(data)
        elif opcode == TEXTURE_PALETTE_OPCODE:
            return TexturePalette(data)
        elif opcode == VERTEX_PALETTE_OPCODE:
            return VertexPalette(data)
        #elif opcode == VERTEX_COLOR_OPCODE = 68
        #elif opcode == VERTEX_COLOR_NORMAL_OPCODE = 69
        elif opcode == VERTEX_COLOR_NORMAL_UV_OPCODE:
            return Vertex(data)
        #elif opcode == VERTEX_COLOR_UV_OPCODE = 71
        elif opcode == VERTEX_LIST_OPCODE:
            return VertexList(data)
        elif opcode == LOD_OPCODE:
            return LOD(data)
        elif opcode == BOUNDING_BOX_OPCODE:
            return BBox(data)
        #elif opcode == ROTATE_ABOUT_EDGE_OPCODE = 76
        #elif opcode == TRANSLATE_OPCODE = 78
        #elif opcode == SCALE_OPCODE = 79
        #elif opcode == ROTATE_ABOUT_POINT_OPCODE = 80
        #elif opcode == ROTATE_SCALE_TO_POINT_OPCODE = 81
        #elif opcode == PUT_OPCODE = 82
        elif opcode == EYEPOINT_TRACKPLANE_PALETTE_OPCODE:
            return EyepointTrackplanePalette(data)
        elif opcode == MESH_OPCODE:
            return Mesh(data)
        elif opcode == LOCAL_VERTEX_POOL_OPCODE:
            return LocalVertexPool(data)
        elif opcode == MESH_PRIMITIVE_OPCODE:
            return MeshPrimative(data)
        elif opcode == ROAD_SEGMENT_OPCODE:
            return RoadSegment(data)
        elif opcode == ROAD_ZONE_OPCODE:
            return RoadZone(data)
        elif opcode == MORPH_VERTEX_LIST_OPCODE:
            return MorphVertexList(data)
        elif opcode == LINKAGE_PALETTE_OPCODE:
            return LinkagePalette(data)
        elif opcode == SOUND_OPCODE:
            return Sound(data)
        elif opcode == ROAD_PATH_OPCODE:
            return RoadPath(data)
        elif opcode == SOUND_PALETTE_OPCODE:
            return SoundPalette(data)
        elif opcode == GENERAL_MATRIX_OPCODE:
            return GeneralMatrix(data)
        elif opcode == TEXT_OPCODE:
            return Text(data)
        elif opcode == SWITCH_OPCODE:
            return Switch(data)
        elif opcode == LINE_STYLE_PALETTE_OPCODE:
            return LineStyle(data)
        elif opcode == CLIP_REGION_OPCODE:
            return ClipRegion(data)
        elif opcode == EXTENSION_OPCODE:
            return Extension(data)
        elif opcode == LIGHT_SOURCE_OPCODE:
            return LightSource(data)
        elif opcode == LIGHT_SOURCE_PALETTE_OPCODE:
            return LightSourcePalette(data)
        #elif opcode == RESERVED103_OPCODE = 103
        #elif opcode == RESERVED104_OPCODE = 104
        elif opcode == BOUNDING_SPHERE_OPCODE:
            return BoundingSphere(data)
        elif opcode == BOUNDING_CYLINDER_OPCODE:
            return BoundingCylinder(data)
        elif opcode == BOUNDING_CONVEX_HULL_OPCODE:
            return BoundingConvexHull(data)
        elif opcode == BOUNDING_VOLUME_CENTER_OPCODE:
            return BoundingVolumeCenter(data)
        elif opcode == BOUNDING_VOLUME_ORIENTATION_OPCODE:
            return BoundingVolumeOrientation(data)
        #elif opcode == RESERVED110_OPCODE = 110
        elif opcode == LIGHT_POINT_OPCODE:
            return LightPoint(data)
        elif opcode == TEXTURE_MAPPING_PALETTE_OPCODE:
            return TextureMappingPalette(data)
        elif opcode == MATERIAL_PALETTE_OPCODE:
            return MaterialPalette(data)
        elif opcode == NAME_TABLE_OPCODE:
            return NameTable(data)
        elif opcode == CAT_OPCODE:
            return CAT(data)
        elif opcode == CAT_DATA_OPCODE:
            return CATData(data)
        #elif opcode == RESERVED117_OPCODE = 117
        #elif opcode == RESERVED118_OPCODE = 118
        elif opcode == BOUNDING_HISTOGRAM_OPCODE:
            return BoundingHistogram(data)
        #elif opcode == RESERVED120_OPCODE = 120
        #elif opcode == RESERVED121_OPCODE = 121
        #elif opcode == PUSH_ATTRIBUTE_OPCODE = 122
        #elif opcode == POP_ATTRIBUTE_OPCODE = 123
        #elif opcode == RESERVED124_OPCODE = 124
        #elif opcode == RESERVED125_OPCODE = 125
        elif opcode == CURVE_OPCODE:
            return Curve(data)
        elif opcode == ROAD_CONSTRUCTION_OPCODE:
            return RoadConstruction(data)
        elif opcode == LIGHT_POINT_APPEARANCE_PALETTE_OPCODE:
            return LightPointAppearancePalette(data)
        elif opcode == LIGHT_POINT_ANIMATION_PALETTE_OPCODE:
            return LightPointAnimationPalette(data)
        elif opcode == INDEXED_LIGHT_POINT_OPCODE:
            return IndexedLightPoint(data)
        elif opcode == LIGHT_POINT_SYSTEM_OPCODE:
            return LightPointSystem(data)
        elif opcode == INDEXED_STRING_OPCODE:
            return IndexedString(data)
        elif opcode == SHADER_PALETTE_OPCODE:
            return ShaderPalette(data)
        #elif opcode == RESERVED134_OPCODE = 134
        elif opcode == EXTENDED_MATERIAL_HEADER_OPCODE:
            return ExtendedMaterialHeader(data)
        elif opcode == EXTENDED_MATERIAL_AMBIENT_OPCODE:
            return ExtendedMaterialAmbient(data)
        elif opcode == EXTENDED_MATERIAL_DIFFUSE_OPCODE:
            return ExtendedMaterialDiffuse(data)
        elif opcode == EXTENDED_MATERIAL_SPECULAR_OPCODE:
            return ExtendedMaterialSpecular(data)
        elif opcode == EXTENDED_MATERIAL_EMISSIVE_OPCODE:
            return ExtendedMaterialEmissive(data)
        elif opcode == EXTENDED_MATERIAL_ALPHA_OPCODE:
            return ExtendedMaterialAlpha(data)
        elif opcode == EXTENDED_MATERIAL_LIGHTMAP_OPCODE:
            return ExtendedMaterialLightmap(data)
        elif opcode == EXTENDED_MATERIAL_NORMALMAP_OPCODE:
            return ExtendedMaterialNormalmap(data)
        elif opcode == EXTENDED_MATERIAL_BUMPMAP_OPCODE:
            return ExtendedMaterialBumpmap(data)
        #elif opcode == RESERVED144_OPCODE = 144
        elif opcode == EXTENDED_MATERIAL_SHADOWMAP_OPCODE:
            return ExtendedMaterialShadowmap(data)
        #elif opcode == RESERVED146_OPCODE = 146
        elif opcode == EXTENDED_MATERIAL_REFLECTION_OPCODE:
            return ExtendedMaterialReflection(data)
        
def _test():
    import doctest
    doctest.testmod()
    
if __name__=='__main__':
    #_test()
    ofile = OpenFlightFile("d:/box1.flt")