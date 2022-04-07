# -*- coding: utf-8 -*-
##
## File = "ExtrusionCounter.py"
##
##  python script to count the number of entries in the 
##  extrusion tables
##
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2015Sep23
##
##  Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##                        yellow highlight to selected scrolled list items
##  Modified by cmj2020Jul09... change hdbClient_v2_0 -> hdbClient_v2_2
##  Modified by cmj2020Jul09... change crvUtilities2018->crvUtilities; cmjGuiLibGrid2018Oct1-> cmjGuiLibGrid2020Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##  Modified by cmj2022Jan28... replace "count(*)" with single view table as per Steve's Email 2022Jan28 11:10 AM
##
#!/bin/env python
from tkinter import *         # get widget class
import sys
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *
from databaseConfig import *
from cmjGuiLibGrid import *       ## 2020Aug03
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import time
##
##
ProgramName = "FiberCounter"
Version = "version2022.01.28"


##############################################################################################
##############################################################################################
###  Class to store extrusion elements
class countFibers(object):
  def __init__(self):
    print('inside class countSimps, init \n')
    self.__cmjDebug = 0        ## no debug statements
    self.__maxColumns = 7      ## maximum columns in the spread sheet
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
## -----------------------------------------------------------------
  def turnOnDebug(self,tempDebugLevel):
    self.__cmjDebug = tempDebugLevel  # turn on debug
    print(("...extrusion::turnOnDebug... turn on debug: level = %s \n") % (self.__cmjDebug))
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn on debug
    print("......__countFibers__::::turnOffDebug... turn off debug \n")
## -----------------------------------------------------------------
  def setDebugLevel(self,tempValue):
    self.__cmjDebug = int(tempValue)  # turn on debug
    print(("......__countFibers__::::setDebugLevel... set debug level = %d\n") % self.__cmjDebug)
## -----------------------------------------------------------------
##
##      Make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__whichDatabase = 'development'
    print("......__countFibers__::getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
    #print("....__countFibers__::setupDevelopmentDatabase... self.__url =  %s") % self.__queryUrl
##
## -------------------------------------------------------------------
##      Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__whichDatabase = 'production'
    print("...__countFibers__::setupProductionDatabase... get from production database \n")
    self.__queryUrl = self.__database_config.getProductionQueryUrl()
    print(("....__countFibers__::setupProductionDatabase... self.__url =  %s") % self.__queryUrl)
## ---------------------------------------------------------------------------
  def countTheFibers(self):
    self.__getDatabaseValue = DataQuery(self.__queryUrl)
    self.__tables = "mu2e_table_cnts"   ## cmj 2022Jan28
    self.__rows = self.__getDatabaseValue.query(self.__database,self.__tables,"fibers_cnt") ## cmj 2022Jan28
    print("\nQuery Results:")
    for self.__row in self.__rows:
      print((self.__row))
    print(("__countExtrusion__:countTheExtrusions:: number of rows = %s ") % self.__rows[0])


##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
#      Build general help string....
  modeString = []
  modeString.append("This script is run in one mode:")
  modeString.append("> python ExtrusionsCounter.py --database ''production''")
  modeString.append("The user may use a relative or absolute path to the spreadsheet")
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
  options, args = parser.parse_args()
##
  mySipm = countFibers()
  print(("\nRunning %s \n") % (ProgramName))
  print(("%s \n") % (Version))
  if(options.database == 'development'):
      mySipm.setupDevelopmentDatabase()  ## turns on send to development database
  elif(options.database == 'production'):
      mySipm.setupProductionDatabase()  ## turns on send to production database
  mySipm.countTheFibers()
#
  print(("Finished running %s \n") % (ProgramName))
