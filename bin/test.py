#!/usr/bin/python3

import os,sys
import time

###
# These variables configure the behavior of the script
# 
datadir = '../data'

go_f = True
while go_f:
    cuto2_psig = float(input('Cutting Oxygen (psig):'))
    soinit_in = float(input('Initial standoff (in):'))
    feedrate_ipm = float(input('Feed rate (ipm):'))
    plate_in = float(input('Plate thickness (in):'))
        
    go_f = input('Is this correct? (y/n):').lower() != 'y'

datadir = os.path.join(datadir, time.strftime('%Y%m%d%H%M%S'))
os.mkdir(datadir)

cmd = 'lcburst -c flow.conf -d ' + os.path.join(datadir, 'flow.dat')
print(cmd)
os.system(cmd)

flags = f'-f soinit_in={soinit_in} -f feedrate_ipm={feedrate_ipm} -f cuto2_psig={cuto2_psig} -f plate_in={plate_in} '
cmd = 'lcrun ' + flags + '-c lcrun.conf -d ' + os.path.join(datadir, 'vis.dat')

print(cmd)
os.system(cmd)
