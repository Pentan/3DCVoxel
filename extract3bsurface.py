# A sample code to convert surface mode's meshs to a obj format.
# But you should use 3D-Coat's File->Export operation.

import sys
from array import array
import ThreeB

def calc_normal_matrix(m):
	# inverse transposed matrix
	ret = array("f", (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0))
	
	detm = m[0] * m[5] * m[10] + m[1] * m[6] * m[8] + m[2] * m[4] * m[9]
	detm -= m[2] * m[5] * m[8] + m[1] * m[4] * m[10] + m[0] * m[6] * m[9]
	
	ret[0] = (m[5] * m[10] - m[6] * m[9]) / detm
	ret[1] = (m[6] * m[8] - m[4] * m[10]) / detm
	ret[2] = (m[4] * m[9] - m[5] * m[8]) / detm
	ret[3] = 0.0
	
	ret[4] = (m[9] * m[2] - m[10] * m[1]) / detm
	ret[5] = (m[10] * m[0] - m[8] * m[2]) / detm
	ret[6] = (m[8] * m[1] - m[9] * m[0]) / detm
	ret[7] = 0.0
	
	ret[8] = (m[1] * m[6] - m[2] * m[5]) / detm
	ret[9] = (m[2] * m[4] - m[0] * m[6]) / detm
	ret[10] = (m[0] * m[5] - m[1] * m[4]) / detm
	ret[11] = 0.0
	
	return ret

def apply_transform(v, vstart, m, ans):
	ans[0] = m[0] * v[vstart] + m[4] * v[vstart + 1] + m[8] * v[vstart + 2] + m[12]
	ans[1] = m[1] * v[vstart] + m[5] * v[vstart + 1] + m[9] * v[vstart + 2] + m[13]
	ans[2] = m[2] * v[vstart] + m[6] * v[vstart + 1] + m[10] * v[vstart + 2] + m[14]

def output_surface_as_obj(voxtree, outname):
	try:
		outfile = open(outname, "w")
	except IOError as error:
		print(error)
	else:
		print("export as {}".format(outname))
		convert_surface_to_obj(voxtree, 0, array("f", (1.0, 0.0, 0.0, 0.0,  0.0, 1.0, 0.0, 0.0,  0.0, 0.0, 1.0, 0.0,  0.0, 0.0, 0.0, 1.0)), outfile)
		outfile.close()
		print("done")

def convert_surface_to_obj(voxbranch, vertcount, mtrx, outf):
	print("exporting Volume: {}".format(voxbranch.name))
	outf.write("# {}\n".format(voxbranch.name))
	
	#print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[0], voxbranch.transform[1], voxbranch.transform[2], voxbranch.transform[3]))
	#print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[4], voxbranch.transform[5], voxbranch.transform[6], voxbranch.transform[7]))
	#print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[8], voxbranch.transform[9], voxbranch.transform[10], voxbranch.transform[11]))
	#print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(voxbranch.transform[12], voxbranch.transform[13], voxbranch.transform[14], voxbranch.transform[15]))
	
	# start converting
	exportedverts = 0
	voldat = voxbranch.volume_data
	if voldat:
		if voldat.representation == 256:
    		# volume data has a surface
			outf.write("g Volume_{}\n".format(voldat.space_ID))
			normmat = calc_normal_matrix(voldat.transform)
			tmpv = array("f", (0.0, 0.0, 0.0))
			vertlist = []
			normlist = []
			facelist = []
			for cell in voldat.cells:
				if cell.has_surface == False:
					continue
				voffset = vertcount + len(vertlist) + 1
				
				# v and vn
				vnum = len(cell.surface_vertices)
				i = 0
				while i < vnum:
					apply_transform(cell.surface_vertices, i, voldat.transform, tmpv)
					vertlist.append("v {0:.8f} {1:.8f} {2:.8f}".format(tmpv[0], tmpv[1], tmpv[2]))
					apply_transform(cell.surface_vertices, i + 3, normmat, tmpv)
					normlist.append("vn {0:.8f} {1:.8f} {2:.8f}".format(tmpv[0], tmpv[1], tmpv[2]))
					i += 7
				tmpfdef = None
				
				# f
				inds = cell.surface_indices
				fnum = len(inds)
				i = 0
				while i < fnum:
					facelist.append("f {0} {1} {2}".format(inds[i] + voffset, inds[i + 1] + voffset, inds[i + 2] + voffset))
					i += 3
			outf.write("\n".join(vertlist) + "\n")
			outf.write("\n".join(normlist) + "\n")
			outf.write("\n".join(facelist) + "\n")
			
			vertcount += len(vertlist)
		else:
			print("This volume has no surfaces")
	else:
		print("No Volume data")
	
	# convert childs
	if voxbranch.childs:
		for childvox in voxbranch.childs:
			vertcount = convert_surface_to_obj(childvox, vertcount, mtrx, outf)
	
	return vertcount

if len(sys.argv) <= 1:
	print("usage {0} file1.3b".format(sys.argv[0]))

for i,fname in enumerate(sys.argv[1:]):
	print("input {0}. reading...".format(fname))
	threeb = ThreeB.load_3bfile(fname)
	if threeb:
		print("creating Voxel Data Tree")
		voxtree = ThreeB.create_VoxTree(threeb)
		output_surface_as_obj(voxtree, fname + ".obj")
	else:
		print("{} is not a 3b file".format(fname))
