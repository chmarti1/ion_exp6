#!/usr/bin/python3

import os,sys

datadir = '../data'
toremove = ['.png']

for dataset in os.listdir(datadir):
    dataset = os.path.join(datadir, dataset)
    for this in os.listdir(dataset):
        for ext in toremove:
            if this.endswith(ext):
                this = os.path.join(dataset,this)
                print(this)
                os.remove(this)
