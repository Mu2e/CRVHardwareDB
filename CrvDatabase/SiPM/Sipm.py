# -*- coding: utf-8 -*-
##
##  File = "Sipm2019.py"
##  Derived from File = "Sipm2019May07.py"
##  Derived from File = "Sipm2019Jan30.py" and "Sipm2019May07-Depreciated.py"
##  Derived from File = "Sipm2019Jan23.py"
##  Derived from File = "Sipm.py"
##  Derived from File = "Sipm2017Nov10.py"
##  Derived from File = "Sipm2017Nov8.py"
##  Derived from File = "Sipm.py"
##  Derived from File = "Sipm2017Oct9.py"
##  Derived from File = "Sipm2017Jul10.py"
##  Derived from File = "Sipm_2017Feb2.py"
##  Derived from File = "readSipmSpreadSheet_2015Jun27.py"
##  Derived from File = "readSipmSpreadSheet_2015Jun24.py"
##  Derived from File = "readSipmSpreadSheet_2015Jan20.py"
##  Derived from File = "readSipmSpreadSheet_2015Jan14.py"
##
##  Program to read a comma-separated data file and enter SiPM values into
##  the QA database.  Here the delimeter is a comma.
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2015Sep23
##  Modified by cmj2016Jun24.Sipm.py.. Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##
#!/bin/env python
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2016Jun24... Read and include SiPM Type...
##  Modified by cmj2017Feb2... Add instructions for use in the call of the script.
##  Modified by cmj2017Feb2... Add test mode option; option to turn off send to database.
##  Modified by cmj2017Oct2.... Change the field names to conform with Steve's renaming...
##				Add changes (i.e. new quantities) requested by Vishnu on 2017Sep21
##  Modified by cmj2017Oct9... Read new spread sheet with extra locally measured information.
##  Modified by cmj2017Nov8... Read the iv files and write to the iv table....
##  Modified by cmj2018Mar28...Changed the directory structure and calls DataLoader versions so these could be accounted for.
##	This version uses the old hdbClient_v1_3
##  Modified by cmj2018May30... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2018Oct9.... Change to hdbClient_v2_2
##  Modified by cmj2019Jan23... Add changes to add I vs V information from a list of I vs V files!
##  Modified by cmj2019Jan25.... Add the GainVbf parameters 1 & 2, and the overall status (green, yellow, red)
##				to the local tests....
##  Modified by cmj2019Apr25... Add a null signoff value to the Sipm entry.
##  Modified by cmj2019May06... Remove obsolete class readWimpCVX File 
##  Modified by cmj2019May06...  Add start and stop time (add method __del__(self)....
##  Modified by cmj2019May06...  Give a maximum of 10 tries for to ask the database to update the SiPMid to 5
##  Modified by cmj2019May07... Add error checking for data transmission to database for "sendSipmLocalMeasToDatabase"
##  Modified by cmj2019May07... Add error checking for data transmission to database for "sendSipmVendorMeasToDatabase"
##  MOdified by cmj2019May09... Change "sendIvMeasurmentsTodatabase" to load for a single SiPM_id all 100 I vs V and 
##				send it to the database in one transaction (send).
##  Modified by cmj2019Man14 from Modified by cmj2019Jan23... Add changes to add I vs V information from a list of I vs V files!
##  Modified by cmj2019May14 from Modified by cmj2019Jan24... Add changes to add Sipm tests or information from regular SiPMs test files
##  Modified by cmj2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid (not used)
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##
##
##
##
##  To run this script (enter all SiPM data:
##	python Sipm.py -i "SiPMSpreadSheets/Sipms_151224_S13360-2050VE_data_2016Jun27TEST.csv" 
##  To enter the SiPM Purchase order information:
##	python Sipm.py -i "SiPMSpreadSheets/Sipms_151224_S13360-2050VE_data_2016Jun27TEST.csv" -m 1
##  To enter the SiPM Purchase order recieved informaion
##	python Sipm.py -i "SiPMSpreadSheets/Sipms_151224_S13360-2050VE_data_2016Jun27TEST.csv" -m 2
##  To enter the SiPM Id numbers into the data018Oct2 add highlight to scrolled listbase:
##	python Sipm.py -i "SiPMSpreadSheets/Sip##  File = "Sipm2017Oct9.py"ms_151224_S13360-2050VE_data_2016Jun27TEST.csv" -m 3
##  To enter the vendor measurement of the SiPMs into the database:
##	python Sipm.py -i "SiPMSpreadSheets/Sipms_151224_S13360-2050VE_data_2016Jun27TEST.csv" -m 4
##  To enter the locally measured quantities into the database:
##	python Sipm.py -i "SiPMSpreadSheets/Sipms_151224_S13360-2050VE_data_2016Jun27TEST.csv" -m 5
##
##
#
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import string
from collections import defaultdict
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul02 add highlight to scrolled list
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from generalUtilities import generalUtilities
ProgramName = "Sipm.py"
Version = "version2020.12.16"


##############################################################################################
##############################################################################################
##############################################################################################
###   This is a class to read in an Excel spreadsheet page saved as a comma separated file
###   for the Sipms... The results are written in the database
###   The user can choose between the development or production database....
###
class sipm(object):
  def __init__(self):
    self.__cmjDebug = 1
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
    self.__queryUrl = '' ## must get the PO number and batch number
    self.sendToDevelopmentDatabase()  ## choose send to development database as default for now
    self.__database = ''
    self.__update = 0
    self.__startTime = strftime('%Y_%m_%d_%H_%M')
    self.__sleepTime = 0.5 ## sleep time between data entries... so we don't send two records at the same time!
    self.__ivSleepTime = 0.5
##	Set maximum numbers of tries to ask the database... sometimes it does not answer
##	Currently for sendSipmIdsToDatabase, only
    self.__maxTries = 10
    self.__maxIVtries = 3
## -----------------------------------------------------------------
  def __del__(self):
    self.__stopTime = strftime('%Y_%m_%d_%H_%M')
    self.__endBanner= []
    self.__endBanner.append("## ----------------------------------------- \n")
    self.__endBanner.append("## Program "+ProgramName+" Starting at time "+self.__startTime+" \n")
    self.__endBanner.append("## Program "+ProgramName+" Terminating at time "+self.__stopTime+" \n")
    print("Program  %s Starting at time %s ") % (ProgramName,self.__startTime)
    print("Program  %s Starting at time %s ") % (ProgramName,self.__stopTime)
    for self.__endBannerLine in self.__endBanner:
      self.__logFile.write(self.__endBannerLine)
## -----------------------------------------------------------------
  def turnOnDebug(self):
    self.__cmjDebug = 5  # turn on debug
    print("...sipm::turnOnDebug... turn on debug \n")
## -----------------------------------------------------------------
  def setDebug(self, tempDebug):
    self.__cmjDebug = tempDebug  # turn on debug
    print("...sipm::turnOnDebug... turn on debug \n")
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn off debug
    print("...sipm::turnOffDebug... turn off debug \n")
## -----------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    print("...sipm::turnOnSendToDataBase... send to database: self.__sendToDatabase = %s \n",self.__sendToDatabase)
## -----------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__sendToDatabase = 0      ## send to database
    print("...sipm::turnOffSendToDatabase... do not send to database \n")
## -----------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__whichDatabase = 'development'
    print("...sipm::sendToDevelopmentDatabase... send to development database \n")
    self.__url = self.__database_config.getWriteUrl()
    self.__password = self.__database_config.getSipmKey()
    self.__queryUrl = self.__database_config.getQueryUrl()  ## also need to query the database for sipm status
    self.__database = 'mu2e_hardware_dev'
## -----------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__whichDatabase = 'production'
    print("...sipm::sendToProductionDatabase... send to production database \n")
    self.__url = self.__database_config.getProductionWriteUrl()
    self.__password = self.__database_config.getSipmProductionKey()
    self.__queryUrl = self.__database_config.getProductionQueryUrl() ## also need to query the database for sipm status
    self.__database = 'mu2e_hardware_prd'
## ---------------------------------------------------------------
##  Change dataloader to update rather than insert.
  def updateMode(self):
    print("...sipm::updateMode ==> change from insert to update mode")
    self.__update = 1
