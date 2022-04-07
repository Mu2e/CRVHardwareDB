# -*- coding: utf-8 -*-
##
## File = "generalUtilities.py""
##
## This class contains general utilities to 
## accomplish various tasks to for python
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