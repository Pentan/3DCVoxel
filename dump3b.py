# A sample code to dump 3D-Coat 3b file's VOL3 chunk
# usage: python dump3b.py file.3b

import sys
import ThreeB

def print_VoxInfo(voxbranch):
    print("{}".format(voxbranch.name))
    print("tree transform")
    print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[0], voxbranch.transform[1], voxbranch.transform[2], voxbranch.transform[3]))
    print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[4], voxbranch.transform[5], voxbranch.transform[6], voxbranch.transform[7]))
    print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[8], voxbranch.transform[9], voxbranch.transform[10], voxbranch.transform[11]))
    print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[12], voxbranch.transform[13], voxbranch.transform[14], voxbranch.transform[15]))
    if voxbranch.volume_data:
        voldat = voxbranch.volume_data
        print("volumeID: {}".format(voldat.space_ID))
        #print("volume transform"
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voldat.transform[0], voldat.transform[1], voldat.transform[2], voldat.transform[3]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voldat.transform[4], voldat.transform[5], voldat.transform[6], voldat.transform[7]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voldat.transform[8], voldat.transform[9], voldat.transform[10], voldat.transform[11]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voldat.transform[12], voldat.transform[13], voldat.transform[14], voldat.transform[15]))
        
        print("num of cells: {0}".format(len(voldat.cells)))
        print("cell AABB: {0}".format(voldat.cell_AABB))
        print("effect AABB: {0}".format(voldat.effect_AABB))
        if voldat.representation == 256:
            print("surface vertices: {}".format(voldat.num_vertices))
            print("surface faces: {}".format(voldat.num_faces))
            print("initial surface vertices: {}".format(voldat.num_init_vertices))
            
    else:
        print("No Volume data")
    
    if voxbranch.childs:
        print("{} childs".format(len(voxbranch.childs)))
        for i in voxbranch.childs:
            print_VoxInfo(i)

if len(sys.argv) <= 1:
    print("usage {0} file1.3b".format(sys.argv[0]))

for i,fname in enumerate(sys.argv[1:]):
    print("input {0}".format(fname))
    threeb = ThreeB.load_3bfile(fname)
    
    chunk = threeb.get("VOL3")
    chunkdata = chunk.data
    print("VOL3 chunk version: {}".format(chunkdata.version))
    #print("VoxTreeXML:\n{0}".format(chunkdata.VoxTreeXML))
    
    voxtree = ThreeB.create_VoxTree(threeb)
    print_VoxInfo(voxtree)