## -----------------------------------------------------------------
  def openFile(self,tempFileName):	## method to open the file
    self.__inFileName = tempFileName
    self.__inFile=open(self.__inFileName,'r')   ## read only file
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##  Methods to read spread sheet contents and decode the spreadsheet
##  These methods assume a comma separated file.
## 
##  Also included are methods to dump the spreadsheet contents....
##
## -----------------------------------------------------------------
##  Read in all files except I vs V data file...
##  This method has been modified so that it can be called multiple times
##  to read a single input file at each call....  2019Jan24... Re-added 2019May14
  def readFile(self,tempTestType,localFileName):		## method to read the file's contents
    print ("XXXX __sipm__::readFile: enter... tempTestType = %s \n") % (tempTestType)
    print("XXXX __sipm__::readFile: enter")
    print("XXXX __sipm__::readFile: read file = %s \n") % localFileName
    self.openFile(localFileName)  ## open the file and read in the contents... cmj2019May14
    self.__poNumber = 'none'
    self.__poNumberWorker = 'none'
    self.__poNumberInstitution = 'none'
    self.__poNumberQuantity = 0
    self.__poNumberDate = 'none'
    ##
    self.__totBatch = 0		# total number of batches
    self.__batchNumber = {}           # list of batch numbers
    self.__batchWorker = {}           # key is bath number
    self.__batchInstitution = {}   # key is batch number
    self.__batchQuantityReceived = {} # key is batch number
    self.__batchDateReceived = {}     # key is batch number
    self.__serialNumber = {}          # list of sipm serial numbers
    self.__batchserialNumber = {}     # key is sipm serial number, value is the batch
    self.__packNumber = {} ## 2018Oct1 ... add pack number
    ## 
    #self.__serialNumber = {} # key is the sipm serial number, value is the sipm serial number
    self.__sipmBatch = {}    # key is the sipm serial nund of sipmmber
    self.__sipm_type = {}     # key is sipm serial number
    self.__vend_worker = {}  # key is the sipm serial number
    self.__vend_workstation = {}  ## must add this to spread sheet
    self.__vend_institution = {}  # key is the sipm serial number
    self.__vend_workstation = {}  # key is the sipm serial number
    self.__vend_Vop = {}  # key is the sipm serial number 
    self.__vend_Gain = {} # key is the sipm serial number
    self.__vend_Id = {}   # key is the sipm serial number
    self.__vend_Temp = {} # key is the sipm serial number
##
    self.__local_worker = {} # key is the sipm serial number... add to spread sheet
    self.__local_institution = {} # key is the sipmp serial number
    self.__local_workstation = {} # key is the sipm serial number... add to spread sheet
    self.__local_testDate = {}
    self.__local_Vop = {}   # key is the sipm serial number 
    self.__local_Id = {}    # key is the sipm serial number
    self.__local_Gain = {}  # key is the sipm serial number
    self.__local_Temp ={}   # key is the sipm serial number
    self.__local_BreakDownVoltage ={}   # key is the sipm serial number
    self.__local_BreakDownVoltageGain ={}   # key is the sipm serial number
    self.__local_VoltageVsCurrentCond ={}   # key is the sipm serial number
    self.__local_DarkCountRate = {}
    self.__local_Xtalk ={}   # key is the sipm serial number
    self.__local_LedResponse ={}   # key is the sipm serial number
    self.__local_DataFilePath ={}   # key is the sipm serial number
    self.__local_DataFileName ={}   # key is the sipm serial number
    self.__local_PackNumber = {}
    self.__local_GainVbrPar1 = {}
    self.__local_GainVbrPar2 = {}
    self.__local_SipmStatus = {}
    self.__sipmLocalTestDate = ''
    self.__sipmLocalInstitution = ''
    self.__sipmLocalWorker = ''
    self.__sipmLocalWorkstation = ''
##
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
##	Sort, define and store information here...
    self.__maxColumns = 25  ## number of columns in spread sheet..2017oct9
    for self.__newLine in self.__fileLine:
      if (self.__cmjDebug > 1): 
	print("readFile::self.__newLine = %s  \n") % (self.__newLine)
	print("readFile::self.__newLine tempTestType = %s  ") % (tempTestType)
      if (tempTestType == 'initial'):
	if (self.__newLine.find('Po Number') != -1): self.storePoNumber(self.__newLine)
	if (self.__newLine.find('Po Worker') != -1): self.storePoWorker(self.__newLine)
	if (self.__newLine.find('Po Institution') != -1): self.storePoInstitution(self.__newLine)
	if (self.__newLine.find('Po Quantity Ordered') != -1): self.storePoQuantityOrdered(self.__newLine)
	if (self.__newLine.find('Po Order Date') != -1): self.storePoOrderDate(self.__newLine)
	##  Sipm Batch
	if (self.__newLine.find('Total Batches')!= -1): self.storeTotalBatch(self.__newLine)
	if (self.__newLine.find('Batch Number') != -1): self.storeBatchNumber(self.__newLine)  
	if (self.__newLine.find('Batch Worker') != -1): self.storeBatchWorker(self.__newLine)
	if (self.__newLine.find('Batch Institution') != -1): self.storeBatchInstitution(self.__newLine)
	if (self.__newLine.find('Batch Quantity Received') != -1): self.storeBatchQuantityReceived(self.__newLine)
	if (self.__newLine.find('Batch Receive Date') != -1): self.storeBatchReceiveDate(self.__newLine)
	if (self.__newLine.find('CrvSipm-') != -1) : self.storeSipmTableQuantities(self.__newLine)
      if(tempTestType == 'packnumber'):
	if (self.__newLine.find('CrvSipm-') != -1 and self.__newLine.find('(ES2)') ) : self.storeSipmTableQuantities(self.__newLine)  ## same spreadsheet as simp Batch
      ##  Sipm measurements
      if (tempTestType == 'vendor'):
	print("readFile::self.__newLine vendor selected ")
	if (self.__newLine.find('CrvSipm-') != -1): self.storeSipmVendorMeasurement(self.__newLine)
      elif(tempTestType == 'local'):
	if(self.__newLine.find('Test_Date') != -1): self.storeLocalTestDate(self.__newLine)
	#if(self.__newLine.find('Batch')): self.storeSipmBatch(self.__newLine)
	self.__sipmLocalBatch = 1
	if(self.__newLine.find('Institution') != -1): self.storeLocalInstitution(self.__newLine)
	if(self.__newLine.find('Worker') != -1): self.storeLocalWorker(self.__newLine)
	if(self.__newLine.find('WorkStation') != -1): self.storeLocalWorkstation(self.__newLine)
	if(self.__newLine.find('CrvSipm-') != -1): self.storeSipmLocalMeasurement(self.__newLine)
    #if(self.__cmjDebug > 1): 
    #  print 'XXXX __sipm__::readFile: exit'
    #  if(tempTestType == 'vendor'): self.dumpSpreadSheet()
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		I vs V... Begin
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
## -----------------------------------------------------------------
##	The following set of methods are for the IV plot storage
## -----------------------------------------------------------------
##  Allow for multiple I vs V files to be opened...
##  Open each one... one at a time... load the I vs V information
##  then close the file....
  def readIVfile(self,localFileName):
    print("XXXX __sipm__::readIVfile: enter")
    print("XXXX __sipm__::readIVfile: read file = %s \n") % localFileName
    self.openFile(localFileName)  ## open the file and read in the contents
    self.__ivSipmId = {}
    self.__ivTestDate = {}
    self.__ivPoint = {}
    self.__ivVoltage = {}
    self.__ivCurrent = {}
    self.__maxIvColumns = 2
    self.__pointCount = 0			## start a new set of points with each file open.
    self.__currentIvSipmId = ''
    self.__currentIvSipmTestDate = ''
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
    print("XXXX __sipm__::readIVfile: len(self.__fileLine) = %d \n") % (len(self.__fileLine))
    for self.__newLine in self.__fileLine:
      if(self.__cmjDebug > 2): 
	print("XXXX __sipm__::readIVfile::self.__newLine = %s  \n") % (self.__newLine)
	print("XXXX __sipm__::self.__newLine.find('# File') = %sxx") % (self.__newLine.find('# File'))
      if (self.__newLine.find('# File') == 0): 
	  self.__currentIvSipmId = self.getIvSipmId(self.__newLine)
      if (self.__newLine.find('#-- created_time') == 0): 
	  self.__currentIvSipmTestDate = self.getIvTestTime(self.__newLine)
      if (self.__newLine.find('#') != 0):  # skip if "#" is found as first character...
	if(self.__currentIvSipmId == ''):
	  print("XXXX __sipm__::readIVfile:: self.__currentIvSipmId is null... exit program \n")
	  break
	if(self.__currentIvSipmTestDate == ''):
	  print("XXXX __sipm__::readIVfile:: self.__currentIvSipmTestDate is null... exit program \n")
	  break
	self.getIV(self.__pointCount,self.__newLine)
	self.__pointCount += 1
    print("XXXX __sipm__::readIVfile: call self.sendIvMeasurmentsTodatabase()")
    self.sendIvMeasurmentsTodatabase()
    self.__inFile.close()  ## close the file
    print("XXXX __sipm__::readIVfile: close file %s \n") % localFileName
    print("XXXX __sipm__::readIVfile: exit")
