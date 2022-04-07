# -*- coding: utf-8 -*-
##
##  File = "Extrusions.py"
##  Derived from File = "Extrusions_2017Feb2.py"
##  Derived from File = "Extrusions_2016Jun24.py"
##  Derived from File = "Extrusions_2016May24.py"
##  Derived from File = "Extrusions_2016May24.py"
##  Derived from File = "Extrusions_2016May22.py"
##  Derived from File = "Extrusions_2016May17.py"
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
##	python Extrusion_2016Jan27.py -i 'LY_Mu2e-5x2-060414-rev-CmjAmended_2016Jan7.csv'
##
##  Modified by cmj 2016Jan7... Add the databaseConfig class to get the URL for 
##		the various databases... change the URL in this class to change for all scripts.
##  Modified by cmj 2016Jan14 to use different directories for support modules...
##		These are located in zip files in the various subdirectories....
##  Modified by cmj2016Jan26.... change the maximum number of columns decoded to use variable.
##				change code to accomodate two hole positions
##  Modifed by cmj2016May22.... Add the counter type which contains one of the values: "test", "prototype" 
##										"pre_production" or "production"
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2017Feb2... Add instructions for use in the call of the script.
##  Modified by cmj2017Feb2... Add test mode option; option to turn off send to database.
##  Modified by cmj2017Jul31... Allow the script to run even if there is an error writing an extrusion to the database
##  Modified by cmj2018Mar01... Choose hdbClient_v1_3 dataloader
##  Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Jun6.... Make default database PRODUCTION
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2020Jul09.... Changed crvUtilities2018->crvUtilities;
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid (not used)
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##
##
sendDataBase = 0  ## zero... don't send to database
#
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
ProgramName="Extrusions"
Version = "version2020.12.16"

##############################################################################################
##############################################################################################
##  Class to read in an extrusion cvs file.
class readExtrusionCvsFile(object):
  def __init__(self):
    print 'inside __init__ \n'
    self.__cmjDebug = 1
  def openFile(self,tempFileName):
    self.__inFileName = tempFileName
    self.__inFile=open(self.__inFileName,'r')   ## read only file
  def readFile(self):
    self.__banner = []
    self.__inLine = []
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()
    for self.__newLine in self.__fileLine:
      print('%s') % self.__newLine   
    print 'end of readExtrusion' 
## -----------------------------------------------------------------
  def openFile(self,tempFileName):	## method to open the file
    self.__inFileName = tempFileName
    self.__inFile=open(self.__inFileName,'r')   ## read only file
##############################################################################################
##############################################################################################
###  Class to store extrusion elements
class extrusion(object):
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
## -----------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    print("...extrusion::turnOnSendToDataBase... send to database: self.__sendToDatabase = %s \n",self.__sendToDatabase)
## -----------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__sendToDatabase = 0      ## send to database
    print("...extrusion::turnOffSendToDatabase... do not send to database \n")
## -----------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    self.__whichDatabase = 'development'
    print("...extrusion::sendToDevelopmentDatabase... send to development database \n")
    self.__url = self.__database_config.getWriteUrl()
    self.__password = self.__database_config.getExtrusionKey()
## -----------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    self.__whichDatabase = 'production'
    print("...extrusion::sendToProductionDatabase... send to production database \n")
    self.__url = self.__database_config.getProductionWriteUrl()
    self.__password = self.__database_config.getExtrusionProductionKey()
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
  def readFile(self):		## method to read the file's contents
    self.__batch = 'none'
    self.__refCounterName = {}
    self.__refCounter = {}
    self.__refStats = {}  # Dictionary to store reference counters Stats
    self.__extStats = {}	# Dictionary to store extrusion Stats
    self.__extName = {}
    self.__extBase = {}
    self.__extHeight = {}
    self.__extLength = {}
    self.__extHole1Dia = {}
    self.__extHole2Dia = {}
    self.__extCount = {}
    self.__extType = {}
    self.__extLocation = {}
    self.__extComment = {}
