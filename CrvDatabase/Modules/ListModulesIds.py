# -*- coding: utf-8 -*-
##
## File = "ListModuleIds.py"
## Modified from File = "CountNumberOfModules.py"
## Derived from File = "ExtrusionCounter.py"
## Modified from File = "ExtrusionCounter.py"
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
##  Modified by cmj2019May16... Change default database to "production"
##  Modified by cmj2019May16... Change "hdbClient_v2_0" to "hdbClient_v2_2
##  Modified by cmj2020Jul09... Change crvUtilities2018 -> crvUtilities; cmjGuiLibGrid2018Oct1->cmjGuiLibGrid2019Jan30
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
#rom scrollList import *  ## temp... import scroll list... afterwards include in cmjGuiLibGrid....
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import time
##
##
ProgramName = "ListModulesIds"
Version = "version2023.06.12"  ## 2020Jul09


##############################################################################################
##############################################################################################
###  Class to list Module Id's
class listModules(object):
  def __init__(self):
    print('inside class listModules, init \n')
    self.__cmjDebug = 0        ## no debug statements
    self.__maxColumns = 7      ## maximum columns in the spread sheet
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
    ##self.sendToDevelopmentDatabase()  ## choose send to development database as default for now
    return
## -----------------------------------------------------------------
  def turnOnDebug(self,tempDebugLevel):
    self.__cmjDebug = tempDebugLevel  # turn on debug
    print(("__listModules__turnOnDebug... turn on debug: level = %s \n") % (self.__cmjDebug))
    return
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn on debug
    print("__listModules__turnOffDebug... turn off debug \n")
    return
## -----------------------------------------------------------------
  def setDebugLevel(self,tempValue):
    self.__cmjDebug = int(tempValue)  # turn on debug
    print(("__listModules__setDebugLevel... set debug level = %d\n") % self.__cmjDebug)
    return
## -----------------------------------------------------------------
##
##      Make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "di_counters Tables"
    self.__whichDatabase = 'development'
    print("__listModules__::getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
    #print("__listModules__::setupDevelopmentDatabase... self.__url =  %s") % self.__queryUrl
    return
##
## -------------------------------------------------------------------
##      Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__whichDatabase = 'production'
    print("__listModules__::setupProductionDatabase... get from production database \n")
    self.__queryUrl = self.__database_config.getProductionQueryUrl()
    #print("....__listModules__::setupProductionDatabase... self.__url =  %s") % self.__queryUrl
    return
## ---------------------------------------------------------------------------
##
##  Find the number of Module Id Entries
  def countTheModules(self):
    self.__getDatabaseValue = DataQuery(self.__queryUrl)
    self.__tables = "mu2e_table_cnts"   ## cmj 2022Jan28
    self.__rows = self.__getDatabaseValue.query(self.__database,self.__tables,"modules_cnt") ## cmj 2022Jan28
    print("\nQuery Results:")
    for self.__row in self.__rows:
      print((self.__row))
    print(("__listModules__:countTheModules:: number of rows = %s ") % self.__rows[0])
    return
## ---------------------------------------------------------------------------
##
##  List the module id's entered into the database.
  def listTheModules(self):
    self.__getDatabaseModuleid = DataQuery(self.__queryUrl)
    self.__tables = "modules"   ## cmj 2022Jan28
    self.__fetchThese = "module_id"
    self.__fetchCondition = 'create_time:gt:2015-08-15'
    self.__returnModuleIds_list = []
    self.__returnModuleIds_list = self.__getDatabaseModuleid.query(self.__database,self.__tables,self.__fetchThese,self.__fetchCondition) ## cmj 2022Jan28
    print("\nQuery Results:")
    print(("__listModules__:listTheModules:: number of modules in database = %d \n") % (len(self.__returnModuleIds_list)))
    for module in self.__returnModuleIds_list:
      print(("__listModules__:listTheModules:: module_id = %s ") % (module))
    return


##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
#      Build general help string....
  modeString = []
  modeString.append("This script is run in one mode:")
  modeString.append("> python ListModulesIds.py --database ''production''")
  modeString.append("The user may use a relative or absolute path to the spreadsheet")
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  options, args = parser.parse_args()
##
  myModules = listModules()
  print(("\nRunning %s \n") % (ProgramName))
  print(("%s \n") % (Version))
  if(options.database == 'development'):
      myModules.setupDevelopmentDatabase()  ## turns on send to development database
  elif(options.database == 'production'):
      myModules.setupProductionDatabase()  ## turns on send to production database
  myModules.countTheModules()
  myModules.listTheModules()
#
  print(("Finished running %s \n") % (ProgramName))
