import os
import sys
from pathlib import Path
from urllib.parse import urlparse
import argparse
import subprocess
import requests
import pandas as pd
import numpy as np
import hashlib
from termcolor import colored, cprint



class UpdateTool(object):
    def __init__(self, cachedir='../cache/', loglevel = 2):
        self.cachedir = cachedir
        self.loglevel = loglevel 

    def log(self, loglevel, msg):
        if( loglevel <= self.loglevel):
            print(msg)

    def make_cachefname(self, url, savefname="auto"):
        fname = os.path.join( self.cachedir, os.path.basename( urlparse(url).path ) )
        if( savefname == "auto"):
            pass
        else:
            if(savefname[-1] == "/"):
                fname = os.path.join(savefname, fname)
            else:
                fname = savefname
        return(fname)

    def download(self, url, savefname=None):
        self.log(1, f'http get method .......  {url}')
        res = requests.get(url)
        if(not res.ok):
            self.log( 1, colored(f'error!! {res}', 'red'))
            return False, None
        if( savefname is not None):
            self.log(1, f"save... {savefname}")
            if(not os.path.exists( Path(savefname).parent)):
                os.makedirs(Path(savefname).parent)
            with open(savefname, "w") as fd:
                fd.write(res.text)
        return True, res.text
    
    def read(self, url, savefname="auto", force_download=False):
        self.log(1, f"read() start")
        self.log(2, f"read(): url={url}")
        self.log(2, f"read(): savefname={url}")
        self.log(2, f"read(): url={url}")
        fname = self.make_cachefname(url, savefname)
        self.log(2, f"read(): fname={fname}")
        
        # cache
        cache_hash = "not exists"
        cache_val = None 
        if( os.path.exists(fname) ):
            with open(fname, "r") as fd:
                cache_val = fd.read()
                cache_hash =  hashlib.sha256( cache_val.encode('utf-8')).hexdigest()
        if( force_download is False):
            return(0, cache_val)
        
        # download
        dl_hash = "no download"
        dl_val = None
        ret, dl_val= self.download(url, savefname=fname)
        assert ret is True, "download error"
        dl_hash = hashlib.sha256( dl_val.encode('utf-8')).hexdigest()
        
        # comparsion
        self.log(1, f"read(): hash cache = {cache_hash}")
        self.log(1, f"read(): hash dl    = {dl_hash}")
        if( dl_hash == dl_val):
            return 1, dl_val
        return(2, dl_val)



            
        

        

        

        

        for target_list in expression_list:
            pass
        