##
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
##	Sort, define and store information here...
    for self.__newLine in self.__fileLine:
      #print("XXX__extrusions__::readFile self_newLine = XXX%sXXX\n") % (self.__newLine)
      if (self.__newLine.find('Batch') != -1): self.storeBatch(self.__newLine)
      if (self.__newLine.find('K2K') != -1): self.storeReference(self.__newLine)
      if (self.__newLine.find('RefCounters') != -1): self.storeReferenceStats(self.__newLine)
      if (self.__newLine.find('Extrusions') != -1): self.storeExtrusionStats(self.__newLine)
      if (self.__newLine.find('mu2e_CRVscin-') != -1 and self.__newLine.find('QC') == -1): self.storeExtrusionCounts(self.__newLine)
      if (self.__newLine.find('QC_dimensions_mu2e_CRVscin-') != -1): self.storeExtrusionCrossSection(self.__newLine)
      if (self.__newLine.find('QC_diameter_mu2e_CRVscin-') != -1): self.storeExtrusionDiameter(self.__newLine)
      ## Use development prefix for extrusions:
      if (self.__newLine.find('RD') != -1 and self.__newLine.find('QC') == -1): self.storeExtrusionCounts(self.__newLine)
      if (self.__newLine.find('QC_dimensions_RD') != -1): self.storeExtrusionCrossSection(self.__newLine)
      if (self.__newLine.find('QC_diameter_RD') != -1): self.storeExtrusionDiameter(self.__newLine)
      ## cmj2018Mar26
      if (self.__newLine.find('Mu2e-CRV') != -1 and self.__newLine.find('QC') == -1): self.storeExtrusionCounts(self.__newLine)
      if (self.__newLine.find('QC_dimensions_Mu2e-CRV') != -1): self.storeExtrusionCrossSection(self.__newLine)
      if (self.__newLine.find('QC_diameter_Mu2e-CRV') != -1): self.storeExtrusionDiameter(self.__newLine)
    print 'end of extrusion::readFile'
