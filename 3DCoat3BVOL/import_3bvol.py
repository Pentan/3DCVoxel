import os
import math
import bpy
from mathutils import Matrix

# import ThreeB

if __name__ == "__main__":
    import ThreeB
else:
    from . import ThreeB

READ_SURFACES = True
FREEZE_VOXELS = False
IMPORT_SCALE = 0.05
VOXEL_DATA_DIR = "voxels"
VOXEL_DIR_PATH = ""

class VoxDataSpec:
    volume_name = ""
    volume_color = (0, 0, 0)
    voxel_file_name = ""
    voxel_file_path = ""
    voxel_size = None
    voxel_AABB = None
    surface_vertices = None
    surface_faces = None
    
    def __init__(self, voxdata, outdir):
        self.volume_name = voxdata.volume_name
        self.volume_color = (
            ((voxdata.default_color >> 16) & 0xff) / 255,
            ((voxdata.default_color >> 8) & 0xff) / 255,
            (voxdata.default_color & 0xff) / 255,
        )
        
        #print("cellAABB:{}".format(voxdata.cell_AABB))
        #print("effAABB:{}".format(voxdata.effect_AABB))
        #print("has volume:{}".format(voxdata.effect_AABB.has_volume()))
        #print("minv:{}, maxv{}".format(minv, maxv))
        
        # check voxel size
        if voxdata.effect_AABB.has_volume() == False:
            # No Volume
            return
        
        minv = (
            max(voxdata.effect_AABB.min[0] - 1, voxdata.cell_AABB.min[0]) * 8,
            max(voxdata.effect_AABB.min[1] - 1, voxdata.cell_AABB.min[1]) * 8,
            max(voxdata.effect_AABB.min[2] - 1, voxdata.cell_AABB.min[2]) * 8
        )
        maxv = (
            (min(voxdata.effect_AABB.max[0] + 1, voxdata.cell_AABB.max[0]) + 1) * 8,
            (min(voxdata.effect_AABB.max[1] + 1, voxdata.cell_AABB.max[1]) + 1) * 8,
            (min(voxdata.effect_AABB.max[2] + 1, voxdata.cell_AABB.max[2]) + 1) * 8
        )
        
        voxsize_x = maxv[0] - minv[0]
        voxsize_y = maxv[1] - minv[1]
        voxsize_z = maxv[2] - minv[2]
        voxelbuf = bytearray(b'\x00' * (voxsize_x * voxsize_y * voxsize_z))
        
        self.voxel_size = (voxsize_x, voxsize_y, voxsize_z)
        self.voxel_AABB = {'min':minv, 'max':maxv}
        
        # Check cells
        self.surface_vertices = []
        self.surface_faces = []
        for voxcell in voxdata.cells:
            # Voxel
            for iz in range(8):
                cellz = voxcell.z * 8 + iz - minv[2]
                if cellz >= voxsize_z:
                    continue
                zindex = voxsize_x * voxsize_y * cellz
                
                for iy in range(8):
                    celly = voxcell.y * 8 + iy - minv[1]
                    if celly >= voxsize_y:
                        continue
                    yindex = voxsize_x * celly
                    
                    for ix in range(8):
                        cellx = voxcell.x * 8 + ix - minv[0]
                        if cellx >= voxsize_x:
                            continue
                        val = voxcell.data[ix + iy * 9 + iz * 81] / 256
                        voxelbuf[cellx + yindex + zindex] = int(min(val, 255))
            # Surface
            if voxcell.has_surface == False:
                continue
            voffset = len(self.surface_vertices)
            vnum = len(voxcell.surface_vertices)
            i = 0
            while i < vnum:
                self.surface_vertices.append(voxcell.surface_vertices[i:i+3])
                i += 7
            fnum = len(voxcell.surface_indices)
            i = 0
            while i < fnum:
                tmpface = (
                    voxcell.surface_indices[i] + voffset,
                    voxcell.surface_indices[i + 1] + voffset,
                    voxcell.surface_indices[i + 2] + voffset
                )
                self.surface_faces.append(tmpface)
                i += 3
        try:
            # Write voxel data
            self.voxel_file_name = "{}_{}_{}_{}.vxl".format(voxdata.volume_name, voxsize_x, voxsize_y, voxsize_z)
            self.voxel_file_path = os.path.join(outdir, self.voxel_file_name)
            # print(self.voxel_file_path)
            voxf = open(self.voxel_file_path, "wb")
        except IOError as err:
            print(err)
            voxel_file_name = ""
        else:
            voxf.write(voxelbuf)
            voxf.close()

