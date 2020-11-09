#!/usr/bin/python3

import numpy as np
import lconfig as lc
import matplotlib.pyplot as plt
import os,sys
from multiprocessing import Pool

def worker(target):
    print(target)
    os.system(f'./post1.py quiet force {target}')

#
# These are lines of code you may want to edit before running post.py
#
datadir = '../data'
nblock = 2000
so_threshold = .03
so_window_sec = 10
####

# The early data are scanned one block at a time to identify the first 
# block where preheating had begun.  This is used to identify the 
# standoff offset height.


force = 'force' in sys.argv[1:]
quiet = 'quiet' in sys.argv[1:]
arg = sys.argv[-1]
sourcedir = None

if arg == 'all':
    contents = os.listdir(datadir)
    contents.sort()
    with Pool(processes=8) as pool:
       pool.map(worker, contents) 
    exit(0)

for this in os.listdir(datadir):
    if this.endswith(arg):
        if sourcedir:
            raise Exception(f'POST1.PY: found multiple data entries that end with {arg}')
        sourcedir = os.path.join(datadir,this)
        
if not quiet: 
    print('Working on: ' + sourcedir)


source = os.path.join(sourcedir,'vis.dat')

# Check for prior post1 results
# Make the post1 directory if it doesn't already exist
targetdir = os.path.join(sourcedir, 'post1')
if os.path.isdir(targetdir):
    if not force and 'y' != input('Overwrite previous post1 results? (y/n):'):
        raise Exception('Disallowed from overwriting prior post1 results')
    os.system(f'rm -rf {targetdir}')
os.mkdir(targetdir)

# LOAD DATA!
data = lc.LConf(source, data=True, cal=True)

