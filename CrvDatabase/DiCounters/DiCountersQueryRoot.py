# -*- coding: utf-8 -*-
##
##  File = "Diself.__eventsQueryRoot.py"
##  Derived from File = "DiCountersRootQuery.py"
##  Derived from File = "DiCountersRootQuery2017Jul14.py"
##  Derived from File = "guiDiCounters.py"
##  Derived from File = "guiDiCounters_2017July11.py"
##
##  python script to read the dicounter test information from 
##  the database and place results in root tree.
##  This version uses PyROOT... to uses it setup
##  root with PyRoot or set up the mu2e runtime enviroment.
##
##  cmj 2017Jul29.....
##  The PyROOT examples save everything in a set of lists which
##  look like one branch in the root macro file for root... The lists
##  appear as arrays in the root file (used by root... i.e.
##  >root 
##  .x rootfile.C
##  I haven't figured out how to get to the string arrays in the
##  root macro file.
##  So, I don't use the normal PyROOT examples, and I have to 
## locally change string list into character arrays to be passed onto
## the root tree!!!!  The resulting tree is like the one used by
## root macros and NOT by PyROOT!  See the root  macro file 
## "outfiles/analyzeDicounters.C" to use this root tree!
##
##  Modified by cmj2018Jun8... Change to hdbClient_v2_0
##  Modified by cmj2018Jul26... Initialize bytearry strings with each event in root tree
##  Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2018Oct11.... Change to hdbClient_v2_2
##  Modified by cmj2020Jul08... Change to cmjGuiLibGrid2019Jan30
##  Modified by cmj2020Jul09... Change crvUtilities2018 -> crvUtilities;
##  Modified by cmj2020Aug03...  cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2015Sep23
##
#!/bin/env python
##
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
##
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09 add highlight to scrolled list
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from cmjGuiLibGrid import *       ## 2020Aug03
from DiCounters import *
##  Import for PyRoot
from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH2F, TGraph, TStyle, TTree, TString, TDirectory
from ROOT import gROOT, gBenchmark, gRandom, gSystem, gStyle, Double, string, vector
from array import array
ProgramName = "DiCountersRootQuerry.py"
Version = "version2020.12.16"
##
##
## -------------------------------------------------------------
## 	A class to interogate the di-counters in the database
##	then product the root tree in the root file!
##
class askDiCounter(object):
  def __init__(self):
    self.__cmjProgramFlow = 0
    if(self.__cmjProgramFlow != 0): print("askDiCounter__init__askDiCounter... enter \n")
    self.__cmjPlotDiag = 0
    self.__database_config  = databaseConfig()
##  Set the stastitics box
    gStyle.SetOptStat("nemruoi")
##  This information is stored such that we need nested dictionaries......
##
    self.__diCounterSipmLocation = {'A1':'A1','A2':'A2','A3':'A3','A4':'A4','B1':'B1','B2':'B2','B3':'B3','B4':'B4'}
    self.__diCounterSipms = ['A1','A2','A3','A4','B1','B2','B3','B4']
    ## Dictionaries to hold the di-counter test results
    self.__diCounterId = {}	## key diCounterId+diCounterDate
    self.__diCounterTestDate = {}	## key diCounterId+diCounterDate
    self.__diCounterLightSource = {}	## key diCounterId+diCounterDate
    self.__diCounterFlashRate = {}	## key diCounterId+diCounterDate
    self.__diCounterVoltage = {}	## key diCounterId+diCounterDate
    self.__diCounterTemperature = {}	## key diCounterId+diCounterDate
    self.__diCounterLightSourceVector = {}	## key diCounterId+diCounterDate
    self.__diCounterLightSourceDistance = {}	## key diCounterId+diCounterDate
    self.__diCounterComment = {}		## key diCounterId+diCounterDate
    self.__diCounterCurrentA1 = {}; self.__diCounterCurrentA2 = {};	## key diCounterId+diCounterDate 
    self.__diCounterCurrentA3 = {}; self.__diCounterCurrentA4 = {};	## key diCounterId+diCounterDate
    self.__diCounterCurrentB1 = {}; self.__diCounterCurrentB2 = {};	## key diCounterId+diCounterDate 
    self.__diCounterCurrentB3 = {}; self.__diCounterCurrentB4 = {};	## key diCounterId+diCounterDate
    self.__diCounterCurrentS1 = {}; self.__diCounterCurrentS2 = {};	## key diCounterId+diCounterDate 
    self.__diCounterCurrentS3 = {}; self.__diCounterCurrentS4 = {};	## key diCounterId+diCounterDate
    self.__diCounterDarkCurrentA1 = {}; self.__diCounterDarkCurrentA2 = {};	## key diCounterId+diCounterDate 
    self.__diCounterDarkCurrentA3 = {}; self.__diCounterDarkCurrentA4 = {};	## key diCounterId+diCounterDate
    self.__diCounterDarkCurrentB1 = {}; self.__diCounterDarkCurrentB2 = {};	## key diCounterId+diCounterDate 
    self.__diCounterDarkCurrentB3 = {}; self.__diCounterDarkCurrentB4 = {};	## key diCounterId+diCounterDate
    self.__diCounterDarkCurrentS1 = {}; self.__diCounterDarkCurrentS2 = {};	## key diCounterId+diCounterDate 
    self.__diCounterDarkCurrentS3 = {}; self.__diCounterDarkCurrentS4 = {};	## key diCounterId+diCounterDate
##  for the root tree...
    ## arrays needed to build root tree....
    self.__signalDiCounterId = {}
    self.__signalTestDate = {}
    self.__signalFlashRate = {}
    self.__signalPosition = {}
    self.__signalTemperature = {}
    self.__signalVoltage = {}
    self.__signalLightSource = {}
    self.__currentA1 = {}; self.__currentA2 = {}; self.__currentA3 = {}; self.__currentA4 = {}
    self.__currentB1 = {}; self.__currentB2 = {}; self.__currentB3 = {}; self.__currentB4 = {}
    self.__numberOfDark = 0
