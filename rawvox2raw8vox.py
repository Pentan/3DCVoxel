# A simple utility to convert 3D-Coat's raw voxel data to flat 8bit raw voxel data.
# usage python rawvox2raw8vox.py file1.voxel
import sys
import struct
import os.path

# max read components at onece. NOT Bytes.
ONECE_READ_MAX = 1024 * 1024 * 4

def convert_8bit(size_x, size_y, size_z, infile, outfile):
    global ONECE_READ_MAX
    #print('convert 8bit to 8bit raw')
    while True:
        buf = infile.read(ONECE_READ_MAX)
        if len(buf) <= 0:
            break
        outfile.write(buf)

def convert_16bit(size_x, size_y, size_z, infile, outfile):
    global ONECE_READ_MAX
    #print('convert 16bit to 8bit raw')
    unpacker = struct.Struct('<{}H'.format(ONECE_READ_MAX))
    readsize = ONECE_READ_MAX * 2
    outbuf = bytearray(b'\x00' * ONECE_READ_MAX)
    while True:
        buf = infile.read(readsize)
        comps = int(len(buf) / 2)
        if comps <= 0:
            break
        elif len(buf) < unpacker.size:
            vals = struct.unpack('<{}H'.format(comps), buf)
        else:
            vals = unpacker.unpack(buf)
        for i, n in enumerate(vals):
            outbuf[i] = int(n / 256)
        outfile.write(outbuf[:comps])

def convert_32bit(size_x, size_y, size_z, infile, outfile):
    global ONECE_READ_MAX
    #print('convert 32bit to 8bit raw')
    unpacker = struct.Struct('<{}f'.format(ONECE_READ_MAX))
    readsize = ONECE_READ_MAX * 4
    outbuf = bytearray(b'\x00' * ONECE_READ_MAX)
    while True:
        buf = infile.read(readsize)
        comps = int(len(buf) / 4)
        if comps <= 0:
            break
        elif len(buf) < unpacker.size:
            vals = struct.unpack('<{}f'.format(comps), buf)
        else:
            vals = unpacker.unpack(buf)
        for i, n in enumerate(vals):
            outbuf[i] = int(n * 255)
        outfile.write(outbuf[:comps])

def convert_voxel(filepath):
    try:
        f = open(filepath, 'rb')
    except IOError as err:
        print(err)
    else:
        (magic, size_x, size_y, size_z, bits) = struct.unpack('<4sLLLL', f.read(20))
        if magic == b'XOVR':
            print('--- input file: {}'.format(filepath))
            print(' size: ({}, {}, {})'.format(size_x, size_y, size_z))
            print(' bits per voxel: {}'.format(bits))
            (nameroot, ext) = os.path.splitext(filepath)
            outname = '{}_{}_{}_{}.raw'.format(nameroot, size_x, size_y, size_z)
            print(' output: {}'.format(outname))
            try:
                outf = open(outname, 'wb')
            except IOError as err:
                print(err)
            else:
                if bits == 8:
                    convert_8bit(size_x, size_y, size_z, f, outf)
                elif bits == 16:
                    convert_16bit(size_x, size_y, size_z, f, outf)
                elif bits == 32:
                    convert_32bit(size_x, size_y, size_z, f, outf)
                outf.close()
        else:
            print('{} is not a 3D-Coat raw voxel format'.format(filepath))
        f.close()

if len(sys.argv) <= 1:
    print('Convert 3D-Coat raw voxel files to 8bit raw voxel file')
    print('usage python {} file [file ...]'.format(sys.argv[0]))
else:
    for i in sys.argv[1:]:
        convert_voxel(i)