# Get channels
voltage = data.get_channel(0)
current = data.get_channel(1)
standoff = data.get_channel(2)
# How many data points were there?
N = data.ndata()
# Truncate N to an integer number of blocks
N = nblock*(N//nblock)

# Get experimental parameters
fs = data.get(0,'samplehz')
fstep = fs / nblock
fex = data.get(0,'aofrequency',aoch=0)
soinit_in = data.get_meta(0, 'soinit_in')
so_window_index = int(so_window_sec * fs)

# If flow.dat exists, get flow information from it
target = os.path.join(sourcedir, 'flow.dat')
if os.path.isfile(target):
    flow = lc.LConf(target, data=True, cal=True)
    fg_scfh = np.mean(flow.get_channel(0))
    o2_scfh = np.mean(flow.get_channel(1))
# Otherwise, get it from the data file itself
else:
    fg_scfh = data.get_meta(0,'fg_scfh')
    o2_scfh = data.get_meta(0,'o2_scfh')
# Calculate the total and ratio
total_scfh = fg_scfh + o2_scfh
ratio_fo = fg_scfh / o2_scfh
# Get cutting O2 pressure
cuto2_psig = data.get_meta(0,'cuto2_psig') if data.is_meta(0,'cuto2_psig') else 75.
# If the plate thickness is not specified, then it is 0.5inches
plate_in = data.get_meta(0,'plate_in') if data.is_meta(0,'plate_in') else 0.5
feedrate_ipm = data.get_meta(0,'feedrate_ipm')

# calculate the index where the excitation frequency may be found
index_ex = int(round(fex / fstep))

so_in = []
time_s = []
VV = np.zeros((nblock, N//nblock), dtype=complex)
II = np.zeros((nblock, N//nblock), dtype=complex)

index_zero = None
for count,index in enumerate(range(0,N,nblock)):
    # If we haven't found the start of preheat yet
    if not index_zero:
        # Look for a window of standoffs where the value does not change for so_window_sec seconds
        window = standoff[index:index+so_window_index]
        if np.max(window) - np.min(window) < so_threshold:
            index_zero = index
        
    vv = voltage[index:index+nblock]
    ii = current[index:index+nblock]
    VV[:,count] = np.fft.fft(vv)/nblock
    II[:,count] = np.fft.fft(ii)/nblock
    so_in.append(np.mean(standoff[index:index+nblock]))
    
so_in = np.array(so_in)
time_s = data.get_time()[0:N:nblock]
r_Mohms = np.real(VV[index_ex,:]/II[index_ex,:])
f_hz = np.arange(0., fs, fstep)

# Adjust the standoff
if not quiet:
    print(f'Found preheat start at index {index_zero}, {data.get_time()[index_zero]} seconds, at height {standoff[index_zero]} in')
so_in += soinit_in - standoff[index_zero]

# Write analysis results to post1.param
with open(os.path.join(targetdir, 'post1.param'), 'w') as ff:
    line = f'soinit_in {soinit_in}\nsomin_in {so_in.min()}\nsomax_in {so_in.max()}\nplate_in {plate_in}\n'
    ff.write(line)
    if not quiet: 
        sys.stdout.write(line)
    line = f'preheat_sec {data.get_time()[index_zero]}\nstart_sec 0.\nstop_sec {time_s[-1]}\n'
    ff.write(line)
    if not quiet: 
        sys.stdout.write(line)
    line = f'fex_hz {fex}\nfs_hz {fs}\nfg_scfh {fg_scfh}\no2_scfh {o2_scfh}\ntotal_scfh {total_scfh}\nratio_fo {ratio_fo}\n'
    ff.write(line)
    if not quiet: 
        sys.stdout.write(line)
    line = f'cuto2_psig {cuto2_psig}\nfeedrate_ipm {feedrate_ipm}\n'
    ff.write(line)
    if not quiet: 
        sys.stdout.write(line)

# Generate waterfall diagrams
fmax = 500.
index = int(fmax / fstep)

target = os.path.join(targetdir, 'vft.png')
f = plt.figure(1)
f.clf()
ax1 = f.subplots(1,1)
ax1.pcolor(time_s, f_hz[:index], 20*np.log10(np.abs(VV[:index,:])), vmin=20*np.log10(.0003), vmax=20*np.log10(.3))
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Frequency (Hz)')
f.savefig(target, dpi=300)

target = os.path.join(targetdir, 'ift.png')
f = plt.figure(1)
f.clf()
ax1 = f.subplots(1,1)
ax1.pcolor(time_s, f_hz[:index], 20*np.log10(np.abs(II[:index,:])), vmax=20*np.log10(20))
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Frequency (Hz)')
f.savefig(target, dpi=300)

f = plt.figure(1)
target = os.path.join(targetdir, 'rst.png')
f.clf()
ax1,ax2 = f.subplots(2,1)
ax1.plot(time_s, so_in, 'k')
ax2.plot(time_s, r_Mohms, 'k')
ax1.minorticks_on()
ax1.grid(b=True, which='minor', ls='-', color=[.9,.9,.9])
ax1.grid(b=True, which='major', ls='-')
ax1.set_ylabel('Standoff (in)')
ax1.set_ylim((0,.3))
ax2.minorticks_on()
ax2.grid(b=True, which='minor', ls='-', color=[.9,.9,.9])
ax2.grid(b=True, which='major', ls='-')
ax2.set_ylabel('R (MOhm)')
ax2.set_ylim((0,.08))
f.savefig(target, dpi=300)

f = plt.figure(1)
target = os.path.join(targetdir, 'rs.png')
f.clf()
ax1 = f.subplots(1,1)
ax1.plot(so_in, r_Mohms, 'k')
ax1.minorticks_on()
ax1.grid(b=True, which='major', ls='-')
ax1.grid(b=True, which='minor', ls='--')
ax1.set_ylabel('Resistance (M$\Omega$)')
ax1.set_xlabel('Standoff (in)')
ax1.set_xlim((0, .3))
f.savefig(target, dpi=300)

f = plt.figure(1)
target = os.path.join(targetdir, 'vt.png')
f.clf()
ax1 = f.subplots(1,1)
ax1.plot(time_s, np.abs(VV[0,:]), 'g', label='DC')
ax1.plot(time_s, np.abs(VV[index_ex,:]), 'k', label='Fundamental')
ax1.plot(time_s, np.abs(VV[2*index_ex,:]), 'b', label='First Harmonic')
ax1.plot(time_s, np.abs(VV[3*index_ex,:]), 'r', label='Second Harmonic')
ax1.set_ylim(0,.3)
ax1.minorticks_on()
ax1.grid(b=True, which='major', ls='-')
ax1.grid(b=True, which='minor', ls='--')
ax1.set_ylabel('Amplitude (V)')
ax1.set_xlabel('Time (s)')
f.savefig(target, dpi=300)

