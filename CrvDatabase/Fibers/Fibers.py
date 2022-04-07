# -*- coding: utf-8 -*-
##
##  File = "Fibers_2022Jan13.py"
##  Derived from File = "Fibers_2021Jan22.py"
##  Derived from File = "Fibers_2016Jun24.py"
##  Derived from File = "Fibers_2016Jun10.py"
##  Derived from File = "Fibers_2016Jun10.py"
##  Derived from File = "Fibers_2016Jun9.py"
##  Derived from File = "Fibers_2016Jun8.py"
##  Derived from File = "Fibers_2016May27.py"
##  Derived from File = "Fibers_2016May23.py"
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
##	$ python Fibers.py -i 'FiberSpreadSheets/Fibers_2017Jun29.csv'  -d 0 -m 1 
##
##  Modified by cmj 2016Jan7... Add the databaseConfig class to get the URL for 
##		the various databases... change the URL in this class to change for all scripts.
##  Modified by cmj 2016Jan14 to use different directories for support modules...
##		These are located in zip files in the various subdirectories....
##  Modified by cmj2016Jan26.... change the maximum number of columns decoded to use variable.
##				change code to accomodate two hole positions
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2017Jun29... Add instructions for use in the call of the script.
##  Modified by cmj2017Jun29... Add test mode option; option to turn off send to database.
##  Modified by cmj2018Jun14... read in new spectrometer spreadsheet format!
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2020Jul09... change hdbClient_v2_0 -> hdbClient_v2_2
##  Modified by cmj2020Jul09... change crvUtilities2018->crvUtilities;
##  Modified by cmj2020Aug03... cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid (not used)
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2022Jan13... add code to enter the new batch of fibers
##
##
sendDataBase = 0  ## zero... don't send to database
#
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from time import *
#from collections import defaultdict   ## this is needed for two dimensional dictionaries
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from generalUtilities import generalUtilities  ## this is needed for three dimensional dictionaries
from collections import defaultdict  ## needed for two dimensional dictionaries

ProgramName = "Fibers.py"
Version = "version2021.01.14"

##############################################################################################
##############################################################################################
##  Class to read in an fiber cvs file.
class readExtrusionCvsFile(object):
  def __init__(self):
    if(self.__cmjDebug != 0): print 'inside __init__ \n'
    self.__cmjDebug = 0
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
###  Class to store fiber elements
class fiber(object):
  def __init__(self):
    self.__cmjDebug = 0        ## no debug statements
    self.__maxColumns = 9  ## maximum columns in the spread sheet
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
    self.__update = 0		# set to 1 to call dataloader in "update  mode"
    ##  2018Jun15... late in the day...
    self.__fiberId = {}			# Dictionary to store the Fiber ID (reel and position)
    self.__fiberProductionDate = {}
    self.__fiberSpoolLength = {}
    self.__fiberCurrentLength = {}
    self.__fiberType = {}
    self.__fiberComments = {}
    self.__vendorDiameter = {}		# Dictionary to store vendor's diameter (key fiberId)
    self.__vendorAttenuation = {}
    ## Vendor measurements
    self.__vendorFiberId = {}		# Dictionary... fiber_id (key: fiber_id)
    self.__vendorSpoolEnd = {}		# Dictionary... End where mesurment was made (key: fiber_id)
    self.__vendorAveDiameter = {}	# Dictionary... average vendor diameter (key: fiber_id)
    self.__vendorSigma = {}		# Dictionary... sigma of average diameter (key: fiber_id)
    self.__vendorNumOfBumpsSpool = {}	# Dictionary... number of bumps per spool (key: fiber_id)
    self.__vendorNumOfBumpsKm = {}	# Dictionary... number of bumps per km
    ## nested dictionaries	
    self.__vendorEccentricity = defaultdict(dict)	# Nested dictionary [fiber_id][spool_end]
    self.__vendorAttenuation = defaultdict(dict)	# Nested dictionary [fiber_id][spool_end]
    self.__vendorVoltAt285cm = defaultdict(dict)	# Nested dictionary [fiber_id][spool_end]
    self.__vendorFiberDistance = {}
    self.__vendorFiberDistanceNumber = {}
    self.__myMultiDimDictionary = generalUtilities()
    self.__vendorAttenuationVsLength = self.__myMultiDimDictionary.nestedDict() # Triply nested dictionary: [fiber_id][spool_end][fiberDistance]
    ##  2018Jun15... late in the day...
    ##
    self.__tempMeasurementDate = ''
    self.__localMeasurementId = {}      # Dictionary to store the local measurment Id
    self.__localMeasurementDate = {}    # Dictionary to store the local measurment date
    self.__localDiameter = {}		# Dictiosevenary to store local diameter measurement (key fiber id)
    self.__localAttenuation = {}	# Dictionary to store local attenuation (key fiberId)
    self.__localLightYield = {}		# Dictionary to store local light yield (key fiberId)
    self.__localTemperature = {}	# Dictionary to store local temp measurement (key fiberId)
    ##
    ##  Variables for the local attenuation measurement
    ##  The local attenuation measurement is reported in ADC counts
    self.__localMeasurementWavelengthId = {}
    self.__localMeasurementWavelengthDate = {}  	
    ## Nested directories do not work when there are degenearate key values...
    ## construct and use nested keys....
    self.__wavelengthTestDate = 'Null'
    self.__wavelengthFiberId = {} ##		[fiberId] = FiberId
    self.__wavelength =  {}			## dictionary to hold the fiber wavelengths [wavelength] = wavelength
    ##  Nested dictionary to hold the ADC vs attenuation for each fiber_atteuation_tests
    ##  The keys to this dictionary are [fiberId][wavelength] = ADC
    self.__wavelengthAdc = defaultdict(dict) ## triply nested dictionary to hold the adc counts
    ##
    ##
    ##  Variables for the Vendor attenuation measurement
    ##  The vendor attenuation measurment is reported in mVolts.
    ##  So these are placed in a different table!
    ##
    self.__vendorAttenuationId = {}
    self.__vendorAttenuationDate = {}  	
    ## Nested directories do not work when there are degenearate key values...
    ## construct and use nested keys....
    self.__vendorAttenuationTestDate = 'Null'
    self.__vendorAttenuationFiberId = {} ##		[fiberId] = FiberId
    self.__vendorAttenuationDistance =  []		## a list to hold the attenuation distance = attenDistance
    self.__vendorAttenuationDistanceNumber = []         ## a list to hold the index for the attenuation distance
    ##  Nested dictionary to hold the ADC vs attenuation for each fiber_atteuation_tests
    ##  The keys to this dictionary are [fiberId][testDate][attenuationDistance] = voltage (milliVolts)
    self.__vendorAttenuationMilliVolt = self.__myMultiDimDictionary.nestedDict() ## triply nested dictionary to hold the adc counts
    ##
    ##  Variables for the Local attenuation measurement
    ##  The vendor attenuation measurment is reported in mVolts.
    ##  So these are placed in a different table!
    ##
    self.__localAttenuationId = {}
    self.__localAttenuationDate = {}
    self.__localAttenuationLength = {}
    ## Nested directories do not work when there are degenearate key values...
    ## construct and use nested keys....
    self.__localAttenuationTestDate = 'Null'
    ##########self.__localAttenuationFiberIdDictionary = {} ##		[fiberId] = FiberId
    self.__localAttenuationDistance =  []		## dictionary to hold the attenuation distance = attenDistance
    ##  Nested dictionary to hold the ADC vs attenuation for each fiber_atteuation_tests
    ##  The keys to this dictionary are [fiberId][testDate][attenuationDistance] = voltage (milliVolts)
    self.__localAttenuationAdcCount = self.__myMultiDimDictionary.nestedDict() ## triply nested dictionary to hold the adc counts
    ##
## -----------------------------------------------------------------
  def turnOnDebug(self):
    self.__cmjDebug = 1  # turn on debug
    print("...fiber::turnOnDebug... turn on debug \n")
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn on debug
    print("...fiber::turnOffDebug... turn off debug \n")

## -----------------------------------------------------------------
  def setDebugLevel(self,tempDebug):
    self.__cmjDebug = tempDebug  # turn on debug
    print("...fiber::setDebugLevel... set debug level: %d \n") % (self.__cmjDebug)

## -----------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    print("...fiber::turnOnSendToDataBase... send to database: self.__sendToDatabase = %s \n") % (self.__sendToDatabase)
## -----------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__sendToDatabase = 0      ## send to database
    print("...fiber::turnOffSendToDatabase... do not send to database \n")
## -----------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    self.__whichDatabase = 'development'
    print("...fiber::sendToDevelopmentDatabase... send to development database \n")
    self.__url = self.__database_config.getWriteUrl()
    self.__password = self.__database_config.getFibersKey()
## -----------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    self.__whichDatabase = 'production'
    print("...fiber::sendToProductionDatabase... send to production database \n")
    self.__url = self.__database_config.getProductionWriteUrl()
    self.__password = self.__database_config.getFibersProductionKey()
## ---------------------------------------------------------------
  def updateMode(self):
    self.__update = 1
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
  def readFiberFileInitial(self):		## method to read the file's contents
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
#	Sort, define and store information here...
    for self.__newLine in self.__fileLine:
      if(self.__cmjDebug > 3): print("XXXX fiber::readFiberFileForInitial : %s \n")% self.__newLine
      if (self.__newLine.find('Kuraray') != -1): self.storeVendorMeasurementDate(self.__newLine)
      if (self.__newLine.find('fiber_lot-') != -1): self.storeFiber(self.__newLine)
      if (self.__newLine.find('M1804-') != -1): self.storeFiber(self.__newLine)
      if (self.__newLine.find('M2103-') != -1): self.storeFiber(self.__newLine) # 2022Jan13
    print 'XXXX readFiberFileForInitial::readFile: end of fiber::readFile'
