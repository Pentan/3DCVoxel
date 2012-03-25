# /usr/bin/bash

ADDON_DIR="3DCoat3BVOL"

if ! [ -e $ADDON_DIR ]; then
mkdir $ADDON_DIR
fi

echo "Updating Blender Addon: $ADDON_DIR"
for i in __init__.py import_3bvol.py ThreeB.py; do
echo "copying $i"
cp $i $ADDON_DIR
done
echo "done"
