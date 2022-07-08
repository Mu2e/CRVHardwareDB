# -*- coding: utf-8 -*-
##
##  File = "DiCounters.py"
##  Derived from File = "DiCounters2017Jul12.py"
##  Derived from File = "DiCounters_2017July10.py"
##  Derived from File = "DiCounters_2017July7.py"
##  Derived from File = "DiCounters_2017July6.py"
##  Derived from File = "DiCounters_2017July5.py"
##  Derived from File = "DiCounters_2017Jun1.py"
##  Derived from File = "DiCounters_2017May30.py"
##  Derived from File = "DiCounters_2017Mar13.py"
##  Derived from File = "DiCounters_2017Jan12.py"
##  Derived from File = "DiCounters_2016Dec27.py"
##  Derived from File = "DiCounters_2016Dec20.py"
##  Derived from File = "DiCounters_2016Dec19.py"
##  Derived from File = "DiCounters_2016Jun14.py"
##  Derived from File = "DiCounters_2016May16.py"
##  Derived from File = "Counters_2016May13.py"
##  Derived from File = "Fibers_2016May12.py"
##  Derived from File = "Extrusions_2016Jan27.py"
##  Derived from File = "Extrusions_2016Jan26.py"
##  Derived File = "Extrusions_2016Jan21.py"
##  Derived from File = "Extrusions_2016Jan14.py"
##  Derived from File = "Extrusions_2016Jan7.py"
##  Derived from File = "Extrusions_2015Oct12.py"
##
##  Test program to read in the lines from a comma separated
##  file saved from a spread sheet.  Here the delimiter is 
##  a tab and text is enclosed in "
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2015Sep23
##
#!/bin/env python
##
##  To run this script:
##      1) Input the initial diCounter information... 
##       python DiCounters_2016Dec27.p -i 'CounterSpreadSheets/Counter_2016May13.csv'
##      2) Input the image file for the cut
##       python DiCounters_2016Dec27.py -i 'diCounterSpreadSheets/DiCounter_Tests_2016Dec20.csv' --mode 'image'
##      3) Input the test results
##       python DiCounters_2016Dec27.py -i 'diCounterSpreadSheets/DiCounter_Tests_2016Dec20.csv' --mode 'measure'
##
##  Modified by cmj 2016Jan7... Add the databaseConfig class to get the URL for 
##            the various databases... change the URL in this class to change for all scripts.
##  Modified by cmj 2016Jan14 to use different directories for support modules...
##            These are located in zip files in the various subdirectories....
##  Modified by cmj2016Jan26.... change the maximum number of columns decoded to use variable.
##                        change code to accomodate two hole positions                                                            "pre_production" or "production"
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##  Modified by cmj2017Mar14... Add instructions for use in the call of the script.
##  Modified by cmj2017Mar14... Add test mode option; option to turn off send to database.
##  Modified by cmj2017May31... Add "di-" identifiery for di-counters.
##  Modified by cmj2018Jun8.... Change to hdbClient_v2_0
##  Modified by cmj2018Jul25... Add update mode to data loader call
##  Modified by cmj2018Jul25... Remove the number of columns for the reads
##  Modified by cmj2018Jun8... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##                        yellow highlight to selected scrolled list items
##  Modified by cmj2018Oct11.... Change to hdbClient_v2_2
##  Modified by cmj2018Oct11.... strip trailing white-space characters for comments.
##  Modified by cmj2018Oct12...  limit comments to 126 characters.
##  Modified by cmj2019May23... Change "hdbClient_v2_0" to "hdbClient_v2_2"
##  Modified by cmj2019May23... Add a loop to give maxTries to send information to database.
##  Modified by cmj2019May23... Add a changeable value for the sleep interval as we have found it can be smaller.
##  Modified by cmj2020Jul09... Change crvUtilities2018 -> crvUtilities
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid (not used)
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##  Modified by cmj2022May10... fix diagnogstic print statements in "sendDiCounterTestsToDatabase", lines 297-338
##  Modified by cmj2022Jul08... fix diagnogstic pring string concatonation on line 340
##  Modified by cmj2022Jul08... fix diagnoistic print statements... removed () on lines 328, 409, 480
##
##
##
sendDataBase = 0  ## zero... don't send to database
#
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from collections import defaultdict
from time import *

#import ssl            ## new for new version of DataLoader
#import random            ## new for new version of Dat##  File = "DiCounters_2017Mar13.py"aLoader
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2018Oct2 add highlight to scrolled list
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from generalUtilities import generalUtilities

ProgramName = "DiCounters"
Version = "version2021.05.14"


##############################################################################################
##############################################################################################
###  Class to store diCounter elements
class diCounter(object):
  def __init__(self):
    self.__cmjDebug = 0        ## no debug statements
    self.__maxColumns1 = 18  ## maximum columns in the spread sheet for input option: initial
    self.__maxColumns2 = 5   ## maximum columns in the spread sheet for input option: image
    self.__maxColumns3 = 14   ## maximum columns in the spread sheet for input option: measure
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
    self.__update = 0
    self.__maxTries = 3            ## set up maximum number of tries to send information to the database.
    self.__sleepTime = 0.5      ## sleep time between data transmission.
    ## Di-Counters Initial information
    self.__startTime = strftime('%Y_%m_%d_%H_%M')
## -----------------------------------------------------------------
  def __del__(self):
    self.__stopTime = strftime('%Y_%m_%d_%H_%M')
    self.__endBanner= []
    self.__endBanner.append("## ----------------------------------------- \n")
    self.__endBanner.append("## Program "+ProgramName+" Terminating at time "+self.__stopTime+" \n")
    for self.__endBannerLine in self.__endBanner:
      self.__logFile.write(self.__endBannerLine)
## -----------------------------------------------------------------
  def turnOnDebug(self,tempMode):
    self.__cmjDebug = tempMode  # turn on debug
    print(("...diCounter::turnOnDebug... turn on debug... debug level = %s \n") %(tempMode))
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn on debug
    print("...diCounter::turnOffDebug... turn off debug \n")
