# -*- coding: utf-8 -*-
##
##  File = "Electronics2019May23.py"
##  Derived from File = "Electronics_2017Oct16.py"
##  Derived from File = "Electronics_2016Jun24.py"
##
##  Program to read a comma-separated data file and enter SiPM values into
##  the QA database.  Here the delimeter is a comma.
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2015Sep23
##
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##  Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##                        yellow highlight to selected scrolled list items
##  Modified by cmj2019May23... Change "hdbClient_v2_0" to "hdbClient_v2_2"
##  Modified by cmj2019May23... Update databaseConfig to accomodate the development database.
##  Modified by cmj2020Jul09... crvUtilities2020 -> crvUtilities; cmjGuiLibGrid2018Oct1->cmjGuiLibGrid2019Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##  Modified by cmj2022Apr01... corrected three python3 print format bugs on lines307, 367, 429 
##
#!/bin/env python
##
##  To run this script:
##      python readElectronicsSpreadSheet_2016May27.py -i "ElectronicsSpreadSheets/Electronics_2016May17.cvs"                         for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##
##
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from collections import defaultdict
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from cmjGuiLibGrid import *       ## 2020Aug03
from generalUtilities import generalUtilities

ProgramName = "Electronics"
Version = "version2021.05.14"

###
###
##############################################################################################
##############################################################################################
##############################################################################################
###   This is a class to read in an Excel spreadsheet page saved as a comma separated file
###   for the Electronicss... The results are written in the database
###   The user can choose between the development or production database....
###
class Electronics(object):
  def __init__(self):

    self.__cmjDebug = 6
    self.__sendToDatabase = 0  ## Do not send to database
    self.__database_config = databaseConfig()
    self.__url = ''
    self.__password = ''
    self.sendToDevelopmentDatabase()  ## choose send to development database as default for now
    ## Electronics Initial information
    self.__startTime = strftime('%Y_%m_%d_%H_%M')
    self.__sleepTime = 1.0
    self.__maxTries = 5            ## set up maximum number of tries to send information to the database.
    self.__update = 0            ## update = 0, add new entry, update = 1, update existing entry.
## -----------------------------------------------------------------
  def turnOnDebug(self):
    self.__cmjDebug = 2  # turn on debug
    print("XXXX __Electronics__::turnOnDebug... turn on debug \n")
## ---------------------------------------------------------------
##  Change dataloader to update rather than insert.
  def updateMode(self):
    print("XXXX __Electronics__:updateMode ==> change from insert to update mode")
    self.__update = 1
## -----------------------------------------------------------------
  def turnOffDebug(self):
    self.__cmjDebug = 0  # turn off debug
    print("XXXX __Electronics__::turnOffDebug... turn off debug \n")
## -----------------------------------------------------------------
  def setDebugLevel(self,tempLevel):
    self.__cmjDebug = tempLevel  # turn off debug
    print(("XXXX __Electronics__::setDebugLevel... debugSet to %d \n",self.__cmjDebug))
## -----------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    print(("XXXX __Electronics__::turnOnSendToDataBase... send to database: self.__sendToDatabase = %s \n") % (self.__sendToDatabase))
## -----------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__sendToDatabase = 0      ## send to database
    print("XXXX __Electronics__::turnOffSendToDatabase... do not send to database \n")
    ## -----------------------------------------------------------------
  def setSleepTime(self,tempSleepTime):
    self.__sleepTime = tempSleepTime      ## send to database
    print(("XXXX __Electronics__::setSleepTime... set sleep time = %f \n") %(self.__sleepTime))
## -----------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__whichDatabase = 'development'
    print("XXXX __Electronics__::sendToDevelopmentDatabase... send to development database \n")
    self.__url = self.__database_config.getWriteUrl()
    self.__password = self.__database_config.getElectronicsKey()
## -----------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__whichDatabase = 'production'
    print("XXXX __Electronics__::sendToProductionDatabase... send to production database \n")
    self.__database_config.setDebugOn()
    self.__url = self.__database_config.getProductionWriteUrl()
    self.__password = self.__database_config.getElectronicsProductionKey()
    ##print("XXXX __Electronics__::sendToProductionDatabase... psswd = xx%sxx \n") % (self.__password)
