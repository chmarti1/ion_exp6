#!/usr/bin/python3

import os,sys,shutil

datadir = '../data'
imdir = '../../../ionimages/'

# Loop through all data entry directories
for sourcedir_short in os.listdir(datadir):
    # sourcedir_short is the name of the source without the path
    sourcedir = os.path.join(datadir,sourcedir_short)
    # Check the source data directory for any compressed image files
    for source in os.listdir(sourcedir):
        if source.endswith('.tar.bz2') or source.endswith('.tar.gz') or source.endswith('.zip'):
            # If there are image data available
            targetdir = os.path.join(imdir, sourcedir_short)
            # If this is the first image file from this dataset, we'll need to create a target directory
            if not os.path.isdir(targetdir):
                os.mkdir(targetdir)
            # Move the file
            print(sourcedir, targetdir, source)
            shutil.move(os.path.join(sourcedir, source), os.path.join(targetdir, source))

