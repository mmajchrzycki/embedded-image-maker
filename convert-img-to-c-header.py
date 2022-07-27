#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
from PIL import Image

RGB_WEIGHTS = [0.2989, 0.5870, 0.1140]

def bytes_to_c_arr(data, lowercase=True):
    return [format(b, '#04x' if lowercase else '#04X') for b in data]

if __name__ == "__main__":
    # get script path
    script_path = os.path.dirname(os.path.realpath(__file__))
    output_path = script_path + '/output-header/'

    # remove output dir if exist and create a fresh one
    if os.path.exists(output_path):
        os.system('rm -rf {}'.format(output_path))
    os.mkdir(output_path)
        
    # read input image
    with open(sys.argv[1], 'rb') as f:
        input_image = Image.open(f).convert('RGB')

    # read the file and store as a raw image
    raw_image888_array = np.asarray(input_image)

    # convert image to RGB565
    R5 = (raw_image888_array[...,0]>>3).astype(np.uint16) << 11
    G6 = (raw_image888_array[...,1]>>2).astype(np.uint16) << 5
    B5 = (raw_image888_array[...,2]>>3).astype(np.uint16)
    raw_image565_array = R5 | G6 | B5

    # convert image to grayscale
    raw_imageBW_array = np.dot(raw_image888_array[...,:3], RGB_WEIGHTS).astype(np.uint16)

    # uncomment to dump converted images to output
    # raw_image888 = Image.fromarray(raw_image888_array)
    # raw_image888.convert('RGB').save(output_path + 'rgb888.jpg')
    # PIL library is not supporting RGB565 format
    # raw_image565 = Image.fromarray(raw_image565_array)
    # raw_image565.save(output_path + 'rgb565.jpg')
    # raw_imageBW = Image.fromarray(raw_imageBW_array)
    # raw_imageBW.convert('RGB').save(output_path + 'bw.jpg')

    # dump all arrays into C-style header file
    file_path = output_path + "images_raw.h"
    with open(file_path, "w") as f:
        # get filename from full path
        filename = file_path.split('/')[-1]
        f.write("#ifndef {}\n".format(filename.upper().replace('.', '_')))
        f.write("#define {}\n".format(filename.upper().replace('.', '_')))
        f.write("\n")
        f.write("#include <stdint.h>\n")
        f.write("\n")
        f.write("const size_t image_width = {};\n".format(input_image.width))
        f.write("const size_t image_height = {};\n".format(input_image.height))
        f.write("\n")
        f.write("const size_t image_888_raw_size = {};\n".format(raw_image888_array.size))
        f.write("const uint8_t image_888_raw[] = {\n")
        f.write(", ".join(bytes_to_c_arr(raw_image888_array.tobytes())))
        f.write("\n};\n")
        f.write("\n")
        f.write("const size_t image_565_raw_size = {};\n".format(raw_image565_array.size * raw_image565_array.dtype.itemsize))
        f.write("const uint8_t image_565_raw[] = {\n")
        f.write(", ".join(bytes_to_c_arr(raw_image565_array.tobytes())))
        f.write("\n};\n")
        f.write("\n")
        f.write("const size_t image_BW_raw_size = {};\n".format(raw_imageBW_array.size * raw_imageBW_array.dtype.itemsize))
        f.write("const uint8_t image_BW_raw[] = {\n")
        f.write(", ".join(bytes_to_c_arr(raw_imageBW_array.tobytes())))
        f.write("\n};\n")
        f.write("\n")
        f.write("#endif\n")
        f.close()