## -----------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    print(("...diCounter::turnOnSendToDataBase... send to database: self.__sendToDatabase = %s \n",self.__sendToDatabase))
## -----------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__sendToDatabase = 0      ## send to database
    print("...diCounter::turnOffSendToDatabase... do not send to database \n")
## -----------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__sendToDatabase = 1      ## send to database

    self.__whichDatabase = 'development'
    print("...diCounter::sendToDevelopmentDatabase... send to development database \n")
    self.__url = self.__database_config.getWriteUrl()
    self.__password = self.__database_config.getCompositeKey()
## -----------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    self.__whichDatabase = 'production'
    print("...diCounter::sendToProductionDatabase... send to production database \n")
    self.__url = self.__database_config.getProductionWriteUrl()
    self.__password = self.__database_config.getCompositeProductionKey()
## ---------------------------------------------------------------
##  Change dataloader to update rather than insert.
  def updateMode(self):
    print("...diCouner::updateMode ==> change from insert to update mode")
    self.__update = 0
###############################################1###############################################
##############################################################################################
##############################################################################################
###   This is a class to read in an Excel spreadsheet page saved as a comma separated file
###   for the Sipms... The results are written in the database
###   The user can choose between the development or production database....
###
### -----------------------------------------------------------------
  def openFile(self,tempFileName):      ## method to open the file
    self.__inFileName = tempFileName
    self.__inFile=open(self.__inFileName,'r')   ## read only file
## -----------------------------------------------------------------
  def readFile(self,tempInputMode):            ## method to read the file's contents
    self.__diCounterId = {}            # Dictionary to hold the dicounter (key for diCounters)
    self.__moduleId = {}            # Dictionary to hold the module this diCounter is in (key diCounterId)
    self.__moduleLayer = {}            # Dictionary to hold the module layer this dicounter ins in (key diCounterId)
    self.__layerPosition = {}            # Dictionary that holds the position of this diCouner in the layer
                              #   the key diCounterId
    self.__scintillatorA = {}            # Dictionary to hold the extrusion id for scintillator 1
    self.__scintillatorB = {}            # Dictionary to hold the extrusion id for scintillator 2
    self.__moduleLength = {}            # Dictionary to hold the module length
    self.__fiberId = {}                  # Dictionary to hold the fiberid
    self.__diCounterManufactorDate = {}      # Dictionary to hold the manufactoring date
    self.__diCounterManufactorLocation = {}      # Dictionary to hold the manufactoring location
    self.__diCounterModuleLocation = {}            # Dictionary to hold the location of the module
    self.__diCounterComments = {}            # Dictionary to hold the comments for each diCounter
    self.__diCounterFiberGuideBarMan = {}      #
    ## Di-Counters Image Information
    self.__diCounterImageDate = {}            ## Dictionary to hold the date the image was captured (key is diCounterId)
    self.__diCounterPosition = {}            ## Dictionary to hold position of the image on the di-counter(key is diCounterId)
    self.__diCounterImageFile = {}            ## Dictionary to hold the image file name(key is diCounterId)
    self.__diCounterImageComment = {}            ##  Dictionary to hold comments on the image file (key is diCounterId)
    ## Di-Counter Test information
##
##  This information is stored such that we need nested dictionaries......
##
    self.__diCounterSipmLocation = {'A1':'A1','A2':'A2','A3':'A3','A4':'A4','B1':'B1','B2':'B2','B3':'B3','B4':'B4','S1':'S1','S2':'S2','S3':'S3','S4':'S4'}
    self.__diCounterSipms = ['A1','A2','A3','A4','B1','B2','B3','B4','S1','S2','S3','S4']
    self.__nestedDirectory = generalUtilities()
    self.__diCounterTestCurrent = self.__nestedDirectory.nestedDict()            ## A nested dictionary to hold a dictionary that holds the
                                                ## current measured for the Sipm at some location on the di-counter
                                                ## the keys are [di-counter][[diCounterTestDate][diCounterSipmLocation]
    self.__diCounterTestDate = defaultdict(dict)            ## Nested dictionary to hold the date of the tests (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestLightSource = defaultdict(dict)            ## Nested dictionary to hold the test light result (keys: [diCounterId][diCounterTestDate])      
    self.__diCounterTestFlashRate = defaultdict(dict)            ## Nested dictionary to hold the test light source flash rate (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestVoltage = defaultdict(dict)            ## Nested dictionary to hold the voltage on the Sipm (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestTemperature = defaultdict(dict)            ## Nested ictionary to hold the temperature the measurement is made (keys: [diCounterId][diCounterTestDate]))
    self.__diCounterTestLightSourceVector = defaultdict(dict)      ## Nested dictionary to hold the side the measurement is made (keys: [diCounterId][diCounterTestDate]))
    self.__diCounterTestLightSourceDistance = defaultdict(dict)      ## Nested dictionary to hold the distance from source measurement is made (keys: [diCounterId][diCounterTestDate]))
    self.__diCounterTestComment = defaultdict(dict)            ## Nested dictionary to hold the comments on the test (keys: [diCounterId][diCounterTestDate])

##
    print('__readFile___: mode value %s \n' % tempInputMode)
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
##      Sort, define and store information here...
    if(self.__cmjDebug > 5) : print(("__readFile___: self.__fileLine = %s ") % (self.__fileLine))
    if(tempInputMode == 'initial'):
      for self.__newLine in self.__fileLine:
        if (self.__newLine.find('diCounter-') != -1): self.storeDiCounterInitial(self.__newLine)
        elif (self.__newLine.find('di-') != -1):  self.storeDiCounterInitial(self.__newLine)
      print('__readFile___:Read in diCounter initial information')
    elif(tempInputMode == 'image'):
      for self.__newLine in self.__fileLine:
        if (self.__newLine.find('diCounter-') != -1): self.storeDiCounterImage(self.__newLine)
        elif (self.__newLine.find('di-') != -1):  self.storeDiCounterImage(self.__newLine)
      print('__readFile___:Read in diCounter image file information')
    elif(tempInputMode == 'measure'):
      for self.__newLine in self.__fileLine:
      ##print("diCounter inline: %s \n") % self.__newLine ###################################### remove ########
        if (self.__newLine.find('diCounter-') != -1): self.storeDiCounterMeasure(self.__newLine)
        elif (self.__newLine.find('di-') != -1):  self.storeDiCounterMeasure(self.__newLine)
      print('__readFile___:Read in diCounter test results information')
    print('__readFile___:end of diCounter::readFile')
