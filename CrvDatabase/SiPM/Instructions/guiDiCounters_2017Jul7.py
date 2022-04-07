# -*- coding: utf-8 -*-
##
##  File = "guiDiCounters_2017July7.py"
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
##	1) Input the initial diCounter information... 
##	 python DiCounters_2016Dec27.p -i 'CounterSpreadSheets/Counter_2016May13.csv'
##	2) Input the image file for the cut
##	 python DiCounters_2016Dec27.py -i 'diCounterSpreadSheets/DiCounter_Tests_2016Dec20.csv' --mode 'image'
##	3) Input the test results
##	 python DiCounters_2016Dec27.py -i 'diCounterSpreadSheets/DiCounter_Tests_2016Dec20.csv' --mode 'measure'
##
##  Modified by cmj 2016Jan7... Add the databaseConfig class to get the URL for 
##		the various databases... change the URL in this class to change for all scripts.
##  Modified by cmj 2016Jan14 to use different directories for support modules...
##		These are located in zip files in the various subdirectories....
##  Modified by cmj2016Jan26.... change the maximum number of columns decoded to use variable.
##				change code to accomodate two hole positions										"pre_production" or "production"
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##  Modified by cmj2017Mar14... Add instructions for use in the call of the script.
##  Modified by cmj2017Mar14... Add test mode option; option to turn off send to database.
##  Modified by cmj2017May31... Add "di-" identifiery for di-counters.
##
##
##
sendDataBase = 0  ## zero... don't send to database
#
from Tkinter import *         # get widget class
import Tkinter as tk
import tkFileDialog
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from collections import defaultdict
from time import *

#import ssl		## new for new version of DataLoader
#import random		## new for new version of Dat##  File = "DiCounters_2017Mar13.py"aLoader
sys.path.append("../../Utilities/Dataloader.zip")
sys.path.append("../CrvUtilities/crvUtilities.zip")
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from generalUtilities import generalUtilities
from cmjGuiLibGrid2017Jun23 import *

ProgramName = "guiDiCounters_2017Jun7.py"
Version = "version2017.06.07"


##############################################################################################
##############################################################################################
###  Class to store diCounter elements
class diCounter(object):
  def __init__(self):
    self.__cmjDebug = 0        ## no debug statements
    self.__maxColumns1 = 18  ## maximum columns in the spread sheet for input option: initial
    self.__maxColumns2 = 5   ## maximum columns in the spread sheet for input option: image
    self.__maxColumns3 = 13   ## maximum columns in the spread sheet for input option: measure
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
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
    print("...diCounter::turnOnDebug... turn on debug \n")
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn on debug
    print("...diCounter::turnOffDebug... turn off debug \n")
## -----------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    print("...diCounter::turnOnSendToDataBase... send to database: self.__sendToDatabase = %s \n",self.__sendToDatabase)
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
###############################################1###############################################
##############################################################################################
##############################################################################################
###   This is a class to read in an Excel spreadsheet page saved as a comma separated file
###   for the Sipms... The results are written in the database
###   The user can choose between the development or production database....
###
### -----------------------------------------------------------------
  def openFile(self,tempFileName):	## method to open the file
    self.__inFileName = tempFileName
    self.__inFile=open(self.__inFileName,'r')   ## read only file
## -----------------------------------------------------------------
  def readFile(self,tempInputMode):		## method to read the file's contents
    self.__diCounterId = {}		# Dictionary to hold the dicounter (key for diCounters)
    self.__moduleId = {}		# Dictionary to hold the module this diCounter is in (key diCounterId)
    self.__moduleLayer = {}		# Dictionary to hold the module layer this dicounter ins in (key diCounterId)
    self.__layerPosition = {}		# Dictionary that holds the position of this diCouner in the layer
					#   the key diCounterId
    self.__scintillatorA = {}		# Dictionary to hold the extrusion id for scintillator 1
    self.__scintillatorB = {}		# Dictionary to hold the extrusion id for scintillator 2
    self.__moduleLength = {}		# Dictionary to hold the module length
    self.__fiberId = {}			# Dictionary to hold the fiberid
    self.__diCounterManufactorDate = {}	# Dictionary to hold the manufactoring date
    self.__diCounterManufactorLocation = {}	# Dictionary to hold the manufactoring location
    self.__diCounterModuleLocation = {}		# Dictionary to hold the location of the module
    self.__diCounterComments = {}		# Dictionary to hold the comments for each diCounter
    self.__diCounterFiberGuideBarMan = {}	#
    ## Di-Counters Image Information
    self.__diCounterImageDate = {}		## Dictionary to hold the date the image was captured (key is diCounterId)
    self.__diCounterPosition = {}		## Dictionary to hold position of the image on the di-counter(key is diCounterId)
    self.__diCounterImageFile = {}		## Dictionary to hold the image file name(key is diCounterId)
    self.__diCounterImageComment = {}		##  Dictionary to hold comments on the image file (key is diCounterId)
    ## Di-Counter Test information