## -----------------------------------------------------------------
##	Method to extract the SiPM ID from the Iv file
  def getIvSipmId(self,tempLine):
      if(self.__cmjDebug > 2): 
	print("XXXX __sipm__::getIvSipmId: enter")
	print("XXXX __sipm__::getIvSipmId:: before tempLine = %s \n") % (tempLine)
      self.__tempLine = tempLine
      self.__tempLine = self.__tempLine.replace('# File = "IV_','',1)
      self.__tempLine = self.__tempLine.replace('.cvs"','',1)
      self.__tempLine = self.__tempLine.rstrip()
      self.__tempLine = self.__tempLine[0:26]
      self.__ivSipmId[self.__tempLine] = self.__tempLine
      if(self.__cmjDebug > 2): 
	print("XXXX __sipm__::getIvSipmId:: self.__tempLine = xxx%sxxx \n") % (self.__tempLine)
	print("XXXX __sipm__::getIvSipmId:: self.__ivSimpId[%s] = xxx%sxxx \n") % (self.__tempLine,self.__ivSipmId[self.__tempLine])
	if(self.__cmjDebug > 2): print("XXXX __sipm__::getIvSipmId: exit\n")
      return self.__tempLine
##
## -----------------------------------------------------------------
##	Method to extract the SiPM test time from the IV file
  def getIvTestTime(self,tempLine):
      if(self.__cmjDebug > 2): print("XXXX __sipm__::getIvTestTime: enter \n")
      self.__tempLine = tempLine
      self.__tempLine = self.__tempLine.replace('#-- created_time ','',1)
      self.__tempLine = self.__tempLine.replace(' AM','',1)
      self.__tempLine = self.__tempLine.rstrip()
      self.__ivTestDate = self.__tempLine
      if(self.__cmjDebug > 2): 
	print("XXXX __sipm__::sgetIvTestTime::self__ivTestDate = xxx%sxxx \n") % (self.__ivTestDate)
	if(self.__cmjDebug > 2): print("XXXX __sipm__::getIvTestTime: exit\n")
      return self.__ivTestDate
## -----------------------------------------------------------------
##	Method to extract the IV values to be stored
  def getIV(self,tempPoint,tempLine):
      if(self.__cmjDebug > 2): print("xx enter sipm::getIV")
      self__ivPair = []
      self.__ivPair = tempLine.rsplit(',',self.__maxIvColumns)
      ## Store voltage and current in dictionary
      self.__ivPoint[tempPoint] = int(tempPoint)
      self.__ivVoltage[tempPoint] = float(self.__ivPair[0])
      self.__ivCurrent[tempPoint] = float(self.__ivPair[1])
      if(self.__cmjDebug > 3):
	#print("  sipm.getIV:: self.__ivVoltage[%s][%s][%s] = %s | self.__ivCurrent[%s][%s][%s] = %s \n") % (tempPoint,self.__currentIvSipmId,self.__currentIvSipmTestDate,self.__ivVoltage[tempPoint][self.__currentIvSipmId][self.__currentIvSipmTestDate],tempPoint,self.__currentIvSipmId,self.__currentIvSipmTestDate,self.__ivCurrent[tempPoint][self.__currentIvSipmId][self.__currentIvSipmTestDate])
	print("XXXX __sipm__::sipm.getIV:: self.__ivVolage[%s] = %s | self.__ivCurrent[%s] = %s ") % (tempPoint,self.__ivVoltage[tempPoint],tempPoint,self.__ivCurrent[tempPoint])
      if(self.__cmjDebug > 2): print("XXXX __sipm__::sipm.getIV: exit")
