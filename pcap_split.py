import os
import numpy
import errno
from PIL import Image
import binascii
from array import *
from random import shuffle
import sys
PNG_SIZE = 28

stringConmmand = "SplitCap.exe -r "
new_filename = bytes('./'+sys.argv[1],encoding='utf-8')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def getMatrixfrom_pcap(filename,width):
    with open(filename, 'rb') as f:
        content = f.read()
    hexst = binascii.hexlify(content)
    fh = numpy.array([int(hexst[i:i+2],16) for i in range(0, len(hexst), 2)])
    if len(fh)<784:
        x = numpy.zeros(784)
        x[:len(fh)]=fh
        fh = x
    if len(fh)>784:
        fh = fh[:784]
    rn = int(len(fh)/width)
    fh = numpy.reshape(fh[:(rn*width)],(-1,width))
    fh = numpy.uint8(fh)
    return fh

def session2png(output,output_png):
    listdir = os.listdir(output)
    for file in listdir:
        out_f = os.path.join(output_png,file)
        file = os.path.join(output,file)
        im = Image.fromarray(getMatrixfrom_pcap(file, PNG_SIZE))
        png_full = out_f + '.png'
        im.save(png_full)

def png2mnist(png_path,mnist_path):
    listdir = os.listdir(png_path)
    shuffle(listdir)
    data_image = array('B')
    for file in listdir:
        ture_file = os.path.join(png_path,file)
        Im = Image.open(ture_file)
        pixel = Im.load()
        width, height = Im.size
        for x in range(0,width):
            for y in range(0,width):
                data_image.append(pixel[y,x])
    hexval = "{0:#0{1}x}".format(len(listdir), 6)
    hexval = '0x' + hexval[2:].zfill(8)
    header = array('B')
    header.extend([0, 0, 8, 1])
    header.append(int('0x' + hexval[2:][0:2], 16))
    header.append(int('0x' + hexval[2:][2:4], 16))
    header.append(int('0x' + hexval[2:][4:6], 16))
    header.append(int('0x' + hexval[2:][6:8], 16))
    header.extend([0, 0, 0, 28, 0, 0, 0, 28])
    header[3] = 3  # Changing MSB for image data (0x00000803)
    data_image = header + data_image
    output_png_img = mnist_path+ 'unclassifed' + '-images-idx3-ubyte'
    print(output_png_img)
    output_file = open(output_png_img,'wb')
    data_image.tofile(output_file)
    output_file.close()
    os.system('gzip '+output_png_img)

def execCommand(command):
    #执行命令
    print(command)
    os.system(command)
    print('\n')
def split(filename):
    filename = './'+filename.split('/')[1][:-1]
    output = './'+filename[2:-5] + "/pcap_dir/"
    output_png = './'+filename[2:-5]+"/png_dir/"
    mnist_path = './'+filename[2:-5]+'/mnist_dir/'
    mkdir_p(output)
    mkdir_p(output_png)
    mkdir_p(mnist_path)
    command = stringConmmand + filename + ' -o ' +output
    print(command)
    p = os.popen(command)
    return output,output_png,mnist_path
output,output_png,mnist_path = split(str(new_filename))
session2png(output,output_png)
png2mnist(output_png,mnist_path)