from glob import glob
from os import mkdir
from os.path import join, isdir, isfile
from shutil import copytree
import logging
import sys

import pandas as pd
import h5py
import yaml

DEFAULT = ['No', 'Pre-Plus', 'Plus']


def make_sub_dir(dir_, sub, tree=None):

    sub_dir = join(dir_, sub)
    if not isdir(sub_dir):

        if tree:
            copytree(tree, sub_dir, ignore=ignore_files)
        else:
            mkdir(sub_dir)

    return sub_dir


def ignore_files(dir, files):
    return [f for f in files if isfile(join(dir, f))]


def find_images(im_path, extensions=[]):

    files = []
    for ext in ['*.bmp', '*.BMP', '*.png', '*.jpg', '*.tif'] + extensions:
        files.extend(glob(join(im_path, ext)))

    return sorted(files)


def find_images_by_class(im_path, classes=None):

    if classes is None:
        classes = DEFAULT

    images = {}
    for class_ in classes:
        images[class_] = find_images(join(im_path, class_))

    return images


def get_subdirs(root_dir):

    return [x for x in glob(join(root_dir, '*')) if isdir(x)]


def write_hdf5(arr, outfile):
    with h5py.File(outfile, "w") as f:
        f.create_dataset("image", data=arr, dtype=arr.dtype)


def parse_yaml(conf_file):

    with open(conf_file, 'r') as f:
        return yaml.load(f)


def setup_log(log_file, to_file=False):

    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if to_file:
        l_open = open(log_file, 'a')
        fh = logging.FileHandler(log_file)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        sys.stdout, sys.stderr = l_open, l_open
    else:
        sout = logging.StreamHandler(sys.stdout)
        sout.setFormatter(fmt)
        logger.addHandler(sout)


def dict_to_csv(my_dict, my_csv):

    pd.DataFrame(my_dict).to_csv(my_csv)


def csv_to_dict(my_csv):

    return pd.read_csv(my_csv).to_dict(orient='list')


def series_to_plot_dict(series, key, value):

    sorted_list = [{key: k, value: v} for k, v in series.to_dict().items()]
    return pd.DataFrame(data=sorted_list)