## -----------------------------------------------------------------
  def readFiberFileVendor(self):		## method to read the file's contents
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
#	Sort, define and store information here...
    self.__previousLine = 0
    self.__ncount = 0
    self.__vendorSpoolEnd['start'] = 'start'
    self.__vendorSpoolEnd['end'] = 'end'
    for self.__newLine in self.__fileLine:
      if(self.__cmjDebug > 3): print("XXXX fiber::readFiberFileVendor (%d) : %s \n")% (self.__ncount, self.__newLine)
      if (self.__newLine.find('Kuraray') != -1): self.storeVendorMeasurementDate(self.__newLine)
      if (self.__newLine.find('[cm]') != -1): print("XXXX fiber::readFiberFileVendor self.__newLine.find('[cm]') %s ") % (self.__newLine.find('[cm]'))
      if (self.__newLine.find('[mV]') != -1): print("XXXX fiber::readFiberFileVendor self.__newLine.find('[mv]') %s ") % (self.__newLine.find('[mV]'))
      if (self.__newLine.find('[cm]') > -1 and self.__newLine.find('[mV]') > -1) : self.storeVendorAttenuationLengths(self.__newLine)
      if (self.__newLine.find('fiber_lot-') != -1): 
	if(self.__cmjDebug > 3):print("readFiberFileVendor: fiber lot")
	self.storeVendorFiberMeasurement(self.__newLine,0)
      ##  Read alternating lines -- M1804
      if (self.__newLine.find('M1804-') != -1 and self.__previousLine == 0  and self.__newLine.find('start') != -1): 
	if(self.__cmjDebug > 3):print("readFiberFileVendor: M1804 - 0")
	self.storeVendorFiberMeasurement(self.__newLine,self.__previousLine)
	self.__previousLine = 1
      elif(self.__previousLine == 1 and self.__newLine.find('end') != -1):
	if(self.__cmjDebug > 3):print("readFiberFileVendor: M1804 - 1")
	self.storeVendorFiberMeasurement(self.__newLine,self.__previousLine)
	self.__previousLine = 0
	## 2022Jan13
	##  Read alternating lines -- M2103
      if (self.__newLine.find('M2103-') != -1 and self.__previousLine == 0  and self.__newLine.find('start') != -1): 
	if(self.__cmjDebug > 3):print("readFiberFileVendor: M2103 - 0")
	self.storeVendorFiberMeasurement(self.__newLine,self.__previousLine)
	self.__previousLine = 1
      elif(self.__previousLine == 1 and self.__newLine.find('end') != -1):
	if(self.__cmjDebug > 3):print("readFiberFileVendor: M2103 - 1")
	self.storeVendorFiberMeasurement(self.__newLine,self.__previousLine)
	self.__previousLine = 0
	## 2022Jan13
      self.__ncount += 1
    if(self.__cmjDebug > 0):print 'XXXX readFiberFileVendor::: end of fiber::readFile'
##
## -----------------------------------------------------------------
##  Read the Local Fiber Diameter Measurement File
##
  def readLocalMeasurementFile(self):
    if(self.__cmjDebug > -1): print("XXXX readLocalMeasurmentFile : Enter  \n") 
    for self.__newLine in self.__inFile.readlines():
      if(self.__cmjDebug > -1): print("XXXX readLocalMeasurmentFile : %s \n")% self.__newLine
      if(self.__newLine.find('Measurement-Date') != -1) : self.storeLocalMeasurementDate(self.__newLine)
      if(self.__newLine.find('m1804-') != -1) : self.storeLocalMeasurement(self.__newLine)
      if(self.__newLine.find('M1804-') != -1) : self.storeLocalMeasurement(self.__newLine)
      if(self.__newLine.find('m2103-') != -1) : self.storeLocalMeasurement(self.__newLine)  # 2022Jan13
      if(self.__newLine.find('M2103-') != -1) : self.storeLocalMeasurement(self.__newLine)  # 2022Jan13
##
##	Method to setup access to the database
## -----------------------------------------------------------------
## -----------------------------------------------------------------
####  Next send the fiber data to the database... one fiber at a time!
####  This done after the statistics for a batch have been loaded....
  def sendFiberToDatabase(self):
    self.__group = "Fiber Tables"
    self.__fiberTable = "fibers"
    if(self.__cmjDebug > 0):
      print("xxxxxxxxxx __fiber__senfFiberToDatabase:  fiberId = %s \n") % self.__fiberId
    for self.__localFiberId in sorted(self.__fiberId.keys()):
      ### Must load the fiber table first!
      self.__fiberString = self.buildRowString_for_Fiber_table(self.__localFiberId)
      if (self.__cmjDebug > 8): 
	print ("XXXX __fiber__::sendFiberToDatabase: self.__group = %s \n") % (self.__group)
	print ("XXXX __fiber__::sendFiberToDatabase: self.__fiberTable = %s \n") % (self.__fiberTable)
	print ("XXXX __fiber__::sendFiberToDatabase: self.__localFiberId = %s") % (self.__localFiberId)
	self.dumpFiberString()  ## debug.... dump fiber string...
      if self.__sendToDatabase != 0:
	print "send to fiber database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__fiberTable)
	if(self.__update == 0):
	  self.__myDataLoader1.addRow(self.__fiberString)  ## use this to insert new entry
	else:
	  self.__myDataLoader1.addRow(self.__fiberString,'update')  ## use this to update existing entry
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()   ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	if self.__retVal:				## sucess!  data sent to database
	  print "XXXX __fiber__::sendFiberToDatabase: Fiber Batch Transmission Success!!!"
	  print self.__text
	elif self.__password == '':
	  print('XXXX __fiber__::sendFiberToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')
	  return 2
	else:
	  print "XXXX __fiber__::sendFiberToDatabase:  Fiber Batch Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
	  return 1		## problem with transmission!   communicate failure
      else:
        print("XXXX __fiber__::sendFiberToDatabase: in test mode... do not send to database \n")
        return 0
    return 0
## -----------------------------------------------------------------
## -----------------------------------------------------------------
#### Build the string for an fiber
  def buildRowString_for_Fiber_table(self,tempKey):  
      self.__sendFiberRow ={}
      if(self.__cmjDebug > 1): print("XXXX __fiber__::buildRowString_for_Fiber_table = %s \n") % tempKey
      self.__sendFiberRow['fiber_id'] 			= self.__fiberId[tempKey]
      self.__sendFiberRow['production_date'] = self.__fiberProductionDate[tempKey]
      self.__sendFiberRow['initial_length'] = self.__fiberSpoolLength[tempKey]
      self.__sendFiberRow['current_length'] = self.__fiberCurrentLength[tempKey]
      self.__sendFiberRow['vendor_diameter_micron']	= self.__vendorDiameter[tempKey]
      #self.__sendFiberRow['vendor_attenuation_mm'] 	= self.__vendorAttenuation[tempKey]
      self.__sendFiberRow['vendor_light_yield'] 	= float(-9999.99)  ## redefined or not given
      self.__sendFiberRow['fiber_type'] = self.__fiberType[tempKey]
      #self.__sendFiberRow['comments'] = self.__fiberComments[tempKey]
      return self.__sendFiberRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpFiberString(self):
      print "XXXX __fiber__::dumpFiberString:  Diagnostic"
      print "XXXX __fiber__::dumpFiberString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendFiberRow:
	print('    self.__sendFiberRow[%s] = %s') % (self.__tempLocal,str(self.__sendFiberRow[self.__tempLocal]))