##
##  This informationis stored such that we need nested dictionaries......
##
    self.__diCounterSipmLocation = {'A1':'A1','A2':'A2','A3':'A3','A4':'A4','B1':'B1','B2':'B2','B3':'B3','B4':'B4'}
    self.__diCounterSipms = ['A1','A2','A3','A4','B1','B2','B3','B4']
    self.__nestedDirectory = generalUtilities()
    self.__diCounterTestCurrent = self.__nestedDirectory.nestedDict()		## A nested dictionary to hold a dictionary that holds the
								## current measured for the Sipm at some location on the di-counter
								## the keys are [di-counter][[diCounterTestDate][diCounterSipmLocation]
    self.__diCounterTestDate = defaultdict(dict)		## Nested dictionary to hold the date of the tests (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestLightSource = defaultdict(dict)		## Nested dictionary to hold the test light result (keys: [diCounterId][diCounterTestDate])	
    self.__diCounterTestFlashRate = defaultdict(dict)		## Nested dictionary to hold the test light source flash rate (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestVoltage = defaultdict(dict)		## Nested dictionary to hold the voltage on the Sipm (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestTemperature = defaultdict(dict)		## Nested ictionary to hold the temperature the measurement is made (keys: [diCounterId][diCounterTestDate]))
    self.__diCounterTestLightSourceVector = defaultdict(dict)	## Nested dictionary to hold the side the measurement is made (keys: [diCounterId][diCounterTestDate]))
    self.__diCounterTestLightSourceDistance = defaultdict(dict)	## Nested dictionary to hold the distance from source measurement is made (keys: [diCounterId][diCounterTestDate]))
    self.__diCounterTestTransmissionDate = defaultdict(dict)	## Nested dictionary to hold the date the transmission measurement is made (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestTransmission = defaultdict(dict)	## Nested dictionary to hold the transmission of the counter (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestTransmissionDate = defaultdict(dict)	## Nested dictionary to hold the transmission test date of the counter (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestLightTight = defaultdict(dict)		## Nested dictionary to hold the light tight test restults (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestCutInspection = defaultdict(dict)	## Nested dictionary to hold the cut inspection comments (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestLightYieldDate = defaultdict(dict)	## Nested dictionary to hold the date of the light yield tests (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestLightYield = defaultdict(dict)		## Nested dictionary to hold the light yeild (keys: [diCounterId][diCounterTestDate])
    self.__diCounterTestComment = defaultdict(dict)		## Nested dictionary to hold the comments on the test (keys: [diCounterId][diCounterTestDate])

##
    print 'mode value %s \n' % tempInputMode
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
##	Sort, define and store information here...
    if(tempInputMode == 'initial'):
      for self.__newLine in self.__fileLine:
	if (self.__newLine.find('diCounter-') != -1): self.storeDiCounterInitial(self.__newLine)
	elif (self.__newLine.find('di-') != -1):  self.storeDiCounterInitial(self.__newLine)
      print 'Read in diCounter initial information'
    elif(tempInputMode == 'image'):
      for self.__newLine in self.__fileLine:
	if (self.__newLine.find('diCounter-') != -1): self.storeDiCounterImage(self.__newLine)
	elif (self.__newLine.find('di-') != -1):  self.storeDiCounterImage(self.__newLine)
      print 'Read in diCounter image file information'
    elif(tempInputMode == 'measure'):
      for self.__newLine in self.__fileLine:
	##print("diCounter inline: %s \n") % self.__newLine ###################################### remove ########
	if (self.__newLine.find('diCounter-') != -1): self.storeDiCounterMeasure(self.__newLine)
	elif (self.__newLine.find('di-') != -1):  self.storeDiCounterMeasure(self.__newLine)
      print 'Read in diCounter test results information'
    print 'end of diCounter::readFile'
