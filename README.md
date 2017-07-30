# 3D-Coat .3b file utilities.

ThreeB.py is a voxel data reading utility for 3D-Coat's .3b file.

## Samples for ThreeB.py
* pydump3b.py : A simple .3b file dumper.
* extract3bsurface.py : A simple .3b file's surface mesh extracter.
* rawvox2raw8vox.py : A simple tool to convert Raw Voxel data that exported from 3D-Coat to 8bit flat voxel data.
   
   usage: python rawvox2raw8vox.py file0 ...

## Blender addons
### 3b file voxel importer

3DCoat3BVOL.zip is Blender addon to import voxels as volume textured objects.

### How to install

1. Select menu "File->User Preferences..." and open "Addon" tab.
2. Press "Install Addon..." button at bottom bar.
3. Select 3DCoat3BVOL.zip.

or

1. unzip and move 3DCoat3BVOL directory to Blender's script/addon directory.

After install, enable "3D-Coat 3b file" addon at "Import-Export" category.

#### Import options
* Import Scale (Number) : Common scaling value for importing objects.
* Import Surface (Check box) : Ckeck this is you want to import surface mode's mesh.
  - Imported meshes are "RAW" mesh generated from voxels.
    Faces are separeted by 3D-Coat's internal voxel cells.
* Voxel Directory (String) : Relative path from the blend file. Converted voxel datas will be exported in here.
* Use ID number(Check box) : Impoted objects names ID number instead of volel layer name. This is a safety option for multi-byte environment user.

### support commands:
- Collect Textures : Collect textures from selected objects and add it to the active object. No menu interface. Exec "Collect Texture" from space key's menu.
- Fit Voxel data in Bound Box : A voxel texture's offset and size fit in object's bound box. No menu interface. Exec "Fit Voxel data in Bound Box" from space key's menu.

## History

* 1.0
  - release
* 1.0.1
  - Volume texture's color refers to voxel default color.
* 2.0.0
  - Change volume texture's transform manipulation. Now using Empty to transform volume textures.
  - Remove import option "Apply Transform".
* 2.0.1
  - Changes to set a imported surfaces's parent to volume's root empty.

## License

ThreeB.py and sample codes are zlib License.

Blender addon codes are GPL v2.

2012 Satoru NAKAJIMA