## -----------------------------------------------------------------
## -----------------------------------------------------------------
####  Next send the local measurment fiber data to the database... one fiber at a time!
####  This done after the statistics for a batch have been loaded....
  def sendFiberLocalMeasurementToDatabase(self):
    self.__group = "Fiber Tables"
    self.__fiberTable = "fiber_tests"  ## this is not correct!!!!
    for self.__localFiberTestId in sorted(self.__localMeasurementId.keys()):
      ### Must load the fiber table first!
      self.__fiberLocalMeasurementString = self.buildRowString_for_FiberLocalMeasurement_table(self.__localFiberTestId)
      if (self.__cmjDebug > 8): 
	print ("XXXX __fiber__::sendFiberLocalMeasurementToDatabase: self.__group = %s \n") % (self.__group)
	print ("XXXX __fiber__::sendFiberLocalMeasurementToDatabase: self.__fiberTable = %s \n") % (self.__fiberTable)
	print ("XXXX __fiber__::sendFiberLocalMeasurementToDatabase: self.__localFiberId = %s") % (self.__localFiberTestId)
	self.dumpFiberLocalMeasurementString()  ## debug.... dump fiber string...
      if self.__sendToDatabase != 0:
	print "send to fiber local measurments database!"
	self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__fiberTable)
	if(self.__update == 0):
	  self.__myDataLoader1.addRow(self.__fiberLocalMeasurementString)  ## use this to insert new entry.
	else:
	  self.__myDataLoader1.addRow(self.__fiberLocalMeasurementString,'update')   ## use this to update existing entry
	(self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	print "self.__text = %s" % self.__text
	time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	if self.__retVal:				## sucess!  data sent to database
	  print "XXXX __fiber__::sendFiberLocalMeasurementToDatabase: Fiber Local Measurment Transmission Success!!!"
	  print self.__text
	elif self.__password == '':
	  print('XXXX __fiber__::sendFiberLocalMeasurementToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')
	  return 2
	else:
	  print "XXXX __fiber__::sendFiberLocalMeasurementToDatabase:  Fiber Fiber Local Measurment Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
	  return 1
    return 0

## -----------------------------------------------------------------
## -----------------------------------------------------------------
## Build the string for an fiber
## fiber local measurement.
## 
  def buildRowString_for_FiberLocalMeasurement_table(self,tempKey):  
      self.__sendFiberLocalMeasurementRow ={}
      if(self.__cmjDebug > 1): print("XXXX __fiber__::buildRowString_for_FiberLocalMeasurment_table = %s \n") % tempKey
      self.__sendFiberLocalMeasurementRow['fiber_id'] = self.__localMeasurementId[tempKey]
      self.__sendFiberLocalMeasurementRow['test_timestamp'] = self.__localMeasurementDate[tempKey].rstrip()
      self.__sendFiberLocalMeasurementRow['diameter_micron'] 	= self.__localDiameter[tempKey]
      self.__sendFiberLocalMeasurementRow['spool_side'] = 'start'
      self.__sendFiberLocalMeasurementRow['measurement'] = 'local'
      #self.__sendFiberLocalMeasurementRow['local_light_yield']		= self.__localLightYield[tempKey]
      #self.__sendFiberLocalMeasurementRow['local_temperature_degc']	= self.__localTemperature[tempKey]
      return self.__sendFiberLocalMeasurementRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpFiberLocalMeasurementString(self):
      print "XXXX __fiber__::dumpFiberLocalMeasurementString:  Diagnostic"
      print "XXXX __fiber__::dumpFiberLocalMeasurementString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendFiberLocalMeasurementRow:
	print('    self.__sendFiberLocalMeasurmentRow[%s] = %s') % (self.__tempLocal,str(self.__sendFiberLocalMeasurementRow[self.__tempLocal]))

## -----------------------------------------------------------------
## -----------------------------------------------------------------
####  Next send the vendor measurment fiber data to the database... one fiber at a time!
####  This done after the statistics for a batch have been loaded....
  def sendFiberVendorMeasurementToDatabase(self):
    if(self.__cmjDebug > 2):
      print ("XXXX __fiber__::sendFiberVendorMeasurementToDatabase: Enter \n") 
      print ("XXXX __fiber__::sendFiberVendorMeasurementToDatabase: len(self.__vendorFiberId.keys()) = %d | len(self.__self.__vendorSpoolEnd.keys()) = %d ") % (len(self.__vendorFiberId.keys()),len(self.__vendorSpoolEnd.keys()))
    self.__group = "Fiber Tables"
    self.__fiberTable = "fiber_tests"
    for self.__localFiberTestId in sorted(self.__vendorFiberId.keys()):
      for self.__localSpoolEnd in sorted(self.__vendorSpoolEnd.keys()):
	### Must load the fiber table first!
	self.__fiberVendorMeasurementString = self.buildRowString_for_FiberVendorMeasurement_table(self.__localFiberTestId,self.__localSpoolEnd)
	if (self.__cmjDebug > 2): 
	  print ("XXXX __fiber__::sendFiberVendorMeasurementToDatabase: self.__group = %s \n") % (self.__group)
	  print ("XXXX __fiber__::sendFiberVendorMeasurementToDatabase: self.__fiberTable = %s \n") % (self.__fiberTable)
	  print ("XXXX __fiber__::sendFiberVendorMeasurementToDatabase self.__localFiberId = %s") % (self.__localFiberTestId)
	  self.dumpFiberVendorMeasurementString()  ## debug.... dump fiber string...
	if self.__sendToDatabase != 0:
	  print "send to fiber vendor measurements database!"
	  self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__fiberTable)
	  if(self.__update == 0):
	    self.__myDataLoader1.addRow(self.__fiberVendorMeasurementString)  ## use this to insert new entry.
	  else:
	    self.__myDataLoader1.addRow(self.__fiberVendorMeasurementString,'update')   ## use this to update existing entry
	  (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	  print "self.__text = %s" % self.__text
	  time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	  if self.__retVal:				## sucess!  data sent to database
	    print "XXXX __fiber__::sesendFiberVendorMeasurementToDatabase: Fiber Local Measurment Transmission Success!!!"
	    print self.__text
	  elif self.__password == '':
	    print('XXXX __fiber__::sendFiberVendorMeasurementToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')
	    return 2
	  else:
	    print "XXXX __fiber__::sendFiberVendorMeasurementToDatabase:  Fiber Fiber Local Measurment Transmission: Failed!!!"
	    print self.__code
	    print self.__text 
	    return 1
    return 0
## -----------------------------------------------------------------
#### Build the string for an fiber
  def buildRowString_for_FiberVendorMeasurement_table(self,tempKey1,tempKey2):  
      self.__sendFiberVendorMeasurementRow ={}
      if(self.__cmjDebug > 1): print("XXXX __fiber__::buildRowString_for_FiberLocalMeasurment_table = %s, %s \n") % (tempKey1,tempKey2)
      self.__sendFiberVendorMeasurementRow['fiber_id'] = self.__vendorFiberId[tempKey1]
      self.__sendFiberVendorMeasurementRow['test_timestamp'] = self.__fiberProductionDate[tempKey1]
      self.__sendFiberVendorMeasurementRow['diameter_micron'] 	= self.__vendorAveDiameter[tempKey1]
      self.__sendFiberVendorMeasurementRow['diameter_sigma_micron'] = self.__vendorSigma[tempKey1]
      self.__sendFiberVendorMeasurementRow['eccentricity'] = self.__vendorEccentricity[tempKey1][tempKey2]
      self.__sendFiberVendorMeasurementRow['number_of_bumps_spool'] = self.__vendorNumOfBumpsSpool[tempKey1]
      self.__sendFiberVendorMeasurementRow['number_of_bumps_km'] = self.__vendorNumOfBumpsKm[tempKey1]
      self.__sendFiberVendorMeasurementRow['spool_side'] = tempKey2
      self.__sendFiberVendorMeasurementRow['measurement'] = 'vendor'
      #self.__sendFiberVendorMeasurementRow['local_temperature_degc']	= self.__localTemperature[tempKey1]
      self.__sendFiberVendorMeasurementRow['attenuation_length_cm'] = self.__vendorAttenuation[tempKey1][tempKey2]
      self.__sendFiberVendorMeasurementRow['attenuation_voltage_at256cm_mv'] = self.__vendorVoltAt285cm[tempKey1][tempKey2]
      return self.__sendFiberVendorMeasurementRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpFiberVendorMeasurementString(self):
      print "XXXX __fiber__::dumpFiberVendorMeasurementString:  Diagnostic"
      print "XXXX __fiber__::dumpFiberVendorMeasurementString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendFiberVendorMeasurementRow:
	print('    self.__sendFiberVendorMeasurementRow[%s] = %s') % (self.__tempLocal,str(self.__sendFiberVendorMeasurementRow[self.__tempLocal]))


## ------------------------------r-----------------------------------   
### Store functions.... must be called within the class to store the information
## -----------------------------------------------------------------
##    Read date that the vendor made the fiber tests
  def storeVendorMeasurementDate(self,tempDate):
    if(self.__cmjDebug > 3): print "XXXX __fiber__::storeVendorMeasurementDate"
    self.__item = []
    self.__item = tempDate.rsplit(',')
    self.__vendorMeasurementDate = self.__item[10]   
    self.__vendorAttenuationTestDate = self.__vendorMeasurementDate+" 00:00"
## -----------------------------------------------------------------
##  Store the vendor fiber measurements
  def storeFiber(self,tempFiber):
    self.__item = []
    self.__item = tempFiber.rsplit(',')
    self.__fiberId[self.__item[1]] = self.__item[1]
    ##self.__tempDate = self.dateStamper(self.__vendorMeasurementDate)  ## convert excel date into timestamp format
    self.__tempDate = self.__vendorMeasurementDate+" 00:00"
    self.__fiberProductionDate[self.__item[1]] = self.__tempDate
    self.__fiberSpoolLength[self.__item[1]]  = self.__item[2]
    self.__fiberCurrentLength[self.__item[1]]  = self.__item[2] 
    self.__vendorDiameter[self.__item[1]] = float(self.__item[4])
    if(self.__item[9]):
      self.__vendorAttenuation[self.__item[1]] = float(self.__item[9])*10.0  ## given in cm, convert to mm
    else:
      self.__vendorAttenuation[self.__item[1]] = float(-9999.99)
    self.__fiberType[self.__item[1]] = 'production'
    if(self.__cmjDebug > 2):
	print("XXXX __fiber__::storeFiber \n")
	print (".... __fiber__::storeFiber = self.__item[0] = %s \n") % self.__item[0]
	print("    fiberId = %s | fiberProductionDate = %s | fiberSpoolLength = %s | currentSpoolLength = %s | fiberType = %s | comments = %s |  vendDiameter = %s | vendAtten = %s | vendLY = %s") %(self.__fiberId[self.__item[0]],self.__fiberProductionDate[self.__item[0]],self.__fiberSpoolLength[self.__item[0]],self.__fiberCurrentLength[self.__item[0]],self.__fiberType[self.__item[0]],self.__fiberComments[self.__item[0]],self.__vendorDiameter[self.__item[0]],self.__vendorAttenuation[self.__item[0]],self.__vendorLightYield[self.__item[0]])
## ---
## -----------------------------------------------------------------
##  Store the vendor fiber measurements
  def storeVendorFiberMeasurement(self,tempFiber,tempWhichLine):
    if(self.__cmjDebug > 2): print ("XXXX __fiber__::storeVendorFiberMeasurement, tempWhichLine = %d") % (tempWhichLine)
    self.__item = []
    self.__item = tempFiber.rsplit(',')
    #print("XXXX __fiber__::storeVendorFiberMeasurement... len(self.__item) = %d ") %(len(self.__item))
    if(tempWhichLine == 0):
      self.__vendorFiberId[self.__item[1]] = self.__item[1]
      self.__tempFiberId = self.__item[1]
      ##self.__tempDate = self.dateStamper(self.__vendorMeasurementDate+" 00:00")  ## convert excel date into timestamp format
      self.__tempDate = self.__vendorMeasurementDate+" 00:00"
      if(self.__cmjDebug > 5): print("...................... self.__tempDate = %s ") % (self.__tempDate)
      self.__fiberProductionDate[self.__item[1]] = self.__tempDate
      ## These quantities are the same for both ends of the spool
      if(self.__item[4] != ''):
	self.__vendorAveDiameter[self.__item[1]] = float(self.__item[4])
      else:
	self.__vendorAveDiameter[self.__item[1]] = float(-9999.99)
      if(self.__item[5] != ''):
	self.__vendorSigma[self.__item[1]] = float(self.__item[5])
      else:
	self.__vendorSigma[self.__item[1]] = float(-9999.99)
      if(self.__item[7] != ''):
	self.__vendorNumOfBumpsSpool[self.__item[1]] = int(self.__item[7])
      else:
	self.__vendorNumOfBumpsSpool[self.__item[1]] = int(-1)
      if(self.__item[8] != ''):
	self.__vendorNumOfBumpsKm[self.__item[1]] = int(self.__item[8])
      else:
	self.__vendorNumOfBumpsKm[self.__item[1]] = int(-1)
    ## These quantities are different for each end of the spool on different lines in the input file
      if(self.__item[6] != ''):
	self.__tempEccentricity=self.__item[6].replace('%','')
	#print("tempEccentricity = %s ") % (self.__tempEccentricity)
	self.__tempEccentrictyFloat = float(self.__tempEccentricity)
	self.__vendorEccentricity[self.__item[1]]['start'] = float(self.__tempEccentrictyFloat/100.0)
      else:
	## 2022Jan13 self.__tempEccentricity[self.__item[1]]['start'] = float(-9999.99)
	self.__vendorEccentricity[self.__item[1]]['start'] = float(-9999.99)
      if(self.__item[9] != ''):
	self.__vendorAttenuation[self.__item[1]]['start'] = float(self.__item[9])
	#print(" self.__item[9] = %s ") % (self.__item[9])
      else:
	self.__vendorAttenuation[self.__item[1]]['start'] = float(-9999.99)
      if(self.__item[10] != ''):
	self.__vendorVoltAt285cm[self.__item[1]]['start'] = float(self.__item[10])
      else:
	self.__vendorVoltAt285cm[self.__item[1]]['start'] = float(-9999.99)
      self.storeVendorAttenuationLightOutput(self.__tempFiberId,self.__tempDate,'start',self.__item)
   ## end side of spool... on the following line!
    if(self.__previousLine == 1):
      if(self.__item[6] != ''):
	#print("tempEccentricity = %s ") % (self.__tempEccentricity)
	self.__tempEccentrictyFloat = float(self.__tempEccentricity)
	self.__vendorEccentricity[self.__tempFiberId]['end'] = float(self.__tempEccentrictyFloat/100.0)
      else:
	self.__tempEccentricity[self.__tempFiberId]['end'] = float(-9999.99)
      if(self.__item[9] != ''):
	self.__vendorAttenuation[self.__tempFiberId]['end'] = float(self.__item[9])
      else:
	self.__vendorAttenuation[self.__tempFiberId]['end'] = float(-9999.99)
      if(self.__item[10] != ''):
	self.__vendorVoltAt285cm[self.__tempFiberId]['end'] = float(self.__item[10])
      else:
	self.__vendorVoltAt285cm[self.__tempFiberId]['end'] = float(-9999.99)
      self.storeVendorAttenuationLightOutput(self.__tempFiberId,self.__tempDate,'end',self.__item)
    if(self.__cmjDebug > 2):
	print("XXXX __fiber__::storeVendorFiberMeasurement \n")
	print (".... __fiber__::storeVendorFiberMeasurement = self.__item[1] = %s \n") % self.__item[1]
	if(self.__previousLine == 0):
	  print("    fiberId = %s | fiberProductionDate = %s | side = start | vendDiameter = %e | vendSig = %e | vendNumBumpSpool = %e | vendNumbBumpKm = %d | venEccen = %e | vendAtten = %e | vendVolt = %e ") %(self.__vendorFiberId[self.__item[1]],self.__fiberProductionDate[self.__item[1]],self.__vendorAveDiameter[self.__item[1]],self.__vendorSigma[self.__item[1]],self.__vendorNumOfBumpsSpool[self.__item[1]],self.__vendorNumOfBumpsKm[self.__item[1]],self.__vendorEccentricity[self.__item[1]]['start'],self.__vendorAttenuation[self.__item[1]]['start'],self.__vendorVoltAt285cm[self.__item[1]]['start'])
	  print("XXXX __fiber__::storeVendorFiberMeasurement \n")
	if(self.__previousLine == 1):
	  print (".... __fiber__::storeVendorFiberMeasurement = self.__item[1] = %s \n") % self.__item[1]
	  print("    fiberId = %s | fiberProductionDate = %s |storeVendorAttenuationLightOutput side = end | vendDiameter = %e | vendSig = %e | vendNumBumpSpool = %e | vendNumbBumpKm = %d | venEccen = %e | vendAtten = %e | vendVolt = %e ") %(self.__vendorFiberId[self.__tempFiberId],self.__fiberProductionDate[self.__tempFiberId],self.__vendorAveDiameter[self.__tempFiberId],self.__vendorSigma[self.__tempFiberId],self.__vendorNumOfBumpsSpool[self.__tempFiberId],self.__vendorNumOfBumpsKm[self.__tempFiberId],self.__vendorEccentricity[self.__tempFiberId]['end'],self.__vendorAttenuation[self.__tempFiberId]['end'],self.__vendorVoltAt285cm[self.__tempFiberId]['end'])
	  #print("    fiberId = %s | fiberProductionDate = %s | side = end | vendDiameter = %e | vendSig = %e | vendNumBumpSpool = %e | vendNumbBumpKm = %d ") %(self.__fiberId[self.__tempFiberId],self.__fiberProductionDate[self.__tempFiberId],self.__vendorDiameter[self.__tempFiberId],self.__vendorSigma[self.__tempFiberId],self.__vendorNumOfBumpsSpool[self.__tempFiberId],self.__vendorNumOfBumpsKm[self.__tempFiberId])

## -----------------------------------------------------------------
##  Store the vendor measured light output in units of mV 
##  for the light output vs distance  measurement.
  def storeVendorAttenuationLightOutput(self,tempFiberId,tempTestDate,tempEnd,tempLine):
    if(self.__cmjDebug > 2):
      print("XXXX __fiber__:storeVendorAttenuationLightOutput: tempLine = %s \n") % (tempLine)
    if(self.__cmjDebug > 3):
      print("XXXX __fiber__:storeVendorAttenuationLightOutput: len(self.__item) = %d \n") % (len(self.__item))
    self.__vendorAttenuationFiberId[tempFiberId] = tempFiberId
    self.__keyCount = 0
    for self.__mcount in range(len(tempLine)):
      if(self.__mcount < 12) : continue
      if(self.__cmjDebug > 4): print("XXXX __fiber__:storeVendorAttenuationLightOutput: self.__item[%d] = xxx%sxxx \n") % (self.__mcount,tempLine[self.__mcount]) 
      self.__tempString = self.__item[self.__mcount].rstrip('cm')
      self.__tempString = self.__tempString.rstrip()
      self.__tempString = self.__tempString.rstrip('cm\n')
      self.__tempString = self.__tempString.rstrip('\r')
      self.__tempString = self.__tempString.rstrip('\r\n')
      self.__tempString = self.__tempString.rstrip()
      self.__vendorAttenuationMilliVolt[tempFiberId][tempEnd][self.__vendorAttenuationDistance[int(self.__keyCount)]] = self.__tempString
      #if(self.__cmjDebug > 3): 
	#print("XXXX __fiber__:storeVendorAttenuationLightOutput: self.__vendorAttenuationDistance.keys(%d) = %s") % (int(self.__keyCount),self.__vendorAttenuationDistance[int(self.__keyCount)])
	#print("XXXX __fiber__:storeVendorAttenuationLightOutput: self.__vendorAttenuationMilliVolt[%s][%s][%s] = xxx%fxxx self.__vendorAttenuationDistdtance = xxx%fxxx \n") % (tempFiberId,tempTestDate,tempEnd,self.__vendorAttenuationDistance[int(self.__keyCount)],self.__vendorAttenuationMilliVolt[tempFiberId][tempEnd][self.__vendorAttenuationDistance[int(self.__keyCount)]])
      self.__keyCount += 1
## -----------------------------------------------------------------
## -----------------------------------------------------------------
  def storeLocalMeasurementDate(self,tempDate):
    if(self.__cmjDebug > 2):
      print("XXXX __fiber__:storeLocalMeasurementDate: tempDate = %s \n") % (tempDate)
    self.__item = []
    self.__item = tempDate.rsplit(',')
    self.__tempTestDate = self.__item[2]
    self.__savePreLocalMeasurementDate = self.timeStamper(self.__tempTestDate)
    if(self.__cmjDebug > -1) :
      print("XXXX __fiber__:storeLocalMeasurementDate: self.__item[2] = %s \n") % (self.__item[2])
      print("XXXX __fiber__:storeLocalMeasurementDate: self.__savePreLocalMeasurementDate = %s \n") % (self.__savePreLocalMeasurementDate)
## -----------------------------------------------------------------
  def storeLocalMeasurement(self,tempMeasure):
    if(self.__cmjDebug > 2):
      print("XXXX __fiber__:storeLocalMeasurement: tempMeasure = %s \n") % (tempMeasure) 
    self.__item = []
    self.__item = tempMeasure.rsplit(',')
    self.__temporaryFiberId = str(self.__item[2]).rstrip()
    self.__temporaryFiberId = self.__temporaryFiberId.upper()
    #print("self.__temporaryFiberId = %s ") % (self.__temporaryFiberId)
    self.__localMeasurementId[self.__temporaryFiberId] = self.__temporaryFiberId
    self.__localMeasurementDate[self.__temporaryFiberId]  = self.__savePreLocalMeasurementDate
    self.__localTemperature[self.__temporaryFiberId]  = -273.15
    self.__localLightYield[self.__temporaryFiberId] = float(-9999.99)
    self.__localAttenuation[self.__temporaryFiberId] = float(-9999.99)
    #print("XXXX __fiber__:storeLocalMeasurement: self.__item[3] = %s") % (self.__item[3])
    if(self.__item[3] != '' and self.__item[3] != '-'):  ## 2022Jan14
      self.__localDiameter[self.__temporaryFiberId] = float(self.__item[3])*1.0e3 ## convert to microns
    else:
      self.__localDiameter[self.__temporaryFiberId] = float(-9999.99)
    if(self.__cmjDebug > -1):
      print("XXXX __fiber__:storeLocalMeasurement")
      print(" key: %s ||| localMeasurmentId = %s | localMeasurmentDate = %s | localDiameter = %s ") % (self.__temporaryFiberId,self.__localMeasurementId[self.__temporaryFiberId],self.__localMeasurementDate[self.__temporaryFiberId],self.__localDiameter[self.__temporaryFiberId])
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## -----------------------------------------------------------------
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
##             This group of methods stores the vendor measured attenuation vs distance...
##             problems?  Look at Fibers-2018Aug02.py --- version before this overhaul!
## ----------------------------------------------------------------
##   Vendor Attenuation table
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##  Store the lengths of fibers that the vendor used to measure theself.storeVendorAttenuationLightOutput(self.__tempFiberId,self.__tempDate,self.__item)
##  attenuation.  This method is called once at the beginning of the script
##  to initialize the self.__vendorAttenuationDistance dictionary
  def storeVendorAttenuationLengths(self,tempLine):
    if(self.__cmjDebug > 3):
      print("XXXX __fiber__:storeVendorAttenuationLengths: tempLine = %s \n") % (tempLine)
    self.__item = []
    self.__item = tempLine.rsplit(',')
    if(self.__cmjDebug > 3):
      print("XXXX __fiber__:storeVendorAttenuationLengths: len(self.__item) = %d \n") % (len(self.__item))
    self.__keyCount = 0
    self.__distanceIndex = 0
    for self.__mcount in range(len(self.__item)):
      if(self.__mcount < 4): continue
      if(self.__cmjDebug > 4): print("XXXX __fiber__:storeVendorAttenuationLengths: self.__item[%d] = xxx%sxxx \n") % (self.__mcount,self.__item[self.__mcount])
      self.__tempString = self.__item[self.__mcount].rstrip('cm')
      self.__tempString = self.__tempString.rstrip()
      self.__tempString = self.__tempString.rstrip('cm\n')
      self.__tempString = self.__tempString.rstrip('\r')
      self.__tempString = self.__tempString.rstrip('\r\n')
      self.__tempString = self.__tempString.rstrip()
      #self.__vendorAttenuationDistance[int(self.__keyCount)] = self.__tempString
      #if(self.__cmjDebug > -1): print("XXXX __fiber__:storeVendorAttenuationLengths: self.__vendorAttenuationDistance[%s] = %s \n") % (self.__keyCount,self.__vendorAttenuationDistance[int(self.__keyCount)])
      self.__vendorAttenuationDistance.append(int(self.__tempString))
      self.__vendorAttenuationDistanceNumber.append(int(self.__distanceIndex))
      self.__keyCount += 1
      self.__distanceIndex += 1
## -----------------------------------------------------------------
## -----------------------------------------------------------------
####  Next send the vendor attenuation measurment fiber data to the database... one fiber at a time!
####  This done after the statistics for a batch have been loaded....
####	.......
  def sendFiberVendorAttenuationToDatabase(self):
    if(self.__cmjDebug > -1):
      print ("XXXX __fiber__::sendFiberVendorAttenuationToDatabase: Enter \n") 
      print ("XXXX __fiber__::sendFiberVendorAttenuationToDatabase: len(self.__vendorFiberId.keys()) = %d | self.__vendorAttenuationTestDate = %s | len(self.__self.__vendorSpoolEnd.keys()) = %d | len(self.__vendorAttenuationDistance.keys) = %d  ") % (len(self.__vendorAttenuationFiberId.keys()),self.__vendorAttenuationTestDate,len(self.__vendorSpoolEnd.keys()),len(self.__vendorAttenuationDistance))
    self.__group = "Fiber Tables"
    self.__fiberTable = "fiber_attenuation_vendor_lengths"
    #print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
    for self.__localFiberTestId in sorted(self.__vendorAttenuationFiberId.keys()):
      #print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
      for self.__localSpoolEnd in sorted(self.__vendorSpoolEnd.keys()):
	self.__localIndex = 0
	for self.__localDistance in sorted(self.__vendorAttenuationDistance):
	  self.__localNumber = int(self.__vendorAttenuationDistanceNumber[self.__localIndex])
	  self.__localIndex += 1
	### Must load the fiber table first!
	  self.__fiberVendorAttenuationString = self.buildRowString_for_FiberVendorAttenuation_table(self.__localFiberTestId,self.__vendorAttenuationTestDate,self.__localSpoolEnd,self.__localDistance,self.__localNumber)
	  if (self.__cmjDebug > -1): 
	    print ("XXXX __fiber__::sendFiberVendorAttenuationToDatabase: self.__group = %s \n") % (self.__group)
	    print ("XXXX __fiber__::sendFiberVendorAttenuationToDatabase: self.__fiberTable = %s \n") % (self.__fiberTable)
	    print ("XXXX __fiber__::sendFiberVendorAttenuationToDatabase: self.__localFiberId = %s") % (self.__localFiberTestId)
	    self.dumpFiberVendorAttenuationString()  ## debug.... dump fiber string...
	  if self.__sendToDatabase != 0:
	    print "send to fiber local measurements database!"
	    self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__fiberTable)
	    if(self.__update == 0):
	      self.__myDataLoader1.addRow(self.__fiberVendorAttenuationString)  ## use this to insert new entry.
	      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	      print "self.__text = %s" % self.__text
	      time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	      if self.__retVal:				## sucess!  data sent to database
		print "XXXX __fiber__::sendFiberVendorMeasurementToDatabase: Fiber Local Measurment Transmission Success!!!"
		print self.__text
	      elif self.__password == '':
		print('XXXX __fiber__::sendFiberVendorMeasurementToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')
		return 2
	      else:
		print "XXXX __fiber__::sendFiberVendorMeasurementToDatabase:  Fiber Fiber Local Measurment Transmission: Failed!!!"
		print self.__code
		print self.__text 
		#return 1
	    else:
	      self.__myDataLoader1.addRow(self.__fiberVendorAttenuationString,'update')   ## use this to update existing entry
	      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	      print "self.__text = %s" % self.__text
	      time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	      if self.__retVal:				## sucess!  data sent to database
		print "XXXX __fiber__::sendFiberVendorMeasurementToDatabase: Fiber Local Measurment Transmission Success!!!"
		print self.__text
	      elif self.__password == '':
		print('XXXX __fiber__::sendFiberVendorMeasurementToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')
		return 2
	      else:
		print "XXXX __fiber__::sendFiberVendorMeasurementToDatabase:  Fiber Fiber Local Measurment Transmission: Failed!!!"
		print self.__code
		print self.__text 
		#return 1
    return 0
