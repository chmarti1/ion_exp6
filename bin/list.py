#!/usr/bin/python3

import os,sys

datadir = '../data'

searchfor = None
if len(sys.argv) > 1:
    searchfor = sys.argv[1:]

# Loop over the contents of the data directory
# Each is a data set
go_f = False
count = 0
contents = os.listdir(datadir)
contents.sort()
for this in contents:
    post1 = os.path.join(datadir, this, 'post1/post1.param')
    p1param = {'this':this[-5:]}
    go_f = False
    if os.path.isfile(post1):
        count += 1
        if searchfor is not None:
            go_f = False
            for sf in searchfor:
                if this.endswith(sf):
                    go_f = True
                    break
        else:
            go_f = True
        
    if go_f:
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
                    
        sys.stdout.write(f'{count:02d}:' + '{this} {plate_in:.2f}in  {feedrate_ipm:.1f}ipm  {total_scfh:.2f}scfh  {ratio_fo:.3f}f/o  {cuto2_psig:.0f}psig  {somin_in:.3f} to {somax_in:.3f}in\n'.format(**p1param))
    else:
        sys.stdout.write('{this}\n'.format(**p1param))