##
##
## -----------------------------------------------------------------
##      Methods to open logfiles
##    def setLogFileName(self,tempFileName):
##        self.__logFileName = 'logFiles/'+tempFileName+strftime('%Y_%m_%d_%H_%M')+'.txt'
## -----------------------------------------------------------------
  def openLogFile(self):
    self.__logFileName = 'logFiles/di-counter-logFile-'+strftime('%Y_%m_%d_%H_%M')+'.txt'
    self.__logFile = open(self.__logFileName,"w+")
    if(self.__cmjDebug == 2): print('----- saveResult::openFile: write to %s' % self.__logFileName)
    self.__banner = []
    self.__banner.append("##")
    self.__banner.append("##  di-counter log file: "+self.__logFileName+"\n")
    self.__banner.append("##      This is a file that logs then di-counter entries into \n")
    self.__banner.append("##      the Mu2e CRV Quality Assurance/Quality Control Harware database \n")
    self.__banner.append("##  Program "+ProgramName+" Begining at time "+self.__startTime+" \n")
    self.__banner.append("##    Input Dicounter Serial Number File (.csv) = "+self.__inFileName+" \n")
    self.__banner.append("##    Start :"+self.__startTime+"\n")
    self.__banner.append("## \n")
    self.__banner.append("## ----------------------------------------- \n")
    self.__banner.append("## \n")
    for self.__beginBannerLine in self.__banner:
      self.__logFile.write(self.__beginBannerLine)
