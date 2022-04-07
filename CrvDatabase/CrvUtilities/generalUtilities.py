# -*- coding: utf-8 -*-
##
## File = "generalUtilities.py""
##
## This class contains general utilities to 
## accomplish various tasks to for python
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May11... replace tabs with spaces for block statements to convert to python 3
##
#!/bin/env python
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from collections import defaultdict
##
class generalUtilities(object):
  def __init__(self):
    return
  def nestedDict(self):		## this method allows construction of nested dictionaries
    return defaultdict(self.nestedDict)	## that are nested more than twice.