## -----------------------------------------------------------------
  def openFile(self,tempFileName):      ## method to open the file
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
  def readFile(self):            ## method to read the file's contents
    print ("XXXX __Electronics__::readFile: Enter \n")
    ##   FEB Board Specifics
    self.__febBoard_Number = None
    self.__febBoard_Type = None
    self.__febBoard_TestLocation = None
    self.__febBoard_Comments = None
    ##      FEB Chips
    self.__febChip_ChipId = {}
    self.__febChip_Bias0Gain = {}
    self.__febChip_Bias0Offset = {}
    self.__febChip_Bias1Gain = {}
    self.__febChip_Bias1Offset = {}

    ## FEB Chip Channels... 8 Channels per chip (64 channels per FEB)}
    self.__febChannel_Id = {}            # key is FEB Channel Number 
    self.__febChannel_FebBoard = {}      # key is FEB Channel Number
    self.__febChannel_ChipId = {}      # key is FEB Channel Number
    self.__febChannel_ChipComments = {}            # key is FEB Channel Number
    self.__febChannel_Slope = {}            # key is FEB Channel Number
    self.__febChannel_Intercept = {}      # key is FEB Channel Number
    self.__febChannel_Trim = {}            # key is FEB Channel Number
    self.__febChannel_Comments = {}      # key is FEB Channel Number
    self.__febChannel_CmbId = {}            # key is FEB Channel Number
    self.__febChannel_SipmId = {}      # key is FEB Channel Number
##
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
##      Sort, define and store information here...
    #self.__maxColumns = 11  ## number of columns in spread sheet
    for self.__newLine in self.__fileLine:
      if(self.__cmjDebug > 5): print(("XXXX __Electronics__::readFile: self.__newLine = xxx%sxxx") % (self.__newLine))
      if (self.__newLine.find('feb-') != -1 & self.__newLine.find('fpga-') == -1 & self.__newLine.find('channel-') == -1): self.storeFeb(self.__newLine)
      if (self.__newLine.find('feb-') != -1 & self.__newLine.find('fpga-') != -1 & self.__newLine.find('channel-') == -1): self.storeFebChip(self.__newLine)
      ##  Electronics measurements
      if (self.__newLine.find('channel-') != -1): self.storeElectronicsMeasurement(self.__newLine)
    if(self.__cmjDebug != 0): print('XXXX __Electronics__::readFile: Exit \n')
## ----------------------------------------------------------------- 
##      Read in the spread sheets that only have the Feb Id's and
##      the Feb location and comment.
  def readFebId(self):
    if(self.__cmjDebug > 1): print ("XXXX __Electronics__::readFebId: Enter \n")
    ##   FEB Board Specifics
    self.__febBoard_Number = None
    self.__febBoard_Type = None
    self.__febBoard_TestLocation = None
    self.__febBoard_Comments = None
    ##
    self.__fileLine = []
    self.__fileLine = self.__inFile.readlines()  ## Read whole file here....
    for self.__newLine in self.__fileLine:
      if(self.__cmjDebug > 5): print(("XXXX __Electronics__::readFebId: self.__newLine = xxx%sxxx") % (self.__newLine))
      if (self.__newLine.find('feb-') != -1 & self.__newLine.find('fpga-') == -1 & self.__newLine.find('channel-') == -1): 
        self.storeFeb(self.__newLine)
        self.sendFrontEndBoardsToDatabase()
    if(self.__cmjDebug > 1): print("XXXX __Electronics__::readFebId: Exit \n")
      
