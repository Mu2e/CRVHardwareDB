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
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2020Jul09.... Changed crvUtilities2018->crvUtilities; changed cmjGuiLibGrid2018Oct1->cmjGuiLibGrid2019Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##
#!/bin/env python
from Tkinter import *         # get widget class
import sys
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")        ## 2020Jul09
from DataLoader import *
from databaseConfig import *
from cmjGuiLibGrid import *	## 2020Aug03
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import time
##
##
ProgramName = "ExtrusionCounter"
Version = "version2020.12.16"


##############################################################################################
##############################################################################################
###  Class to store extrusion elements
class countExtrusions(object):
  def __init__(self):
    print 'inside class extrusion, init \n'
    self.__cmjDebug = 0        ## no debug statements
    self.__maxColumns = 7      ## maximum columns in the spread sheet
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
    ##self.sendToDevelopmentDatabase()  ## choose send to development database as default for now
## -----------------------------------------------------------------
  def turnOnDebug(self,tempDebugLevel):
    self.__cmjDebug = tempDebugLevel  # turn on debug
    print("...extrusion::turnOnDebug... turn on debug: level = %s \n") % (self.__cmjDebug)
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn on debug
    print("...extrusion::turnOffDebug... turn off debug \n")
## -----------------------------------------------------------------
  def setDebugLevel(self,tempValue):
    self.__cmjDebug = int(tempValue)  # turn on debug
    print("...extrusion::setDebugLevel... set debug level = %d\n") % self.__cmjDebug
## -----------------------------------------------------------------
##
##	Make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Extrusions Tables"
    self.__whichDatabase = 'development'
    print("......__countExtrusions__::getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
    #print("....__countExtrusions__::setupDevelopmentDatabase... self.__url =  %s") % self.__queryUrl
##
## -------------------------------------------------------------------
##	Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    #self.__group = "Extrusions Tables"
    self.__whichDatabase = 'production'
    print("...__countExtrusions__::setupProductionDatabase... get from production database \n")
    self.__queryUrl = self.__database_config.getProductionQueryUrl()
    #print("....__countExtrusions__::setupProductionDatabase... self.__url =  %s") % self.__queryUrl
## ---------------------------------------------------------------------------
  def countTheExtrusions(self):
    self.__getDatabaseValue = DataQuery(self.__queryUrl)
    self.__tables = "extrusions"
    #rows = dataQuery.query('mu2e_hardware_prd', 'sipms', 'count(*)', echoUrl=True)
    self.__rows = self.__getDatabaseValue.query(self.__database,self.__tables,'count(*)')
    print("\nQuery Results:")
    for self.__row in self.__rows:
      print(self.__row)
    print("__countExtrusion__:countTheExtrusions:: number of rows = %s ") % self.__rows[0]


##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
#	Build general help string....
  modeString = []
  modeString.append("This script is run in one mode:")
  modeString.append("> python ExtrusionsCounter.py --database ''production''")
  modeString.append("The user may use a relative or absolute path to the spreadsheet")
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
  options, args = parser.parse_args()
##
  myExtrusions = countExtrusions()
  print ("\nRunning %s \n") % (ProgramName)
  print ("%s \n") % (Version)
  if(options.database == 'development'):
      myExtrusions.setupDevelopmentDatabase()  ## turns on send to development database
  elif(options.database == 'production'):
      myExtrusions.setupProductionDatabase()  ## turns on send to production database
  myExtrusions.countTheExtrusions()
#
  print("Finished running %s \n") % (ProgramName)