def create_voxel_object(voxspec, transform):
    minv = voxspec.voxel_AABB['min']
    maxv = voxspec.voxel_AABB['max']
    voxverts = (
        (minv[0], minv[1], minv[2]),
        (minv[0], minv[1], maxv[2]),
        (maxv[0], minv[1], maxv[2]),
        (maxv[0], minv[1], minv[2]),
        (minv[0], maxv[1], minv[2]),
        (minv[0], maxv[1], maxv[2]),
        (maxv[0], maxv[1], maxv[2]),
        (maxv[0], maxv[1], minv[2])
    )
    voxfaces = (
        (3, 2, 1, 0),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7)
    )
    voxmesh = bpy.data.meshes.new(voxspec.volume_name + "_VolMesh")
    voxobj = bpy.data.objects.new(voxspec.volume_name + "_Volume", voxmesh)
    bpy.context.scene.objects.link(voxobj)
    bpy.context.scene.objects.active = voxobj
    voxmesh.from_pydata(voxverts, [], voxfaces)
    voxmesh.update()
    voxobj.matrix_world = transform
    voxobj.draw_type = 'WIRE'
    
    # Create Voxel Texture
    voxtex = bpy.data.textures.new(voxspec.volume_name + "_Voxel", type='VOXEL_DATA')
    voxtex.voxel_data.file_format = 'RAW_8BIT'
    voxtex.voxel_data.filepath = voxspec.voxel_file_path
    voxtex.voxel_data.resolution = voxspec.voxel_size
    # Color ramp for 3D-Coat looks shape
    voxtex.use_color_ramp = True
    ramp = voxtex.color_ramp
    ramp.elements[0].position = 0.5
    ramp.elements[0].color = (1, 1, 1, 0)
    ramp.elements[1].position = 0.51
    ramp.elements[1].color = (1, 1, 1, 1)
    
    # Create Volume Material
    voxmat = bpy.data.materials.new(voxspec.volume_name + "_VolMat")
    voxmat.type='VOLUME'
    voxmat.volume.density = 0
    voxmat.use_transparent_shadows = True
    texslot = voxmat.texture_slots.add()
    texslot.texture = voxtex
    texslot.use_map_density = True
    texslot.density_factor = 1.0
    # texslot.use_map_color_emission = False
    texslot.offset = (
        (maxv[0] + minv[0]) * -0.5,
        (maxv[1] + minv[1]) * -0.5,
        (maxv[2] + minv[2]) * -0.5
    )
    texslot.scale = (
        2 / voxspec.voxel_size[0],
        2 / voxspec.voxel_size[1],
        2 / voxspec.voxel_size[2]
    )
    # Attach
    voxmesh.materials.append(voxmat)
    return voxobj

def create_surface_object(voxspec, transform):
    # Create Mesh
    if len(voxspec.surface_vertices) <= 0:
        return None
    surfmesh = bpy.data.meshes.new(voxspec.volume_name + "_SurfMesh")
    surfobj = bpy.data.objects.new(voxspec.volume_name + "_Surface", surfmesh)
    bpy.context.scene.objects.link(surfobj)
    bpy.context.scene.objects.active = surfobj
    surfmesh.from_pydata(voxspec.surface_vertices, [], voxspec.surface_faces)
    surfmesh.update()
    surfobj.matrix_world = transform
    
    surfmat = bpy.data.materials.new(voxspec.volume_name + "_SurfMat")
    surfmat.diffuse_color = voxspec.volume_color
    surfmat.use_transparent_shadows = True
    surfmesh.materials.append(surfmat)
    return surfobj
    