## -----------------------------------------------------------------   
##      Accessor functions for the spreadsheet read/decode/dump 
## Store functions.... must be called within the class to store the information
## The store functions store the information read from the spreadsheet in 
## dictionaries used to build the strings sent to the database.
##
## -----------------------------------------------------------------
##      Function to parse the input line and get the FEB information.
  def storeFeb(self,temp):
    self.__item =  []
    self.__item = temp.rsplit(',')
    if(self.__cmjDebug > 0 ): print("XXXX __Electronics__::storeFeb")
    self.__febBoard_Number = self.__item[0]
    self.__febBoard_Type = self.__item[1].lstrip()
    ## don't record the test date here...;
    self.__febBoard_TestLocation = self.__item[3].strip()
    self.__febComment = self.__item[4]
    if(self.__cmjDebug > 1):
      print(("XXXX __Electronics__::storeFeb...self.__febBoard_Number = xxx%sxxx ") % (self.__febBoard_Number))
      print(("XXXX __Electronics__::storeFeb...self.__febBoard_Type = xxx%sxxx ") % (self.__febBoard_Type))
      print(("XXXX __Electronics__::storeFeb...self.__febBoard_TestLocation = xxx%sxxx ") % (self.__febBoard_TestLocation))

## -----------------------------------------------------------------
##     Function to parse the input line and get the FEB chip information
  def storeFebChip(self,temp):
    self.__item = []
    self.__item = temp.rsplit(',')
    if(self.__cmjDebug > 1): print("XXXX __Electronics__::storeFebChip")
    self.__tempChipId = "febchip-"+self.__item[1].strip()+"-"+self.__item[0].strip() # Feb Number + fpga channel Number
    self.__febChip_ChipId[self.__tempChipId] = self.__tempChipId
    # don't read the date..
    self.__febChip_Bias0Gain[self.__tempChipId] = self.__item[3].strip()
    self.__febChip_Bias0Offset[self.__tempChipId] = self.__item[4].strip()
    self.__febChip_Bias1Gain[self.__tempChipId] = self.__item[5].strip()
    self.__febChip_Bias1Offset[self.__tempChipId] = self.__item[6].strip()
    if(self.__cmjDebug > 1):
      print(("XXXX __Electronics__::storeFebChip...self.__febChip_ChipId[%s] = %s") % (self.__tempChipId,self.__febChip_ChipId[self.__tempChipId]))
      print(("XXXX __Electronics__::storeFebChip...self.__febChip_Bias0Gain[%s] = %s") % (self.__tempChipId,self.__febChip_Bias0Gain[self.__tempChipId]))
      print(("XXXX __Electronics__::storeFebChip...self.__febChip_Bias0Offset[%s] = %s") % (self.__tempChipId,self.__febChip_Bias0Offset[self.__tempChipId]))
      print(("XXXX __Electronics__::storeFebChip...self.__febChip_Bias1Gain[%s] = %s") % (self.__tempChipId,self.__febChip_Bias1Gain[self.__tempChipId]))
      print(("XXXX __Electronics__::storeFebChip...self.__febChip_Bias1Offset[%s] = %s") % (self.__tempChipId,self.__febChip_Bias1Offset[self.__tempChipId]))