##
##
## -----------------------------------------------------------------
##	Methods to open logfiles
##    def setLogFileName(self,tempFileName):
##	  self.__logFileName = 'logFiles/'+tempFileName+strftime('%Y_%m_%d_%H_%M')+'.txt'
## -----------------------------------------------------------------
  def openLogFile(self):
    self.__logFileName = 'logFiles/di-counter-logFile-'+strftime('%Y_%m_%d_%H_%M')+'.txt'
    self.__logFile = open(self.__logFileName,"w+")
    if(self.__cmjDebug == 2): print '----- saveResult::openFile: write to %s' % self.__logFileName
    self.__banner = []
    self.__banner.append("##")
    self.__banner.append("##  di-counter log file: "+self.__logFileName+"\n")
    self.__banner.append("##	This is a file that logs then di-counter entries into \n")
    self.__banner.append("##	the Mu2e CRV Quality Assurance/Quality Control Harware database \n")
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
##		Utility method to make large numbers of nested dictionaries
#  def nestedDict(self):
#    return defaultdict(self.nestedDict)
##
## -----------------------------------------------------------------
##
##
##	Method to setup access to the database
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##
##	This method allows three different types of entries:
##	1) (inital) Setup the initial dicounter dimensions and history
##      2) (image) Enter in the fiber image file name
##	3) (measure) Enter the test results... this may be done multiple times
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
      print ("XXXX __diCounter__::sendToDatabase: invalid choice inputMode = %s") % tempInputMode    
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
    if(self.__cmjDebug != 0):  print "XXXX __diCounter__::sendDiCounterToDatabase... self.__url = %s " % self.__url
    if(self.__cmjDebug == 10): print "XXXX __diCounter__::sendDiCounterToDatabase... self.__password = %s \n" % self.__password
    for self.__localDiCounterId in sorted(self.__diCounterId.keys()):
      ### Must load the diCounter table first!
      self.__diCounterString = self.buildRowString_for_DiCounter_table(self.__localDiCounterId)
      self.logDiCounterString()
      if self.__cmjDebug != 0: 
	print ("XXXX __diCounter__::sendDiCounterToDatabase: self.__localFiberId = %s") % (self.__localDiCounterId)
	self.dumpDiCounterString()  ## debug.... dump diCounter string...
      if self.__sendToDatabase != 0:
	print "send to diCounter database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__diCounterTable)
	self.__myDataLoader1.addRow(self.__diCounterString)
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	if self.__retVal:				## sucess!  data sent to database
	  print "XXXX __diCounter__::sendDiCounterToDatabase: Counter Transmission Success!!!"
	  print self.__text
	elif self.__password == '':
	  print('XXXX__diCounter__::sendDiCounterToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	else:
	  print "XXXX__diCounter__::sendDiCounterToDatabase:  Counter Transmission: Failed!!!"
	  if(self.__cmjDebug > 1): 
	    print("XXXX__diCounter__:sendCounterToDatabase... Counter Transmission Failed: \n")
	    print("XXXX__diCounter__:sendCounterToDatabase... String sent to dataLoader: \n")
	    print("XXXX__diCounter__:sendCounterToDatabase... self.__diCounterString \%s \n") % (self.__diCounterString)
	  print ("XXXX__diCounter__:sendCounterToDatabase... self.__code = %s \n") % (self.__code)
	  print ("XXXX__diCounter__:sendCounterToDatabase... self.__text = %s \n") % (self.__text) 
	  self.__logFile.write("XXXX__diCounter__::sendDiCounterToDatabase:  Counter Transmission: Failed!!!")
	  self.__logFile.write('XXXX__diCounter__:sendCounterToDatabase... self.__code = '+self.__code+'\n')
	  self.__logFile.write('XXXX__diCounter__:sendCounterToDatabase... self.__text = '+self.__text+'\n')
	  ## remove this for di-counters... send as many as possible!!! return 1		## problem with transmission!   communicate failure
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
      print "XXXX __diCounter__::dumpDiCounterString:  Diagnostic"
      print "XXXX __diCounter__::dumpDiCounterString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendDiCounterRow:
	print('    self.__sendDiCounterRow[%s] = %s') % (self.__tempLocal,str(self.__sendDiCounterRow[self.__tempLocal]))
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
    if(self.__cmjDebug != 0):  print "XXXX __diCounter__::sendDiCounterImageToDatabase... self.__url = %s " % self.__url
    if(self.__cmjDebug == 01): print "XXXX __diCounter__::sendDiCounterImageToDatabase... self.__password = %s \n" % self.__password
    for self.__localDiCounterImageId in sorted(self.__diCounterId.keys()):
      ### Must load the diCounter table first!
      self.__diCounterImageString = self.buildRowString_for_DiCounterImage_table(self.__localDiCounterImageId)
      if (self.__cmjDebug != 0): 
	print ("XXXX __diCounter__::sendDiCounterImageToDatabase: self.__localDiCounterImageId = <%s>") % (self.__localDiCounterImageId)
	self.dumpDiCounterImageString()  ## debug.... dump diCounter string...
      if self.__sendToDatabase != 0:
	print "send to diCounter database!"
	self.__logFile.write(self.__diCounterImageString)
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__diCounterImageTable)
	self.__myDataLoader1.addRow(self.__diCounterImageString)
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	if self.__retVal:				## sucess!  data sent to database
	  print "XXXX __diCounter__::sendDiCounterImageToDatabase: Counter Transmission Success!!!"
	  print self.__text
	elif self.__password == '':
	  print('XXXX __diCounter__::sendDiCounterImageToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	else:
	  print "XXXX __diCounter__::sendDiCounterImageToDatabase:  Counter Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
	  self.__logFile.write("XXXX __diCounter__::sendDiCounterImageToDatabase:  Counter Transmission: Failed!!!")
	  self.__logFile.write(self.__code)
	  self.__logFile.write(self.__code)
	  ## remove this for di-counters.... add as many as we can!  return 1		## problem with transmission!   communicate failure
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
      print "XXXX __diCounter__::dumpDiCounterImageString:  Diagnostic"
      print "XXXX __diCounter__::dumpDiCounterImageString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendDiCounterImageToRow:
	print('    self.__sendDiCounterImageRow[%s] = %s') % (self.__tempLocal,str(self.__sendDiCounterImageToRow[self.__tempLocal]))
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
    if(self.__cmjDebug != 0):  print "XXXX __diCounter__::sendDiCounterTestsToDatabase... self.__url = %s " % self.__url
    if(self.__cmjDebug == 10): print "XXXX __diCounter__::sendDiCounterTestsToRowoDatabase... self.__password = %s \n" % self.__password
    for self.__localDiCounterTestsId in sorted(self.__diCounterId.keys()):
      print ("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localDiCounterTestsId = <%s>") % (self.__localDiCounterTestsId)
      ### Must load the diCounter table first!
      for self.__localSipmTestDate in sorted(self.__diCounterTestDate[self.__localDiCounterTestsId].keys()):
	for self.__localSipmPosition in sorted(self.__diCounterSipms):
	  if(self.__cmjDebug > 2): print ("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localSipmPosition = <%s>") % ( self.__localSipmPosition)
	  self.__diCounterTestsString = self.buildRowString_for_DiCounterTests_table(self.__localDiCounterTestsId,self.__localSipmTestDate,self.__localSipmPosition)
	  if (self.__cmjDebug > 0): 
	    print ("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localDiCounterTestsId = <%s>") % (self.__localDiCounterTestsId)
	    print ("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__localSipmPosition = <%s>") % ( self.__localSipmPosition)
	    print ("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__diCounterTestsString = <%s>") % (self.__diCounterTestsString)
	    self.dumpDiCounterTestsString()  ## debug.... dump diCounter string...
	  if self.__sendToDatabase != 0:
	    print ("__diCounter__::sendDiCounterTestsToDatabase:... Send to diCounter %s database! \n") %(self.__localDiCounterTestsId)
	    self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__diCounterTestsTable)
	    self.__myDataLoader1.addRow(self.__diCounterTestsString)
	    (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	    print "self.__text = %s" % self.__text
	    time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	    if self.__retVal:				## sucess!  data sent to database
	      print "XXXX __diCounter__::sendDiCounterTestsToDatabase: Counter Transmission Success!!!"
	      print self.__text
	    elif self.__password == '':
	      print('XXXX __diCounter__::sendDiCounterTestsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	    else:
	      print "XXXX __diCounter__::sendDiCounterTestsToDatabase:  Counter Transmission: Failed!!!"
	      print self.__code
	      print self.__text 
	      return 1		## problem with transmission!   communicate failure
	else:
	  if(self.__cmjDebug < 0):
	    print("XXXX __diCounter__::sendDiCounterTestsToDatabase: self.__diCounterTestsString = <%s>") % (self.__diCounterTestsString) 
    return 0
## -----------------------------------------------------------------
## -----------------------------------------------------------------
#### Build the string for a diCounter image file record
  def buildRowString_for_DiCounterTests_table(self,tempKey,tempSecondKey,tempThirdKey): 
      if(self.__cmjDebug > 3):
	print("XXXX __diCounter__::buildRowString_for_DiCounterTests_table tempKey = %s | tempSecondKey = %s | tempThirdKey  = %s\n") % (tempKey,tempSecondKey,tempThirdKey)
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
      if(self.__diCounterTestTransmissionDate[tempKey] != None):
	self.__sendDiCounterTestsToRow['counter_transmission_date'] = self.__diCounterTestTransmissionDate[tempKey]
      if(self.__diCounterTestTransmission[tempKey] != None):
	self.__sendDiCounterTestsToRow['counter_transmission'] = self.__diCounterTestTransmission[tempKey]
      if(self.__diCounterTestLightTight[tempKey] != None):
	self.__sendDiCounterTestsToRow['counter_light_tight'] = self.__diCounterTestLightTight[tempKey]
      if(self.__diCounterTestCutInspection[tempKey] != None):
	self.__sendDiCounterTestsToRow['counter_cut_inspection'] = self.__diCounterTestCutInspection[tempKey]
      if(self.__diCounterTestLightYieldDate[tempKey] != None):
	self.__sendDiCounterTestsToRow['light_yield_date'] = self.__diCounterTestLightYieldDate[tempKey]
      if(self.__diCounterTestLightYield[tempKey] != None):
	self.__sendDiCounterTestsToRow['light_yield'] =      self.__diCounterTestLightYield[tempKey]
      if(self.__diCounterTestComment[tempKey] != None):
	self.__sendDiCounterTestsToRow['comments'] = self.__diCounterTestComment[tempKey]
      ##	Add these temporarily.... These are required columns, but Craig does not measure these....
      self.__sendDiCounterTestsToRow['counter_light_tight'] = 'not inspected!'
      self.__sendDiCounterTestsToRow['counter_cut_inspection'] = 'dummy inspection'
      self.__sendDiCounterTestsToRow['light_yield_date'] = self.__diCounterTestDate[tempKey][tempSecondKey]
      self.__sendDiCounterTestsToRow['light_yield'] = -9999
      self.__sendDiCounterTestsToRow['pedestal_amps'] = -999.99
      return self.__sendDiCounterTestsToRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpDiCounterTestsString(self):
      print "XXXX __diCounter__::dumpDiCounterTestsString:  Diagnostic"
      print "XXXX __diCounter__::dumpDiCounterTestsString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendDiCounterTestsToRow:
	print('    self.__sendDiCounterTestsToRow[%s] = %s') % (self.__tempLocal,str(self.__sendDiCounterTestsToRow[self.__tempLocal]))
##
##
## -----------------------------------------------------------------   
### Store functions.... must be called within the class to store the information
## -----------------------------------------------------------------
##
##	Read in diCounter initial information: option 1: "initial"
  def storeDiCounterInitial(self,tempCounter):
    self.__item = []
    self.__item = tempCounter.rsplit(',',self.__maxColumns1)
    self.__diCounterId[self.__item[0]] = self.__item[0]
    self.__moduleLength[self.__item[0]] = self.__item[1]
    self.__diCounterManufactorDate[self.__item[0]] = self.dateStamper(self.__item[2])
    self.__scintillatorA[self.__item[0]] = self.__item[3]
    self.__scintillatorB[self.__item[0]] = self.__item[4]
    self.__fiberId[self.__item[0]] = self.__item[6]
    self.__moduleId[self.__item[0]] = None	## The initial value for the module_id is null
						## Update this value when the module is built.
    self.__diCounterManufactorLocation[self.__item[0]] = self.__item[7]
    self.__diCounterFiberGuideBarMan[self.__item[0]] = self.__item[7]
    self.__moduleLayer[self.__item[0]] = None  ## The initial value for the module layer is null
						## Update this value when the module is built
    self.__layerPosition[self.__item[0]] = None	## The initial value for the module position is null
						## Update this value when the module is built.
    self.__diCounterModuleLocation[self.__item[0]] = self.__item[16]
    self.__diCounterComments[self.__item[0]] = self.__item[17]
## -----------------------------------------------------------------
##	Read in diCounter image file information: option 2: "image"
  def storeDiCounterImage(self,tempCounter):
    self.__item = []
    self.__item = tempCounter.rsplit(',',self.__maxColumns2)
    self.__diCounterId[self.__item[0]+'_'+self.__item[2]] = self.__item[0]
    self.__diCounterImageDate[self.__item[0]+'_'+self.__item[2]] = self.__item[1]
    self.__diCounterPosition[self.__item[0]+'_'+self.__item[2]] = self.__item[2]
    self.__diCounterImageFile[self.__item[0]+'_'+self.__item[2]] = self.__item[3]
    self.__diCounterImageComment[self.__item[0]+'_'+self.__item[2]] = self.__item[4]
## -----------------------------------------------------------------
##	Read in diCounter measured test results: option 3: "measure"
  def storeDiCounterMeasure(self,tempCounter):
    self.__item = []
    self.__item = tempCounter.rsplit(',',self.__maxColumns3)
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
    if(self.__item[5].strip() == 'Source'):
      self.__diCounterTestLightSource[self.__item[0]][self.__item[3]] = 'rad'
    else:
      self.__diCounterTestLightSource[self.__item[0]][self.__item[3]] = self.__item[5].lower()
    self.__diCounterTestFlashRate[self.__item[0]][self.__item[3]] = '0.3mCi'
    n = 6
    for self.__location in self.__diCounterSipms:
      self.__diCounterTestCurrent[self.__item[0]][self.__item[3]][self.__location] = self.__item[n].strip()
      if(self.__cmjDebug > 3):
	print("XXXX __storeDiCounterMeasure__ self.__diCounterTestCurrent =[%s][%s][%s] = %s \n") % \
	(self.__item[0],self.__item[3],self.__location,self.__diCounterTestCurrent[self.__item[0]][self.__item[3]][self.__location])
      n += 1
    self.__diCounterTestTransmissionDate[self.__item[0]] = None
    self.__diCounterTestTransmission[self.__item[0]] = None
    self.__diCounterTestLightTight[self.__item[0]] = None
    self.__diCounterTestCutInspection[self.__item[0]] = None
    self.__diCounterTestLightYieldDate[self.__item[0]] = None
    self.__diCounterTestLightYield[self.__item[0]] = None
    self.__diCounterTestComment[self.__item[0]] = None
##
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##	Utility methods...
##
##
## -----------------------------------------------------------------
##  This method translates the excel spreadiCounterd sheet date into the
##  format expected by the timestamp used in the database
##
  def dateStamper(self,tempInput):
    self.__tempDate = tempInput
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
      print("XXXX__diCounter__:dateStamper...... self.__tempDate      = <%s>") % (self.__tempDate)
      print("XXXX__diCounter__:dateStamper...... self.__tempMmDdYy    = <%s>") % (self.__tempMmDdYy)
      print("XXXX__diCounter__:dateStamper...... self.__tempMonth     = <%s>") % (self.__tempMonth)
      print("XXXX__diCounter__:dateStamper....diCounter.. self.__tempDay       = <%s>") % (self.__tempDay)
      print("XXXX__diCounter__:dateStamper...... self.__tempYear      = <%s>") % (self.__tempYear)
    if(self.__cmjDebug > 10):
      print("XXXX__diCounter__:dateStamper...... self.__tempDateStamp = <%s>") % (self.__tempDateStamp)
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
    self.__tempMmDdYy = {}
    self.__tempMmDdYy = self.__tempDate.rsplit('/',3)
    self.__tempMonth = self.__tempMmDdYy[0] 
    if (int(self.__tempMonth) < 10): self.__tempMonth = '0'+self.__tempMonth
    self.__tempDay = self.__tempMmDdYy[1]
    if (int(self.__tempDay) < 10) : self.__tempDay = '0'+self.__tempDay
    self.__tempCombined = {}
    self.__tempCombined = self.__tempMmDdYy[2]
    self.__tempYyHM = {}
    self.__tempYyHM = self.__tempCombined.rsplit(' ',2)
    self.__tempYear = self.__tempYyHM[0]
    self.__tempTime = {}
    self.__tempTime = self.__tempYyHM[1].rsplit(':',2)
    self.__tempHour = self.__tempTime[0]

    self.__tempMin  = self.__tempTime[1]
    if(int(self.__tempHour) < 10): self.__tempHour = '0'+ self.__tempHour
    #if(int(self.__tempMin) < 10): self.__tempMin = '0' + self.__tempMin
    self.__tempTimeStamp = self.__tempYear+'-'+self.__tempMonth+'-'+self.__tempDay+' '+self.__tempHour+':'+self.__tempMin
    if(self.__cmjDebug > 11):
      print("XXXX__diCounter__:timeStamper...... self.__tempDate     = <%s>") % (self.__tempDate)
      print("XXXX__diCounter__:timeStamper...... self.__tempMmDdYy   = <%s>") % (self.__tempMmDdYy)
      print("XXXX__diCounter__:timeStamper...... self.__tempMonth    = <%s>") % (self.__tempMonth)
      print("XXXX__diCounter__:timeStamper...... self.__tempDay      = <%s>") % (self.__tempDay)
      print("XXXX__diCounter__:timeStamper...... self.__tempCombined = <%s>") % (self.__tempCombined)
      print("XXXX__diCounter__:timeStamper...... self.__tempYear     = <%s>") % (self.__tempYear)
      print("XXXX__diCounter__:timeStamper...... self.__tempHour  = <%s>") % (self.__tempHour)
      print("XXXX__diCounter__:timeStamper...... self.__tempMin   = <%s>") % (self.__tempMin)
    if(self.__cmjDebug > 10):
      print("XXXX__diCounter__:timeStamper....... self.__tempTimeStamp   = <%s>") % (self.__tempTimeStamp)
    #  End excel/timestamp format translation.
    return self.__tempTimeStamp

## -----------------------------------------------------------------
##

##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
#if __name__ == '__main__':
#  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
#  modeString = []
#  modeString.append("To run in the default mode (enter the di-counter information) \t\t\t\t\t\t")
#  modeString.append(">python DiCounters.py -i 'DicounterSpreadsheet.cvs' \t\t\t\t\t")
#  modeString.append("To add the measurment data to the database \t\t\t\t")
#  modeString.append(">python DiCounters.py -i 'DicounterSpreadsheet.cvs' -mode 'measure'\t\t\t\t\t\t\t")
#  modeString.append("To add the image of the cut fiber to the database \t")
#  modeString.append(">python DiCounters.py -i 'DicounterSpreadsheet.cvs' -mode 'image'\t")
#  ##
#  parser.add_option('-i',dest='inputCvsFile',type='string',default="",help=modeString[0]+modeString[1]+modeString[2]+modeString[3]+modeString[4]+modeString[5])
#  modeString1 = []
#  modeString1.append("Input Mode: This script is run in several modes: \t\t")
#  modeString1.append("all: performs initial, measure and image mode in sequence")
#  modeString1.append("initial: The default mode enters the initial di-counter information. ")
#  modeString1.append("measure: This mode enters di-counter test results into the database... Multiple tests may be entered. ")
#  modeString1.append("image: Enters the image file name into the database.")
#
#  parser.add_option('--mode',dest='inputMode',type='string',default="initial",help=modeString1[0]+modeString[1]+modeString[2]+modeString[3])
#  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
#  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
#  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
#  options, args = parser.parse_args()
#  inputDiCounterFile = options.inputCvsFile
#  if(inputDiCounterFile == ''):
#    print("\n")
#    print(" ---------------------------")
#    print("Supply input spreadsheet comma-separated-format file")
#    for outString in modeString:
#      print("%s") % outString
#    print ("")
#    for outString in modeString1:
#      print("%s") % outString
#    exit()
#  print ("\nRunning %s \n") % (ProgramName)
#  print ("%s \n") % (Version)
#  print "inputDiCounterFile = %s " % inputDiCounterFile
#  myDiCounters = diCounter()
#  if(options.debugMode == 0):
#    myDiCounters.turnOffDebug()
#  else:
#    myDiCounters.turnOnDebug(options.debugMode)
#  if(options.testMode == 0):
#    if(options.database == 'development'):
#      myDiCounters.sendToDevelopmentDatabase()  ## turns on send to development database
#    elif(options.database == 'production'):
#      myDiCounters.sendToProductionDatabase()  ## turns on send to production database
#  else:
#    myDiCounters.turnOffSendToDatabase()
#  ## --------------------------------------------
#  inputModeValue = options.inputMode
#  print '__name__ inputModeValue = %s \n' % inputModeValue
#  myDiCounters.openFile(inputDiCounterFile)
#  myDiCounters.openLogFile()
#  myDiCounters.readFile(inputModeValue)
#  myDiCounters.sendToDatabase(inputModeValue) 
##
#  if (options.inputMode == "initial"): myDiCounters    self.__myDiCounters.readFile())		## store di-counters to database
#  elif (options.inputMode == "measure"): myDiCounters.sendDiCounterTestsToDatabase()	## store the di-counter measurments to database
#  elif (options.inputMode == "image"): myDiCounters.sendDiCounterImageToDatabase()	## store the di-counter image of the fiber to database
#  else:
#    print("invalid option... retry")
#    for outString in modeString1:
#      print("%s") % outString
#    exit()
#
#  print("FiguiDiCounters_2017Jul7.pynished running %s \n") % (ProgramName)
#
## -------------------------------------------------------------
## 	A class to set up the main window to drive the
##	python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__myDiCounters  = diCounter()
    #self.__myDiCounters.sendToDevelopmentDatabase()  ## set up communications with database
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
##	Arrays to plot...keep these in scope in the whole class
    self.__sipmId = {}
    self.__sipmNumber = {}
    self.__testType = {}
    self.__biasVoltage ={}
    self.__darkCurrent = {}
    self.__gain = {}
    self.__temperature = {}
    self.__sipmResults = []
    self.__plotSipmId = []
    self.__plotSipmNumber = []
    self.__plotTestType = []
    self.__plotBiasVoltage = []
    self.__plotDarkCurrent = []
    self.__plotGain = []
    self.__plotTemperature = []
##	Dictionary of arrays to hold the Sipm Batch information
    self.__sipmBatch={}
##	Define Output Log file... remove this later
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('sipmQuerries')
    self.__mySaveIt.openFile()
    self.__row = 0
    self.__col = 0
    self.__strName = []
    self.__sCount = 0
##Scatter Plots
##
##
##	First Column...
    self.__col = 0
    self.__firstRow = 0
##
##	Instruction Box...
    self.__myInstructions = myScrolledText(self)
    self.__myInstructions.setTextBoxWidth(50)
    self.__myInstructions.makeWidgets()
    self.__myInstructions.setText('','Instructions/InstructionsForGuiDiCounters2017Jul7.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__col = 0
    self.__secondRow = 1
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Get Input File',command=self.openFileDialog,width=self.__buttonWidth,bg='lightblue',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Send initial Sipm information: PO number, batches recieved and vendor measurements...
    self.__getValues = Button(self,text='Initial',command=self.startInitialEntries,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
    self.__getValues = Button(self,text='Measurements',command=self.sendMeasurements,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Setup Debug option
    self.__col = 1
    self.__secondRow = 2
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Test',command=self.__myDiCounters.turnOffSendToDatabase,width=self.__buttonWidth,bg='orange',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Setup Debug option
    self.__col = 1
    self.__secondRow = 3
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Debug',command=self.turnOnDebug,width=self.__buttonWidth,bg='orange',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Third Column...
    self.__row = 0
    self.__col = 2
    self.__logo = mu2eLogo(self,self.__row,self.__col)     # display Mu2e logo!
    self.__logo.grid(row=self.__row,column=self.__col,rowspan=2,sticky=NE)
##         Display the script's version number
    self.__version = myLabel(self,self.__row,self.__col)
    self.__version.setForgroundColor('blue')
    self.__version.setFontAll('Arial',10,'bold')
    self.__version.setWidth(20)
    self.__version.setText(Version)
    self.__version.makeLabel()
    self.__version.grid(row=self.__row,column=self.__col,stick=E)
    self.__row += 1
##         Display the date the script is being run
    self.__date = myDate(self,self.__row,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__row,column=self.__col,sticky=E)
    self.__col = 0
    self.__row += 1
    self.__buttonWidth = 10
##	Add Control Bar at the bottom...
    self.__col = 0
    self.__firstRow = 6
    self.__quitNow = Quitter(self,0,self.__col)
    self.__quitNow.grid(row=self.__firstRow,column=0,sticky=W)
##sendMeasurements
##
## --------------------------------------------------------------------
##
##	Open up file dialog....
  def openFileDialog(self):
    self.__filePath=tkFileDialog.askopenfilename()
    print("__multiWindow__::openDialogFile = %s \n") % (self.__filePath)
    self.__myDiCounters.turnOffDebug()
    self.__myDiCounters.openFile(self.__filePath)
    self.__myDiCounters.openLogFile()
    self.__myDiCounters.turnOnSendToDatabase()
    self.__myDiCounters.sendToDevelopmentDatabase()
##
## --------------------------------------------------------------------
##
  def startInitialEntries(self):
    self.__myDiCounters.readFile("initial")
    self.__myDiCounters.sendDiCounterToDatabase()
##
## --------------------------------------------------------------------
##
  def sendMeasurements(self):
    self.__myDiCounters.readFile("measure")
    self.__myDiCounters.sendDiCounterTestsToDatabase()
##
## --------------------------------------------------------------------
##
  def sendImages(self):
    self.__myDiCounters.readFile("image")
    self.__myDiCounters.sendDiCounterImageToDatabase()
##
  def turnOnDebug(self):
    self.__myDiCounters.turnOnDebug(1)
##
#  def sendInitialToDatabase(self):
#    self.__mySipm.sendPoNumberToDatabase()
#    self.__mySipm.sendReceivedPoToDatabase()
#    self.__mySipm.sendSipmIdsToDatabase()
#    self.__mySipm.sendSipmVendMeasToDatabase()
    
##
##
## --------------------------------------------------------------------
if __name__ == '__main__':
     root = Tk()              # or Toplevel()
     bannerText = 'Mu2e::'+ProgramName
     root.title(bannerText)  
     root.geometry("+100+500")  ## set offset of primary window....
     myMultiForm = multiWindow(root,0,0)
     myMultiForm.grid()
     root.mainloop()



