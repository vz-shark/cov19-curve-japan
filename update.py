#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import requests
import pandas as pd
import numpy as np
import hashlib
from termcolor import colored, cprint


datadir = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
cachedir = './cache/'

vslist = {
    'confirmed_global':{
        'url': 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        'updates': ['curvefit-global.ipynb']
    },
    'confirmed_us':{
        'url': 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv',
        'updates': ['curvefit-us.ipynb']
    }
}

def cli():
    parser = argparse.ArgumentParser(description='update html')
    parser.add_argument('--forced', action='store_true', default=False, help='fourced update flag')
    parser.add_argument('--gitupdate',action='store_true', default=False, help='git update (add/commit/push) flag')
    args = parser.parse_args()

    errcount = 0
    print('========== Check Update ==========')
    updateset = set()
    for key, val in vslist.items():
        print(f'##### {key}')

        #local cache
        locf = os.path.join(cachedir, val['url'].split('/')[-1])
        print(f'\tlocal cache file ......  ', end='')
        lochash = 'not exists'
        if( os.path.exists(locf) ):
            with open(locf, 'r') as fd:
                nakami = fd.read()
                lochash = hashlib.sha256(nakami.encode('utf-8')).hexdigest()
        print(f'hash="{lochash}"')
        
        #http get
        print(f'\thttp get method .......  ', end='')
        newhash = 'HTTP GET NG'
        res = requests.get(val['url'])
        if(not res.ok):
            cprint(f'error!! {res}', 'red')
            continue
        newhash = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
        print(f'hash={newhash}')
        
        #comparsion
        if(lochash == newhash and args.forced is False):
            print(f'\tSkipped!!  (allready latest)')        
            continue
        with open(locf, 'w') as fd:
            fd.write(res.text)
        
        #
        for one in val['updates']:
            print('\tset update target : ', one)
            updateset.add(one)
    
    print('\n=========== Update HTML ==========')
    print(f'\tnum of update = {len(updateset)}')
    updatecount = 0
    for one in updateset:
        print(f'##### nvconvert : {one} ........')
        #cmdstr = f'jupyter nbconvert --to html --execute {one}  --template=nbextensions --output ./{os.path.splitext( os.path.basename(one))[0]}.html'
        cmdstr = f'jupyter nbconvert --to notebook --execute {one}'
        ret = subprocess.run(cmdstr, shell=True, capture_output=True, check=True)
        print('\t',ret)
        if(ret.returncode != 0 ):
            cprint(f'\tError!!!', 'red')
            errcount += 1
            continue
        updatecount += 1
    print('\tupdate success = ', updatecount)

    if(args.gitupdate and updatecount != 0):
        print('\n============ GIT =============')
        if(errcount != 0):
            cprint(f'\t Cancel !!. (errcount={errcount})', 'red')
            return(-1)
        
        cmsg = 'auto update'
        if(args.forced):
            cmsg = 'forced auto update'
        subprocess.run(f'git add --all', shell=True)
        subprocess.run(f'git commit -m "{cmsg}"', shell=True)
        subprocess.run(f'git push', shell=True)

    print('\n\nFinish!')
    return(0)   

        
if __name__ == '__main__':
    cli()