## -----------------------------------------------------------------
  def buildRowString_for_FiberVendorAttenuation_table(self,tempFiber,tempDate,tempSpoolEnd,tempDistance,tempFiberNumber):
    if(self.__cmjDebug > -1): print("XXXX __fiber__::buildRowString_for_FiberVendorAttenuation_table: tempFiber = %s | tempDate = %s | tempSpoolEnd = %s | tempDistance = %s \n") % (tempFiber,tempDate,tempSpoolEnd,tempDistance)
    self.__sendVendorAttenuationRow = {}
    self.__sendVendorAttenuationRow['fiber_id'] = tempFiber
    self.__sendVendorAttenuationRow['fiber_test_date'] = tempDate
    self.__sendVendorAttenuationRow['fiber_end'] = tempSpoolEnd
    self.__sendVendorAttenuationRow['fiber_number'] = tempFiberNumber
    self.__sendVendorAttenuationRow['fiber_distance'] = tempDistance
    self.__sendVendorAttenuationRow['fiber_light_output_mv'] = self.__vendorAttenuationMilliVolt[tempFiber][tempSpoolEnd][tempDistance]
    return self.__sendVendorAttenuationRow
## -----------------------------------------------------------------
#### Diagnostic function to print out the dictionary for the fiber batch table:
  def dumpFiberVendorAttenuationString(self):
    print "XXXX __fiber__::dumpFiberVendorAttenuationString:  Diagnostic"
    print "XXXX __fiber__::dumpFiberVendorAttenuationString:  Print dictionary sent to database"
    for self.__tempLocal in self.__sendVendorAttenuationRow:
      print('    self.__dumpFiberVendorAttenuationString[%s] = %s') % (self.__tempLocal,str(self.__sendVendorAttenuationRow[self.__tempLocal]))