##	Method to setup access to the database
## -----------------------------------------------------------------
#### Load statistics to table.... this must be done first
  def sendStatisticsToDatabase(self):
    if(self.__cmjDebug > 3):
      print "XXX__extrusions__::sendStatisticsToDatabase.... self.__url = %s " % self.__url
      print "XXX__extrusions__::sendStatisticsToDatabase.... self.__password = %s \n" % self.__password
    self.__group = "Extrusion Tables"
    self.__statTable = "extrusion_batches"
    ### Must load the batch table first!
    self.__extrusionBatchString = {}
    self.__extrusionsBatchString = self.buildRowString_for_ExtrusionsBatch_table()
    if(self.__cmjDebug != 0): self.dumpStatisticsString()
    if self.__sendToDatabase != 0:
      if(self.__cmjDebug > 2):
        print "send to extrusion statistics database!"
        print "self.__url = %s" % self.__url
        print "self.__password = %s " % self.__password
        print "self.__group = %s " % self.__group
        print "self.__statTable = %s " % self.__statTable
        print "self.__extrusionsBatchString = %s " % self.__extrusionsBatchString
      self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__statTable)
      self.__myDataLoader1.addRow(self.__extrusionsBatchString)
      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send(True)  ## send it to the data base!
      if(self.__cmjDebug > 1): print "self.__text = %s" % self.__text   
      if self.__retVal:				## sucess!  data sent to database
	print "XXXX __extrusion__::sendStatisticsToDatabase: Extrusion Batch Transmission Success!!!"
	print self.__text
	return 0		## comunicate sucess
      elif self.__password == '':
	print('XXXX __extrusion__::sendStatisticsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	return 0		## test mode... mimic success
      else:
	print "XXXX __extrusion__::sendStatisticsToDatabase:  Extrusion Batch Transmission: Failed!!!!!!!"
	print self.__code
	print self.__text 
	#return 1		## problem with transmission!   communicate failure
## -----------------------------------------------------------------
####  Next send the extrusion data to the database... one extrusion at a time!
####  This done after the statistics for a batch have been loaded....
  def sendExtrusionsToDatabase(self):
    if(self.__cmjDebug > 3):
      print "XXX__extrusions__::sendExtrusionsToDatabase.... self.__url = %s " % self.__url
      print "XXX__extrusions__::sendExtrusionsToDatabase.... self.__password = %s \n" % self.__password
    self.__group = "Extrusion Tables"
    self.__extTable = "extrusions"
    for self.__localExtrusion in sorted(self.__extName.keys()):
      self.buildRowString_for_Extrusions_table(self.__localExtrusion)
      if(self.__cmjDebug > 2): print ("XXXX __extrusion__::sendExtrusionsToDatabase: self.__localExtrusion = %s") % (self.__localExtrusion)
      if self.__cmjDebug != 0: self.dumpExtrusionString()
      ### Must load the batch table first!
      self.__extrusionsExtString = self.buildRowString_for_Extrusions_table(self.__localExtrusion)
      if self.__sendToDatabase != 0:
	print "send to extrusion database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__extTable)
	self.__myDataLoader1.addRow(self.__extrusionsExtString)
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(2)     ## sleep so we dont' send two records with the same timestamp....
	if self.__retVal:				## sucess!  data sent to database
	  print "XXXX __extrusion__::sendExtrusionsToDatabase: Extrusion Batch Transmission Success!!!"
	  print self.__text
	elif self.__password == '':
	  print('XXXX __extrusion__::sendExtrusionsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	else:
	  print "XXXX __extrusion__::sendExtrusionsToDatabase:  Extrusion Batch Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
	  #return 1		## problem with transmission!   communicate failure

## -----------------------------------------------------------------
####  Next send the reference counter data to the database... one counter at a time!
####  This done after the statistics for a batch have been loaded....
  def sendReferenceCounterToDatabase(self):
    if(self.__cmjDebug > 3):
      print "XXX__extrusions__::sendReferenceCounterToDatabase.... self.__url = %s " % self.__url
      print "XXX__extrusions__::sendReferenceCounterToDatabase.... self.__password = %s \n" % self.__password
    self.__group = "Extrusion Tables"
    self.__extTable = "extrusion_tests"
    for self.__localRefCounter in sorted(self.__refCounterName.keys()):
      self.buildRowString_for_RefCounter_table(self.__localRefCounter)
      if(self.__cmjDebug > 2): print ("XXXX __extrusion__::sendReferenceCounterToDatabase: self.__localTestExtrusion = %s") % (self.__localRefCounter)
      if self.__cmjDebug != 0: self.dumpRefCounterString()
      ### Must load the batch table first!
      self.__refCounterString = self.buildRowString_for_RefCounter_table(self.__localRefCounter)
      if self.__sendToDatabase != 0:
	print "send to reference counter database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__extTable)
	self.__myDataLoader1.addRow(self.__refCounterString)
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(2)     ## sleep so we dont' send two records with the same timestamp....
	if self.__retVal:				## sucess!  data sent to database
	  print "XXXX __extrusion__::sendReferenceCounterToDatabase: Extrusion Batch Transmission Success!!!"
	  print self.__text
	elif self.__password == '':
	  print('XXXX __extrusion__::sendReferenceCounterToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	else:
	  print "XXXX __extrusion__::sendReferenceCounterToDatabase:  Extrusion Batch Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
	  #return 1		## problem with transmission!   communicate failure

## -----------------------------------------------------------------
#### Build the string for the extrusion batch statistics
  def buildRowString_for_ExtrusionsBatch_table(self):  ## Build the string for the extrusion batch statistics
      self.__sendExtBatchRow = {}
      self.__sendExtBatchRow['batch_id']             = self.__batch
      self.__sendExtBatchRow['average_ref_counts']     = self.__refStats['AveRefCounters']
      self.__sendExtBatchRow['stdev_ref_counters']       = self.__refStats['StdRefCounters']
      self.__sendExtBatchRow['percent_ref_counters']     = self.__refStats['PercentRefCounters']
      self.__sendExtBatchRow['average_light_yield_cnt'] = self.__extStats['AveExtrusions']
      self.__sendExtBatchRow['stdev_light_yield_cnt']   = self.__extStats['StdExtrusions']
      self.__sendExtBatchRow['percent_light_yield_cnt'] = self.__extStats['PercentExtrusions']
      return self.__sendExtBatchRow
## -----------------------------------------------------------------
#### Build the string for an extrusion
  def buildRowString_for_Extrusions_table(self,tempKey):  
      self.__sendExtrusionRow ={}
      self.__sendExtrusionRow['extrusion_id'] 		= self.__extName[tempKey]
      self.__sendExtrusionRow['batch_id'] 		= self.__batch
      self.__sendExtrusionRow['base_mm'] 		= self.__extBase[tempKey]
      self.__sendExtrusionRow['height_mm'] 		= self.__extHeight[tempKey]
      self.__sendExtrusionRow['hole_diameter_1_mm'] 	= self.__extHole1Dia[tempKey]
      self.__sendExtrusionRow['hole_diameter_2_mm'] 	= self.__extHole2Dia[tempKey]
      self.__sendExtrusionRow['light_yield'] 		= self.__extCount[tempKey]
      self.__sendExtrusionRow['extrusion_type'] 	= self.__extType[tempKey]
      self.__sendExtrusionRow['comments'] 		= self.__extComment[tempKey]
      if(self.__extLength[tempKey] != ''):
	self.__sendExtrusionRow['length_mm'] 		= self.__extLength[tempKey]
      else:
	self.__sendExtrusionRow['length_mm'] = -9.99
      return self.__sendExtrusionRow

## -----------------------------------------------------------------
#### Build the string for a reference counter
  def buildRowString_for_RefCounter_table(self,tempKey):  
      self.__sendRefCounterRow ={}
      self.__sendRefCounterRow['test_ref_id'] 	= self.__refCounterName[tempKey]
      self.__sendRefCounterRow['batch_id'] 	= self.__batch
      self.__sendRefCounterRow['counts_ref'] 	= self.__refCounter[tempKey]
      return self.__sendRefCounterRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the extrusion batch table:
  def dumpStatisticsString(self):
      print "XXXX __extrusion__::dumpStatisticsString:  Diagnostic"
      print "XXXX __extrusion__::dumpStatisticsString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendExtBatchRow:
	print('self.__sendExtBatchRow[%s] = %s') % (self.__tempLocal,str(self.__sendExtBatchRow[self.__tempLocal]))
## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the extrusion batch table:
  def dumpExtrusionString(self):
      print "XXXX __extrusion__::dumpExtrusionString:  Diagnostic"
      print "XXXX __extrusion__::dumpExtrusionString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendExtrusionRow:
	print('self.__sendExtrusionRow[%s] = %s') % (self.__tempLocal,str(self.__sendExtrusionRow[self.__tempLocal]))

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the reference counter table:
  def dumpRefCounterString(self):
      print "XXXX __extrusion__::dumpRefCounterString:  Diagnostic"
      print "XXXX __extrusion__::dumpRefCounterString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendRefCounterRow:
	print('self.__sendExtrusionRow[%s] = %s') % (self.__tempLocal,str(self.__sendRefCounterRow[self.__tempLocal]))
##
##
## -----------------------------------------------------------------   
##	Accessor functions
### Store functions.... must be called within the class to store the information
  def storeBatch(self,tempBatch):
    if(self.__cmjDebug > 0): print "----> extrusion::storeBatch... tempBatch = %s " % tempBatch
    ## cmj2018Jul11 self.__item = tempBatch.rsplit(',',self.__maxColumns)
    self.__item = tempBatch.rsplit(',')
    self.__batch = self.__item[1].rstrip()
    self.__batch = self.__batch.replace('/','_',2)
    self.__batch = self.__batch.replace(':','_',1)
    self.__batch = 'batch_'+self.__batch
    if (self.__cmjDebug !=0) : print(" XXX extrusion::storeBatch... self.__batch = %s \n") % self.__batch
## -----------------------------------------------------------------
  def storeReference(self,tempRef):  ## save reference counter information in dictionary
    ## cmj2018Jul11 self.__item = tempRef.rsplit(',',self.__maxColumns)
    self.__item = tempRef.rsplit(',')
    #self.__refKey = self.__item[0]
    #self.__refVal = float(self.__item[1])
    if(self.__cmjDebug != 0): print(" XXX extrusion::storeReference... tempRef = %s \n") % (tempRef)
    self.__refCounterName[self.__item[0]] = self.__item[0]
    self.__refCounter[self.__item[0]] = float(self.__item[1])
    if (self.__cmjDebug !=0) : print(" XXX extrusion::storeReference... self.__refCounter[%s] = %e \n") % (self.__item[0],self.__refCounter[self.__item[0]])
## -----------------------------------------------------------------
  def storeReferenceStats(self,tempRefStat):
    ## cmj2018Jul11 self.__item = tempRefStat.rsplit(',',self.__maxColumns)
    self.__item = tempRefStat.rsplit(',')
    self.__refStats[self.__item[0]] = float(self.__item[1])
    if (self.__cmjDebug !=0) : print(" XXX extrusion::storeReferenceStats... self.__refStats[%s] = %e \n") % (self.__item[0],self.__refStats[self.__item[0]])
## -----------------------------------------------------------------
  def storeExtrusionStats(self,tempExtStat):
    ## cmj2018Jul11 self.__item = tempExtStat.rsplit(',',self.__maxColumns)
    self.__item = tempExtStat.rsplit(',')
    self.__extStats[self.__item[0]] = float(self.__item[1])
    if (self.__cmjDebug !=0) : print(" XXX extrusion::storeReferenceStats... self.__refStats[%s] = %s \n") % (self.__item[0],self.__extStats[self.__item[0]])
    if (self.__cmjDebug !=0) : print(" XXX extrusion::storeReferenceStats... self.__refStats[%s] = %e \n") % (self.__item[0],self.__extStats[self.__item[0]])
## -----------------------------------------------------------------
  def storeExtrusionCounts(self,tempExtrusion):
    ##self.__item = tempExtrusion.rsplit(',',self.__maxColumns)
    self.__item = tempExtrusion.rsplit(',')  ## cmj2018Jul10
    if(self.__cmjDebug > 1) : print("self.__item = %s") % (self.__item)
    self.__extName[self.__item[0]] = self.__item[0]
    if(self.__cmjDebug != 0) : print("**************storeExtrusionCounts self.__item[0] = %s self.__item[1] = %s self.__item[2] = %s") % (self.__item[0],self.__item[1], self.__item[2])
    self.__extCount[self.__item[0]] = int(self.__item[1])
    try:
      self.__extLength[self.__item[0]] = 10*float(self.__item[2])
    except:
      print("**************storeExtrusionCounts.. ERROR IN UNPACK! \n")
      print("**************storeExtrusionCounts.. tempExtrusion = %s \n") % (tempExtrusion)
      print("**************storeExtrusionCounts.. self.__item[0] = %s \n") % (self.__item[0])
      sys.exit()
    self.__extType[self.__item[0]] = self.__item[3]
    self.__extComment[self.__item[0]] = self.__item[4].rstrip()
    ##self.__extBase[self.__item[0]] = None       # initialize value... fill later if recorded
    ##self.__extHeight[self.__item[0]] = None     # initialize value... fill later if recorded
    ##self.__extHole1Dia[self.__item[0]] = None   # initialize value... fill later if recorded
    ##self.__extHole2Dia[self.__item[0]] = None   # initialize value... fill later if recorded
    self.__extBase[self.__item[0]] = -9.99       # initialize value... fill later if recorded
    self.__extHeight[self.__item[0]] = -9.99     # initialize value... fill later if recorded
    self.__extHole1Dia[self.__item[0]] = -9.99   # initialize value... fill later if recorded
    self.__extHole2Dia[self.__item[0]] = -9.99   # initialize value... fill later if recorded

## -----------------------------------------------------------------
  def storeExtrusionCrossSection(self,tempExtrusion):
    ##self.__item = tempExtrusion.rsplit(',',self.__maxColumns)
    self.__item = tempExtrusion.rsplit(',')  ## cmj2018Jul10
    self.__tempExtName = self.__item[0].replace('QC_dimensions_','',1)
    if(self.__extBase[self.__tempExtName] != ""): 
      if(self.__item[1] != ""):
	self.__extBase[self.__tempExtName] = float(self.__item[1])
      else:
	self.__extBase[self.__tempExtName] = -9.99
    else:
      self._extBase[self.__tempExtName] = -9.99
    if(self.__extHeight[self.__tempExtName] != ""):
      if(self.__item[2] != ""):
	self.__extHeight[self.__tempExtName] = float(self.__item[2])
      else:
	self.__extHeight[self.__tempExtName] = -9.99
    else:
      self.__extHeight[self.__tempExtName] = -9.99
    if(self.__cmjDebug > 2): print("XXXX __extrusion__storeExtrusionCrossSection:: self_tempExtName = %s") %  self.__tempExtName

## -----------------------------------------------------------------
  def storeExtrusionDiameter(self,tempExtrusion):
    ##self.__item = tempExtrusion.rsplit(',',self.__maxColumns)
    self.__item = tempExtrusion.rsplit(',')  ## cmj2018Jul10
    self.__tempExtName = self.__item[0].replace('QC_diameter_','',1)
    if(self.__extHole1Dia[self.__tempExtName] != ""): 
      if(self.__item[1] != ""):
	self.__extHole1Dia[self.__tempExtName] = float(self.__item[1])
      else:
	self.__extHole1Dia[self.__tempExtName] = -9.99
    else:
      self.__extHole1Dia[Self.__tempExtName] = -9.99
    if(self.__extHole2Dia[self.__tempExtName] != ""): 
      if(self.__item[2] != ""):
	self.__extHole2Dia[self.__tempExtName] = float(self.__item[2])
      else:
	self.__extHole2Dia[self.__tempExtName] = -9.99
    else:
      self.__extHole2Dia[self.__tempExtName] = -9.99
    if(self.__cmjDebug > 2): print("XXXX __extrusion__storeExtrusionDiameter:: self_tempExtName = %s") %  self.__tempExtName

## -----------------------------------------------------------------
##
####    "getter" functions... Allows the retrieval of information... even outside the class
  def getBatch(self):
    return self.__batch
  def getReference(self):  	## return the Reference Counter Dictionary
    return self.__refCounter
  def getRefStats(self):  	## return the Reference Counter Stastitics dictionary
    return self.__refStats
  def getextStats(self):	## returns the Extrusion Stats dictionary
    return self.__extStats
  def getExtName(self):		## returns the Extrusion Names dictionary
    return self.__extName
  def getExtBase(self):		## returns the Extrusion Base length dictionary
    return self.__extBase
  def getExtHeight(self):	## returns the Extrusion Base Height dictionary
    return self.__extHeight
  def getExtLength(self):	## returns the Extrusion Length dictionary
    return self.__extLength
  def getExtHoleX1(self):	## returns the Extrusion X location of the hole dictionary
    return self.__extHoleX1
  def getExtHoleY1(self):	## returns the Extrusion Y location of the hole dictionary
    return self.__extHoleY1
  def getExtHoleX2(self):	## returns the Extrusion X location of the hole dictionary
    return self.__extHoleX2
  def getExtHoleY2(self):	## returns the Extrusion Y location of the hole dictionary
    return self.__extHoleY2
  def getLocation(self):	## returns the a dictionary with the extrusion's location
    return self.__extLocation
  def getExtCount(self):	## returns the Extrusion counts dictionary for Light Yield
    return self.__extCount
  def getExtComment(self):	## returns the extrusion comment dictionary
    return self.__extComment
##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
#	Build general help string....
  modeString = []
  modeString.append("This script is run in one mode:")
  modeString.append("> python Extrusions.py -i ExtrusionSpreadsheet.cvs")
  modeString.append("The user may use a relative or absolute path to the spreadsheet")
  parser.add_option('-i',dest='inputCvsFile',type='string',default="",help=modeString[0]+'\t\t\t\t '+modeString[2]) 
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  options, args = parser.parse_args()
  inputExtrusionFile = options.inputCvsFile
  if(inputExtrusionFile == ''):
    print("Supply input spreadsheet comma-separated-file")
    for outString in modeString:
      print ("%s") %  outString
    exit()
  print ("\nRunning %s \n") % (ProgramName)
  print ("%s \n") % (Version)
  print "inputExtrusionFile = %s " % inputExtrusionFile
  myExtrusions = extrusion()
  if(options.debugMode == 0):
    myExtrusions.turnOffDebug()
  else:
    myExtrusions.setDebugLevel(4)
  if(options.testMode == 0):
    if(options.database == 'development'):
      myExtrusions.sendToDevelopmentDatabase()  ## turns on send to development database
    elif(options.database == 'production'):
      myExtrusions.sendToProductionDatabase()  ## turns on send to production database
  else:
    myExtrusions.turnOffSendToDatabase()    ## call this after sentToDevelopment or sendToProduction to turn off
  ## --------------------------------------------
  myExtrusions.openFile(inputExtrusionFile)
  myExtrusions.readFile()
  localExtName = myExtrusions.getExtName()
  myExtrusions.sendStatisticsToDatabase()
  myExtrusions.sendReferenceCounterToDatabase()
  myExtrusions.sendExtrusionsToDatabase()
#
  print("Finished running %s \n") % (ProgramName)
#