## -----------------------------------------------------------------
## Decode the Electronics measurement of the spread sheet.
##     Store results in dictionaries
##
  def storeElectronicsMeasurement(self,tempElectronics):
    if(self.__cmjDebug > 1): print("XXXX __Electronics__::storeElectronicsMeasurement")
    self.__item = []
    self.__item = tempElectronics.rsplit(',')
    self.__tempChipId = "febchip-"+self.__item[2].strip()+"-"+self.__item[1].strip() # Feb Number + fpga channel Number
    self.__tempChannelId = self.__tempChipId+self.__item[0].strip()                        # Feb Number + fpga channel Number + channel number
    #
    self.__febChannel_ChipId[self.__tempChannelId] = self.__tempChipId
    self.__febChannel_Id[self.__tempChannelId] = self.__tempChannelId
    self.__febChannel_Slope[self.__tempChannelId] = float.fromhex(self.__item[4])  ## convert Hex into decimal
    self.__febChannel_Intercept[self.__tempChannelId] = float.fromhex(self.__item[5]) ## convert Hex into decimall
    self.__febChannel_Comments[self.__tempChannelId] = self.__item[3]
    self.__febChannel_Trim[self.__tempChannelId] = -9.999
    self.__febChannel_SipmId[self.__tempChannelId] = None
    #self.__febChannel_Trim[self.__tempChannelId] = '{0:10.2f}'.format(float(self.__item[6]))  ## need for the future
    #self.__febChannel_Comments[self.__tempChannelId] = self.__item[7]                      ## need for the future
    #  keep below for the future...
    #if(self.__item[8] != ''):
    #  self.__febChannelCmbId[self.__item[0]] = self.__item[8]
    #else:
    #  self.__febChannelCmbId[self.__item[0]] = None
    #if(self.__item[9] != ''):
    #  self.__febChannelSipmId[self.__item[0]] = self.__item[9]
    #else:
    #  self.__febChannelSipmId[self.__item[0]] = None
    if(self.__cmjDebug > 1):
      print("XXXX __Electronics__::storeElectronicsMeasurement...") 
      print(("XXXX __Electronics__::storeElectronicsMeasurement...self.__febChannel_ChipId[%s]  = %s") % (self.__tempChannelId,self.__febChannel_ChipId[self.__tempChannelId]))
      print(("XXXX __Electronics__::storeElectronicsMeasurement...self.__febChannel_Id[%s] = %s") % (self.__tempChannelId,self.__febChannel_Id[self.__tempChannelId]))
      print(("XXXX __Electronics__::storeElectronicsMeasurement...self.__febChannel_Slope[%s]  = %s") % (self.__tempChannelId,self.__febChannel_Slope[self.__tempChannelId]))
      print(("XXXX __Electronics__::storeElectronicsMeasurement...self.__febChannel_Intercept[%s]  = %s") % (self.__tempChannelId,self.__febChannel_Intercept[self.__tempChannelId]))
      print(("XXXX __Electronics__::storeElectronicsMeasurement...self.__febChannel_Comments[%s]  = %s") % (self.__tempChannelId,self.__febChannel_Comments[self.__tempChannelId]))
      print(("XXXX __Electronics__::storeElectronicsMeasurement...self.__febChannel_Trim[%s]  = %s") % (self.__tempChannelId,self.__febChannel_Trim[self.__tempChannelId]))
      print(("XXXX __Electronics__::storeElectronicsMeasurement...self.__febChannel_SipmId[%s]  = %s") % (self.__tempChannelId,self.__febChannel_SipmId[self.__tempChannelId]))
