#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import argparse
import subprocess
import requests
import hashlib
from termcolor import colored, cprint

sys.path.append("../utils/")
import updatelib


datadir = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
cachedir = './cache/'

vslist = {
    'confirmed_global':{
        'url': 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        'updates': ['./curvefit-global.ipynb']
    },
    'confirmed_us':{
        'url': 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv',
        'updates': ['./curvefit-us.ipynb']
    },
    'confirmed_japan':{
        'url': 'https://raw.githubusercontent.com/swsoyee/2019-ncov-japan/master/Data/byDate.csv',
        'updates': ['./curvefit-japan.ipynb', './curvefit-animate-japan.ipynb' ]
    }
}

def cli():
    git_action = ['no', 'stage', 'commit', 'push'] 
    parser = argparse.ArgumentParser(description='update html')
    parser.add_argument('--forced', action='store_true', default=False, help='fourced update flag')
    parser.add_argument('--git', default=git_action[0], choices=git_action, help='git action [no|stage|commit|push]')
    args = parser.parse_args()

    uptool = updatelib.UpdateTool(loglevel=0)


    errcount = 0
    print('========== Check Update ==========')
    updateset = set()
    for key, val in vslist.items():
        print(f'##### {key}')
        fl, _ = uptool.read(val['url'], force_download=True)
        if( fl <= 2 and args.forced is False):
            print(f'\tSkipped!!  (allready latest)')        
            continue
        for one in val['updates']:
            print('\tset update target : ', one)
            updateset.add(one)
    
    print('\n=========== Update Notebook ===========')
    print(f'\tnum of update = {len(updateset)}')
    updatecount = 0
    updatefiles = ""
    for one in updateset:
        print(f'##### nvconvert to notebook: {one} ........')
        #cmdstr = f'jupyter nbconvert --to html --execute {one}  --template=nbextensions --output ./{os.path.splitext( os.path.basename(one))[0]}.html'
        cmdstr = f'jupyter nbconvert --to notebook --execute {one} --output ./{one}'
        ret = subprocess.run(cmdstr, shell=True, capture_output=True, check=True)
        print('\t',ret)
        if(ret.returncode != 0 ):
            cprint(f'\tError!!!', 'red')
            errcount += 1
            continue
        updatecount += 1
        updatefiles += f" {one}"
        #
        htmlfname = Path(one).with_suffix(".html")
        print(f'##### nvconvert to html    : {one} ........')
        cmdstr = f'jupyter nbconvert --to html {one} --output ./{htmlfname}'
        ret = subprocess.run(cmdstr, shell=True, capture_output=True, check=True)
        print('\t',ret)
        if(ret.returncode != 0 ):
            cprint(f'\tError!!!', 'red')
            errcount += 1
            continue
        updatecount += 1
        updatefiles += f" {htmlfname}"
    print('\tupdate success = ', updatecount)

    if(args.git != git_action[0]):
        print('\n============ GIT =============')
        if(errcount != 0):
            cprint(f'\t Cancel !!. (errcount={errcount})', 'red')
            return(-1)
        cmsg = 'auto update'
        if(args.forced):
            cmsg = 'forced auto update'
        if(args.git in git_action[1:]):
            subprocess.run(f'git add {updatefiles}', shell=True)
        if(args.git in git_action[2:]):
            subprocess.run(f'git commit -m "{cmsg}"', shell=True)
        if(args.git in git_action[3:]):
            subprocess.run(f'git push'.split())

    print('\n\nFinish!')
    return(0)   

        
if __name__ == '__main__':
    #sys.argv += ["--forced"]
    cli()
