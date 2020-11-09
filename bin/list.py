#!/usr/bin/python3

import os,sys

datadir = '../data'

# Loop over the contents of the data directory
# Each is a data set
contents = os.listdir(datadir)
contents.sort()
for this in contents:
    post1 = os.path.join(datadir, this, 'post1/post1.param')
    p1param = {'this':this[-5:]}
    if os.path.isfile(post1):
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
                    
        sys.stdout.write('{this} {plate_in:.2f}in  {feedrate_ipm:.1f}ipm  {total_scfh:.2f}scfh  {ratio_fo:.3f}f/o  {cuto2_psig:.0f}psig  {somin_in:.3f} to {somax_in:.3f}in\n'.format(**p1param))
    else:
        sys.stdout.write('{this}\n'.format(**p1param))
