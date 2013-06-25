#!/usr/bin/env python
# encoding: utf-8
"""
IdeasGeneratorWrapper.py

Created by VL and LN on 2012-08-15.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
os.chdir(os.path.expanduser(os.sep.join(['~/', 'Dropbox', 'Personal', 'ideas_generator'])))
import IG
reload(IG)
import random as rand

def main():
	
	mainwindow = IG.MainWindow()

if __name__ == '__main__':
    main()