def build_objects(voxdata):
    global READ_SURFACES, FREEZE_VOXELS, IMPORT_SCALE, VOXEL_DATA_DIR, VOXEL_DIR_PATH
    #print('--- create object {} ---'.format(voxdata.volume_name))
    #print(' cells: {}'.format(len(voxdata.cells)))
    
    # initialize
    ret = {'volume':None, 'surface':None}
    
    # make transform
    # Z-up and scaling
    basetrans = Matrix.Rotation(math.pi * 0.5, 4, 'X') * Matrix.Scale(IMPORT_SCALE, 4)
    # and Volume transform
    tmpmtrx = voxdata.transform
    voxtmtrx = Matrix((
        (tmpmtrx[0], tmpmtrx[4], tmpmtrx[8], tmpmtrx[12]),
        (tmpmtrx[1], tmpmtrx[5], tmpmtrx[9], tmpmtrx[13]),
        (tmpmtrx[2], tmpmtrx[6], tmpmtrx[10], tmpmtrx[14]),
        (tmpmtrx[3], tmpmtrx[7], tmpmtrx[11], tmpmtrx[15]),
    ))
    voxtransform = basetrans * voxtmtrx
    
    # Transforms for freeze location and scale. ignore rotation.
    if FREEZE_VOXELS:
        (loc, rot, scl) = voxtransform.decompose()
        loc.rotate(rot.conjugated())
        frzlocalmtrx = Matrix((
            (scl[0], 0, 0, loc[0]),
            (0, scl[1], 0, loc[1]),
            (0, 0, scl[2], loc[2]),
            (0, 0, 0, 1)
        ))
        frzworldmtrx = rot.to_matrix().to_4x4()
    
    # Parse data
    voxspec = VoxDataSpec(voxdata, VOXEL_DIR_PATH)
    if voxspec.voxel_size == None:
        # No Volume data
        return ret
    
    # fix file path to relative
    voxspec.voxel_file_path = "//" + os.path.join(VOXEL_DATA_DIR, voxspec.voxel_file_name)
    
    # Create Volume
    obj = create_voxel_object(voxspec, voxtransform)
    if FREEZE_VOXELS:
        mesh = obj.data
        mesh.transform(frzlocalmtrx)
        mesh.update()
        obj.matrix_world = frzworldmtrx
        txslot = obj.active_material.texture_slots[0]
        txslot.scale = (
            2 / (voxspec.voxel_size[0] * frzlocalmtrx[0][0]),
            2 / (voxspec.voxel_size[1] * frzlocalmtrx[1][1]),
            2 / (voxspec.voxel_size[2] * frzlocalmtrx[2][2])
        )
        txslot.offset = (
            txslot.offset[0] * frzlocalmtrx[0][0] - frzlocalmtrx[0][3],
            txslot.offset[1] * frzlocalmtrx[0][0] - frzlocalmtrx[1][3],
            txslot.offset[2] * frzlocalmtrx[0][0] - frzlocalmtrx[2][3],
        )
    
    ret.update(volume=obj)
    
    # Create Surface
    if READ_SURFACES:
        obj = create_surface_object(voxspec, voxtransform)
        if obj != None:
            if FREEZE_VOXELS:
                mesh = obj.data
                mesh.transform(frzlocalmtrx)
                mesh.update()
                obj.matrix_world = frzworldmtrx
            ret.update(surface=obj)
    
    return ret

def traverse_VoxTree(voxbranch, objlist):
    # print('{}+ Volume "{}"'.format(indent, voxbranch.name))
    if voxbranch.volume_data:
        objs = build_objects(voxbranch.volume_data)
        objlist.append(objs)
        
    
    if voxbranch.childs:
        for subbranch in voxbranch.childs:
            traverse_VoxTree(subbranch, objlist)
    return

def load(filepath,
         import_scale=0.05,
         freeze_volumes=False,
         read_surface=True,
         voxel_dir=VOXEL_DATA_DIR):
    global READ_SURFACES, FREEZE_VOXELS, IMPORT_SCALE, VOXEL_DATA_DIR, VOXEL_DIR_PATH
    
    READ_SURFACES =read_surface
    FREEZE_VOXELS = freeze_volumes
    IMPORT_SCALE = import_scale
    VOXEL_DATA_DIR = voxel_dir
    
    # Voxel Directory check
    curdir = os.path.dirname(bpy.data.filepath)
    #if len(curdir) <= 0:
    if True:
        #raise NameError("The blend file must be saved to export voxel datas.")
        return 'Please save the blend file before import'
    
    VOXEL_DIR_PATH = os.path.join(curdir, VOXEL_DATA_DIR)
    if os.path.exists(VOXEL_DIR_PATH):
        # Directory is exists
        if os.path.isfile(VOXEL_DIR_PATH):
            # It is file!
            # raise IOError("Same name file found: {}".format(VOXEL_DIR_PATH))
            return 'Voxel save dir open Error'
    else:
        # Create dir
        os.makedirs(VOXEL_DIR_PATH)
    
    # Load File
    contents = ThreeB.load_3bfile(filepath)
    if contents:
        voxtree = ThreeB.create_VoxTree(contents)
        objlist = []
        traverse_VoxTree(voxtree, objlist)
    
    return None

##### For Debugging
# import imp
# imp.reload(ThreeB)
if __name__ == "__main__":
    
    #filename = "sample/surf2_trans.3b"
    #filename = "sample/vox3_layer3.3b"
    #filename = "sample/vox2_layer2_2x.3b"
    filename = "sample/vox2_surface1_layer3.3b"
    curdir = os.path.dirname(bpy.data.filepath)
    filepath = os.path.join(curdir, filename)
    #print(filepath)
    
    load(filepath)