######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
##             This group of methods stores the locally measured attenuation vs distance...
##             problems?  Look at Fibers-2018Aug02.py --- version before this overhaul!
## -----------------------------------------------------------------
##  Read the photodiode spreadsheet
##    Read the file that contains the locally measured attenuation vs wavelength
##    This file is written into the database by calling self.sendFiberWavelengthMeasurementToDatabase()
##     that appears later in this script.
  def readLocalAttenuationFile(self):
    if(self.__cmjDebug > 0): print("XXXX readLocalAttenuationFile : Enter  \n") 
    for self.__newLine in self.__inFile.readlines():
      if(self.__cmjDebug > 1): print("XXXX readLocalAttenuationFile : %s \n")% self.__newLine
      if(self.__newLine.find('Date') != -1) : self.storeLocalAttenuationTestDate(self.__newLine)
      if(self.__newLine.find('Fiber') != -1) : self.storeLocalAttenuationFiberId(self.__newLine)
      if(self.__newLine.find('MEAS') != -1) : self.storeLocalAttenuationMeasurements(self.__newLine)
## -----------------------------------------------------------------
##	Store the local attenuation test date:
  def storeLocalAttenuationTestDate(self,tempTestDate):
    if(self.__cmjDebug > 3):
      print("XXXX__fiber__:sstoreLocalAttenuationTestDate... tempTestDate = %s \n") % (tempTestDate)
    self.__item = []
    self.__item = tempTestDate.rsplit(',')
    self.__tempTestDate = self.__item[2]
    self.__localAttenuationTestDate = self.timeStamper(self.__tempTestDate)
    return
## -----------------------------------------------------------------
##	Store the attenuation fiber id's:
  def storeLocalAttenuationFiberId(self,tempFiberId):
    if(self.__cmjDebug > 2):
      print("XXXX__fiber__:storeLocalAttenuationFiberId... tempFiberId = %s \n") % (tempFiberId)
    self.__item = []
    self.__item = tempFiberId.rsplit(',')
    self.__localAttenuationFiberId = []
    self.__mcount = 0
    for self.__newFiber in self.__item:
      self.__temporary = "xxxx"		## 2021Jan14
      if (self.__newFiber == 'Fiber'): continue  ## skip the first column
      if (self.__newFiber == 'Dist'): continue	## skip the second column
      if(str(self.__newFiber).rstrip() == "2270"):
	self.__temporary = "fiber_lot-22701"
      elif(str(self.__newFiber).find("fiber_lot") != -1):	## 2022Jan13
	self.__temporary = "fiber_lot-15112502"				## 2022Jan13
      elif(str(self.__newFiber).find("M2103-") != -1):			## 2022Jan13
	self.__temporary = str(self.__newFiber).rstrip()			## 2022Jan13
      else:
	self.__temporary = 'M1804-'+str(self.__newFiber).rstrip()
      self.__localAttenuationId[self.__temporary] = self.__temporary
      self.__localAttenuationFiberId.append(self.__temporary)			## the spreadsheet needs to be transposed... therefore the list...
      if(self.__cmjDebug > 1): print("XXXX__fiber__:storeLocalAttenuationId... self.__localAttenuationId[%s] = %s") % (self.__temporary,self.__localAttenuationId[self.__temporary])
