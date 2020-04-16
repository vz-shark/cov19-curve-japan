#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import argparse

import requests
import hashlib
from termcolor import colored, cprint

sys.path.append("../utils/")
import updatelib



def cli():
    git_action = ['no', 'stage', 'commit', 'push'] 
    parser = argparse.ArgumentParser(description='update html')
    parser.add_argument('--forced', action='store_true', default=False, help='fourced update flag')
    parser.add_argument('--git', default=git_action[0], choices=git_action, help='git action [no|stage|commit|push]')
    args = parser.parse_args()

    uptool = updatelib.UpdateTool(loglevel=0)






if __name__ == "__main__":
    cli()

    


#scp -r app utils mksv:ncs/

