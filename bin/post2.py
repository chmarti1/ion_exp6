#!/usr/bin/python3

import numpy as np
import lconfig as lc
import lplot
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os,sys

lplot.set_defaults(font_size=14)

#
# These are lines of code you may want to edit before running post.py
#
datadir = '../data'
nblock = 2000
color = True
####


# Which data set are we operating on?
arg = sys.argv[1]
sourcedir = None
for this in os.listdir(datadir):
    if this.endswith(arg):
        if sourcedir:
            raise Exception(f'POST2.PY: found multiple data entries that end with {arg}')
        sourcedir = os.path.join(datadir,this)

# Tell the user what we're doing
print('Working on: ' + sourcedir)

# Check for prior post2 results
# Make the post 2 directory if it doesn't already exist
targetdir = os.path.join(sourcedir, 'post2')
if os.path.isdir(targetdir):
    if 'y' != input('Overwrite previous post2 results? (y/n):'):
        raise Exception('Disallowed from overwriting prior post2 results')
    os.system(f'rm -rf {targetdir}')
os.mkdir(targetdir)

# Where do I expect to find the post 1 result summary?
post1 = os.path.join(sourcedir, 'post1', 'post1.param')
# Initialize a dictionary that will contain the post 1 result summary
p1param = {}
if not os.path.isfile(post1):
    raise Exception(f'POST2.PY: Failed to find post 1 results. Did you forget to run post1.py?\n Missing file ==> {post1}')
# Tell the user that we're loading prior results
print(f'Loading prior results from {post1}')

with open(post1,'r') as ff:
    for thisline in ff:
        # Ignore comments
        if thisline.startswith('#'):
            parts = []
        else:
            parts = thisline.split()
        # If this is a properly formatted line
        if len(parts) == 2:
            try:
                p1param[parts[0]] = float(parts[1])
            except:
                raise Exception(f'Could not parse line: {thisline}\n In file ==> {post1}')
        # Ignore empty lines and comments
        elif len(parts) == 0:
            pass
        # All other lines generate an error
        else:
            raise Exception(f'Could not parse line: {thisline}\n In file ==> {post1}')

print('Opening raw data file')

vis = os.path.join(sourcedir,'vis.dat')
data = lc.LConf(vis, data=True, cal=True)

voltage = data.get_channel(0)
current = data.get_channel(1)
standoff = data.get_channel(2)
N = data.ndata()
# Truncate N to be an integer multiple of the number of blocks
N = nblock*(N//nblock)

# Calculate frequency parameters
fs = data.get(0,'samplehz')
fstep = fs / nblock
fex = data.get(0,'aofrequency',aoch=0)

# calculate the index where the excitation frequency may be found
index_ex = int(round(fex / fstep))
# Tell the user
print(f'   Sample rate: {fs}Hz')
print(f'    Excitation: {fex}Hz')
print(f'    Block size: {nblock}')
print(f'FFT Resolution: {fstep}Hz')

# Find the height where preheating started
index = int(p1param['preheat_sec'] * fs)
so_preheat_in = standoff[index]
# Tell the user
print(f'Preheat is taken to start at time: {p1param["preheat_sec"]}sec')
print(f'   time index: {index}')
print(f'       height: {so_preheat_in}in')


# Calculate start and stop time indices
index_start = int(round(p1param['start_sec'] * fs))
index_stop = int(round(p1param['stop_sec'] * fs))
# truncate the stop index to a multiple of nblock
ntime = (index_stop-index_start)//nblock
index_stop = nblock*ntime + index_start

# Tell the user about the amount of data being used.
print(f'Starting at {p1param["start_sec"]} sec.')
print(f'Stopping at {p1param["stop_sec"]} sec.')
print(f'Start index: {index_start}')
print(f' Stop index: {index_stop}')
print(f'     Blocks: {ntime}')


so_in = []
time_s = []
VV = np.zeros((nblock, ntime), dtype=complex)
II = np.zeros((nblock, ntime), dtype=complex)


for count,index in enumerate(range(index_start,index_stop,nblock)):
    vv = voltage[index:index+nblock]
    ii = current[index:index+nblock]
    VV[:,count] = np.fft.fft(vv)/nblock
    II[:,count] = np.fft.fft(ii)/nblock
    so_in.append(np.mean(standoff[index:index+nblock]))
    time_s.append(data.get_time()[index])
so_in = np.array(so_in)
time_s = np.array(time_s)
r_Mohms = np.real(VV[index_ex,:]/II[index_ex,:])
f_hz = np.arange(0., fs, fstep)

# Adjust the standoff
so_in += data.get_meta(0,'soinit_in') - so_preheat_in

print('Generating figures')

ax1,ax2 = lplot.init_xxyy(xlabel='Standoff (mm)', ylabel='Resistance (M$\Omega$)',\
        x2label = 'Standoff (in)', label_size=14)

if color:
    # Adjust the time array to start at 0 and trim it to be N-1 long
    
    time_s = 0.5*(time_s[:-1] + time_s[1:]) - time_s[0]
    # assemble line segments
    # Borrowed from 
    # https://matplotlib.org/3.3.2/gallery/lines_bars_and_markers/multicolored_line.html
    points = np.array([so_in * 25.4, r_Mohms]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(time_s.min(), time_s.max())
    lc = LineCollection(segments, cmap='viridis', norm=norm)
    lc.set_array(time_s)
    lc.set_linewidth(2)
    ax1.add_collection(lc)
    
else:
    ax1.plot(so_in, r_Mohms, 'k')
    
ax2.set_xlim([0., 7/25.4])
ax1.set_xlim([0., 7])
ax1.set_ylim([0., 0.05])

target = os.path.join(targetdir, 'rs.png')
ax1.get_figure().savefig(target, dpi=300)