##
##------------------------------------------------------------------
##    Dump the contents of the spreadsheet that was read in
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## -----------------------------------------------------------------
## ----------------------------------------------------------------
##      Methods to setup access to the database
##      These methods are structured in triplets...
##            The first method sends the string to the database
##            The second method builds the string that is sent to the database
##            The third method dumps the string (as a diagnositc)
## ----------------------------------------------------------------
##      Front End Boards
  def sendFrontEndBoardsToDatabase(self):
    self.__group = "Electronic Tables"
    self.__frontEndBoardsTable = "front_end_boards"
    self.__frontEndBoardString = self.buildRowString_for_Electronics_FrontEndBoards_table()
    if(self.__cmjDebug != 0): 
      print(("XXXX __Electronics__::sendFrontEndBoardsToDatabase: self.__frontEndBoardString = %s") % (self.__frontEndBoardString))
      self.dumpString_for_Electronics_FrontEndBoards_table(self.__frontEndBoardString)
    if self.__sendToDatabase != 0:
      print("send Front End Boards to database!")
      self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__frontEndBoardsTable)
      if(self.__update == 0):                                           ##cmj2019May23... add update
        if(self.__cmjDebug > 2): print("XXXX __Electronics__::sendFrontEndBoardsToDatabase: insert")
        self.__myDataLoader1.addRow(self.__frontEndBoardString,'insert')      ##cmj2019May23... add new line
      else:
        if(self.__cmjDebug > 2): print("XXXX __Electronics__::sendFrontEndBoardsToDatabase: update")
        self.__myDataLoader1.addRow(self.__frontEndBoardString,'update')      ##cmj2019May23... update existing line
      for n in range(0,self.__maxTries):                              ## cmj2019May23... try to send maxTries time to database
        (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()      ## send it to the data base!
        print("self.__text = %s" % self.__text)
        sleep(self.__sleepTime)
        if self.__retVal:                                          ## sucess!  data sent to database
          print("XXXX __Electronics__::sendFrontEndBoardsToDatabase:Electronics FEB "+self.__febBoard_Number+"  Transmission Success!!!")
          print(self.__text)
          break
        elif self.__password == '':
          print(('XXXX __Electronics__::sendFrontEndBoardsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
          break
        else:
          print("XXXX __Electronics__::sendFrontEndBoardsToDatabase:  Electronics FEB "+self.__febBoard_Number+"  Transmission: Failed!!!")
          print(self.__code)
          print(self.__text) 
    return 0  ## success
## ----------------------------------------------------------------
  def buildRowString_for_Electronics_FrontEndBoards_table(self):
    self.__sendElectronicsFrontEndBoards = {}
    self.__sendElectronicsFrontEndBoards['feb_id'] = self.__febBoard_Number.strip()
    self.__sendElectronicsFrontEndBoards['feb_type'] = self.__febBoard_Type.lstrip()
    self.__sendElectronicsFrontEndBoards['comments'] = self.__febBoard_Comments
    self.__sendElectronicsFrontEndBoards['module_id'] = None
    self.__sendElectronicsFrontEndBoards['module_position'] = -1
    self.__sendElectronicsFrontEndBoards['location'] = self.__febBoard_TestLocation
    return self.__sendElectronicsFrontEndBoards
## ----------------------------------------------------------------
  def dumpString_for_Electronics_FrontEndBoards_table(self,tempString):
    print("XXXX __Electronics__::dumpString_for_Electronics_FrontEndBoards_table.... Dump string sent to database ")
    print("%s \n" % tempString)
    print(("XXXX __Electronics__::dumpString_for_Electronics_FrontEndBoards_table... self.__sendElectronicsFrontEndBoards['feb_id'] =  %s") % (self.__sendElectronicsFrontEndBoards['feb_id']))
    print(("XXXX __Electronics__::dumpString_for_Electronics_FrontEndBoards_table... self.__sendElectronicsFrontEndBoards['feb_type'] = xx%sxx") % (self.__sendElectronicsFrontEndBoards['feb_type']))
    print(("XXXX __Electronics__::dumpString_for_Electronics_FrontEndBoards_table... self.__sendElectronicsFrontEndBoards['comments'] = %s") % (self.__sendElectronicsFrontEndBoards['comments']))
    print(("XXXX __Electronics__::dumpString_for_Electronics_FrontEndBoards_table... self.__sendElectronicsFrontEndBoards['module_id'] %s") % (self.__sendElectronicsFrontEndBoards['module_id']))
    print(("XXXX __Electronics__::dumpString_for_Electronics_FrontEndBoards_table... self.__sendElectronicsFrontEndBoards['module_position'] %s") % (self.__sendElectronicsFrontEndBoards['module_position']))
    print(("XXXX __Electronics__::dumpString_for_Electronics_FrontEndBoards_table... self.__sendElectronicsFrontEndBoards['location']%s") % (self.__sendElectronicsFrontEndBoards['location']))

## ----------------------------------------------------------------
##      Send FEB Chip inoformation to database
  def sendFebChipsToDatabase(self):
    self.__group = "Electronic Tables"
    self.__ElectronicsTable = "feb_chips"
    self.__firstCall = 0
    if(self.__cmjDebug > 1): print(("XXXX __Electronics__::sendFebChipsToDatabase... enter: number of chips: %d") % (len(self.__febChip_ChipId))) 
    for self.__localChipID in sorted(self.__febChip_ChipId.keys()):
      if(self.__cmjDebug != 0): print(("XXXX __Electronics__::sendFebChipsToDatabase: self.__localChipID = %s") % (self.__localChipID))
      self.__chipIdString = self.buildString_for_febChipId_table(self.__localChipID)
      ### Must load the batch table first!
      if(self.__cmjDebug != 0): 
        self.dumpString_for_ChipID(self.__chipIdString,self.__firstCall)
        self.__firstCall += 1
      if self.__sendToDatabase != 0:
        print("send ChipId to database!")
        self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__ElectronicsTable)
        if(self.__update == 0):                               ##cmj2019May23... add update
          if(self.__cmjDebug > 2): print("XXXX __Electronics__::sendFebChipsToDatabase: insert")
          self.__myDataLoader1.addRow(self.__chipIdString,'insert')      ##cmj2019May23... add new line
        else: 
          if(self.__cmjDebug > 2): print("XXXX __Electronics__::sendFebChipsToDatabase: update")
          self.__myDataLoader1.addRow(self.__chipIdString,'update')      ##cmj2019May23... update existing line
        for n in range(0,self.__maxTries):                        ## cmj2019May23... try to send maxTries time to database
          (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
          print("self.__text = %s" % self.__text)
          sleep(self.__sleepTime)
          if self.__retVal:                        ## sucess!  data sent to database
            print("XXXX __Electronics__::sendFebChipsToDatabase: Electronics ChipID "+self.__localChipID+" Transmission Success!!!")
            print(self.__text)
            break
          elif self.__password == '':
            print(('XXXX __Electronics__::sendFebChipsToDatabase Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
            break
          else:
            print("XXXX __Electronics__::sendFebChipsToDatabase:  Electronics ChipID "+self.__localChipID+" Transmission: Failed!!!")
            print(self.__code)
            print(self.__text) 
    return 0  ## success
## ----------------------------------------------------------------
  def buildString_for_febChipId_table(self,tempKey):
    self.__sendElectronicsChipId = {}
    print(("XXXX __Electronics__::buildString_for_febChipId_table... tempKey = %s") % (tempKey))
    self.__sendElectronicsChipId['feb_chip_id'] = self.__febChip_ChipId[tempKey]
    self.__sendElectronicsChipId['feb_id'] = self.__febBoard_Number
    self.__sendElectronicsChipId['bias_bus'] = -9.99  ## bias bus value must be float!
    self.__sendElectronicsChipId['comments'] = None
    #self.__sendElectronicsChipId['Bias0Gain'] = float(self.__febChip_Bias0Gain[tempKey])
    #self.__sendElectronicsChipId['Bias0Offset'] = float(self.__febChip_Bias0Offset[tempKey])
    #self.__sendElectronicsChipId['Bias1Gain'] = float(self.__febChip_Bias1Gain[tempKey])
    #self.__sendElectronicsChipId['Bias1Offset'] = float(self.__febChip_Bias1Offs"feb-"+self.__febChip_ChipId[tempKey]et[tempKey])
    return self.__sendElectronicsChipId
## ----------------------------------------------------------------
  def dumpString_for_ChipID(self,tempString,firstCall):
    print("XXXX __Electronics__::dumpString_for_ChipID.... Dump string sent to database ")
    print("%s \n" % tempString)
    print(("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['feb_chip_id'] =  %s") % (self.__sendElectronicsChipId['feb_chip_id']))
    print(("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['feb_id'] = %s") % (self.__sendElectronicsChipId['feb_id']))
    print(("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['bias_bus'] = %s") % (self.__sendElectronicsChipId['bias_bus']))
    print(("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['comments'] = %s") % (self.__sendElectronicsChipId['comments']))
    #print("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['Bias0Gain'] = %f") % (self.__sendElectronicsChipId['Bias0Gain'])
    #print("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['Bias0Offset'] = %f") % (self.__sendElectronicsChipId['Bias0Offset'])
    #print("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['Bias1Gain'] = %f") % (self.__sendElectronicsChipId['Bias1Gain'])
    #print("XXXX __Electronics__::dumpString_for_ChipID.... self.__sendElectronicsChipId['Bias1Offset'] = %f") % (self.__sendElectronicsChipId['Bias1Offset'])
## ----------------------------------------------------------------
##      Send FEB Channel information to database
  def sendElectronicsMeasurementsToDatabase(self):
    if(self.__cmjDebug != 0): print("XXXX __Electronics__::sendElectronicsMeasurementsToDatabase \n")
    self.__group = "Electronic Tables"
    self.__electronicsTable = "feb_channels"
    self.__firstCall = 0
    if(self.__cmjDebug > 1): print(("XXXX __Electronics__::sendElectronicsMeasurementsToDatabase... enter: number of channels: %d") % (len(self.__febChannel_Id)))
    for self.__localElectronicsMeasurments in sorted(self.__febChannel_Id.keys()):
      self.__electronicsMeasurmentString = self.buildString_for_ElectronicsMeasurementsTable(self.__localElectronicsMeasurments)
      ### Must load the batch table first!
      if(self.__cmjDebug != 0): 
        self.dumpString_for_ElectronicsMeasurmentsTable(self.__electronicsMeasurmentString,self.__firstCall)
        self.__firstCall += 1
      if self.__sendToDatabase != 0:
        print("send Electronics Measurements to database!")
        self.__myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__electronicsTable)
        if(self.__update == 0):
          self.__myDataLoader1.addRow(self.__electronicsMeasurmentString,'insert')
        else:
          self.__myDataLoader1.addRow(self.__electronicsMeasurmentString,'update')
        for n in range(0,self.__maxTries):                        ## cmj2019May23... try to send maxTries time to database
          (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()  ## send it to the data base!
          print("self.__text = %s" % self.__text)
          sleep(self.__sleepTime)
          if self.__retVal:                        ## sucess!  data sent to database
            print("XXXX __Electronics__::sendElectronicsMeasurementsToDatabase: Electronics Measurement for "+self.__localElectronicsMeasurments+" DatabaseTransmission Success!!!")
            print(self.__text)
            break
          elif self.__password == '':
            print(('XXXX __Electronics__::sendElectronicsMeasurementsToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
            break
          else:
            print("XXXX __Electronics__::sendElectronicsMeasurementsToDatabase: Electronics Measurement for "+self.__localElectronicsMeasurments+" Database Transmission: Failed!!!")
            print(self.__code)
            print(self.__text) 
    return 0   ## success
## -----------------------------------------------------------------
  def buildString_for_ElectronicsMeasurementsTable(self,tempKey):
    self.__sendElectronicsMeasurements = {}
    self.__sendElectronicsMeasurements['feb_chip_id'] = self.__febChannel_ChipId[tempKey]
    self.__sendElectronicsMeasurements['channel'] = self.__febChannel_Id[tempKey]
    self.__sendElectronicsMeasurements['dac_slope'] = self.__febChannel_Slope[tempKey]
    self.__sendElectronicsMeasurements['dac_intercept'] = self.__febChannel_Intercept[tempKey]
    self.__sendElectronicsMeasurements['trim'] = self.__febChannel_Trim[tempKey]
    self.__sendElectronicsMeasurements['comments'] = self.__febChannel_Comments[tempKey]
    # for the future
    #self.__sendElectronicsMeasurements['sipm_id'] = self.__febChannelSipmId[vendKey].strip()
    #self.__sendElectronicsMeasurements['cmb_id'] = self.__febChannel_CmbId[tempKey]
    return self.__sendElectronicsMeasurements
## ----------------------------------------------------------------
  def dumpString_for_ElectronicsMeasurmentsTable(self,tempString, firstCall):
    print(("XXXX __Electronics__::dumpString_for_ElectronicsMeasurmentsTable...self.__sendElectronicsMeasurements['feb_chip_id'] = %s") % (self.__sendElectronicsMeasurements['feb_chip_id']))
    print(("XXXX __Electronics__::dumpString_for_ElectronicsMeasurmentsTable...self.__sendElectronicsMeasurements['channel'] = %s") % (self.__sendElectronicsMeasurements['channel']))
    print(("XXXX __Electronics__::dumpString_for_ElectronicsMeasurmentsTable...self.__sendElectronicsMeasurements['dac_slope'] = %f") % (self.__sendElectronicsMeasurements['dac_slope']))
    print(("XXXX __Electronics__::dumpString_for_ElectronicsMeasurmentsTable...self.__sendElectronicsMeasurements['dac_intercept'] = %f") % (self.__sendElectronicsMeasurements['dac_intercept']))
    print(("XXXX __Electronics__::dumpString_for_ElectronicsMeasurmentsTable...self.__sendElectronicsMeasurements['trim'] = %s") % (self.__sendElectronicsMeasurements['trim']))
    print(("XXXX __Electronics__::dumpString_for_ElectronicsMeasurmentsTable...self.__sendElectronicsMeasurements['comments'] = %s") % (self.__sendElectronicsMeasurements['comments']))
 
##
##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('-i',dest='inputCvsFile',type='string',default="ElectronicsSpreadSheets\FEB_Database_Sample_cmjModified2019May24.csv",help="Name of cvs extrution spread sheet file")
  modeString = []
  modeString.append("To run in the default mode (enter the FEB board) \t\t\t\t\t\t")
  modeString.append(">python Electronics.py -i 'ElectronicsDataFiles\FEB_Database_Sample_cmjModified2019May24.csv' \t\t\t\t\t")
  modeString.append("To add the FEB Chips to the database \t\t\t\t")
  modeString.append(">python Electronics.py -i 'ElectronicsDataFiles\FEB_Database_Sample_cmjModified2019May24.csv' --mode 'chip'\t\t\t\t\t\t\t")
  modeString.append("To add the image of the cut fiber to the database \t")
  modeString.append(">python Electronics.py -i 'ElectronicsDataFiles\FEB_Database_Sample_cmjModified2019May24.csv' --mode 'measurement'\t")
  parser.add_option('--mode',dest='inputMode',type='string',default="initial",help=modeString[0]+modeString[1]+modeString[2]+modeString[3])
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='--database = ''production'' ')
  parser.add_option('--update',dest='update',type='int',default=0,help='--update 1 ... change from insert to update mode')
  options, args = parser.parse_args()
  inputElectronicsFile = options.inputCvsFile
  print(("\nRunning %s \n") % (ProgramName))
  print(("%s \n") % (Version))
  print("inputElectronicsFile = %s " % inputElectronicsFile)
  myElectronics = Electronics()
  myElectronics.openFile(inputElectronicsFile)
  if(options.debug == 1): 
    myElectronics.turnOnDebug()
  else:
    myElectronics.turnOffDebug()
  myElectronics.readFile()      ## read the intput file..
  if(options.testMode == 0):  
    myElectronics.turnOnSendToDatabase()
  else:
    myElectronics.turnOffSendToDatabase()
  if(options.database == "development"):
    myElectronics.sendToDevelopmentDatabase()  ######## SEND TO DEVELOPMENT DATABASE!!!!
  else:
    myElectronics.sendToProductionDatabase()  ######## SEND TO PRODUCTION DATABASE!!!!
  ##
  if (options.mode == 'initial'):  
    proceed1 = myElectronics.sendFrontEndBoardsToDatabase()
    if(proceed1 == 0):
      print(("Program: %s, mode = %s Add FEB to Database Successful! \n") % (ProgramName,options.mode))
    else:
      print(("Program: %s, mode = %s Add FEB to Database FAILED! Find problem, try again \n") % (ProgramName,options.mode))
  if(options.mode == 'chip' ): 
    proceed2 = myElectronics.sendFebChipsToDatabase()
    if(proceed2 == 0):
      print(("Program: %s, mode = %s Add FEB Chips to Database Successful! \n") % (ProgramName,options.mode))
    else:
      print(("Program: %s, mode = %s Add FEB Chips to Database FAILED!  Find problem, try again \n") % (ProgramName,options.mode))
  if(options.mode == 'measurement'): 
    proceed3 = myElectronics.sendElectronicsMeasurementsToDatabase()
    if(proceed3 == 0):
      print(("Program: %s, mode = %s Add FEB Measurements to Database Successful! \n") % (ProgramName,options.mode))
    else:
      print(("Program: %s, mode = %s Add FEB Measurements to Database FAILED!  Find problem, try again \n") % (ProgramName,options.mode))
  print(("Finished running %s \n") % (ProgramName))
##
##