##
    self.__darkCurrentId = {}
    self.__darkCurrentTestDate = {}
    self.__darkCurrentTemperature = {}   
    self.__darkCurrentVoltage = {}
    self.__darkCurrentA1 = {}; self.__darkCurrentA2 = {}; self.__darkCurrentA3 = {}; self.__darkCurrentA4 = {}
    self.__darkCurrentB1 = {}; self.__darkCurrentB2 = {}; self.__darkCurrentB3 = {}; self.__darkCurrentB4 = {}
## -------------------------------------------------------------
  def __del__(self):
    if(self.__cmjProgramFlow != 0) : print("askDiCounter__del__askDiCounter... enter \n") 
## -------------------------------------------------------------
  def turnOnDebug(self,temp):
    self.__cmjPlotDiag = temp
    self.__cmjProgramFlow = temp
    print("__askDiCounter__turnOnDebug... cmjPlotDiag debug level =  %s \n") % (self.__cmjPlotDiag)
    print("__askDiCounter__turnOnDebug... cmjProgramFlow debug level =  %s \n") % (self.__cmjProgramFlow)
## -------------------------------------------------------------
##	Make queries to data base
##	Set up queries to the development database
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Composite Tables"
    self.__whichDatabase = 'development'
    if(self.__cmjPlotDiag != 0): print("__askDicounter__getFromDevelopmentDatabase... get to development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
    if(self.__cmjPlotDiag > 2) : 
      print("__askDiCounter__getFromDevelopmentDatabase... self.__database = %s \n") % (self.__database)
      print("__askDiCounter__getFromDevelopmentDatabase... self._queryUrl = %s \n") %(self.__queryUrl)
## -------------------------------------------------------------
##	Make queries to the database
##	Setup queries to the production database
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Composite Tables"
    self.__whichDatabase = 'production'
    if(self.__cmjPlotDiag != 0): print("__askDicounter__getFromProductionDatabase... get to production database \n")
    self.__queryUrl = self.__database_config.getProductionQueryUrl()
    if(self.__cmjPlotDiag > 2) : 
      print("__askDiCounter__getFromProductionDatabase... self.__database = %s \n") % (self.__database)
      print("__askDicounter__getFromProductionDatabase... self._queryUrl = %s \n") %(self.__queryUrl)
## -------------------------------------------------------------
##  Ask the database for the di-counter information here!
  def loadDiCounterRequest(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__loadDiCounterRequest... enter \n")
    self.__tempResults = self.getDiCounterFromDatabase()
    self.loadDiCounterInformation(self.__tempResults)
## -------------------------------------------------------------
  def getDiCounterFromDatabase(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__getDiCounterFromDatabase... enter \n")
    self.__getDiCounterValues = DataQuery(self.__queryUrl)
    self.__diCounterResults = []
    self.__table = "di_counter_tests"
    self.__fetchThese = "di_counter_id,test_date,sipm_location,current_amps,light_source,flash_rate_hz,temperature,distance,distance_vector,sipm_test_voltage,comments"
    self.__fetchCondition = "test_date:gt:2017-01-01"
    self.__numberReturned = 0
    if(self.__cmjPlotDiag > 0):
      print (".... getSipmsBatchesFromDatabase: self.__queryUrl   = %s \n") % (self.__queryUrl)
      print (".... getSipmsBatchesFromDatabase: self.__table                = %s \n") % (self.__table)
      print (".... getSipmsBatchesFromDatabase: self.__fetchThese           = %s \n") % (self.__fetchThese)
    self.__diCounterResults = self.__getDiCounterValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjPlotDiag > 4): print ("__askDicounter__getDiCounterFromDatabase... self.__diCounterResults = %s \n") % (self.__diCounterResults)
    if(self.__cmjPlotDiag > 5):
      for self.__l in self.__diCounterResults:
	print self.__l
    return self.__diCounterResults  
## -------------------------------------------------------------
  def loadDiCounterInformation(self,tempResults):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__getDiCounterFromDatabase... enter \n")
    for self.__tempLine in tempResults:
      self.__item = []
      self.__item = self.__tempLine.rsplit(",")
      if(len(self.__tempLine) < 1) : continue  ## reject empty lines....
      self.__Id = self.__item[0]
      self.__Date = self.__item[1]
      self.__SipmPosition = self.__item[2]
      self.__LightSource = self.__item[4]
      self.__FlashRate = self.__item[5]
      self.__Temperature = self.__item[6]
      self.__LightDistance = self.__item[7]
      self.__LightPosition = self.__item[8]
      self.__SipmVoltage = self.__item[9]
      self.__DiCounterTestComment = self.__item[10]
      ## setup key with di-counter-id and test date
      ## These are the same for all 8 dicounter position measurements... take the last one
      self.__localKey = self.__Id+'-'+self.__Date.replace(" ","-")
      self.__diCounterId[self.__localKey] = self.__Id
      self.__diCounterTestDate[self.__localKey] = self.__Date
      self.__diCounterLightSource[self.__localKey] = self.__LightSource
      self.__diCounterFlashRate[self.__localKey] = self.__FlashRate
      self.__diCounterVoltage[self.__localKey] = self.__SipmVoltage
      self.__diCounterTemperature[self.__localKey] = self.__Temperature
      if(not self.__LightDistance) :  ## null string
	self.__diCounterLightSourceDistance[self.__localKey] = -9999.99
      else:
	self.__diCounterLightSourceDistance[self.__localKey] = float(self.__LightDistance)
      if(not self.__LightPosition):  ##  null string
	self.__diCounterLightSourceVector[self.__localKey] = 'None Given'
      else:
	self.__diCounterLightSourceVector[self.__localKey] = self.__LightPosition
      if(not self.__DiCounterTestComment):  ## null stringa
	self.__diCounterComment[self.__localKey] = 'None Given'
      else:
	self.__diCounterComment[self.__localKey] = self.__DiCounterTestComment
      ## for convienince sort current values according to positon on the di-counter!
      #if(self.__LightSource == 'rad' or self.__LightSource == '1mCi Cs^137' or self.__LightSource == 'led' or self.__LightSource == 'cos'):
      if(self.__LightSource != 'dark'):
	if(self.__SipmPosition == 'a1') : self.__diCounterCurrentA1[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'a2') : self.__diCounterCurrentA2[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'a3') : self.__diCounterCurrentA3[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'a4') : self.__diCounterCurrentA4[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b1') : self.__diCounterCurrentB1[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b2') : self.__diCounterCurrentB2[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b3') : self.__diCounterCurrentB3[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b4') : self.__diCounterCurrentB4[self.__localKey] = float(self.__item[3])
	  
      if(self.__LightSource == 'dark'):
	if(self.__SipmPosition == 'a1') : self.__diCounterDarkCurrentA1[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'a2') : self.__diCounterDarkCurrentA2[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'a3') : self.__diCounterDarkCurrentA3[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'a4') : self.__diCounterDarkCurrentA4[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b1') : self.__diCounterDarkCurrentB1[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b2') : self.__diCounterDarkCurrentB2[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b3') : self.__diCounterDarkCurrentB3[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 'b4') : self.__diCounterDarkCurrentB4[self.__localKey] = float(self.__item[3])
      if(self.__LightSource == 'crystal_rad'):
	if(self.__SipmPosition == "s1") : self.__diCounterCurrentS1[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == "s2") : self.__diCounterCurrentS2[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == "s3") : self.__diCounterCurrentS3[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == "s4") : self.__diCounterCurrentS4[self.__localKey] = float(self.__item[3])
      if(self.__LightSource == 'crystal_dark'):
	if(self.__SipmPosition == 's1') : self.__diCounterDarkCurrentS1[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 's2') : self.__diCounterDarkCurrentS2[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 's3') : self.__diCounterDarkCurrentS3[self.__localKey] = float(self.__item[3])
	if(self.__SipmPosition == 's4') : self.__diCounterDarkCurrentS4[self.__localKey] = float(self.__item[3])
    
  
## -------------------------------------------------------------
  def getScatterPlots(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__getScatterPlots... enter \n")
    self.plotScatterPlots(self)
## -------------------------------------------------------------
  def getHistograms(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__getHistograms... enter \n")
    self.bookHistograms()     
    self.fillHistograms(self.__diCounterResults)
    self.drawCanvas()
    self.defineTree()
## -------------------------------------------------------------
  def plotScatterPlots(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__plotScatterPlots... enter \n")
## -------------------------------------------------------------
  def bookHistograms(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__bookHistograms... enter \n")
    self.__nBins = 100; self.__lowBin = 0.0; self.__hiBin = 2.0e4
    ##  All Signal Sources
    self.__allSourceCurrentColor = 9
    self.__hSipmA1 = TH1F("self.__hSipmA1","All Sipm Current A1",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmA1.SetFillColor(self.__allSourceCurrentColor)
    self.__hSipmA2 = TH1F("self.__hSipmA2","All Sipm Current A2",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmA2.SetFillColor(self.__allSourceCurrentColor)
    self.__hSipmA3 = TH1F("self.__hSipmA3","All Sipm Current A3",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmA3.SetFillColor(self.__allSourceCurrentColor)
    self.__hSipmA4 = TH1F("self.__hSipmA4","All Sipm Current A4",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmA4.SetFillColor(self.__allSourceCurrentColor)
    self.__hSipmB1 = TH1F("self.__hSipmB1","All Sipm Current B1",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmB1.SetFillColor(self.__allSourceCurrentColor)
    self.__hSipmB2 = TH1F("self.__hSipmB2","All Sipm Current B2",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmB2.SetFillColor(self.__allSourceCurrentColor)
    self.__hSipmB3 = TH1F("self.__hSipmB3","All Sipm Current B3",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmB3.SetFillColor(self.__allSourceCurrentColor)
    self.__hSipmB4 = TH1F("self.__hSipmB4","All Sipm Current B4",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmB4.SetFillColor(self.__allSourceCurrentColor)
    ##  Led Signal 
    self.__nBins = 100; self.__lowBin = 0.0; self.__hiBin = 20000.0;
    self.__ledCurrentColor = 2
    self.__hSipmLedA1 = TH1F("self.__hSipmLedA1","Sipm Current A1, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedA1.SetFillColor(self.__ledCurrentColor)
    self.__hSipmLedA2 = TH1F("self.__hSipmLedA2","Sipm Current A2, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedA2.SetFillColor(self.__ledCurrentColor)
    self.__hSipmLedA3 = TH1F("self.__hSipmLedA3","Sipm Current A3, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedA3.SetFillColor(self.__ledCurrentColor)
    self.__hSipmLedA4 = TH1F("self.__hSipmLedA4","Sipm Current A4, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedA4.SetFillColor(self.__ledCurrentColor)
    self.__hSipmLedB1 = TH1F("self.__hSipmLedB1","Sipm Current B1, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedB1.SetFillColor(self.__ledCurrentColor)
    self.__hSipmLedB2 = TH1F("self.__hSipmLedB2","Sipm Current B2, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedB2.SetFillColor(self.__ledCurrentColor)
    self.__hSipmLedB3 = TH1F("self.__hSipmLedB3","Sipm Current B3, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedB3.SetFillColor(self.__ledCurrentColor)
    self.__hSipmLedB4 = TH1F("self.__hSipmLedB4","Sipm Current B4, LED",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmLedB4.SetFillColor(self.__ledCurrentColor)
    ##  Source Signal 
    self.__nBins = 100; self.__lowBin = 0.0; self.__hiBin = 2.0;  ## first data... UVa may switch to counts instead.
    self.__ledSourceColor = 3
    self.__hSipmSourceA1 = TH1F("self.__hSipmSourceA1","Sipm Current A1, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceA1.SetFillColor(self.__ledSourceColor)
    self.__hSipmSourceA2 = TH1F("self.__hSipmSourceA2","Sipm Current A2, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceA2.SetFillColor(self.__ledSourceColor)
    self.__hSipmSourceA3 = TH1F("self.__hSipmSourceA3","Sipm Current A3, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceA3.SetFillColor(self.__ledSourceColor)
    self.__hSipmSourceA4 = TH1F("self.__hSipmSourceA4","Sipm Current A4, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceA4.SetFillColor(self.__ledSourceColor)
    self.__hSipmSourceB1 = TH1F("self.__hSipmSourceB1","Sipm Current B1, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceB1.SetFillColor(self.__ledSourceColor)
    self.__hSipmSourceB2 = TH1F("self.__hSipmSourceB2","Sipm Current B2, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceB2.SetFillColor(self.__ledSourceColor)
    self.__hSipmSourceB3 = TH1F("self.__hSipmSourceB3","Sipm Current B3, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceB3.SetFillColor(self.__ledSourceColor)
    self.__hSipmSourceB4 = TH1F("self.__hSipmSourceB4","Sipm Current B4, Radioactive Source",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmSourceB4.SetFillColor(self.__ledSourceColor)
    ##  Cosmic Signal 
    self.__nBins = 100; self.__lowBin = 0.0; self.__hiBin = 2.0e4;
    self.__cosmicSourceColor = 6
    self.__hSipmCosmicA1 = TH1F("self.__hSipmCosmicA1","Sipm Current A1, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicA1.SetFillColor(self.__cosmicSourceColor)
    self.__hSipmCosmicA2 = TH1F("self.__hSipmCosmicA2","Sipm Current A2, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicA2.SetFillColor(self.__cosmicSourceColor)
    self.__hSipmCosmicA3 = TH1F("self.__hSipmCosmicA3","Sipm Current A3, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicA3.SetFillColor(self.__cosmicSourceColor)
    self.__hSipmCosmicA4 = TH1F("self.__hSipmCosmicA4","Sipm Current A4, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicA4.SetFillColor(self.__cosmicSourceColor)
    self.__hSipmCosmicB1 = TH1F("self.__hSipmCosmicB1","Sipm Current B1, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicB1.SetFillColor(self.__cosmicSourceColor)
    self.__hSipmCosmicB2 = TH1F("self.__hSipmCosmicB2","Sipm Current B2, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicB2.SetFillColor(self.__cosmicSourceColor)
    self.__hSipmCosmicB3 = TH1F("self.__hSipmCosmicB3","Sipm Current B3, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicB3.SetFillColor(self.__cosmicSourceColor)
    self.__hSipmCosmicB4 = TH1F("self.__hSipmCosmicB4","Sipm Current B4, Cosmic Rays",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmCosmicB4.SetFillColor(self.__cosmicSourceColor)
    ## Dark current... all sources
    self.__nBins = 100; self.__lowBin = 0.0; self.__hiBin = 2.0;
    self.__darkSourceColor = 1
    self.__hSipmDarkA1 = TH1F("self.__hSipmDarkA1","Sipm Dark Current A1",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkA1.SetFillColor(self.__darkSourceColor)
    self.__hSipmDarkA2 = TH1F("self.__hSipmDarkA2","Sipm Dark Current A2",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkA2.SetFillColor(self.__darkSourceColor)
    self.__hSipmDarkA3 = TH1F("self.__hSipmDarkA3","Sipm Dark Current A3",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkA3.SetFillColor(self.__darkSourceColor)
    self.__hSipmDarkA4 = TH1F("self.__hSipmDarkA4","Sipm Dark Current A4",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkA4.SetFillColor(self.__darkSourceColor)
    self.__hSipmDarkB1 = TH1F("self.__hSipmDarkB1","Sipm Dark Current B1",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkB1.SetFillColor(self.__darkSourceColor)
    self.__hSipmDarkB2 = TH1F("self.__hSipmDarkB2","Sipm Dark Current B2",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkB2.SetFillColor(self.__darkSourceColor)
    self.__hSipmDarkB3 = TH1F("self.__hSipmDarkB3","Sipm Dark Current B3",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkB3.SetFillColor(self.__darkSourceColor)
    self.__hSipmDarkB4 = TH1F("self.__hSipmDarkB4","Sipm Dark Current B4",self.__nBins,self.__lowBin,self.__hiBin)
    self.__hSipmDarkB4.SetFillColor(self.__darkSourceColor)

## -------------------------------------------------------------
  def fillHistograms(self,tempResults):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__fillHistograms... enter \n")
    self.__numberOfSignal  = 0
    self.__numberOfDark = 0
    for self.__event in self.__diCounterId.keys():
      self.__localLightSource = self.__diCounterLightSource[self.__event]
      if(self.__localLightSource ==  'rad' or self.__localLightSource == 'led' or self.__localLightSource == 'cos'):
	try:
	  self.__hSipmA1.Fill(float(self.__diCounterCurrentA1[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentA1[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmA2.Fill(float(self.__diCounterCurrentA2[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentA2[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmA3.Fill(float(self.__diCounterCurrentA3[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentA3[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmA4.Fill(float(self.__diCounterCurrentA4[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentA4[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmB1.Fill(float(self.__diCounterCurrentB1[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentB1[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmB2.Fill(float(self.__diCounterCurrentB2[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentB2[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmB3.Fill(float(self.__diCounterCurrentB3[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentB3[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmB4.Fill(float(self.__diCounterCurrentB4[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterCurrentB4[%s] is MISSING!") % self.__event
      if(self.__localLightSource == 'dark'):
	try:
	  self.__hSipmDarkA1.Fill(float(self.__diCounterDarkCurrentA1[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentA1[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmDarkA2.Fill(float(self.__diCounterDarkCurrentA2[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentA2[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmDarkA3.Fill(float(self.__diCounterDarkCurrentA3[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentA3[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmDarkA4.Fill(float(self.__diCounterDarkCurrentA4[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentA4[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmDarkB1.Fill(float(self.__diCounterDarkCurrentB1[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentB1[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmDarkB2.Fill(float(self.__diCounterDarkCurrentB2[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentB2[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmDarkB3.Fill(float(self.__diCounterDarkCurrentB3[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentB3[%s] is MISSING!") % self.__event
	try:
	  self.__hSipmDarkB4.Fill(float(self.__diCounterDarkCurrentB4[self.__event]))
	except:
	  print("__askDicounter__fillHistograms... diCounterDarkCurrentB4[%s] is MISSING!") % self.__event
	## the lists have been tested and warnings issued!
      if(self.__localLightSource ==  'led'):
	try: self.__hSipmLedA1.Fill(float(self.__diCounterCurrentA1[self.__event]))
	except: continue
	try: self.__hSipmLedA2.Fill(float(self.__diCounterCurrentA2[self.__event]))
	except: continue
	try: self.__hSipmLedA3.Fill(float(self.__diCounterCurrentA3[self.__event]))
	except: continue
	try: self.__hSipmLedA4.Fill(float(self.__diCounterCurrentA4[self.__event]))
	except: continue
	try: self.__hSipmLedB1.Fill(float(self.__diCounterCurrentB1[self.__event]))
	except: continue
	try: self.__hSipmLedB2.Fill(float(self.__diCounterCurrentB2[self.__event]))
	except: continue
	try: self.__hSipmLedB3.Fill(float(self.__diCounterCurrentB3[self.__event]))
	except: continue
	try: self.__hSipmLedB4.Fill(float(self.__diCounterCurrentB4[self.__event]))
	except: continue
      if(self.__localLightSource ==  'rad'):
	try: self.__hSipmSourceA1.Fill(float(self.__diCounterCurrentA1[self.__event]))
	except: continue
	try: self.__hSipmSourceA2.Fill(float(self.__diCounterCurrentA2[self.__event]))
	except: continue
	try: self.__hSipmSourceA3.Fill(float(self.__diCounterCurrentA3[self.__event]))
	except: continue
	try: self.__hSipmSourceA4.Fill(float(self.__diCounterCurrentA4[self.__event]))
	except: continue
	try: self.__hSipmSourceB1.Fill(float(self.__diCounterCurrentB1[self.__event]))
	except: continue
	try: self.__hSipmSourceB2.Fill(float(self.__diCounterCurrentB2[self.__event]))
	except: continue
	try: self.__hSipmSourceB3.Fill(float(self.__diCounterCurrentB3[self.__event]))
	except: continue
	try: self.__hSipmSourceB4.Fill(float(self.__diCounterCurrentB4[self.__event]))
	except: continue
      if(self.__localLightSource ==  'source'):
	try: self.__hSipmCosmicA1.Fill(float(self.__diCounterCurrentA1[self.__event]))
	except: continue
	try: self.__hSipmCosmicA2.Fill(float(self.__diCounterCurrentA2[self.__event]))
	except: continue
	try: self.__hSipmCosmicA3.Fill(float(self.__diCounterCurrentA3[self.__event]))
	except: continue
	try: self.__hSipmCosmicA4.Fill(float(self.__diCounterCurrentA4[self.__event]))
	except: continue
	try: self.__hSipmCosmicB1.Fill(float(self.__diCounterCurrentB1[self.__event]))
	except: continue
	try: self.__hSipmCosmicB2.Fill(float(self.__diCounterCurrentB2[self.__event]))
	except: continue
	try: self.__hSipmCosmicB3.Fill(float(self.__diCounterCurrentB3[self.__event]))
	except: continue
	try: self.__hSipmCosmicB4.Fill(float(self.__diCounterCurrentB4[self.__event]))
	except: continue


## -------------------------------------------------------------
  def drawCanvas(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__drawCanvas... enter \n")
    self.__cX = 200
    self.__cY = 10
    self.__cWidth = 700	## canvas width
    self.__cHeight = 500	## canvas height
    self.__delX = 20
    self.__delY = 20
    self.__windowTitle = "DiCounter Sipm Current - All Sources"
    self.__c1 = TCanvas('self.__c1',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c1.Divide(4,2)  ## split canvas into pads....
    self.__c1.cd(1)
    self.__hSipmA1.Draw()
    self.__c1.cd(2)
    self.__hSipmA2.Draw()
    self.__c1.cd(3)
    self.__hSipmA3.Draw()
    self.__c1.cd(4)
    self.__hSipmA4.Draw()
    self.__c1.cd(5)
    self.__hSipmB1.Draw()
    self.__c1.cd(6)
    self.__hSipmB2.Draw()
    self.__c1.cd(7)
    self.__hSipmB3.Draw()
    self.__c1.cd(8)
    self.__hSipmB4.Draw()
    
    #  Plot the LED histograms
    self.__cX += self.__delX; self.__cY += self.__delY
    self.__windowTitle = "DiCounter Sipm Current - LED"
    self.__c3 = TCanvas('self.__c3',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c3.Divide(4,2)  ## split canvas into pads....
    self.__c3.cd(1)
    self.__hSipmLedA1.Draw()
    self.__c3.cd(2)
    self.__hSipmLedA2.Draw()
    self.__c3.cd(3)
    self.__hSipmLedA3.Draw()
    self.__c3.cd(4)
    self.__hSipmLedA4.Draw()
    self.__c3.cd(5)
    self.__hSipmLedB1.Draw()
    self.__c3.cd(6)
    self.__hSipmLedB2.Draw()
    self.__c3.cd(7)
    self.__hSipmLedB3.Draw()
    self.__c3.cd(8)
    self.__hSipmLedB4.Draw()

    #  Plot the Source histograms
    self.__cX += self.__delX; self.__cY += self.__delY
    self.__windowTitle = "DiCounter Sipm Current - Radioactive Source"
    self.__c4 = TCanvas('self.__c4',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c4.Divide(4,2)  ## split canvas into pads....
    self.__c4.cd(1)
    self.__hSipmSourceA1.Draw()
    self.__c4.cd(2)
    self.__hSipmSourceA2.Draw()
    self.__c4.cd(3)
    self.__hSipmSourceA3.Draw()
    self.__c4.cd(4)
    self.__hSipmSourceA4.Draw()
    self.__c4.cd(5)
    self.__hSipmSourceB1.Draw()
    self.__c4.cd(6)
    self.__hSipmSourceB2.Draw()
    self.__c4.cd(7)
    self.__hSipmSourceB3.Draw()
    self.__c4.cd(8)
    self.__hSipmSourceB4.Draw()

    #  Plot the Cosmic histograms
    self.__cX += self.__delX; self.__cY += self.__delY
    self.__windowTitle = "DiCounter Sipm Current - Cosmic Rays"
    self.__c5 = TCanvas('self.__c5',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c5.Divide(4,2)  ## split canvas into pads....
    self.__c5.cd(1)
    self.__hSipmCosmicA1.Draw()
    self.__c5.cd(2)
    self.__hSipmCosmicA2.Draw()
    self.__c5.cd(3)
    self.__hSipmCosmicA3.Draw()
    self.__c5.cd(4)
    self.__hSipmCosmicA4.Draw()
    self.__c5.cd(5)
    self.__hSipmCosmicB1.Draw()
    self.__c5.cd(6)
    self.__hSipmCosmicB2.Draw()
    self.__c5.cd(7)
    self.__hSipmCosmicB3.Draw()
    self.__c5.cd(8)
    self.__hSipmCosmicB4.Draw()


    #
    self.__cX += self.__delX
    self.__cY += self.__delY
    self.__windowTitle = "DiCounter Sipm Dark Current"
    self.__c2 = TCanvas('self.__c2',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c2.Divide(4,2)  ## split canvas into pads....
    self.__c2.cd(1)
    self.__hSipmDarkA1.Draw()
    self.__c2.cd(2)
    self.__hSipmDarkA2.Draw()
    self.__c2.cd(3)
    self.__hSipmDarkA3.Draw()
    self.__c2.cd(4)
    self.__hSipmDarkA4.Draw()
    self.__c2.cd(5)
    self.__hSipmDarkB1.Draw()
    self.__c2.cd(6)
    self.__hSipmDarkB2.Draw()
    self.__c2.cd(7)
    self.__hSipmDarkB3.Draw()
    self.__c2.cd(8)
    self.__hSipmDarkB4.Draw()
    ## save graphics
    print("save graphics \n")
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveGraphicsTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outputGraphicsDirectory = "outputFiles/graphics/"
    self.__c1.SaveAs(self.__outputGraphicsDirectory+"signal_"+self.__saveGraphicsTime+".png")
    self.__c2.SaveAs(self.__outputGraphicsDirectory+"darkCurrent"+self.__saveGraphicsTime+".png")

## -------------------------------------------------------------
##	This method defines the root tree and
##	the file that it is saved on.
##  The root tree has two directories... one for the signal and 
##  one for the dark current readings...  The tree contains information
##  to allow the user to select sides that the source was positioned
##  di-counter id and the test dates.
##
  def defineTree(self):
    if(self.__cmjProgramFlow != 0): print("__askDicounter__defineTree... enter \n")
    ## Define the root tree output file
    self.__treeTime = myTime()
    self.__treeTime.getComputerTime()
    self.__saveTreeTime = self.__treeTime.getTimeForSavedFiles()
    self.__outRootTreeFileName = "outputFiles/DiCounters"+self.__saveTreeTime+".root"
    self.__rootTreeFile = TFile(self.__outRootTreeFileName,'RECREATE')
    ## place the signal in one directory
    
    #self.__rootTreeFile.mkdir('DiCounterSignal')
    #self.__rootTreeFile.cd('DiCounterSignal')
    self.__localRootTree1 = TTree('diCounterTests','root tree with ntuples')
    ## define arrays for the signal...
    if(self.__cmjPlotDiag > 2): print("__askDicounter__defineTree... define arrays \n")
    self.__tempDiCounterId = bytearray(30)  ## the di-counter Id
    self.__tempTestDate = bytearray(30)
    self.__tempLightSource=bytearray(30)
    self.__tempFlashRate = bytearray(30)
    self.__tempLightSourceSide = bytearray(30)
    self.__tempComment = bytearray(120)
    self.__arrayCurrentA1 = array('f',[0])
    self.__arrayCurrentA2 = array('f',[0])
    self.__arrayCurrentA3 = array('f',[0])
    self.__arrayCurrentA4 = array('f',[0])
    self.__arrayCurrentB1 = array('f',[0])
    self.__arrayCurrentB2 = array('f',[0])
    self.__arrayCurrentB3 = array('f',[0])
    self.__arrayCurrentB4 = array('f',[0])
    self.__arraySignalTemperature = array('f',[0])
    self.__arraySignalPosition = array('f',[0])
    self.__arraySignalVoltage = array('f',[0])
    ## define branches....  for the signal
    if(self.__cmjPlotDiag > 2): print("__askDicounter__defineTree... define branches \n")
    self.__localRootTree1.Branch('diCounterId',self.__tempDiCounterId,'self.__tempDiCounterId[30]/C')
    self.__localRootTree1.Branch('testDate',self.__tempTestDate,'self.__tempTestDate[30]/C')
    self.__localRootTree1.Branch('lightSource',self.__tempLightSource,'self.__tempLightSource[30]/C')
    self.__localRootTree1.Branch('flashRate',self.__tempFlashRate,'self.__tempFlashRate[30]/C')
    self.__localRootTree1.Branch('lightSourceSide',self.__tempLightSourceSide,'self.__tempLightSourceSide[30]/C')
    self.__localRootTree1.Branch('comment',self.__tempComment,'self.__comment[120]/C')
    self.__localRootTree1.Branch('currentA1',self.__arrayCurrentA1,'self.__arrayCurrentA1[1]/F')
    self.__localRootTree1.Branch('currentA2',self.__arrayCurrentA2,'self.__arrayCurrentA2[1]/F')
    self.__localRootTree1.Branch('currentA3',self.__arrayCurrentA3,'self.__arrayCurrentA3[1]/F')
    self.__localRootTree1.Branch('currentA4',self.__arrayCurrentA4,'self.__arrayCurrentA4[1]/F')
    self.__localRootTree1.Branch('currentB1',self.__arrayCurrentB1,'self.__arrayCurrentB1[1]/F')
    self.__localRootTree1.Branch('currentB2',self.__arrayCurrentB2,'self.__arrayCurrentB2[1]/F')
    self.__localRootTree1.Branch('currentB3',self.__arrayCurrentB3,'self.__arrayCurrentB3[1]/F')
    self.__localRootTree1.Branch('currentB4',self.__arrayCurrentB4,'self.__arrayCurrentB4[1]/F')
    self.__localRootTree1.Branch('temperature',self.__arraySignalTemperature,'self.__arraySignalTemperature[1]/F')
    self.__localRootTree1.Branch('light_source_position',self.__arraySignalPosition,'self.__arraySignalPosition[1]/F')
    self.__localRootTree1.Branch('sipmVoltage',self.__arraySignalVoltage,'self.__arraySignalVoltage[1]/F')
    for self.__event in self.__diCounterId.keys():
      self.__LightSource = self.__diCounterLightSource[self.__event]
      #if(self.__LightSource == 'rad' or self.__LightSource == 'led' or self.__LightSource == 'cos'):
      if(self.__LightSource == 'rad' or self.__LightSource == "cos"):
	try: 
	  self.__arrayCurrentA1[0] = self.__diCounterCurrentA1[self.__event]
	except: 
	  self.__arrayCurrentA1[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA2[0] = self.__diCounterCurrentA2[self.__event]
	except: 
	  self.__arrayCurrentA2[0] = float(-9999.99)
	try:
	  self.__arrayCurrentA3[0] = self.__diCounterCurrentA3[self.__event]
	except:
	  self.__arrayCurrentA3[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA4[0] = self.__diCounterCurrentA4[self.__event]
	except: 
	  self.__arrayCurrentA4[0] = float(-9999.99)
	try:
	  self.__arrayCurrentB1[0] = self.__diCounterCurrentB1[self.__event]
	except:
	  self.__arrayCurrentB1[0] = float(-9999.99)
	try:
	  self.__arrayCurrentB2[0] = self.__diCounterCurrentB2[self.__event]
	except: 
	  self.__arrayCurrentB2[0] = float(-9999.99)
	try:
	  self.__arrayCurrentB3[0] = self.__diCounterCurrentB3[self.__event]
	except: 
	  self.__arrayCurrentB3[0] = float(-9999.99)
	try:
	  self.__arrayCurrentB4[0] = self.__diCounterCurrentB4[self.__event]
	except: 
	  self.__arrayCurrentB4[0] = float(-9999.99)

      if(self.__LightSource == 'crystal_rad'):
	try: 
	  self.__arrayCurrentA1[0] = self.__diCounterCurrentS1[self.__event]
	except: 
	  self.__arrayCurrentA1[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA2[0] = self.__diCounterCurrentS2[self.__event]
	except: 
	  self.__arrayCurrentA2[0] = float(-9999.99)
	try:
	  self.__arrayCurrentA3[0] = self.__diCounterCurrentS3[self.__event]
	except:
	  self.__arrayCurrentA3[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA4[0] = self.__diCounterCurrentS4[self.__event]
	except: 
	  self.__arrayCurrentA4[0] = float(-9999.99)
	self.__arrayCurrentB1[0] = float(-9999.99) 
	self.__arrayCurrentB2[0] = float(-9999.99) 
	self.__arrayCurrentB3[0] = float(-9999.99)
	self.__arrayCurrentB4[0] = float(-9999.99)

      if(self.__LightSource == 'dark'):
	try:
	  self.__arrayCurrentA1[0] = self.__diCounterDarkCurrentA1[self.__event]
	except:
	  self.__arrayCurrentA1[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA2[0] = self.__diCounterDarkCurrentA2[self.__event]
	except:
	  self.__arrayCurrentA2[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA3[0] = self.__diCounterDarkCurrentA3[self.__event]
	except:
	  self.__arrayCurrentA3[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA4[0] = self.__diCounterDarkCurrentA4[self.__event]
	except:
	  self.__arrayCurrentA4[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentB1[0] = self.__diCounterDarkCurrentB1[self.__event]
	except:
	  self.__arrayCurrentB1[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentB2[0] = self.__diCounterDarkCurrentB2[self.__event]
	except:
	  self.__arrayCurrentB2[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentB3[0] = self.__diCounterDarkCurrentB3[self.__event]
	except:
	  self.__arrayCurrentB3[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentB4[0] = self.__diCounterDarkCurrentB4[self.__event]
	except:
	  self.__arrayCurrentB4[0] = float(-9999.99)

      if(self.__LightSource == 'crystal_dark'):
	try:
	  self.__arrayCurrentA1[0] = self.__diCounterDarkCurrentS1[self.__event]
	except:
	  self.__arrayCurrentA1[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA2[0] = self.__diCounterDarkCurrentS2[self.__event]
	except:
	  self.__arrayCurrentA2[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA3[0] = self.__diCounterDarkCurrentS3[self.__event]
	except:
	  self.__arrayCurrentA3[0] = float(-9999.99)
	try: 
	  self.__arrayCurrentA4[0] = self.__diCounterDarkCurrentS4[self.__event]
	except:
	  self.__arrayCurrentA4[0] = float(-9999.99)
	self.__arrayCurrentB1[0] = float(-9999.99)
	self.__arrayCurrentB2[0] = float(-9999.99)
	self.__arrayCurrentB3[0] = float(-9999.99)
	self.__arrayCurrentB4[0] = float(-9999.99)


      #
      self.__arraySignalTemperature[0] = float(self.__diCounterTemperature[self.__event])
      self.__arraySignalPosition[0] = self.__diCounterLightSourceDistance[self.__event]
      self.__arraySignalVoltage[0] = float(self.__diCounterVoltage[self.__event])
      if(self.__cmjPlotDiag > 2): print("self.__arrayCurrentA1[%s] = %s, %s, %s, %s, %s, %s, %s, %s ") % (self.__event,self.__arrayCurrentA1[0],self.__arrayCurrentA2[0],self.__arrayCurrentA3[0],self.__arrayCurrentA4[0],self.__arrayCurrentB1[0],self.__arrayCurrentB2[0],self.__arrayCurrentB3[0],self.__arrayCurrentB4[0])
##	There has to be a better way to do this...
##	But amaziningly, there is now easy way to take a 
##	string and convert it into a character!...
##	And the Root trees need a character array to 
##	be read by a root macro later!
      ## first initialize the arrays:
      for n in range(0,29):
	self.__tempDiCounterId[n] = 0
	self.__tempTestDate[n] = 0
	self.__tempLightSource[n] = 0
	self.__tempFlashRate[n] = 0
	self.__tempLightSourceSide[n] =0
      for n in range(0,119):
	self.__tempComment[n] = 0
      m = 0
      for self.__character in self.__diCounterId[self.__event]:
	self.__tempDiCounterId[m] = self.__character
	m += 1
      m = 0
      for self.__character in self.__diCounterTestDate[self.__event]:
	self.__tempTestDate[m] = self.__character
	m += 1
      m = 0
      for self.__character in self.__diCounterFlashRate[self.__event]:
	self.__tempFlashRate[m] = self.__character
	m += 1
      m = 0
      for self.__character in self.__diCounterLightSource[self.__event]:
	self.__tempLightSource[m] = self.__character
	m += 1
      m = 0
      for self.__character in self.__diCounterLightSourceVector[self.__event]:
	self.__tempLightSourceSide[m] = self.__character
	m += 1
      m = 0
      for self.__character in self.__diCounterComment[self.__event]:
	self.__tempComment[m] = self.__character
	m += 1
      self.__localRootTree1.Fill()  ## fill for every entry... not at once as a list....
    self.__localRootTree1.Write()
##
    #if(self.__cmjPlotDiag > 1) : 
    #  print("__askDicounter__defineTree... self.__localRootTree1.Scan() \n")
    #  self.__localRootTree1.Scan("diCounterId:currentA1:currentA2:currentA3:currentA4:currentB1:currentB2:currentB3:currentB4:testDate:temperature:position:sipmVoltage:lightSource:flashRate","","precision=4")   ## use for debug... let's see what is in the root tree...

##
##
## -------------------------------------------------------------
## 	A class to set up the main window to drive the
##	python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__myDiCounters  = askDiCounter()
    self.__myDiCounters.setupDevelopmentDatabase()  ## set up communications with database
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
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
    self.__myInstructions.setText('','Instructions/InstructionsForDiCountersRootQuery2017Jul14.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__col = 0
    self.__secondRow = 1
    self.__buttonWidth = 20
##	Send initial Sipm information: PO number, batches recieved and vendor measurements...
    self.__getValues = Button(self,text='Get Di-Counters',command=self.__myDiCounters.loadDiCounterRequest,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
    self.__getValues = Button(self,text='Histogram',command=self.__myDiCounters.getHistograms,width=self.__buttonWidth,bg='green',fg='black')
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
    self.__myDiCounters.openFile(self.__filePath)
    self.__myDiCounters.openLogFile()
## --------------------------------------------------------------------
##
  def turnOnDebug(self,tempDebug):
    self.__myDiCounters.turnOnDebug(tempDebug)
    print("__multiWindow__::turnOnDebug = debug level = %s") % (tempDebug)
## --------------------------------------------------------------------
## --------------------------------------------------------------------
## --------------------------------------------------------------------
## --------------------------------------------------------------------
## --------------------------------------------------------------------
## --------------------------------------------------------------------
##   Run the pyton script from here!!!
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('--debug',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
  options, args = parser.parse_args()
  print("'__main__': options.debugMode = %s \n") % (options.debugMode)
  print("'__main__': options.testMode  = %s \n") % (options.testMode)
  print("'__main__': options.database  = %s \n") % (options.database)
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry("+100+500")  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.debugMode != 0): myMultiForm.turnOnDebug(options.debugMode)
  myMultiForm.grid()
  root.mainloop()



