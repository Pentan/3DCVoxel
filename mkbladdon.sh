# /usr/bin/bash

ADDON_DIR="3DCoat3BVOL"
SRC_FILES="__init__.py import_3bvol.py ThreeB.py fit_voxel_in_bounds.py collect_textures.py"

if ! [ -e $ADDON_DIR ]; then
mkdir $ADDON_DIR
fi

echo "Updating Blender Addon: $ADDON_DIR"
for i in $SRC_FILES; do
echo "copying $i"
cp $i $ADDON_DIR
done

ZIP_FILE="$ADDON_DIR.zip"
if [ -e $ZIP_FILE ]; then
rm -f $ZIP_FILE
fi

echo "$ZIP_FILE archiving"
zip $ZIP_FILE $ADDON_DIR/*.py -x $ADDON_DIR/.*

echo "done"
