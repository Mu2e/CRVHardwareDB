# -*- coding: utf-8 -*-
##	File = 'SipmMeasurements.py'
## ====================================================================
## ====================================================================
##	Class to display secondary window with Sipm Measurements
##
##  Modified by cmj 2020Jun15 to use cmjGuiLibGrid2019Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May11... replace dataloader3.zip with dataloader.zip
##
##
#!/bin/env python
from tkinter import *         # get widget class
import tkinter as tk
import tkinter.filedialog
import os
import sys        ## 
import optparse   ## parser module... to parse the commaAll Filesnd line arguments
import math
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2021May11
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2018Oct2 add highlight to scrolled list
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from cmjGuiLibGrid import *  ## 2020Aug03
#from Sipm2019Jan30 import *
from Sipm import *
##
ProgramName = "goodSipm2021May12.py"
Version = "version2021.05.12"
##
class getSipmMeasurements(Frame):
  def __init__(self,parent=None, myRow=0, myCol=0):
    Frame.__init__(self,parent)
    print("__SimpMeasurements__sipmMeasurementWindow... enter \n")
    self.__database_config = databaseConfig()
    self.setupDevelopmentDatabase()
    #self.setupProductionDatabase()
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('sipmMeasurement')
    self.__mySaveIt.openFile()
##     
## -------------------------------------------------------------------
##	Make querries to data base for Sipm Status
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Sipm Tables"
    self.__whichDatabase = 'development'
    print("__SimpMeasurements__getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
##
## -------------------------------------------------------------------
##	Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Sipm Tables"
    self.__whichDatabase = 'production'
    print("__SimpMeasurements__getFromProductionDatabase... get from production database \n")
    self.__url = self.__database_config.getProductionQueryUrl()
##
## -------------------------------------------------------------------
  def getSipmIdFromPackNumber(self,tempPackNumber):
    print(" -------------------------------------- ")
    self.__packNumber = tempPackNumber
    print(("__SimpMeasurements__getSipmIdFromPackNumber:: packNumber = %s") % self.__packNumber)
    self.__getSipmIds = DataQuery(self.__queryUrl)
    self.__table = "sipms"
    self.__fetchThese = "sipm_id,"
    self.__fetchCondition = "pack_number:eq:"+str(self.__packNumber)
    print((".... getSipmsFromWafflePack: self.__queryUrl   = %s \n") % (self.__queryUrl))
    print((".... getSipmsFromWafflePack: self.__table                = %s \n") % (self.__table))
    print((".... getSipmsFromWafflePack: self.__fetchThese           = %s \n") % (self.__fetchThese))
    print((".... getSipmsFromWafflePack: self.__fetchCondition       = %s \n") % (self.__fetchCondition))
    self.__sipmId = []
    self.__sipmId = self.__getSipmIds.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    print(("__SimpMeasurements__getSipmIdFromPackNumber:: self.__sipmId = %s") % (self.__sipmId))
    
##
## -------------------------------------------------------------------
  def getSipmVendorMeasurementsFromDatabase(self,tempSipmId):
    print(" -------------------------------------- ")
    self.__sipmId=tempSipmId
    print(("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase:: self.__sipmId = %s") % self.__sipmId)
    self.__getSipmValues = DataQuery(self.__queryUrl)
    self.__table = "sipm_measure_tests"
    #self.__fetchThese = "sipm_id,measure_test_date,test_type,worker_barcode,workstation_barcode,"
    #self.__fetchThese += "bias_voltage,dark_count,gain,temp_degc,breakdown_voltage,dark_count_rate,"
    #self.__fetchThese += "current_vs_voltage_condition,x_talk,led_response,data_file_location,"
    #self.__fetchThese += "data_file_name"
    self.__fetchThese = "dark_count,gain"
    self.__fetchCondition = "sipm_id:eq:"+str(self.__sipmId)+"&test_type:eq:vendor"
    self.__localSipmResult = []
    self.__localSipmResult = self.__getSipmValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    print(("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase::len(self.__localSipmResult) = %d") % len(self.__localSipmResult))
    print(("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase::self.__localSipmResult = %s") % self.__localSipmResult)
    print("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase:: exit")
##
## -------------------------------------------------------------------
  def getSipmLocalMeasurementsFromDatabase(self,tempSipmId):
    print(" -------------------------------------- ")
    self.__sipmId=tempSipmId
    print(("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase:: self.__sipmId = %s") % self.__sipmId)
    self.__getSipmValues = DataQuery(self.__queryUrl)
    self.__table = "sipm_measure_tests"
    self.__fetchThese = "sipm_id,measure_test_date,test_type,worker_barcode,workstation_barcode,"
    self.__fetchThese += "bias_voltage,dark_count,gain,temp_degc,breakdown_voltage,dark_count_rate,"
    self.__fetchThese += "current_vs_voltage_condition,x_talk,led_response,data_file_location,"
    self.__fetchThese += "data_file_name"
    self.__fetchCondition = "sipm_id:eq:"+str(self.__sipmId)+"&test_type:eq:measured"
    self.__localSipmResult = []
    self.__localSipmResult = self.__getSipmValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    print(("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase::len(self.__localSipmResult) = %d") % len(self.__localSipmResult))
    print(("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase::self.__localSipmResult = %s") % self.__localSipmResult)
    print("__SimpMeasurements__getSipmVendorMeasurementsFromDatabase:: exit")
##
## -------------------------------------------------------------------
##
##	Set up the window, and display information from the database
class packWindow(Frame):
  def __init__(self,parent=None,myRow=0,myCol=0,mySipmId='default'):
      Frame.__init__(self,parent)
      print("SipmMeasurements... packWindow")
      self.__sipmId = mySipmId
      self.__row = myRow
      self.__col = myCol
      self.__borderWidth = 2
      self.__borderStyle = 'solid'
      self.__width = int(30)
      self.__packNumber_label = myLabel(self,0,0,self.__width)
      self.__packNumber_label.setText(self.__sipmId)
      self.__packNumber_label.grid(row=0,column=0)
      self.__sipmInformation = getSipmMeasurements()
      #self.__sipmInformation.getSipmIdFromPackNumber(self.__sipmId)
      self.__sipmInformation.getSipmVendorMeasurementsFromDatabase(self.__sipmId)


