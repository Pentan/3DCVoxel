bl_info = {
    "name": "3D-Coat 3b file",
    "author": "Satoru NAKAJIMA",
    "version": (1, 0),
    "blender": (2, 6, 2),
    "location": "File > Import-Export",
    "description": "Import 3D-Coat 3b. Import Voxels as Volume and Surfaces.",
    "tracker_url": "",
    "category": "Import-Export"}

if 'bpy' in locals():
    import imp
    if 'ThreeB' in locals():
        imp.reload(ThreeB)
    if 'import_3bvol' in locals():
        imp.reload(import_3bvol)

import bpy
from bpy.props import FloatProperty, BoolProperty, StringProperty
from bpy_extras.io_utils import ImportHelper
from . import import_3bvol, ThreeB
from . import fit_voxel_in_bounds
from . import collect_textures

# Operator class
class IMPORT_OT_3dc_3b_volumes(bpy.types.Operator, ImportHelper):
    """Import 3D-Coat Voxels"""
    bl_idname = "import.3dcoat_3b"
    bl_label = "Import 3D-Coat 3b"
    bl_options = {'PRESET', 'UNDO'}
    
    filename_ext = ".3b"
    filter_glob = StringProperty(
        default="*.3b",
        options={'HIDDEN'}
    )
    
    filepath = StringProperty(
        name="File Path",
        description="File Path used for importing the 3B file",
        maxlen=1024,
        default=""
    )
    
    import_scale = FloatProperty(
        name="Import Scale",
        description="Scaling value for importing objects",
        default=0.05, min=0.0, max=1.0
    )
    
    import_surfaces = BoolProperty(
        name="Import Surfaces",
        description="Import surface mode's meshes",
        default=False
    )
    
    freeze_objects = BoolProperty(
        name="Apply Transforms",
        description="Apply loc and scale transforms to imported objects",
        default=True
    )
    
    voxel_dir = StringProperty(
        name="Voxel directory",
        description="Directory name to save voxel datas. Relative path from the blend file",
        maxlen=1024,
        default="voxels"
    )
    
    def execute(self, context):
        (err, msg) = import_3bvol.load(self.filepath,
                                       self.import_scale,
                                       self.freeze_objects,
                                       self.import_surfaces,
                                       self.voxel_dir)
        if err:
            self.report(err, msg)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        vm = context.window_manager
        vm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Registration
def menu_func_volume_import(self, context):
    self.layout.operator(
        IMPORT_OT_3dc_3b_volumes.bl_idname,
        text="3D-Coat Volumes (.3b)"
    )

def register():
    bpy.utils.register_class(IMPORT_OT_3dc_3b_volumes)
    bpy.types.INFO_MT_file_import.append(menu_func_volume_import)
    fit_voxel_in_bounds.register()
    collect_textures.register()

def unregister():
    bpy.utils.unregister_class(IMPORT_OT_3dc_3b_volumes)
    bpy.types.INFO_MT_file_import.remove(menu_func_volume_import)
    fit_voxel_in_bounds.unregister()
    collect_textures.unregister()

if __name__ == '__main__':
    register()