##
## ----------------------------------------------------------------
##            Utility method to make large numbers of nested dictionaries
#  def nestedDict(self):
#    return defaultdict(self.nestedDict)
##
## -----------------------------------------------------------------
##
##
##      Method to setup access to the database
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##
##      This method allows three different types of entries:
##      1) (inital) Setup the initial dicounter dimensions and history
##      2) (image) Enter in the fiber image file name
##      3) (measure) Enter the test results... this may be done multiple times
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##
  def sendToDatabase(self,tempInputMode):
    if(tempInputMode.strip() == 'initial'):
      self.sendDiCounterToDatabase()
    elif(tempInputMode.strip() == 'image'):
      self.sendDiCounterImageToDatabase()
    elif(tempInputMode.strip() == 'measure'):
      self.sendDiCounterTestsToDatabase()
    else:
      print(("XXXX __diCounter__::sendToDatabase: invalid choice inputMode = %s") % tempInputMode)    
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
####  The next three functions construct the output string sent to the
####    database, send the string to the database and dump the string if needed...
####  Option 1: "initial": Send diCounter initial information to the database
####  Next send the diCounter data to the database... one diCounter at a time!
####  This done after the statistics for a batch have been loaded....
  def sendDiCounterToDatabase(self):
    self.__group = "Composite Tables"
    self.__diCounterTable = "Di_Counters"
    if(self.__cmjDebug != 0):  print("XXXX __diCounter__::sendDiCounterToDatabase... self.__url = %s " % self.__url)
    if(self.__cmjDebug == 10): print("XXXX __diCounter__::sendDiCounterToDatabase... self.__password = %s \n" % self.__password)
    for self.__localDiCounterId in sorted(self.__diCounterId.keys()):
      ### Must load the diCounter table first!
      self.__diCounterString = self.buildRowString_for_DiCounter_table(self.__localDiCounterId)
      self.logDiCounterString()
      if self.__cmjDebug != 0: 
        print(("XXXX __diCounter__::sendDiCounterToDatabase: self.__localDiCounterId = %s") % (self.__localDiCounterId))  ## cmj2022May10
        self.dumpDiCounterString()  ## debug.... dump diCounter string...
      if self.__sendToDatabase != 0:
        print("send to diCounter database!")
        self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__diCounterTable)
        if(self.__update == 0):
          self.__myDataLoader1.addRow(self.__diCounterString)
        else:
          self.__myDataLoader1.addRow(self.__diCounterString,'update')
        for n in range(0,self.__maxTries):            ## cmj2019May23... try to send maxTries time to database
          (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
          print("self.__text = %s" % self.__text)
          time.sleep(self.__sleepTime)     ## sleep so we don't send two records with the same timestamp....
          if self.__retVal:                        ## sucess!  data sent to database
            print("XXXX __diCounter__::sendDiCounterToDatabase: di-Counter Transmission Success!!!")
            print(self.__text)
            self.__logFile.write('XXXX__diCounter__::sendDiCounterToDatabase: sent '+self.__localDiCounterId+' to database')
            break
          elif self.__password == '':
            print(('XXXX__diCounter__::sendDiCounterToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')) ## cmj2022Jul08
            break
          else:
            print("XXXX__diCounter__::sendDiCounterToDatabase:  di-Counter Transmission: Failed!!!")
            if(self.__cmjDebug > 1): 
              print("XXXX__diCounter__:sendDiCounterToDatabase... di-Counter Transmission Failed: \n")  ## cmj2022May10
              print("XXXX__diCounter__:sendDiCounterToDatabase... String sent to dataLoader: \n")  ## cmj2022May10
              print(("XXXX__diCounter__:sendDiCounterToDatabase... self.__diCounterString \%s \n") % (self.__diCounterString))  ## cmj2022May10
            print(("XXXX__diCounter__:sendDiCounterToDatabase... self.__code = %s \n") % (self.__code))   ## cmj2022May10
            print(("XXXX__diCounter__:sendDiCounterToDatabase... self.__text = %s \n") % (self.__text))   ## cmj2022May10
            self.__logFile.write("XXXX__diCounter__::sendDiCounterToDatabase:  di-Counter Transmission: Failed!!!")
            self.__logFile.write('XXXX__diCounter__:sendDiCounterToDatabase... self.__code = '+self.__code+'\n')   ## cmj2022May10
            self.__logFile.write('XXXX__diCounter__:sendDiCounterToDatabase... self.__text = '+str(self.__text)+'\n')   ## cmj2022May10 ## cmj2022Jul08
    return 0
## -----------------------------------------------------------------
## -----------------------------------------------------------------
#### Build the string for a diCounter
  def buildRowString_for_DiCounter_table(self,tempKey):  
      self.__sendDiCounterRow = {}
      self.__sendDiCounterRow['di_counter_id'] = self.__diCounterId[tempKey]
      self.__sendDiCounterRow['fiber_id'] = self.__fiberId[tempKey]
      self.__sendDiCounterRow['module_id'] = self.__moduleId[tempKey]
      self.__sendDiCounterRow['module_layer'] = self.__moduleLayer[tempKey]
      self.__sendDiCounterRow['layer_position'] = self.__layerPosition[tempKey]
      self.__sendDiCounterRow['length_m'] = self.__moduleLength[tempKey]
      self.__sendDiCounterRow['manf_date'] = self.__diCounterManufactorDate[tempKey]
      self.__sendDiCounterRow['manf_loc'] = self.__diCounterManufactorLocation[tempKey]
      self.__sendDiCounterRow['location'] = self.__diCounterModuleLocation[tempKey]
      self.__sendDiCounterRow['scint_1'] = self.__scintillatorA[tempKey]
      self.__sendDiCounterRow['scint_2'] = self.__scintillatorB[tempKey]
      self.__sendDiCounterRow['comments'] = self.__diCounterComments[tempKey]
      self.__sendDiCounterRow['fgb_man'] = self.__diCounterFiberGuideBarMan[tempKey]
      return self.__sendDiCounterRow
## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpDiCounterString(self):
      print("XXXX __diCounter__::dumpDiCounterString:  Diagnostic")
      print("XXXX __diCounter__::dumpDiCounterString:  Print dictionary sent to database")
      for self.__tempLocal in self.__sendDiCounterRow:
        print(('    self.__sendDiCounterRow[%s] = %s') % (self.__tempLocal,str(self.__sendDiCounterRow[self.__tempLocal])))
## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def logDiCounterString(self):
      for self.__tempLocal in self.__sendDiCounterRow:
        self.__logFile.write(' self.__sendDiCounterRow['+self.__tempLocal+'] = '+str(self.__sendDiCounterRow[self.__tempLocal])+'\n')
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
####  The next three functions construct the output string sent to the
####    database, send the string to the database and dump the string if needed...
####  Option 2: "image": Send diCounter image file information to the database
####  Next send the diCounter data to the database... one diCounter at a time!
####  This done after the statistics for a batch have been loaded....
  def sendDiCounterImageToDatabase(self):
    self.__group = "Composite Tables"
    self.__diCounterImageTable = "Di_Counter_Images"
    if(self.__cmjDebug != 0):  print("XXXX __diCounter__::sendDiCounterImageToDatabase... self.__url = %s " % self.__url)
    if(self.__cmjDebug == 0o1): print("XXXX __diCounter__::sendDiCounterImageToDatabase... self.__password = %s \n" % self.__password)
    for self.__localDiCounterImageId in sorted(self.__diCounterId.keys()):
      ### Must load the diCounter table first!
      self.__diCounterImageString = self.buildRowString_for_DiCounterImage_table(self.__localDiCounterImageId)
      if (self.__cmjDebug != 0): 
        print(("XXXX __diCounter__::sendDiCounterImageToDatabase: self.__localDiCounterImageId = <%s>") % (self.__localDiCounterImageId))
        self.dumpDiCounterImageString()  ## debug.... dump diCounter string...
      if self.__sendToDatabase != 0:
        print("send to diCounter database!")
        self.__logFile.write(self.__diCounterImageString)
        self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__diCounterImageTable)
        if(self.__update == 0):
          self.__myDataLoader1.addRow(self.__diCounterString)
        else:
          self.__myDataLoader1.addRow(self.__diCounterString,'update')
        for n in range(0,self.__maxTries):            ## cmj2019May23... try to send maxTries time to database
          (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
          print("self.__text = %s" % self.__text)
          time.sleep(self.__sleepTime)     ## sleep so we don't send two records with the same timestamp....
          if self.__retVal:                        ## sucess!  data sent to database
            print("XXXX __diCounter__::sendDiCounterImageToDatabase: di-Counter Image Transmission Success!!!")
            print(self.__text)
            break
          elif self.__password == '':
            print(('XXXX __diCounter__::sendDiCounterImageToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')) ## cmj2022Jul08
            break
          else:
            print("XXXX __diCounter__::sendDiCounterImageToDatabase:  di-Counter Image Transmission: Failed!!!")
            print(self.__code)
            print(self.__text) 
            self.__logFile.write("XXXX __diCounter__::sendDiCounterImageToDatabase:  di-Counter Image Transmission: Failed!!!")
            self.__logFile.write(self.__code)
            self.__logFile.write(self.__code)
        ## remove this for di-counters.... add as many as we can!  return 1            ## problem with transmission!   communicate failure
    return 0
## -----------------------------------------------------------------
## -----------------------------------------------------------------
#### Build the string for a diCounter image file record
  def buildRowString_for_DiCounterImage_table(self,tempKey):  
      self.__sendDiCounterImageToRow = {}
      self.__sendDiCounterImageToRow['di_counter_id'] = self.__diCounterId[tempKey]
#      self.__sendDiCounterImageToRow['create_time'] = self.__diCounterImageDate[tempKey]
      self.__sendDiCounterImageToRow['image_point'] = self.__diCounterPosition[tempKey]
      #self.__sendDiCounterImageToRow['image_file'] = open(self.__diCounterImageFile[tempKey],"rb")
      self.__sendDiCounterImageToRow['image_file'] = self.__diCounterImageFile[tempKey]
      self.__sendDiCounterImageToRow['comments'] = self.__diCounterImageComment[tempKey]
      return self.__sendDiCounterImageToRow
## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpDiCounterImageString(self):
      print("XXXX __diCounter__::dumpDiCounterImageString:  Diagnostic")
      print("XXXX __diCounter__::dumpDiCounterImageString:  Print dictionary sent to database")
      for self.__tempLocal in self.__sendDiCounterImageToRow:
        print(('    self.__sendDiCounterImageRow[%s] = %s') % (self.__tempLocal,str(self.__sendDiCounterImageToRow[self.__tempLocal])))
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
####  The next three functions construct the output string sent to the
####    database, send the string to the database and dump the string if needed...
####  Option 3: "measure": Send diCounter test results information to the database
####  Next send the diCounter data to the database... one diCounter at a time!
####  This done after the statistics for a batch have been loaded....
  def sendDiCounterTestsToDatabase(self):
    self.__group = "Composite Tables"
    self.__diCounterTestsTable = "Di_Counter_Tests"
    if(self.__cmjDebug != 0):  print("XXXX __diCounter__::sendDiCounterTestsToDatabase... self.__url = %s " % self.__url)
    if(self.__cmjDebug == 10): print("XXXX __diCounter__::sendDiCounterTestsToRowoDatabase... self.__password = %s \n" % self.__password)
    for self.__localDiCounterTestsId in sorted(self.__diCounterId.keys()):
      print(("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localDiCounterTestsId = <%s>") % (self.__localDiCounterTestsId))
      ### Must load the diCounter table first!
      for self.__localSipmTestDate in sorted(self.__diCounterTestDate[self.__localDiCounterTestsId].keys()):
        for self.__localSipmPosition in sorted(self.__diCounterSipms):
          if(self.__cmjDebug > 2): print(("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localSipmPosition = <%s>") % ( self.__localSipmPosition))
          self.__diCounterTestsString = self.buildRowString_for_DiCounterTests_table(self.__localDiCounterTestsId,self.__localSipmTestDate,self.__localSipmPosition)
          if (self.__cmjDebug > 0): 
            print(("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localDiCounterTestsId = <%s>") % (self.__localDiCounterTestsId))
            print(("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localSipmPosition = <%s>") % ( self.__localSipmPosition))
            print(("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__diCounterTestsString = <%s>") % (self.__diCounterTestsString))
            self.dumpDiCounterTestsString()  ## debug.... dump diCounter string...
          if self.__sendToDatabase != 0:
            print(("__diCounter__::sendDiCounterTestsToDatabase:... Send to diCounter %s database! \n") %(self.__localDiCounterTestsId))
            self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__diCounterTestsTable)
            if(self.__update == 0):
              self.__myDataLoader1.addRow(self.__diCounterTestsString)
            else:
              self.__myDataLoader1.addRow(self.__diCounterTestsString,'update')
            for n in range(0,self.__maxTries):            ## cmj2019May23... try to send maxTries time to database
              (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
              print("self.__text = %s" % self.__text)
              time.sleep(self.__sleepTime)     ## sleep so we don't send two records with the same timestamp....
              if self.__retVal:                        ## sucess!  data sent to database
                print("XXXX __diCounter__::sendDiCounterTestsToDatabase: di-Counter "+self.__localDiCounterTestsId+" test result Transmission Success!!!")
                print(self.__text)
                break
              elif self.__password == '':
                print(('XXXX __diCounter__::sendDiCounterTestsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')) ## cmj2022Jul08
                break
              else:
                print("XXXX __diCounter__::sendDiCounterTestsToDatabase:  di-Counter "+self.__localDiCounterTestsId+" test result Transmission: Failed!!!")
                print(self.__code)
                print(self.__text) 
        else:
          if(self.__cmjDebug < 0):
            print(("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__diCounterTestsString = <%s>") % (self.__diCounterTestsString)) 
    return 0
## -----------------------------------------------------------------
## -----------------------------------------------------------------
#### Build the string for a diCounter image file record
  def buildRowString_for_DiCounterTests_table(self,tempKey,tempSecondKey,tempThirdKey): 
      if(self.__cmjDebug > 3):
        print(("XXXX __diCounter__::buildRowString_for_DiCounterTests_table tempKey = %s | tempSecondKey = %s | tempThirdKey  = %s\n") % (tempKey,tempSecondKey,tempThirdKey))
      self.__sendDiCounterTestsToRow = {}
      self.__sendDiCounterTestsToRow['di_counter_id'] = self.__diCounterId[tempKey]
      self.__sendDiCounterTestsToRow['sipm_test_voltage'] = self.__diCounterTestVoltage[tempKey][tempSecondKey]
      self.__sendDiCounterTestsToRow['test_date'] = self.__diCounterTestDate[tempKey][tempSecondKey]
      self.__sendDiCounterTestsToRow['sipm_location'] = self.__diCounterSipmLocation[tempThirdKey].lower()
      self.__sendDiCounterTestsToRow['current_amps'] = self.__diCounterTestCurrent[tempKey][tempSecondKey][tempThirdKey]
      self.__sendDiCounterTestsToRow['current_amps_date'] = self.__diCounterTestDate[tempKey][tempSecondKey]
      if(self.__diCounterTestTemperature[tempKey] != None):
        self.__sendDiCounterTestsToRow['temperature'] = self.__diCounterTestTemperature[tempKey][tempSecondKey]
      self.__sendDiCounterTestsToRow['distance'] = self.__diCounterTestLightSourceDistance[tempKey][tempSecondKey]
      self.__sendDiCounterTestsToRow['distance_vector'] = self.__diCounterTestLightSourceVector[tempKey][tempSecondKey]
      self.__sendDiCounterTestsToRow['light_source'] = self.__diCounterTestLightSource[tempKey][tempSecondKey]
      self.__sendDiCounterTestsToRow['flash_rate_hz'] = self.__diCounterTestFlashRate[tempKey][tempSecondKey]
      if(self.__diCounterTestComment[tempKey] != None):
        self.__sendDiCounterTestsToRow['comments'] = self.__diCounterTestComment[tempKey]
      return self.__sendDiCounterTestsToRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpDiCounterTestsString(self):
      print("XXXX __diCounter__::dumpDiCounterTestsString:  Diagnostic")
      print("XXXX __diCounter__::dumpDiCounterTestsString:  Print dictionary sent to database")
      for self.__tempLocal in self.__sendDiCounterTestsToRow:
        print(('    self.__sendDiCounterTestsToRow[%s] = %s') % (self.__tempLocal,str(self.__sendDiCounterTestsToRow[self.__tempLocal])))
##
##
## -----------------------------------------------------------------   
### Store functions.... must be called within the class to store the information
## -----------------------------------------------------------------
##
##      Read in diCounter initial information: option 1: "initial"
  def storeDiCounterInitial(self,tempCounter):
    self.__item = []
    ## cmj2018Jul25 self.__item = tempCounter.rsplit(',',self.__maxColumns1)
    self.__item = tempCounter.rsplit(',')
    self.__diCounterId[self.__item[0]] = self.__item[0]
    self.__moduleLength[self.__item[0]] = self.__item[1]
    self.__diCounterManufactorDate[self.__item[0]] = self.dateStamper(self.__item[2])
    self.__scintillatorA[self.__item[0]] = self.__item[3]
    self.__scintillatorB[self.__item[0]] = self.__item[4]
    self.__fiberId[self.__item[0]] = self.__item[6]
    self.__moduleId[self.__item[0]] = None      ## The initial value for the module_id is null
                                    ## Update this value when the module is built.
    self.__diCounterManufactorLocation[self.__item[0]] = self.__item[7]
    self.__diCounterFiberGuideBarMan[self.__item[0]] = self.__item[7]
    self.__moduleLayer[self.__item[0]] = None  ## The initial value for the module layer is null
                                    ## Update this value when the module is built
    self.__layerPosition[self.__item[0]] = None      ## The initial value for the module position is null
                                    ## Update this value when the module is built.
    self.__diCounterModuleLocation[self.__item[0]] = self.__item[16]
    self.__diCounterComments[self.__item[0]] = self.__item[17].rstrip() ## cmj2018Oct11... remove trailing white characters
    if(len(self.__diCounterComments[self.__item[0]]) > 126) :           ## cmj2018Oct12
      self.__tempString = self.__diCounterComments[self.__item[0]]
      self.__diCounterComments[self.__item[0]] = ''
      self.__diCounterComments[self.__item[0]] = self.__tempString[0:126]  ## limit comment string to 127 characters
## -----------------------------------------------------------------
##      Read in diCounter image file information: option 2: "image"
  def storeDiCounterImage(self,tempCounter):
    self.__item = []
    self.__item = tempCounter.rsplit(',',self.__maxColumns2)
    self.__diCounterId[self.__item[0]+'_'+self.__item[2]] = self.__item[0]
    self.__diCounterImageDate[self.__item[0]+'_'+self.__item[2]] = self.__item[1]
    self.__diCounterPosition[self.__item[0]+'_'+self.__item[2]] = self.__item[2]
    self.__diCounterImageFile[self.__item[0]+'_'+self.__item[2]] = self.__item[3]
    self.__diCounterImageComment[self.__item[0]+'_'+self.__item[2]] = self.__item[4].rstrip() ## cmj2018Oct11... remove trailing white characters
    if(len(self.__diCounterImageComment[self.__item[0]+'_'+self.__item[2]]) > 126) :          ## cmj2018Oct12
      self.__tempString = self.__diCounterImageComment[self.__item[0]+'_'+self.__item[2]]
      self.__diCounterImageComment[self.__item[0]+'_'+self.__item[2]] = ''
      self.__diCounterImageComment[self.__item[0]+'_'+self.__item[2]] = self.__tempString[1:126]   ## limit comment string to 127 characters
## -----------------------------------------------------------------
##      Read in diCounter measured test results: option 3: "measure"
  def storeDiCounterMeasure(self,tempCounter):
    self.__item = []
    ##cmj2018Jul25 self.__item = tempCounter.rsplit(',',self.__maxColumns3)
    self.__item = tempCounter.rsplit(',')
    if(self.__cmjDebug > 4):
      print(("XXXX __storeDiCounterMeasure__ self.__item = %s \n") % (self.__item))
    self.__diCounterId[self.__item[0]] = self.__item[0]
    self.__diCounterTestVoltage[self.__item[0]][self.__item[3]] = self.__item[1]
    if(self.__item[2] != ''):
      self.__diCounterTestTemperature[self.__item[0]][self.__item[3]] = self.__item[2]
    else:
      self.__diCounterTestTemperature[self.__item[0]][self.__item[3]] = -999.99
    self.__diCounterTestDate[self.__item[0]][self.__item[3]] = self.timeStamper(self.__item[3])
    if(self.__item[4] != ''):
      self.__diCounterTestLightSourceDistance[self.__item[0]][self.__item[3]] = self.__item[4]
    else:
      self.__diCounterTestLightSourceDistance[self.__item[0]][self.__item[3]] = -999.99
    self.__diCounterTestLightSourceVector[self.__item[0]][self.__item[3]] = 'from side A'
    self.__diCounterTestLightSource[self.__item[0]][self.__item[3]] =self.__item[5].lower()
    if(self.__item[6] != "") : 
      self.__diCounterTestFlashRate[self.__item[0]][self.__item[3]] = self.__item[6]
    else:
      self.__diCounterTestFlashRate[self.__item[0]][self.__item[3]] = ''
    if(self.__cmjDebug > 4): 
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterId[%s] = %s \n") % (self.__item[0],self.__diCounterId[self.__item[0]]))
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestVoltage[%s][%s] = %s \n") % (self.__item[0],self.__item[3],self.__diCounterTestVoltage[self.__item[0]][self.__item[3]]))
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestTemperature[%s][%s] = %s \n") % (self.__item[0],self.__item[3],self.__diCounterTestTemperature[self.__item[0]][self.__item[3]]))
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestDate[%s][%s] = %s \n") % (self.__item[0],self.__item[3],self.__diCounterTestDate[self.__item[0]][self.__item[3]]))
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestLightSourceDistance[%s][%s] = %s \n") % (self.__item[0],self.__item[3],self.__diCounterTestLightSourceDistance[self.__item[0]][self.__item[3]]))
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestLightSourceVector[%s][%s] = %s \n") % (self.__item[0],self.__item[3],self.__diCounterTestLightSourceVector[self.__item[0]][self.__item[3]]))
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestSource[%s][%s] = %s \n") % (self.__item[0],self.__item[3],self.__diCounterTestLightSource[self.__item[0]][self.__item[3]]))
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestFlashRate[%s][%s] = %s \n") % (self.__item[0],self.__item[3],self.__diCounterTestFlashRate[self.__item[0]][self.__item[3]]))
    n = 7 ## begining column
    for self.__location in self.__diCounterSipms:
      self.__diCounterTestCurrent[self.__item[0]][self.__item[3]][self.__location] = self.__item[n].strip()
      if(self.__cmjDebug > 3):
        print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestCurrent =[%s][%s][%s] = %s \n") % \
        (self.__item[0],self.__item[3],self.__location,self.__diCounterTestCurrent[self.__item[0]][self.__item[3]][self.__location]))
      n += 1
    if (not self.__item[19]) :  ## empty string
      self.__diCounterTestComment[self.__item[0]] = None
    else: 
      self.__diCounterTestComment[self.__item[0]] = self.__item[19].rstrip()
      if(len(self.__diCounterTestComment[self.__item[0]]) > 126) :            ## limit comment string to 127 characters
        self.__tempString = self.__diCounterTestComment[self.__item[0]]            ## cmj2018Oct12
        self.__diCounterTestComment[self.__item[0]] = ''
        self.__diCounterTestComment[self.__item[0]] = self.__tempString[0:126]
    if(self.__cmjDebug > 4): 
      print(("XXXX __storeDiCounterMeasure__ self.__diCounterTestComment[%s] = %s \n") % (self.__item[0],self.__diCounterTestComment[self.__item[0]]))
##
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##      Utility methods...
##
##
## -----------------------------------------------------------------
##  This method translates the excel spreadiCounterd sheet date into the
##  format expected by the timestamp used in the database
##
  def dateStamper(self,tempInput):
    self.__tempDate = tempInput
    if(self.__cmjDebug > 11):
      print(("XXXX__diCounter__:dateStamper...... self.__tempDate = %s \n") % (self.__tempDate))
    self.__tempMmDdYy = {}
    self.__tempMmDdYy = self.__tempDate.rsplit('/',3)
    self.__tempMonth = self.__tempMmDdYy[0]
    if (int(self.__tempMonth) < 10): self.__tempMonth = '0'+self.__tempMonth 
    self.__tempDay   = self.__tempMmDdYy[1]
    if (int(self.__tempDay) < 10 ): self.__tempDay = '0'+self.__tempDay
    self.__tempYear  = self.__tempMmDdYy[2]
    if (int(self.__tempYear) < 2000 ): self.__tempYear = '20'+self.__tempYear
    self.__tempDateStamp = self.__tempMonth+'/'+self.__tempDay+'/'+self.__tempYear
    if(self.__cmjDebug > 11):
      print(("XXXX__diCounter__:dateStamper...... self.__tempDate      = <%s>") % (self.__tempDate))
      print(("XXXX__diCounter__:dateStamper...... self.__tempMmDdYy    = <%s>") % (self.__tempMmDdYy))
      print(("XXXX__diCounter__:dateStamper...... self.__tempMonth     = <%s>") % (self.__tempMonth))
      print(("XXXX__diCounter__:dateStamper....diCounter.. self.__tempDay       = <%s>") % (self.__tempDay))
      print(("XXXX__diCounter__:dateStamper...... self.__tempYear      = <%s>") % (self.__tempYear))
    if(self.__cmjDebug > 10):
      print(("XXXX__diCounter__:dateStamper...... self.__tempDateStamp = <%s>") % (self.__tempDateStamp))
    return self.__tempDateStamp


## -----------------------------------------------------------------
##  This method translates the excel spread sheet date and time into the
##  format expected by the timestamp used in the database
##
  def timeStamper(self,tempInput):
    #  The following code is to compensate between the different time formats between excel & database
    #  Begin excel/timestamp format translation.
    #  Allowable formats for production_date are  YYYY-MM-DD or MM/DD/YYYY with year in range 2000-2049
    self.__tempDate = tempInput
    if(self.__cmjDebug > 10):
      print(("XXXX__diCounter__:timeStamper...... self.__tempDate = %s \n") % (self.__tempDate))
    self.__tempMmDdYy = {}
    self.__tempMmDdYy = self.__tempDate.rsplit('/',3)
    self.__tempMonth = self.__tempMmDdYy[0] 
    if (int(self.__tempMonth) < 10 and self.__tempMonth[0] != '0'): 
      if(self.__cmjDebug > 10): print(("self.__tempMonth[0] = |||%s||| self.__tempMonth[1] = |||%s||| ") % (self.__tempMonth[0],self.__tempMonth[1]))
      self.__tempMonth = '0'+self.__tempMonth
    self.__tempDay = self.__tempMmDdYy[1]
    if (int(self.__tempDay) < 10 and self.__tempDay != '0') : 
      if(self.__cmjDebug > 10): print(("self.__tempDay[0] = |||%s||| self.__tempDay[1] = |||%s||| ") % (self.__tempDay[0],self.__tempDay[1]))
      self.__tempDay = '0'+self.__tempDay
    self.__tempCombined = {}
    self.__tempCombined = self.__tempMmDdYy[2]
    self.__tempYyHM = {}
    self.__tempYyHM = self.__tempCombined.rsplit(' ',2)
    self.__tempYear = self.__tempYyHM[0]
    self.__tempTime = {}
    self.__tempTime = self.__tempYyHM[1].rsplit(':',2)
    self.__tempHour = self.__tempTime[0]
    if(int(self.__tempHour) < 10 and self.__tempHour[0] != '0'): 
      self.__tempHour = '0'+ self.__tempHour  ## cmj2018Aug24
      if(self.__cmjDebug > 10): print(("self.__tempHour[0] = |||%s||| self.__tempHour[1] = |||%s||| ") % (self.__tempHour[0],self.__tempHour[1]))
    self.__tempMin  = self.__tempTime[1]
    ## cmj2018Aug24...
    try:
      self.__tempSec  = self.__tempTime[2]
      self.__tempTimeStamp = self.__tempYear+'-'+self.__tempMonth+'-'+self.__tempDay+' '+self.__tempHour+':'+self.__tempMin+':'+self.__tempSec
    except:
      self.__tempTimeStamp = self.__tempYear+'-'+self.__tempMonth+'-'+self.__tempDay+' '+self.__tempHour+':'+self.__tempMin
    #cmj2018Aug24if(int(self.__tempHour) < 10): self.__tempHour = '0'+ self.__tempHour
    #if(int(self.__tempMin) < 10): self.__tempMin = '0' + self.__tempMin
    if(self.__cmjDebug > 10):
      print(("XXXX__diCounter__:timeStamper...... self.__tempDate     = <%s>") % (self.__tempDate))
      print(("XXXX__diCounter__:timeStamper...... self.__tempMmDdYy   = <%s>") % (self.__tempMmDdYy))
      print(("XXXX__diCounter__:timeStamper...... self.__tempMonth    = <%s>") % (self.__tempMonth))
      print(("XXXX__diCounter__:timeStamper...... self.__tempDay      = <%s>") % (self.__tempDay))
      print(("XXXX__diCounter__:timeStamper...... self.__tempCombined = <%s>") % (self.__tempCombined))
      print(("XXXX__diCounter__:timeStamper...... self.__tempYear     = <%s>") % (self.__tempYear))
      print(("XXXX__diCounter__:timeStamper...... self.__tempHour  = <%s>") % (self.__tempHour))
      print(("XXXX__diCounter__:timeStamper...... self.__tempMin   = <%s>") % (self.__tempMin))
    if(self.__cmjDebug > 10):
      print(("XXXX__diCounter__:timeStamper....... self.__tempTimeStamp   = <%s>") % (self.__tempTimeStamp))
    #  End excel/timestamp format translation.
    return self.__tempTimeStamp

## -----------------------------------------------------------------
##

##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  modeString = []
  modeString.append("To run in the default mode (enter the di-counter information) \t\t\t\t\t\t")
  modeString.append(">python DiCounters.py -i 'DicounterSpreadsheet.cvs' \t\t\t\t\t")
  modeString.append("To add the measurment data to the database \t\t\t\t")
  modeString.append(">python DiCounters.py -i 'DicounterSpreadsheet.cvs' --mode 'measure'\t\t\t\t\t\t\t")
  modeString.append("To add the image of the cut fiber to the database \t")
  modeString.append(">python DiCounters.py -i 'DicounterSpreadsheet.cvs' --mode 'image'\t")
  ##
  parser.add_option('-i',dest='inputCvsFile',type='string',default="",help=modeString[0]+modeString[1]+modeString[2]+modeString[3]+modeString[4]+modeString[5])
  modeString1 = []
  modeString1.append("Input Mode: This script is run in several modes: \t\t")
  modeString1.append("all: performs initial, measure and image mode in sequence")
  modeString1.append("initial: The default mode enters the initial di-counter information. ")
  modeString1.append("measure: This mode enters di-counter test results into the database... Multiple tests may be entered. ")
  modeString1.append("image: Enters the image file name into the database.")

  parser.add_option('--mode',dest='inputMode',type='string',default="initial",help=modeString1[0]+modeString[1]+modeString[2]+modeString[3])
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='--database = ''production'' ')
  parser.add.option('--update',dest='update',type='int',default=0,help='--update 1 ... change from insert to update mode')
  options, args = parser.parse_args()
  inputDiCounterFile = options.inputCvsFile
  if(inputDiCounterFile == ''):
    print("\n")
    print(" ---------------------------")
    print("Supply input spreadsheet comma-separated-format file")
    for outString in modeString:
      print(("%s") % outString)
    print ("")
    for outString in modeString1:
      print(("%s") % outString)
    exit()
  print(("\nRunning %s \n") % (ProgramName))
  print(("%s \n") % (Version))
  print("inputDiCounterFile = %s " % inputDiCounterFile)
  myDiCounters = diCounter()
  if(options.debugMode == 0):
    myDiCounters.turnOffDebug()
  else:
    myDiCounters.turnOnDebug(options.debugMode)
  if(options.testMode == 0):
    if(options.database == 'development'):
      myDiCounters.sendToDevelopmentDatabase()  ## turns on send to development database
    elif(options.database == 'production'):
      myDiCounters.sendToProductionDatabase()  ## turns on send to production database
  else:
    myDiCounters.turnOffSendToDatabase()
  ## --------------------------------------------
  inputModeValue = options.inputMode
  print('__name__ inputModeValue = %s \n' % inputModeValue)
  myDiCounters.openFile(inputDiCounterFile)
  myDiCounters.openLogFile()
  myDiCounters.readFile(inputModeValue)
  myDiCounters.sendToDatabase(inputModeValue) 
##
#
  print(("Finished running %s \n") % (ProgramName))
#