##
## -----------------------------------------------------------------
##
##    Store the information from the file that contains the locally measured attenuation vs fiber length
##    This file is written into the database by calling self.sendFiberLocalAttenuationMeasurementToDatabase()
##     that appears later in this script.
##  There are three keys in the database: Fiber_Id, TimeStamp (date the test is done)
##   and length that the attenuation is measured.  
##
##  Each fiber will be measured (Fiber_Id), at some time (TimeStamp) for a number of distances
##  The measurment for a fiber may be repeated at different times...
##
  def storeLocalAttenuationMeasurements(self,tempAttenLength):
    if(self.__cmjDebug > 2):
      print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... tempAttenuation = %s \n") % (tempAttenLength)
    self.__item = []
    self.__item = tempAttenLength.rsplit(',')  ## split all columns
    if(not self.__item[0]): return ## reject empty rows
    self.__numberOfColumns = len(self.__item)
    if(self.__cmjDebug > 6):
      print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... self.__numberOfColumns = %d \n") % (self.__numberOfColumns)
    if(self.__numberOfColumns <= 0):
      print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... self.__numberOfColumns = %d ") % int(self.__numberOfColumns)
      return
    self.__localAttenuationLength[self.__item[1]] = self.__item[1]
    self.__localAttenuationAdcValue = []
    self.__mcount = 0
    for self.__column in range(self.__numberOfColumns):
      if(self.__column == 0) : continue
      if(self.__column == 1) : continue
      self.__localAttenuationAdcValue.append(self.__item[self.__column])
      if(self.__cmjDebug > 6): print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... self.__column = %s self.__item[%s] = %s") % (self.__column,self.__mcount,self.__item[self.__column])
      self.__mcount += 1
    if(self.__cmjDebug > 6): 
      print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... len(self.__localAdcValue) = %d ") % int(len(self.__localAttenuationAdcValue))
      print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... len(self.__localAttenuationFiberId) = %d ") % int(len(self.__localAttenuationFiberId))
    for self.__mcount in range(len(self.__localAttenuationFiberId)):
	self.__localAttenuationAdcCount[self.__localAttenuationFiberId[self.__mcount]][self.__localAttenuationLength[self.__item[1]]] = self.__localAttenuationAdcValue[self.__mcount]
	if(self.__cmjDebug > 2): print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... self.__localAttenuationAdcCount[%s][%s] = %s ") % (self.__localAttenuationFiberId[self.__mcount],self.__item[1],self.__localAttenuationAdcCount[self.__localAttenuationFiberId[self.__mcount]][self.__localAttenuationLength[self.__item[1]]])
	#if(self.__cmjDebug >-1): print("XXXX__fiber__:storeLocalAttenuationLocalMeasurements... self.__localAttenuationAdcCount[%s][%s]  ") % (self.__localAttenuationFiberId[self.__mcount],self.__item[1])
    #  self.__mcount += 1
## -----------------------------------------------------------------
  def dumpLocalAttenuationVsDistance(self):
    print(" --------------------------------------- \n")
    print("XXXX__fiber__:dumpLocalAttenuationVsDistance")
    print("   self.__localAttenuationDate = %s ") % (self.__localAttenuationDate)
    print("   len(self.__localAttenuationId) = %d ") % (len(self.__localAttenuationId))
    for self.__m in sorted(self.__localAttenuationId.keys()):
      print(" self__wavelengthFiberId.keys() = %s ") % self.__m
      for self.__n in sorted(self.__localAttenuationLength.keys()):
	print(" self.__localAttenuationId = %s self.__localAttenuationAdcCount = %s ADC = %e") % (self.__localAttenuationId[self.__m],self.__localAttenuationLength[self.__n],float(self.__localAttenuationAdcCount[self.__m][self.__n]))
    print(" --------------------------------------- \n")
    return