## -----------------------------------------------------------------
  def sendIvMeasurmentsTodatabase(self):
    print("XXXX __sipm__::sendIvMeasurmentsTodatabase: enter \n")
    self.__group = "SiPM Tables"
    self.__sipmTable = "sipm_current_vs_voltages"
    self.__firstCall = 0
    for self.__localSipmIv in sorted(self.__ivPoint.keys()):
      self.__sipmIvString = self.buildString_for_SiPM_IV_table(self.__localSipmIv)
      if(self.__cmjDebug >= 1): 
	  self.dumpString_for_SiPM_IV(self.__sipmIvString)
      if self.__sendToDatabase != 0:
	print "XXXX __sipm__::send Local Iv Measurements to database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTable)
	## Use Steve's suggestion and load multiple lines (100 in this case) to be sent in one transaction... below.
	if(self.__update == 0):
	  self.__myDataLoader1.addRow(self.__sipmIvString)  ## use this to insert new entry
	  ##cmj2019May09(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	else:
	  self.__myDataLoader1.addRow(self.__sipmIvString,'update')
	  ##cmj2019May09 (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	print "self.__sipmIvString = %s" % self.__sipmIvString
      ## cmj2019May09... Use Steve's suggestion to send all I vs V values for one SiPM (100 lines) in one transaction (send).
    for n in range(0,self.__maxIVtries):
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	time.sleep(self.__ivSleepTime) ## sleep so we don't send two records with the same timestamp!
	if self.__retVal:				## success!  data sent to database
	  if(self.__update == 0) :
	    print "XXXX __sipm__::sendIvMeasurmentsTodatabase: "+self.__currentIvSipmId+" bin "+str(self.__ivPoint[self.__localSipmIv])+" DatabaseTransmission Success!!!"+" url = "+self.__url
	  else:
	    print "XXXX __sipm__::sendIvMeasurmentsTodatabase: "+self.__currentIvSipmId+" bin "+str(self.__ivPoint[self.__localSipmIv])+" Update DatabaseTransmission Success!!!"+" url = "+self.__url
	  print self.__text
	  break
	elif self.__password == '':
	  print('XXXX __sipm__::sendIvMeasurmentsTodatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	else:
	  print "XXXX __sipm__::sendIvMeasurmentsTodatabase:  Database Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
    print("XXXX __sipm__::sendIvMeasurmentsTodatabase: exit \n")
    return 0 ## success
## -----------------------------------------------------------------
  def buildString_for_SiPM_IV_table(self,tempKey):
    if(self.__cmjDebug > 1 ) : print("XXXX __sipm__::buildString_for_SiPM_IV_table: enter")
    self.__sendIVrow = {}		## define empty dictionary
    self.__sendIVrow['sipm_id'] = self.__currentIvSipmId
    self.__sendIVrow['measure_test_date'] = self.__currentIvSipmTestDate
    self.__sendIVrow['point'] = int(self.__ivPoint[tempKey])
    self.__sendIVrow['voltage'] = float(self.__ivVoltage[tempKey])
    self.__sendIVrow['current'] = float(self.__ivCurrent[tempKey])
    #if(self.__cmjDebug > 2): print("XXXX __sipm__::buildString_for_SiPM_IV_table: %i %f %f") %(tempKey,self.__sendIVrow[tempKey],self.__sendIVrow[tempKey])
    if(self.__cmjDebug > 1) : print("XXXX __sipm__::buildString_for_SiPM_IV_table: exit")
    return(self.__sendIVrow)
##
  def dumpString_for_SiPM_IV(self,tempString):
     print("XXXX __sipm__::dumpString_for_SiPM_IV: %s \n") %(tempString)
## -----------------------------------------------------------------
##	End the set of methods are for the IV plot storage
## -----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		I vs V... End
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------   
##	Accessor functions for the spreadsheet read/decode
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Purchase Orders... Begin
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## Store functions.... must be called within the class to store the information
## The store functions store the information read from the spreadsheet in 
## dictionaries used to build the strings sent to the database.
##
## -----------------------------------------------------------------
  def storePoNumber(self,temp):
    self.__item = temp.rsplit(',')
    self.__poNumber = self.__item[1]
## -----------------------------------------------------------------
  def storePoWorker(self,temp):
    self.__item = temp.rsplit(',')
    self.__poNumberWorker = self.__item[1]
## -----------------------------------------------------------------
  def storePoInstitution(self,temp):
    self.__item = temp.rsplit(',')
    self.__poNumberInstitution = self.__item[1]
## -----------------------------------------------------------------
  def storePoQuantityOrdered(self,temp):
    self.__item = temp.rsplit(',')
    self.__poNumberQuantity = self.__item[1]			
## -----------------------------------------------------------------
  def storePoOrderDate(self,temp):
    self.__item = temp.rsplit(',')
    self.__poNumberDate = self.__item[1]
## -----------------------------------------------------------------
  def storeTotalBatch(self,temp):
    self.__item = temp.rsplit(',')
    self.__totBatch = self.__item[1]
## -----------------------------------------------------------------
  def storeBatchNumber(self,temp):
    self.__item = temp.rsplit(',')
    del self.__item[0]
    for m in self.__item:
      if (m != ''): self.__batchNumber[m] = m
    del self.__batchNumber['\r\n']
## -----------------------------------------------------------------
  def storeBatchWorker(self,tempInput):
    self.__item = tempInput.rsplit(',') 
    del self.__item[0]
    nn = 0
    for batch in self.__batchNumber:
      if(batch != ''): self.__batchWorker[batch] = self.__item[nn]
      nn += 1
## -----------------------------------------------------------------
  def storeBatchInstitution(self,tempInput):
    self.__item = tempInput.rsplit(',') 
    del self.__item[0]
    nn = 0
    for batch in self.__batchNumber:
      self.__batchInstitution[batch] = self.__item[nn]
      nn += 1
## -----------------------------------------------------------------
  def storeBatchQuantityReceived(self,tempInput):
    self.__item = tempInput.rsplit(',',self.__maxColumns) 
    del self.__item[0]
    nn = 0
    for batch in self.__batchNumber:
      self.__batchQuantityReceived[batch] = self.__item[nn]
      nn += 1
## -----------------------------------------------------------------
  def storeBatchReceiveDate(self,tempInput):
    self.__item = tempInput.rsplit(',',self.__maxColumns) 
    del self.__item[0]
    nn = 0
    for batch in self.__batchNumber:
      self.__batchDateReceived[batch] = self.__item[nn]
      nn += 1
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## ----------------------------------------------------------------
##	Methods to setup access to the database
##	These methods are structured in triplets...
##		The first method sends the string to the database
##		The second method builds the string that is sent to the database
##		The third method dumps the string (as a diagnositc)
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Purchase Orders... Begin
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##	Purchase orders
  def sendPoNumberToDatabase(self):
    self.__group = "SiPM Tables"
    self.__sipmTable = "sipm_purchase_orders"
    #####self.__user = "merrill (SLF6.6:GUI)"
    self.__sipmPoString = self.buildRowString_for_SiPM_Po_table()
    if(self.__cmjDebug >= 1): 
	print ("XXXX __sipm__::sendPoNumberToDatabase: self.__sipmPoString = %s") % (self.__sipmPoString)
	self.dumpString_for_Sipm_Po_table(self.__sipmPoString)
	print ("XXXX __sipm__::sendPoNumberToDatabase: self.__whichDatabase = %s | self.__url = %s ") % (self.__whichDatabase, self.__url)
    if self.__sendToDatabase != 0:
      print "send PO to database!!!"
      self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTable)
      if(self.__update == 0):
	self.__myDataLoader1.addRow(self.__sipmPoString) ## use this to insert new entry
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
      else:
	self.__myDataLoader1.addRow(self.__sipmPoString,'update') ## use this to update existing entry
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
      print "self.__text = %s" % self.__text
      time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
      if self.__retVal:				## sucess!  data sent to database
	print "XXXX __sipm__::sendPoNumberToDatabase: Sipm PO Transmission Success!!!"
	print self.__text
      elif self.__password == '':
	print('XXXX __sipm__::sendPoNumberToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
      else:
##		Purchase Orderss
	print "XXXX __sipm__::sendPoNumberToDatabase:  Sipm PO Transmission: Failed!!!"
	print self.__code
	print self.__text 
	return 1		## problem with transmission!   communicate failure\
    return 0  ## success
## ----------------------------------------------------------------
  def buildRowString_for_SiPM_Po_table(self):
    self.__sendSipmPo = {}
    self.__sendSipmPo['po_number'] = self.__poNumber
    self.__sendSipmPo['quantity_ordered'] = self.__poNumberQuantity
    self.__sendSipmPo['date_ordered'] = self.__poNumberDate
    return self.__sendSipmPo
## ----------------------------------------------------------------
  def dumpString_for_Sipm_Po_table(self,tempString):
    print "XXXX __sipm__::dumpString_for_Sipm_Po_table.... Dump string sent to database "
    print "%s \n" % tempString
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Purchase Orders... End
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Received Purchase Orders (Batches)... Begin
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##	Send Received Purchase orders to database
  def sendReceivedPoToDatabase(self):
    self.__group = "SiPM Tables"
    self.__sipmTable = "sipm_batches"
    self.__user = "merrill (SLF6.6:GUI)"
    self.__firstCall = 0
    for self.__localSipmBatch in sorted(self.__batchNumber.keys()):
      #if(self.__cmjDebug != 0): print ("XXXX __sipm__::sendReceivedPoToDatabase: self.__localSipmBatch = %s") % (self.__localSipmBatch)
      ### Must load the batch table first!
      self.__sipmBatchString = self.buildString_for_SiPM_ReceivedPo_table(self.__localSipmBatch)
      if(self.__cmjDebug >= 1): 
	self.dumpString_for_receivedPo(self.__sipmBatchString,self.__firstCall)
	self.__firstCall += 1
      if self.__sendToDatabase != 0:
	print "send Po Received to database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTable)
	if(self.__update == 0):
	  self.__myDataLoader1.addRow(self.__sipmBatchString) ## use this to insert new entry
	  (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	else:
	  self.__myDataLoader1.addRow(self.__sipmBatchString,'update')  ## use this to update existing entry
	  (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	if self.__retVal:				## sucess!  data sent to database
	  print "XXXX __sipm__::sendReceivedPoToDatabase: Sipm PO Transmission Success!!!"
	  print self.__text
	elif self.__password == '':
	  print('XXXX __sipm__::sendReceivedPoToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	else:
	  print "XXXX __sipm__::sendReceivedPoToDatabase:  Sipm PO Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
	  return 1		## problem with transmission!   communicate failure
    return 0  ## success
## ----------------------------------------------------------------
  def buildString_for_SiPM_ReceivedPo_table(self,tempKey):
    self.__sendSipmReceivedPo = {}
    self.__sendSipmReceivedPo['po_number'] = self.__poNumber
    self.__sendSipmReceivedPo['batch_number'] = self.__batchNumber[tempKey]
    self.__sendSipmReceivedPo['quantity_received'] = self.__batchQuantityReceived[tempKey]
    self.__sendSipmReceivedPo['date_received'] = self.__batchDateReceived[tempKey]
    self.__sendSipmReceivedPo['worker_barcode'] = self.__batchWorker[tempKey]
    self.__sendSipmReceivedPo['institution'] = self.__batchInstitution[tempKey]
    return self.__sendSipmReceivedPo
## ----------------------------------------------------------------
  def dumpString_for_receivedPo(self,tempString,firstCall):
    if(firstCall == 0):
      print "XXXX __sipm__::dumpString_for_receivedPo.... Dump string sent to database "
      print "  Send Po Received to database \n"
    print "%s \n" % tempString
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Received Purchase Orders (Batches)... End
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Sipms... Begin
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##	Store the Sipm table quantities
  def storeSipmTableQuantities(self,tempLine):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::::storeSipmTableQuantities: enter -- tempLine = %s ") %(tempLine)
    self.__item = []
    self.__item = tempLine.rsplit(',')
    self.__tempSipmId = self.__item[0]
    self.__tempSipmBatch = self.__item[1]
    self.__tempSipmType = self.__item[5]
    self.__tempSipmLocation = self.__item[11]
    self.__tempSipmPackNumber = self.__item[17]
    #
    self.__serialNumber[self.__tempSipmId] = self.__tempSipmId
    self.__sipmBatch[self.__tempSipmId] = self.__tempSipmBatch
    self.__sipm_type[self.__tempSipmId] = self.__tempSipmType
    self.__vend_institution[self.__tempSipmId] = self.__tempSipmLocation
    self.__packNumber[self.__tempSipmId] = self.__tempSipmPackNumber
    if(self.__cmjDebug > 1):
      print("XXXX __sipm__::::storeSipmTableQuantities: self.__serialNumber[%s] = %s") % (self.__tempSipmId,self.__serialNumber[self.__tempSipmId])
      print("XXXX __sipm__::::storeSipmTableQuantities: self.__sipmBatch[%s] = %s") % (self.__tempSipmId,self.__sipmBatch[self.__tempSipmId])
      print("XXXX __sipm__::::storeSipmTableQuantities: self.__sipm_type[%s] = %s") % (self.__tempSipmId,self.__sipm_type[self.__tempSipmId])
      print("XXXX __sipm__::::storeSipmTableQuantities: self.__packNumber[%s] = %s") % (self.__tempSipmId,self.__packNumber[self.__tempSipmId])
      print("XXXX __sipm__::::storeSipmTableQuantities: self.__vend_institution[%s] = %s") % (self.__tempSipmId,self.__vend_institution[self.__tempSipmId])
      print("XXXX __sipm__::::storeSipmTableQuantities: self.__sipmLocalInstitution = XX%sXX \n") % (self.__sipmLocalInstitution)
      print("XXXX __sipm__::::storeSipmTableQuantities: exit")
## --------------------------------------------------------------
##	Send Sipm Id's to database
  def sendSipmIdsToDatabase(self):
    self.__group = "SiPM Tables"
    self.__sipmTable = "sipms"
    self.__user = "merrill (SLF6.6:GUI)"
    self.__firstCall = 0
    for self.__localSipmId in sorted(self.__serialNumber.keys()):
      if(self.__cmjDebug != 0): 
	  print ("XXXX __sipm__::sendSipmIdsToDatabase: self.__localSipmId = %s") % (self.__localSipmId)
	  print ("XXXX __sipm__::sendSipmIdsToDatabase: self.__whichDatabase = %s | self.__url = %s") % (self.__whichDatabase,self.__url)
      ### Must load the batch table first!
      self.__sipmIdString = self.buildString_for_SipmIdTable(self.__localSipmId)
      if(self.__cmjDebug >= 1): 
	self.dumpString_for_SipmIdTable(self.__sipmIdString,self.__firstCall)
	self.__firstCall += 1
      if self.__sendToDatabase != 0:
	print "send Sipm Id's to database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTable)
	if(self.__update == 0):
	  self.__myDataLoader1.addRow(self.__sipmIdString) #sendToDevelopmentDatabase# use this to insert new entry
	  for n in range(0,self.__maxTries):
	    (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	    print "self.__text = %s" % self.__text
	    time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	    if self.__retVal:				## sucess!  data sent to database
	      print "XXXX __sipm__::sendSipmIdsToDatabase: "+self.__serialNumber[self.__localSipmId]+" -pack number: "+self.__packNumber[self.__localSipmId]+" Transmission Success!!!"+" url = "+self.__url
	      print self.__text
	      break;
	    elif self.__password == '':
	      print('XXXX __sipm__::sendSipmIdsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	    else:
	      print "XXXX __sipm__::sendSipmIdsToDatabase:  Database Transmission: Failed!!!"
	      print self.__code
	      print self.__text 
	else:
	  self.__myDataLoader1.addRow(self.__sipmIdString,'update')  ## use this to update existing entry
	  for n in range(0,self.__maxTries):
	    (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	    print "self.__text = %s" % self.__text
	    time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	    if self.__retVal:				## sucess!  data sent to database
	      print "XXXX __sipm__::sendSipmIdsToDatabase: "+self.__serialNumber[self.__localSipmId]+" -pack number: "+self.__packNumber[self.__localSipmId]+" Updated Database Transmission Success!!!"+" url = "+self.__url
	      print self.__text
	      break;
	    elif self.__password == '':
	      print('XXXX __sipm__::sendSipmIdsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	    else:
	      print "XXXX __sipm__::sendSipmIdsToDatabase:  Database Transmission: Failed!!!"
	      print self.__code
	      print self.__text 
	  #return 1		## problem with transmission!   communicate failure
    return 0   ## success
## -----------------------------------------------------------------
  def buildString_for_SipmIdTable(self,vendKey):
    self.__sendSipmId = {}
    self.__sendSipmId['po_number'] = self.__poNumber
    self.__sendSipmId['batch_number'] = self.__sipmBatch[vendKey]
    self.__sendSipmId['location'] = self.__vend_institution[vendKey]
    self.__sendSipmId['sipm_id'] = self.__serialNumber[vendKey]
    self.__sendSipmId['sipm_type'] = self.__sipm_type[vendKey]
    self.__sendSipmId['pack_number'] = self.__packNumber[vendKey]  ## 2018Oct1
    self.__sendSipmId['sipm_signoff'] = 'not tested'  ## 2019May7
    return self.__sendSipmId
## ----------------------------------------------------------------
  def dumpString_for_SipmIdTable(self,tempString, firstCall):
    if (firstCall == 0):
      print "XXXX __sipm__::dumpString_for_SipmIdTable.... Dump string sent to database "
      print "  Send Sipm Id's to database"
    print "%s \n" % tempString
##   
## ---------------------------------------------------------------
## Send pack number to databaseConfig
## --------------------------------------------------------------
##	Send Sipm Id's to database
  def sendPackNumberToDatabase(self):
    self.__group = "SiPM Tables"
    self.__sipmTable = "sipms"
    self.__firstCall = 0
    for self.__localSipmId in sorted(self.__serialNumber.keys()):
      if(self.__cmjDebug != 0): 
	  print ("XXXX __sipm__::sendPackNumberToDatabase: self.__localSipmId = %s") % (self.__localSipmId)
	  print ("XXXX __sipm__::sendPackNumberToDatabase: self.__whichDatabase = %s | self.__url = %s") % (self.__whichDatabase,self.__url)
      ### Must load the batch table first!
      self.__sipmIdString = self.buildString_for_SipmPackNumber(self.__localSipmId)
      if(self.__cmjDebug >= 1): 
	self.dumpString_for_SipmPackNumber(self.__sipmIdString,self.__firstCall)
	self.__firstCall += 1
      if self.__sendToDatabase != 0:
	print "send Sipm Pack Number to database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTable)
	## Sipm record is already in the database... so we must update the line
	self.__myDataLoader1.addRow(self.__sipmIdString,'update')  ## use this to update existing entry
	for n in range(0,self.__maxTries):
	  (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	  print "self.__text = %s" % self.__text
	  time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	  if self.__retVal:				## sucess!  data sent to database
	    print "XXXX __sipm__::sendPackNumberToDatabase: DatabaseTransmission Success!!!"
	    print self.__text
	    break;
	  elif self.__password == '':
	    print('XXXX __sipm__::sendPackNumberToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	  else:
	    print "XXXX __sipm__::sendPackNumberToDatabase:  Database Transmission: Failed!!!"
	    print self.__code
	    print self.__text 
    return 0   ## success
## -----------------------------------------------------------------
  def buildString_for_SipmPackNumber(self,vendKey):
    self.__sendSipmPackNumber = {}
    self.__sendSipmPackNumber['sipm_id'] = self.__serialNumber[vendKey]
    self.__sendSipmPackNumber['pack_number'] = self.__packNumber[vendKey]
    return self.__sendSipmPackNumber
## ----------------------------------------------------------------
  def dumpString_for_SipmPackNumber(self,tempString, firstCall):
    if (firstCall == 0):
      print "XXXX __sipm__::dumpString_for_SipmIdTable.... Dump string sent to database "
      print "  Send Sipm Id's to database"
    print "%s \n" % tempString



##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Sipms... End
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Local Measurements...  Begin
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##	Decode and store the locally conducted test date!
  def storeLocalTestDate(self,tempDate):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::::storeLocalTestDate: enter -- tempDate = %s") % (tempDate)
    self.__sipmLocalTestDate = tempDate
    self.__sipmLocalTestDate = self.__sipmLocalTestDate.replace('Test_Date ','',1)
    self.__sipmLocalTestDate = self.__sipmLocalTestDate.replace(',','',12)
    self.__sipmLocalTestDate = self.__sipmLocalTestDate.lstrip()
    self.__sipmLocalTestDate = self.__sipmLocalTestDate.rstrip()
    if(self.__cmjDebug > 1): 
      print("XXXX __sipm__::::storeLocalTestDate: self.__sipmLocalTestDate = XX%sXX \n") % (self.__sipmLocalTestDate)
      print("XXXX __sipm__::::storeLocalTestDate: exit")
## -----------------------------------------------------------------
##	Decode and store the locally conducted test institution!
  def storeLocalInstitution(self,tempInstitution):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::::storeLocalInstitution: enter -- tempInstitution = %s ") %(tempInstitution)
    self.__sipmLocalInstitution = tempInstitution
    self.__sipmLocalInstitution = self.__sipmLocalInstitution.replace('Institution  ','',1)
    self.__sipmLocalInstitution = self.__sipmLocalInstitution.replace(',','',12)
    self.__sipmLocalInstitution = self.__sipmLocalInstitution.lstrip()
    self.__sipmLocalInstitution = self.__sipmLocalInstitution.rstrip()
    if(self.__cmjDebug > 1): 
      print("XXXX __sipm__::::storeLocalInstitution: self.__sipmLocalInstitution = XX%sXX \n") % (self.__sipmLocalInstitution)
      print("XXXX __sipm__::::storeLocalInstitution: exit")
## -----------------------------------------------------------------
##	Decode and store the locally conducted test worker!
  def storeLocalWorker(self,tempLocalWorker):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::::storeLocalWorker: enter -- tempLocalWorker = %s") % (tempLocalWorker)
    self.__sipmLocalWorker = tempLocalWorker
    self.__sipmLocalWorker = self.__sipmLocalWorker.replace('Worker ','',1)
    self.__sipmLocalWorker = self.__sipmLocalWorker.replace(',','',12)
    self.__sipmLocalWorker = self.__sipmLocalWorker.lstrip()
    self.__sipmLocalWorker = self.__sipmLocalWorker.rstrip()
    if(self.__cmjDebug > 1): 
      print("XXXX __sipm__::::storeLocalWorker: self.__sipmLocalWorker = XX%sXX \n") % (self.__sipmLocalWorker)
      print("XXXX __sipm__::::storeLocalWorker: exit")
## -----------------------------------------------------------------
##	Decode and store the locally conducted test worker!
  def storeLocalWorkstation(self,tempLocalWorkstation):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::::storeLocalWorkstation: enter --- tempLocalWorkstation = %s") % (tempLocalWorkstation)
    self.__sipmLocalWorkstation = tempLocalWorkstation
    self.__sipmLocalWorkstation = self.__sipmLocalWorkstation.replace('WorkStation ','',1)
    self.__sipmLocalWorkstation = self.__sipmLocalWorkstation.replace(',','',12)
    self.__sipmLocalWorkstation = self.__sipmLocalWorkstation.lstrip()
    self.__sipmLocalWorkstation = self.__sipmLocalWorkstation.rstrip()
    if(self.__cmjDebug > 1): 
      print("XXXX __sipm__::::storeLocalWorkstation: self.__sipmLocalWorkstation = XX%sXX \n") % (self.__sipmLocalWorkstation)
      print("XXXX __sipm__::::storeLocalWorkstation: exit")
## -----------------------------------------------------------------
## Decode the local Sipm measurements on comma-separated-filet.
##     Store results in dictionaries
##
  def storeSipmLocalMeasurement(self,tempSipm):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::storeSipmLocalMeasurement: enter")
    self.__item = tempSipm.rsplit(',')
    print("tempSipm = %s \n") %(tempSipm)
    self.__serialNumber[self.__item[0]] = self.__item[0]
    self.__local_testDate[self.__item[0]] = self.__sipmLocalTestDate
    self.__sipmBatch[self.__item[0]] = 1
    self.__local_worker[self.__item[0]] = self.__sipmLocalWorker
    self.__local_institution[self.__item[0]] = self.__sipmLocalInstitution
    self.__local_workstation[self.__item[0]] = self.__sipmLocalWorkstation
    self.__sipm_type[self.__item[0]] = 'measured'
    self.__local_Vop[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[1]))
    self.__local_Id[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[2]))
    self.__local_Gain[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[3]))
    self.__local_Temp[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[4]))
    self.__local_BreakDownVoltage[self.__item[0]] = '{0:11.3f}'.format(float(self.__item[5]))
    #self.__local_BreakDownVoltageGain[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[19]))
    self.__local_VoltageVsCurrentCond[self.__item[0]] = '{0:11.3f}'.format(float(self.__item[6]))
    self.__local_DarkCountRate[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[7]))
    self.__local_Xtalk[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[8]))
    self.__local_LedResponse[self.__item[0]] = '{0:11.3f}'.format(float(self.__item[9]))
    self.__local_PackNumber[self.__item[0]] = self.__item[10]
    self.__local_DataFilePath[self.__item[0]] = self.__item[11]
    self.__local_DataFileName[self.__item[0]] = self.__item[12]
    self.__local_GainVbrPar1[self.__item[0]] = self.__item[13]
    self.__local_GainVbrPar2[self.__item[0]] = self.__item[14]
    self.__tempString = self.__item[15].lower() ## lower case
    self.__tempString = self.__tempString.rstrip()  ## remove trailing white space characters
    self.__tempString = self.__tempString.lstrip()  ## remove leading white space characters
    self.__local_SipmStatus[self.__item[0]] = self.__tempString
    if(self.__cmjDebug > 1): print("XXXX __sipm__::storeSipmLocalMeasurement: exit")
## -----------------------------------------------------------------
###             Add locally measured sipm values.
## ----------------------------------------------------------------
##  Send the local SiPM measurements to the database... one SiPM at a time!
  def sendSipmLocalMeasToDatabase(self):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::sendSipmLocalMeasToDatabase: enter")
    self.__group = "SiPM Tables"
    self.__sipmTable = "sipm_measure_tests"
    self.__firstCall = 0
    print("XXXX __sipm__::::sendSipmLocalMeasToDatabase: = %s \n") % (len(self.__serialNumber.keys()))
    for self.__localSipmMeas in sorted(self.__serialNumber.keys()):
      self.__sipmLocMeasString = self.buildString_for_SiPM_LocalValues_table(self.__localSipmMeas)
      if(self.__cmjDebug > 1): 
	  self.dumpString_for_SiPM_LocalValue(self.__sipmLocMeasString,self.__firstCall)
	  self.__firstCall += 1
      if self.__sendToDatabase != 0:
	print "send Local Measurements to database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTable)
	## Use one of the two lines below... for insert new line, or to update existing line
	if(self.__update == 0):
	  self.__myDataLoader1.addRow(self.__sipmLocMeasString)  ## use this to insert new entry
	  #(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	  for n in range(0,self.__maxTries):		## 2019May7... multiple tries to send to database
	    (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	    print "self.__text = %s" % self.__text
	    time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	    if self.__retVal:				## success!  data sent to database
	      print "XXXX __sipm__::sendSipmLocalMeasToDatabase: SiPMid: "+self.__localSipmMeas+" Database Transmission Success!!!"
	      print self.__text
	      break
	    elif self.__password == '':
	      print('XXXX __sipm__::sendSipmLocalMeasToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	    else:
	      print "XXXX __sipm__::sendSipmLocalMeasToDatabase:  Database Transmission: Failed!!!"
	      print self.__code
	      print self.__text
	  self.sendSipmStatusToDatabase(self.__localSipmMeas)  ## send the overall Sipm status to the database
	else:
	  self.__myDataLoader1.addRow(self.__sipmLocMeasString,'update')  ## use this to update existing entry
	  #(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	  for n in range(0,self.__maxTries):		## 2019May7... multiple tries to send to database
	    (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	    print "self.__text = %s" % self.__text
	    time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	    if self.__retVal:				## success!  data sent to database
	      print "XXXX __sipm__::sendSipmLocalMeasToDatabase: SiPMid: "+self.__localSipmMeas+" Update Database Transmission Success!!!"
	      print self.__text
	      break
	    elif self.__password == '':
	      print('XXXX __sipm__::sendSipmLocalMeasToDatabase: Update Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	    else:
	      print "XXXX __sipm__::sendSipmLocalMeasToDatabase:  Database Transmission: Failed!!!"
	      print self.__code
	      print self.__text 
	  self.sendSipmStatusToDatabase(self.__localSipmMeas)  ## send the overall Sipm status to the database
    if(self.__cmjDebug > 1): print("XXXX __sipm__::sendSipmLocalMeasToDatabase: exit")
    return 0 ## success
##-----------------------------------------------------------------
## This method builds the table for the local Sipm test results...
  def buildString_for_SiPM_LocalValues_table(self,tempKey):
    self.__sendSipmRow = {}		## define empty dictionary
    self.__sendSipmRow['sipm_id'] = self.__serialNumber[tempKey]
    self.__sendSipmRow['test_type'] = 'measured'
    self.__sendSipmRow['worker_barcode'] =  self.__local_worker[tempKey]
    self.__sendSipmRow['workstation_barcode'] =  self.__local_workstation[tempKey]
    #self.__sendSipmRow['measure_test_date'] = strftime('%Y-%m-%d %H:%M:%Z')
    self.__sendSipmRow['measure_test_date'] = self.__local_testDate[tempKey]
    self.__sendSipmRow['bias_voltage'] = self.__local_Vop[tempKey]
    self.__sendSipmRow['dark_count'] = self.__local_Id[tempKey]
    self.__sendSipmRow['gain'] = self.__local_Gain[tempKey]
    self.__sendSipmRow['temp_degc'] = self.__local_Temp[tempKey]
    self.__sendSipmRow['breakdown_voltage'] = self.__local_BreakDownVoltage[tempKey]
    self.__sendSipmRow['dark_count_rate'] = self.__local_DarkCountRate[tempKey] ## need to add
    self.__sendSipmRow['current_vs_voltage_condition'] = self.__local_VoltageVsCurrentCond[tempKey]
    self.__sendSipmRow['x_talk'] = self.__local_Xtalk[tempKey]
    self.__sendSipmRow['led_response'] = self.__local_LedResponse[tempKey]
    #self.__sendSipmRow['pack_number'] = self.__local_PackNumber[tempKey]
    self.__sendSipmRow['data_file_location'] = self.__local_DataFilePath[tempKey]
    self.__sendSipmRow['data_file_name'] = self.__local_DataFileName[tempKey]
    self.__sendSipmRow['breakdown_gain'] = self.__local_GainVbrPar1[tempKey]
    self.__sendSipmRow['breakdown_slope'] = self.__local_GainVbrPar2[tempKey]
    return(self.__sendSipmRow)
## ----------------------------------------------------------------
  def dumpString_for_SiPM_LocalValue(self,tempString,firstCall):
    if(firstCall == 0):
      print "XXXX __sipm__::dumpString_for_SiPM_LocalValue"
    print "%s \n" % tempString
##-----------------------------------------------------------------
##	Send the overall Sipm status (green, yellow or red)
##	determined from the local test results
## 	to the Sipm Table...
  def sendSipmStatusToDatabase(self,tempKey):
    if(self.__cmjDebug > 1): print("XXXX __sipm__::sendSipmStatusToDatabase: enter")
    self.__group = "SiPM Tables"
    self.__sipmTableStatus = "sipms"
    #for self.__overAllSipmStatus in sorted(self.__serialNumber.keys()):
    self.__sendSipmStatus = {}  ## One needs the Batch number and Po Number to ammend the "sipms" table.
    self.__sendSipmStatus['sipm_id'] = self.__serialNumber[tempKey]
    self.__sendSipmStatus['sipm_signoff'] = self.__local_SipmStatus[tempKey]
    self.__getSipmValues = DataQuery(self.__queryUrl)  ## get PO Number and Batch number for this Sipm id
    self.__sipmTableReturn = []
    self.__sipmTableInformation = []
    self.__fetchThese = "batch_number,po_number"  ## get these values
    self.__fetchCondition = "sipm_id:eq:"+str(tempKey) ## fetch information based on SipmId
    self.__sipmTableReturn = self.__getSipmValues.query(self.__database,self.__sipmTableStatus,self.__fetchThese,self.__fetchCondition)
    self.__sipmTableInformation = self.__sipmTableReturn[0].rsplit(',')
    self.__sendSipmStatus['batch_number'] = self.__sipmTableInformation[0]
    self.__sendSipmStatus['po_number'] = self.__sipmTableInformation[1]
    if(self.__cmjDebug > 1):
      for mm in self.__sendSipmStatus.keys():
	print("XXXX __sipm__::sendSipmStatusToDatabase:: self.__sendSipmStatus[%s] = xxx%sxxx") %(mm,self.__sendSipmStatus[mm])
    if self.__sendToDatabase != 0:
      print "send Local Measurements to database!"
      self.__myDataLoader2 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTableStatus)
      self.__myDataLoader2.addRow(self.__sendSipmStatus,'update')  ## MUST update... Sipm row already exist!
      for n in range(0,self.__maxTries):
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader2.send()  ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	if self.__retVal:				## success!  data sent to database
	  print "XXXX __sipm__::sendSipmStatusToDatabase: "+self.__serialNumber[tempKey]+" Database Transmission Success!!!"
	  print self.__text
	  break
	elif self.__password == '':
	  print('XXXX __sipm__::sendSipmStatusToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	else:
	  print "XXXX __sipm__::sendSipmStatusToDatabase:  Database Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
    if(self.__cmjDebug > 1): print("XXXX __sipm__::sendSipmStatusToDatabase: exit")
    return 0 ## success
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Local Measurements...  End
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## -----------------------------------------------------------------
##
## +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Vendor Measurements.... Begin
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## -----------------------------------------------------------------
## Decode the Sipm vendor measurement of the spread sheet.
##     Store results in dictionaries
##
  def storeSipmVendorMeasurement(self,tempSipm):
    self.__item = tempSipm.rsplit(',')
    self.__serialNumber[self.__item[0]] = self.__item[0]
    self.__sipmBatch[self.__item[0]] = self.__item[1]
    self.__vend_worker[self.__item[0]] = self.__item[2]
    self.__vend_institution[self.__item[0]] = self.__item[3]
    self.__vend_workstation[self.__item[0]] = self.__item[4]
    self.__sipm_type[self.__item[0]] = self.__item[5]
    self.__vend_Vop[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[6]))
    self.__vend_Id[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[7]))
    self.__vend_Gain[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[8]))
    self.__vend_Temp[self.__item[0]] = '{0:10.2f}'.format(float(self.__item[9]))
## -----------------------------------------------------------------
##------------------------------------------------------------------
##    Dump the contents of the spreadsheet that was read in
##
  def dumpSpreadSheet(self):
    print("sipm::dumpSpreadSheet \n")
    print("PO Number = %s \n") % (self.__poNumber)
    print("PO Worker = %s \n") % (self.__poNumberWorker)
    print("PO Institution = %s \n") %(self.__poNumberInstitution)
    print("PO Quantiy Ordered = %s \n") % (self.__poNumberQuantity)
    print("PO Order Date = %s \n") % (self.__poNumberDate)
    print(" ---------------------------- \n")
    print(" Batch Information \n")
    print(" len(self.__batchNumber) = %d \n") % len(self.__batchNumber)
    for batch in self.__batchNumber:
	print("batch number: %s Worker %s Inst %s Quant %s Date %s \n") % (batch, self.__batchWorker[batch], self.__batchInstitution[batch], self.__batchQuantityReceived[batch], self.__batchDateReceived[batch])
    print(" ----------------------------- \n")
    print(" 'Sipm Information \n")
    for key in self.__serialNumber.keys():
      print('Serial Number %s VendorVop  %9.2f VendorGain %9.2f VendorId %9.2f VendorTemp %9.2f localVop %9.2f localId %9.2f localGain %9.2f localTemp %9.2f \n') % (self.__serialNumber[key],float(self.__vend_Vop[key]),float(self.__vend_Gain[key]),float(self.__vend_Id[key]),float(self.__vend_Temp[key]),float(self.__local_Vop[key]),float(self.__local_Id[key]),float(self.__local_Gain[key]),float(self.__local_Temp[key]))
##
## -----------------------------------------------------------------
##  Send the SiPM vendor measurements to the database... one SiPM at a time!
  def sendSipmVendorMeasToDatabase(self):
    self.__group = "SiPM Tables"
    self.__sipmTable = "sipm_measure_tests"
    self.__user = "merrill (SLF6.6:GUI)"
    self.__firstCall = 0
    for self.__vendorSipmMeas in sorted(self.__serialNumber.keys()):
      #if(self.__cmjDebug != 0): print ("XXXX __sipm__::sendSipmVendMeasToDatabase: self.__vendorSipmMeas = %s") % (self.__vendorSipmMeas)
      ### Must load the batch table first!
      self.__sipmVendMeasString = self.buildRowString_for_SiPM_VendorValues_table(self.__vendorSipmMeas)
      if(self.__cmjDebug > 1): 
	  self.dumpString_for_SiPM_VendorValue(self.__sipmVendMeasString,self.__firstCall)
	  self.__firstCall += 1
      if self.__sendToDatabase != 0:
	print "send Vendor Values to database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__sipmTable)
	if(self.__update == 0):
	  self.__myDataLoader1.addRow(self.__sipmVendMeasString)  ## use this to insert new entry
	  for n in range(0,self.__maxTries):
	    (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!

	    print "self.__text = %s" % self.__text
	    time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	    if self.__retVal:				## success!  data sent to database
	      print "XXXX __sipm__::sendSipmVendorMeasToDatabase: SiPMid: "+self.__vendorSipmMeas+" Database Transmission Success!!!"
	      print self.__text
	      break
	    elif self.__password == '':
	      print('XXXX __sipm__::sendSipmVendorMeasToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	    else:
	      print "XXXX __sipm__::sendSipmVendorMeasToDatabase:  Database Transmission: Failed!!!"
	      print self.__code
	      print self.__text

	else:
	  self.__myDataLoader1.addRow(self.__sipmVendMeasString,'update')  ## use this to update existing entry
	  for n in range(0,self.__maxTries):
	    (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	    print "self.__text = %s" % self.__text
	    time.sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
	    if self.__retVal:				## success!  data sent to database
	      print "XXXX __sipm__::sendSipmVendorMeasToDatabase: SiPMid: "+self.__vendorSipmMeas+" Update Database Transmission Success!!!"
	      print self.__text
	      break
	    elif self.__password == '':
	      print('XXXX __sipm__::sendSipmVendorMeasToDatabase: Update Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
	    else:
	      print "XXXX __sipm__::ssendSipmVendorMeasToDatabase:  Database Transmission: Failed!!!"
	      print self.__code
	      print self.__text
    return 0  ## success

##-----------------------------------------------------------------
## This method builds the table for the vendor Sipm test results...
  def buildRowString_for_SiPM_VendorValues_table(self,tempKey):
    self.__sendSipmRow = {}		## define empty dictionary
    ##  self.__sendSipmRow['po_number'] = self.__poNumber
    self.__sendSipmRow['sipm_id'] = self.__serialNumber[tempKey]
    self.__sendSipmRow['test_type'] = 'vendor'
    self.__sendSipmRow['worker_barcode'] =  self.__vend_worker[tempKey]
    self.__sendSipmRow['workstation_barcode'] =  self.__vend_workstation[tempKey]
    #self.__sendSipmRow['measure_test_date'] = strftime('%Y-%m-%d %H:%M:%Z')
    self.__sendSipmRow['measure_test_date'] = strftime('%Y-%m-%d %H:%M')
    #self.__sendSipmRow['sipm_type'] = self.__sipm_type[tempKey]
    self.__sendSipmRow['bias_voltage'] = self.__vend_Vop[tempKey]
    self.__sendSipmRow['dark_count'] = self.__vend_Id[tempKey]
    self.__sendSipmRow['gain'] = self.__vend_Gain[tempKey]
    self.__sendSipmRow['temp_degc'] = self.__vend_Temp[tempKey]
    return(self.__sendSipmRow)
## ----------------------------------------------------------------
  def dumpString_for_SiPM_VendorValue(self,tempString,firstCall):
    if(firstCall == 0):
      print "XXXX __sipm__::dumpString_for_SiPM_VendorValue.... Dump string sent to database "
      print "  Send Sipm Vendor Values to database \n"
    print "%s \n" % tempString
##
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## ----------------------------------------------------------------
##
##		Vendor Measurements... End
##
## ----------------------------------------------------------------
## ----------------------------------------------------------------
## -----------------------------------------------------------------
##
##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
#	Build general help string:
  modeString = []
  modeString.append("To run in default mode (add all Sipm information to database):")
  modeString.append("> python Sipm.py -i SipmSpreadSheet.cvs")
  modeString.append("The user may use a relative or abosute path name for the spreadsheet file.")
  modeString.append("The spreadsheet file is in comma-separated-format (.cvs)")
  modeString.append("Default mode enters all values for Sipm (from PO to locally measured value) to the database")
  modeString.append("To add Sipm information incrementally:")
  modeString.append("Add PO information (only): \t\t\t\t")
  modeString.append("\t\t > python Sipm.py -i SipmSpreadSheet.cvs -m 1")
  modeString.append("Add Sipms recieved to database): \t\t\t\t ") 
  modeString.append("\t\t > python Sipm.py -i SipmSpreadSheet.cvs -m 2")
  modeString.append("Add Sipm Id numbers to database (only): \t\t\t\t")
  modeString.append("\t\t > python Sipm.py -i SipmSpreadSheet.cvs -m 3")
  modeString.append("Add Sipm vendor measured quantities to database (only): \t")
  modeString.append("\t\t > python Sipm.py -i SipmSpreadSheet.cvs -m 4")
  modeString.append("Add Sipm locally measured quantities to database (only): \t\t")
  modeString.append("\t\t > python Sipm.py -i SipmSpreadSheet.cvs -m 5")

  modeString.append("Add locally measured i vs v curve to database (only): \t\t")
  modeString.append("\t\t > python Sipm.py -i SipmSpreadSheet.cvs -m 6")
  parser.add_option('-i',dest='inputCvsFile',type='string',default="",help=modeString[0]+'\t\t\t\t\t\t\t '+modeString[1]+'\t\t\t '+modeString[2]+'\t\t\t\t\t\t\t '+modeString[3]+'\t\t '+modeString[4]+'\t\t\t\t\t\t\t '+modeString[5]+'\t\t\t\t\t '+modeString[6]+'\t\t\t\t\t '+modeString[7]+'\t\t\t\t\t '+modeString[8]+'\t\t\t\t '+modeString[9]+"\t\t\t\t"+modeString[10]+modeString[11]+'\t\t\t\t'+modeString[12]+modeString[13]+'\t\t\t\t'+modeString[14]+modeString[15])
#	Mode option.... Either run all functions or select a specfic function
  parser.add_option('-m',dest='runMode',type='int',default=0,help=modeString[3]+'\t\t '+modeString[4]+'\t\t\t\t '+modeString[5]+'\t\t\t\t '+modeString[6]+'\t\t '+modeString[7]+'\t\t '+modeString[8]+'\t\t '+modeString[9])
#	Debug level
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default),  integer value set debug level... larger more verbose.')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--update',dest='update',type='int',default=0,help='--update = 1, change from insert to update mode')
  options, args = parser.parse_args()
  inputSipmFile = options.inputCvsFile
  if(inputSipmFile == ''):
    print("Supply input spreadsheet comma-separated-file")
    for outString in modeString:
      print("%s") % outString
    exit()
  print ("\nRunning %s \n") % (ProgramName)
  print ("%s \n") % (Version)
  print "inputSipmFile = %s " % inputSipmFile
  mySipm = sipm()
  mySipm.turnOnDebug()
  mySipm.openFile(inputSipmFile)
  if(options.update == 1): mySipm.updateMode()
  if(options.runMode == 6):	## Read IV file  this is unique mode... only performs this operation
    if(options.testMode == 0):
      mySipm.turnOnSendToDatabase()
      mySipm.sendToDevelopmentDatabase()
    mySipm.setDebug(options.debugMode)
    mySipm.readIVfile()		## read the IV data file
    mySipm.sendIvMeasurmentsTodatabase()
  else:
    mySipm.readFile()
  if(options.debugMode == 0):
    mySipm.turnOffDebug()
  else:
    mySipm.setDebug(options.debugMode)
  if(options.testMode == 0):
    mySipm.turnOnSendToDatabase()
    mySipm.sendToDevelopmentDatabase()
    #mySipm.sendToProductionDatabase()  ######## SEND TO PRODUCTION DATABASE!!!!
  else:
    mySipm.turnOffSendToDatabase()
    print("%s: TEST MODE: DO NOT SEND TO DATABASE") % ProgramName
##	
##	Run the script in various modes.
##
  if(options.runMode == 0): 	# run all
    proceed0 = 0   ## set this to zero to start process..
    proceed1 = 1
    proceed2 = 1
    proceed3 = 1
    proceed4 = 1
    proceed5 = 1
    proceed6 = 1
    if(proceed0 == 0): proceed1 = mySipm.sendPoNumberToDatabase()
    if(proceed1 == 0): proceed2 = mySipm.sendReceivedPoToDatabase()
    if(proceed2 == 0): proceed3  = mySipm.sendSipmIdsToDatabase()
    if(proceed3 == 0): proceed4 = mySipm.sendSipmVendMeasToDatabase()
    if(proceed4 == 0): proceed5 = mySipm.sendSipmLocalMeasToDatabase()
    if(proceed5 == 0): print("%s wrote all elements to database \n") % (ProgramName)
  if(options.runMode == 1):  #  just send PO to database 
    proceed1 = mySipm.sendPoNumberToDatabase()
    if(proceed1 == 0):
      print("%s wrote Perchase Order Information into database!")  % (ProgramName)
    else:
      print("%s DID NOT write Purchase Order Information into database!!!")  % (ProgramName)
  if(options.runMode == 2):  # send recieve PO information from database
    proceed2 = mySipm.sendReceivedPoToDatabase()
    if(proceed2 == 0):
      print("%s wrote Received Purchase Order Information into database!")  % (ProgramName)
    else:
      print("%s DID NOT write Received Purchase Order Information into database!!!")  % (ProgramName)
  if(options.runMode == 3):  # send Sipm Id's to database
    proceed3  = mySipm.sendSipmIdsToDatabase()
    if(proceed3 == 0):
      print("%s wrote SiPM Id numbers into database!")  % (ProgramName)
    else:
      print("%s DID NOT write SiPM Id numbers into database!!!")  % (ProgramName)
  if(options.runMode == 4):	# enter the vendor measured test quanties.
    proceed4 = mySipm.sendSipmVendMeasToDatabase()
    if(proceed4 == 0):
      print("%s wrote SiPM Vendor Measured quantities into database!")  % (ProgramName)
    else:
      print("%s DID NOT write SiPM Vendor Measured quantities into database!!!")  % (ProgramName)
  if(options.runMode == 5):	# enter the locally measured test quantities
    proceed5 = mySipm.sendSipmLocalMeasToDatabase()
    if(proceed5 == 0):
      print("%s wrote SiPM Locally Measured quantities into database!")  % (ProgramName)
    else:
      print("%s DID NOT write SiPM Locally Measured quantities into database!!!")  % (ProgramName)
##
  if(options.testMode == 1): print("IN TEST MODE: the script did not write to the database!")
  print("Finished running %s \n") % (ProgramName)
##
##
