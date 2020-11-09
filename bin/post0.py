#!/usr/bin/python3

import os,sys,shutil
import lconfig

datadir = '../data'
quiet=False
contents = os.listdir(datadir)
contents.sort()

for this in contents:
    source = os.path.join(datadir, this, 'vis.dat')
    post1 = os.path.join(datadir, this, 'post1', 'post1.param')
    
    if os.path.isfile(post1):
        print(post1)
        data = lconfig.LConf(source, data=False)
        
        p1param = {}
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
                    
        # Make a backup copy
        shutil.copyfile(post1, post1+'.back')
        
        ####
        # Modify the p1param here
        ####
        p1param['feedrate_ipm'] = data.get_meta(0,'feedrate_ipm')
        
        locals().update(p1param)
        
        # Write a new post1 file
        with open(post1,'w') as ff:
            line = f'soinit_in {soinit_in}\nsomin_in {somin_in}\nsomax_in {somax_in}\nplate_in {plate_in}\n'
            ff.write(line)
            if not quiet: 
                sys.stdout.write(line)
            line = f'preheat_sec {preheat_sec}\nstart_sec {start_sec}\nstop_sec {stop_sec}\n'
            ff.write(line)
            if not quiet: 
                sys.stdout.write(line)
            line = f'fex_hz {fex_hz}\nfs_hz {fs_hz}\nfg_scfh {fg_scfh}\no2_scfh {o2_scfh}\ntotal_scfh {total_scfh}\nratio_fo {ratio_fo}\n'
            ff.write(line)
            if not quiet: 
                sys.stdout.write(line)
            line = f'cuto2_psig {cuto2_psig}\nfeedrate_ipm {feedrate_ipm}\n'
            ff.write(line)
            if not quiet: 
                sys.stdout.write(line)