###
## -----------------------------------------------------------------
####  Next send the locally measured attenuation vs length data to the database... 
####    one fiber at a time!
####  This sends the locally measured spectral response for a fiber to the database
####  The input file is "Fiber-QA-photodiode-yyyymmdd.csv"
  def sendFiberLocalAttenuationMeasurementToDatabase(self):
    self.__group = "Fiber Tables"
    self.__fiberTable = "fiber_attenuation_local_lengths"
    #for self.__localWavelengthTestId in sorted(self.__localMeasurementWavelength.keys()):
    for self.__m in sorted(self.__localAttenuationId.keys()):
    ##for self.__m in sorted(self.__localAttenuationFiberId.keys()):
      for self.__n in sorted(self.__localAttenuationLength.keys()):
      ### Must load the fiber table first!
	self.__fiberLocalAttenuationMeasurementString = self.buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table(self.__m,self.__n)
	if (self.__cmjDebug > 1): 
	  print ("XXXX __fiber__::sendFiberLocalAttenuationMeasurementToDatabase: self.__group = %s \n") % (self.__group)
	  print ("XXXX __fiber__::sendFiberLocalAttenuationMeasurementToDatabase: self.__fiberTable = %s \n") % (self.__fiberTable)
	  print ("XXXX __fiber__::sendFiberLocalAttenuationMeasurementToDatabase: self.__localFiberId = %s") % (self.__localAttenuationId)
	  self.dumpFiberLocalAttenuationMeasurementString()  ## debug.... dump fiber string...
	if self.__sendToDatabase != 0:
	  print "send to fiber local measurments database!"
	  self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__fiberTable)
	  if(self.__update == 0):
	    self.__myDataLoader1.addRow(self.__fiberLocalAttenuationMeasurementString)  ## use this to insert new entry
	  else:
	    self.__myDataLoader1.addRow(self.__fiberLocalAttenuationMeasurementString,'update') ## use this to update existing entry
	  (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	  print "self.__text = %s" % self.__text
	  time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	  if self.__retVal:				## sucess!  data sent to database
	    print "XXXX __fiber__::sendFiberLocalAttenuationMeasurementToDatabase: Local Attenuation vs Distance Transmission Success!!!"
	    print self.__text
	  elif self.__password == '':
	    print('XXXX __fiber__::sendFiberLocalAttenuationMeasurementToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')
	    return 2
	  else:
	    print "XXXX __fiber__::sendFiberLocalAttenuationMeasurementToDatabase:  Local Attenuation vs Distance Transmission: Failed!!!"
	    print self.__code
	    print self.__text 
	    #return 1
    return 0
## -----------------------------------------------------------------
## -----------------------------------------------------------------
#### Build the string for an fiber attenuation vs wavelength entry
  def buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table(self,tempKeyFiber,tempKeyDistance):  
      self.__sendLocalAttenuationMeasurementRow ={}
      self.__sendLocalAttenuationMeasurementRow['fiber_id'] = self.__localAttenuationId[tempKeyFiber]
      self.__sendLocalAttenuationMeasurementRow['test_timestamp'] = self.__localAttenuationTestDate
      self.__sendLocalAttenuationMeasurementRow['fiber_distance'] 	= self.__localAttenuationLength[tempKeyDistance]
      self.__sendLocalAttenuationMeasurementRow['fiber_adc'] 	= self.__localAttenuationAdcCount[tempKeyFiber][tempKeyDistance]
      if (self.__cmjDebug > 1): 
	print("XXXX __fiber__::buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table----------------------------------- \n")
	print("XXXX __fiber__::buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table... self.__tempTimeStampKey= %s \n") % (self.__localAttenuationTestDate)
	print("XXXX __fiber__::buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table... self.__tempWavelengthFiberId[%s] = %s \n") % (tempKeyFiber,self.__localAttenuationId[tempKeyFiber])
	print("XXXX __fiber__::buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table.... self.__sendLocalAttenuationMeasurementRow['fiber_id'] = %s \n") % (self.__sendLocalAttenuationMeasurementRow['fiber_id'])
	print("XXXX __fiber__::buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table.... self.__sendLocalAttenuationMeasurementRow['test_timestamp'] = %s \n") % (self.__sendLocalAttenuationMeasurementRow['test_timestamp'])
	print("XXXX __fiber__::buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table.... self.__sendLocalAttenuationMeasurementRow['fiber_distance'] = %s \n") % (self.__sendLocalAttenuationMeasurementRow['fiber_distance'])
	print("XXXX __fiber__::buildRowString_for_FiberLocalAttenautionVsDistanceMeasurement_table.... self.__sendLocalAttenuationMeasurementRow['fiber_adc']  = %s \n") % (self.__sendLocalAttenuationMeasurementRow['fiber_adc'])
      return self.__sendLocalAttenuationMeasurementRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the fiber attenuation vs wavelength row:
  def dumpFiberLocalAttenuationMeasurementString(self):
      print "XXXX __fiber__::dumpFiberLocalAttenuationMeasurementString:  Diagnostic"
      print "XXXX __fiber__::dumpFiberLocalAttenuationMeasurementString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendLocalAttenuationMeasurementRow:
	print('    self.__sendLocalAttenuationMeasurementRow[%s] = %s') % (self.__tempLocal,str(self.__sendLocalAttenuationMeasurementRow[self.__tempLocal]))

######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
##
## -----------------------------------------------------------------
##  Read the spectrometer spreadsheet
##    Read the file that contains the locally measured attenuation vs wavelength
##    This file is written into the database by calling self.sendFiberLocalAttenuationMeasurementToDatabase()
##     that appears later in this script.
  def readWavelengthFile(self):
    if(self.__cmjDebug > 0): print("XXXX readWavelengthFile : Enter  \n") 
    for self.__newLine in self.__inFile.readlines():
      if(self.__cmjDebug > 3): print("XXXX readWavelengthFile : %s \n")% self.__newLine
      if(self.__newLine.find('Date') != -1) : self.storeWavelengthTestDate(self.__newLine)
      if(self.__newLine.find('Fiber') != -1) : self.storeWavelengthFiberId(self.__newLine)
      if(self.__newLine.find('MEAS') != -1) : self.storeWavelengthFiberWaveLength(self.__newLine)
##             This group of methods store the locally measured attenuation vs wavelength...
##             problems?  Look at Fibers-2018Aug02.py --- version before this overhaul!
## -----------------------------------------------------------------
##	Store the wavelength test date:
  def storeWavelengthTestDate(self,tempTestDate):
    if(self.__cmjDebug > 3):
      print("XXXX__fiber__:storeWavelengthTestDate... tempTestDate = %s \n") % (tempTestDate)
    self.__item = []
    self.__item = tempTestDate.rsplit(',')
    self.__tempTestDate = self.__item[2]
    self.__wavelengthTestDate = self.timeStamper(self.__tempTestDate)
    return
## -----------------------------------------------------------------
##	Store the wavelength fiber id's:
  def storeWavelengthFiberId(self,tempFiberId):
    if(self.__cmjDebug > 3):
      print("XXXX__fiber__:storeWavelengthFiberId... tempFiberId = %s rWaveLengt\n") % (tempFiberId)
    self.__item = []
    self.__item = tempFiberId.rsplit(',')
    self.__localFiberId = []
    self.__mcount = 0
    for self.__newFiber in self.__item:
      if (self.__newFiber == 'Fiber'): continue  ## skip the first column
      if (self.__newFiber == 'Spl'): continue	## skip the second column
      if(str(self.__newFiber).rstrip() == "2270"):
	self.__temporary = "fiber_lot-22701"
      else:
	self.__temporary = 'M1804-'+str(self.__newFiber).rstrip()
      self.__wavelengthFiberId[self.__temporary] = self.__temporary
      self.__localFiberId.append(self.__temporary)			## the spreadsheet needs to be transposed... therefore the list...
      if(self.__cmjDebug > -1): print("XXXX__fiber__:storeWavelengthFiberId... self.__wavelengthFiberId[%s] = %s") % (self.__temporary,self.__wavelengthFiberId[self.__temporary])
      
## -----------------------------------------------------------------
##
##    Store the information from the file that contains the locally measured attenuation vs wavelength of light
##    This file is written into the database by calling self.sendFiberWavelengthMeasurementToDatabase()
##     that appears later in this script.
##  There are three keys in the database: Fiber_Id, TimeStamp (date the test is done)
##   and wavelength that the attenuation is measured.  
##
##  Each fiber will be measured (Fiber_Id), at some time (TimeStamp) for 10 wavelengths
##  The measurment for a fiber may be repeated at different times...
##
  def storeWavelengthFiberWaveLength(self,tempWavelength):
    if(self.__cmjDebug > -1):
      print("XXXX__fiber__:storeWavelengthFiberWaveLength... tempWavelength = %s \n") % (tempWavelength)
    self.__item = []
    self.__item = tempWavelength.rsplit(',')  ## split all columns
    if(not self.__item[0]): return ## reject empty rows
    self.__numberOfColumns = len(self.__item)
    if(self.__cmjDebug > -1):
      print("XXXX__fiber__:storeWavelengthFiberWaveLength... self.__numberOfColumns = %d \n") % (self.__numberOfColumns)
    if(self.__numberOfColumns <= 0):
      print("XXXX__fiber__:storeWavelengthFiberWaveLength... self.__numberOfColumns = %d ") % int(self.__numberOfColumns)
      return
    self.__wavelength[self.__item[1]] = self.__item[1]
    self.__localAdcValue = []
    self.__mcount = 0
    for self.__column in range(self.__numberOfColumns):
      if(self.__column == 0) : continue
      if(self.__column == 1) : continue
      self.__localAdcValue.append(self.__item[self.__column])
      if(self.__cmjDebug > -1): print("XXXX__fiber__:storeWavelengthFiberWaveLength... self.__column = %s self.__item[%s] = %s") % (self.__column,self.__mcount,self.__item[self.__column])
      self.__mcount += 1
    if(self.__cmjDebug > -1): print("XXXX__fiber__:storeWavelengthFiberWaveLength... len(self.__localAdcValue) = %d ") % int(len(self.__localAdcValue))
    for self.__mcount in range(len(self.__localFiberId)):
	self.__wavelengthAdc[self.__localFiberId[self.__mcount]][self.__wavelength[self.__item[1]]] = self.__localAdcValue[self.__mcount]
	if(self.__cmjDebug >-1): print("XXXX__fiber__:storeWavelengthFiberWaveLength... self.__wavelengthAdc[%s][%s] = %s ") % (self.__localFiberId[self.__mcount],self.__item[1],self.__wavelengthAdc[self.__localFiberId[self.__mcount]][self.__item[1]])
    #  self.__mcount += 1
## -----------------------------------------------------------------
  def dumpWavelengthFiberWaveLength(self):
    print(" --------------------------------------- \n")
    print("XXXX__fiber__:dumpWavelengthFiberWaveLength")
    print("   self.__waveLengthTestDate = %s ") % (self.__wavelengthTestDate)
    print("   len(self.__wavelengthFiberId) = %d ") % (len(self.__wavelengthFiberId))
    for self.__m in sorted(self.__wavelengthFiberId.keys()):
      print(" self__wavelengthFiberId.keys() = %s ") % self.__m
      for self.__n in sorted(self.__wavelength.keys()):
	print(" fiberId = %s wavelength = %s ADC = %e") % (self.__wavelengthFiberId[self.__m],self.__wavelength[self.__n],float(self.__wavelengthAdc[self.__m][self.__n]))
    print(" --------------------------------------- \n")
    return
## -----------------------------------------------------------------
####  Next send the wavelength attenuation data to the database... one fiber at a time!
####  This sends the locally measured spectral response for a fiber to the database
####  The input file is "Fiber-QA-spectrometer-yyyymmdd.csv"
  def sendFiberWavelengthMeasurementToDatabase(self):
    self.__group = "Fiber Tables"
    self.__fiberTable = "fiber_local_spect_attenuations"
    #for self.__localWavelengthTestId in sorted(self.__localMeasurementWavelength.keys()):
    for self.__m in sorted(self.__wavelengthFiberId.keys()):
      for self.__n in sorted(self.__wavelength.keys()):
      ### Must load the fiber table first!
	self.__fiberLocalWavelengthMeasurementString = self.buildRowString_for_FiberWavelengthMeasurement_table(self.__m,self.__n)
	if (self.__cmjDebug > 8): 
	  print ("XXXX __fiber__::sendFiberWavelengthMeasurementToDatabase: self.__group = %s \n") % (self.__group)
	  print ("XXXX __fiber__::sendFiberWavelengthMeasurementToDatabase: self.__fiberTable = %s \n") % (self.__fiberTable)
	  print ("XXXX __fiber__::sendFiberWavelengthMeasurementToDatabase: self.__localFiberId = %s") % (self.__localWavelengthTestId)
	  self.dumpFiberWavelengthMeasurementString()  ## debug.... dump fiber string...
	if self.__sendToDatabase != 0:
	  print "send to fiber local measurments database!"
	  self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__fiberTable)
	  if(self.__update == 0):
	    self.__myDataLoader1.addRow(self.__fiberLocalWavelengthMeasurementString)  ## use this to insert new entry
	  else:
	    self.__myDataLoader1.addRow(self.__fiberLocalWavelengthMeasurementString,'update') ## use this to update existing entry
	  (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
	  print "self.__text = %s" % self.__text
	  time.sleep(2)     ## sleep so we don't send two records with the same timestamp....
	  if self.__retVal:				## sucess!  data sent to database
	    print "XXXX __fiber__::sendFiberWavelengthMeasurementToDatabase: Wavelength Attenuation Transmission Success!!!"
	    print self.__text
	  elif self.__password == '':
	    print('XXXX __fiber__::sendFiberWavelengthMeasurementToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')
	    return 2
	  else:
	    print "XXXX __fiber__::sendFiberWavelengthMeasurementToDatabase:  Wavelength Attenuation Transmission: Failed!!!"
	    print self.__code
	    print self.__text 
	    #return 1
    return 0

## -----------------------------------------------------------------
## -----------------------------------------------------------------
#### Build the string for an fiber attenuation vs wavelength entry
  def buildRowString_for_FiberWavelengthMeasurement_table(self,tempKeyFiber,tempKeyWavelength):  
      self.__sendWavelengthMeasurementRow ={}
      self.__sendWavelengthMeasurementRow['fiber_id'] = self.__wavelengthFiberId[tempKeyFiber]
      self.__sendWavelengthMeasurementRow['test_timestamp'] = self.__wavelengthTestDate
      self.__sendWavelengthMeasurementRow['spool_side'] = 'start'
      self.__sendWavelengthMeasurementRow['wavelength_nm'] 	= self.__wavelength[tempKeyWavelength]
      self.__sendWavelengthMeasurementRow['local_attenuation_mm'] 	= self.__wavelengthAdc[tempKeyFiber][tempKeyWavelength]
      self.__sendWavelengthMeasurementRow['comments']		= 'No Comment!'
      if (self.__cmjDebug > 1): 
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table----------------------------------- \n")
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table... self.__tempTimeStampKey= %s \n") % (self.__wavelengthTestDate)
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table... self.__tempWavelengthFiberId[%s] = %s \n") % (tempKeyFiber,self.__wavelengthFiberId[tempKeyFiber])
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table... self.__tempTimeWavelengthKey[%s] = %s \n") % (tempKeyWavelength,self.__wavelength[tempKeyWavelength])
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table.... self.__sendWavelengthMeasurementRow['fiber_id'] = %s \n") % (self.__sendWavelengthMeasurementRow['fiber_id'])
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table.... self.__sendWavelengthMeasurementRow['test_timestamp'] = %s \n") % (self.__sendWavelengthMeasurementRow['test_timestamp'])
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table.... self.__sendWavelengthMeasurementRow['local_attenuation_mm']  = %s \n") % (self.__sendWavelengthMeasurementRow['local_attenuation_mm'])
	print("XXXX __fiber__::buildRowString_for_FiberWavelengthMeasurement_table.... self.__sendWavelengthMeasurementRow['comments']	 = %s \n") % (self.__sendWavelengthMeasurementRow['comments'])
      return self.__sendWavelengthMeasurementRow

## ----------------------------------------------------------------- 
#### Diagnostic function to print out the fiber attenuation vs wavelength row:
  def dumpFiberWavelengthMeasurementString(self):
      print "XXXX __fiber__::dumpFiberWavelengthMeasurementString:  Diagnostic"
      print "XXXX __fiber__::dumpFiberWavelengthMeasurementString:  Print dictionary sent to database"
      for self.__tempLocal in self.__sendWavelengthMeasurementRow:
	print('    self.__sendWavelengthMeasurementRow[%s] = %s') % (self.__tempLocal,str(self.__sendWavelengthMeasurementRow[self.__tempLocal]))


############################################################################################
############################################################################################
############################################################################################

##
##
## -----------------------------------------------------------------
  def dumpSpreadSheet(self):
    print("XXXX__fiber__:dumpSpreadSheet \n")
#    for self.__localFiberId in sorted(self.__fiberId.keys()):
#      print("self.__localFiberId = %s") % (self.__localFiberId)
    for localKey in sorted(self.__fiberId.keys()):
	print("localKey = %s \n") %(localKey)
        print("  ProductionDate = %s | inital length = %s | current length = %s | fiber type = %s | comments = %s \n") % (self.__fiberProductionDate[localKey], self.__fiberSpoolLength[localKey], self.__fiberCurrentLength[localKey],self.__fiberType[localKey],self.__fiberComments[localKey])

## -----------------------------------------------------------------
## -----------------------------------------------------------------
##	Utility methods...
##
##
## -----------------------------------------------------------------
##  This method translates the excel spread sheet date into the
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
      print("XXXX__fiber__:dateStamper...... self.__tempDate      = <%s>") % (self.__tempDate)
      print("XXXX__fiber__:dateStamper...... self.__tempMmDdYy    = <%s>") % (self.__tempMmDdYy)
      print("XXXX__fiber__:dateStamper...... self.__tempMonth     = <%s>") % (self.__tempMonth)
      print("XXXX__fiber__:dateStamper...... self.__tempDay       = <%s>") % (self.__tempDay)
      print("XXXX__fiber__:dateStamper...... self.__tempYear      = <%s>") % (self.__tempYear)
    if(self.__cmjDebug > 10):
      print("XXXX__fiber__:dateStamper...... self.__tempDateStamp = <%s>") % (self.__tempDateStamp)
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
    if(int(self.__tempMin) < 10): self.__tempMin = '0' + self.__tempMin
    if(int(self.__tempYear) > 2000):
      self.__tempTimeStamp = self.__tempYear+'-'+self.__tempMonth+'-'+self.__tempDay+' '+self.__tempHour+':'+self.__tempMin
    else:
      self.__tempTimeStamp = '20'+self.__tempYear+'-'+self.__tempMonth+'-'+self.__tempDay+' '+self.__tempHour+':'+self.__tempMin
    if(self.__cmjDebug > 11):
      print("XXXX__fiber__:timeStamper...... self.__tempDate     = <%s>") % (self.__tempDate)
      print("XXXX__fiber__:timeStamper...... self.__tempMmDdYy   = <%s>") % (self.__tempMmDdYy)
      print("XXXX__fiber__:timeStamper...... self.__tempMonth    = <%s>") % (self.__tempMonth)
      print("XXXX__fiber__:timeStamper...... self.__tempDay      = <%s>") % (self.__tempDay)
      print("XXXX__fiber__:timeStamper...... self.__tempCombined = <%s>") % (self.__tempCombined)
      print("XXXX__fiber__:timeStamper...... self.__tempYear     = <%s>") % (self.__tempYear)
      print("XXXX__fiber__:timeStamper...... self.__tempHour  = <%s>") % (self.__tempHour)
      print("XXXX__fiber__:timeStamper...... self.__tempMin   = <%s>") % (self.__tempMin)
    if(self.__cmjDebug > 11):
      print("XXXX__fiber__:timeStamper....... self.__tempTimeStamp   = <%s>") % (self.__tempTimeStamp)
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
  modeString.append("To run in default mode (add all Fiber information to database):")
  modeString.append("> python Sipm.py -i FiberSpreadSheet.cvs")
  modeString.append("The user may use a relative or abosute path name for the spreadsheet file.")
  modeString.append("The spreadsheet file is in comma-separated-format (.cvs)")
  modeString.append("Default mode enters all values for Fiber to the database")
  modeString.append("To add Fiberinformation incrementally:")
  modeString.append("Add Fiber information (only): \t\t\t\t")
  modeString.append("\t\t > python Fiber.py -i FiberSpreadSheet.cvs -m 1")
  modeString.append("Add Fiber local test results (only): \t\t\t\t ") 
  modeString.append("\t\t > python Fiber.py -i FiberSpreadSheet.cvs -m 2")
  modeString.append("Add Fiber wavelength results to database (only): \t\t\t\t")
  modeString.append("\t\t > python Fiber.py -i SipmSpreadSheet.cvs -m 3")
  parser.add_option('-i',dest='inputCvsFile',type='string',default="FiberSpreadsheets/Fiber.csv",help=modeString[0]+'\t\t\t\t\t\t\t '+modeString[1]+'\t\t\t '+modeString[2]+'\t\t\t\t\t\t\t '+modeString[3]+'\t\t '+modeString[4]+'\t\t\t\t\t\t\t '+modeString[5]+'\t\t\t\t\t '+modeString[6]+'\t\t\t\t\t '+modeString[7]+'\t\t\t\t\t '+modeString[8]+'\t\t\t\t '+modeString[9]+"\t\t\t\t"+modeString[10]+modeString[11])
  parser.add_option('-m',dest='runMode',type='int',default=0,help=modeString[7]+'\t\t '+modeString[8]+'\t\t\t\t '+modeString[9]+'\t\t\t\t '+modeString[10]+'\t\t '+modeString[11])
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
  options, args = parser.parse_args()
  inputFiberFile = options.inputCvsFile
  print ("\nRunning %s \n") % (ProgramName)
  print ("%s \n") % (Version)
  print ("runMode = %s \n") % (options.runMode)
##
  if(inputFiberFile == ''):
    print("Supply input spreadsheet comma-separated-file")
    for outString in modeString:
      print ("%s") %  outString
    exit()
  print ("\nRunning %s \n") % (ProgramName)
  print ("%s \n") % (Version)
  print "inputFiberFile = %s " % inputFiberFile
  myFibers = fiber()
  if(options.debugMode == 0):
    myFibers.turnOffDebug()
  else:
    myFibers.setDebugLevel(4)
  if(options.testMode == 0):
    if(options.database == 'development'):
      myFibers.sendToDevelopmentDatabase()  ## turns on send to development database
    elif(options.database == 'production'):
      myFibers.sendToProductionDatabase()  ## turns on send to production database
  else:
    myFibers.turnOffSendToDatabase()    ## call this after sentToDevelopment or sendToProduction to turn of


  ## --------------------------------------------
  myFibers.openFile(inputFiberFile)
  myFibers.readFile()

  if(options.runMode == 0):		# enter all data...
    proceed0 = 0			# set this to zero to start process
    proceed1 = 1
    proceed2 = 1
    proceed3 = 1
    if (proceed0 == 0):
      print("__main__ Send Fibers to Database \n")
      proceed1 = myFibers.sendFiberToDatabase()   ## must be called before sendExtrusionsToDatabase
      print("proceed1 = %s \n") % proceed1
      if(proceed1 == 0):
	print("__main__ Wrote intial fiber informaion to database! \n")
      else:
	print("__main__ DID NOT write intial fiber information to database; errorNumber = %d \n") % (proceed1)
    if(proceed1 == 0):
      print("__main__ Send local test results to Database \n")
      proceed2 = myFibers.sendFiberLocalMeasurementToDatabase()
      print("proceed2 = %s \n") % proceed2
      if(proceed2 == 0):
	print("__main__ Wrote local test information into database \n")
      else:
	print("__main__ DID NOT	write local test information into database; errorNumber = %d") % (proceed2)
    if(proceed2 == 0):
      print("__main__ Send local wavelength attenuation measurements to database \n")
      proceed3 = myFibers.sendFiberWavelengthMeasurementToDatabase()
      print("proceed3 = %s \n") % proceed3
      if(proceed3 == 0):
	  print("__main__ Wrote local wavelength attenuation information into database \n")
      else:
	print("__main__ DID NOT write local wavelength attenuation information into database; errorNumber = %d \n") % (proceed3)
#
  if(options.runMode == 1):			# Enter only the initial Fiber informaion
    print("__main__ Send Fibers to Database \n")
    proceed1 = myFibers.sendFiberToDatabase()
    if(proceed1 == 0):
      print("__main__ Wrote intial fiber informaion to database! \n")
    else:
      print("__main__ DID NOT write intial fiber information to database; proceed1 = %d \n") % (proceed1)
  if(options.runMode == 2):			# Enter only the local measurment informatiom
    print("__main__ Send local test results to database \n")
    proceed2 = myFibers.sendFiberLocalMeasurementToDatabase()
    if(proceed2 == 0):
      print("__main__ Wrote local test information into database \n")
    else:
      print("__main__ DID NOT	write local test information into database; errorNumber = %d") % (proceed2)
  if(options.runMode == 3):			# Enter only the local wavelength attenuation information
    print("__main__ Send local wavelength attenuation measurements to database \n")
    proceed3 = myFibers.sendFiberWavelengthMeasurementToDatabase()
    if(proceed3 == 0):
      print("__main__ Wrote local wavelength attenuation information into database \n")
    else:
      print("__main__ DID NOT write local wavelength attenuation information into database; errorNumber = %d \n") % (proceed3)
#
  print("Finished running %s \n") % (ProgramName)

