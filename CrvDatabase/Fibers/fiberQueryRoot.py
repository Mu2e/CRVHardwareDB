# -*- coding: utf-8 -*-
## File = "fiberQuerryRoot.py"
## Derived from File = "extrusionQuerryRoot.py"
##
##      Modified by cmj2018Mar26
##  Major changes:
##   1) Populate the batches: search over all batch_id's starting with the first one entered
##      and not the date.
##   2) Older versions of the "where" argument for ".query" method needed "'-'+self.__fetchThese".  
##      This does not work anymore.  This has been replace with just "self.__fetchThese"
##   3) Changed the directory structure and calls DataLoader versions so these could be accounted for.
##      This version uses the old hdbClient_v1_3
##   4) Sometimes the database does not respond to the DataLoader.query method... try self.__tryAgain times
##   5) Re-wrote the instruction text file to actually give instructions.
##   6) Removed most of the pedigree "Derived" comments.
## Derived from File = "extrusionQuerryRoot2017Jul27.py"
##
##      Re-arrange the GUI
##  Include a list box to display all available batches...
##
##       Use PyRoot to plot graphs...
##
## Derived from File = "extrusionQuerryRoot2017Jul20.py"
##  Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Oct5... Fix bug... return the Production database Query URL instead of the Write URL
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##  Modified by cmj2022Jan20... finally able to save character strings in root trees using python3
##  Modified by cmj2022Jun22... Change instruction file for Fibers instead of extrusions
##
#!/usr/bin/env python
##
##      A python script that uses a Graphical User Interface
##      to allow querry of the extrusion database and plot 
##      the test results.
##
##      Written by       Merrill Jenkins
##                  Department of Physics
##                  University of South Alabama
##
##  Modified by cmj2020Jul09... change hdbClient_v2_0 -> hdbClient_v2_2
##  Modified by cmj2020Jul09... change crvUtilities2018->crvUtilities; cmjGuiLibGrid2018Oct1-> cmjGuiLibGrid2020Jan30
##  Modified by cmj2020Jul09... change default database to production
##  Modified by cmj2020Aug03... cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##  Modified by cmj2022Jan20... finally able to save character strings in root trees using python3
##  Modified by cmj2021Jan22... save character strings in the root trees
##  Modified by cmj2022Jan22... add debug level button to GUI
##  Modified by cmj2022Jan22... make production database default
##
from tkinter import *         # get widget class
import sys
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")  ## change module library## 2020Jul09  Already there
from DataLoader import *
from databaseConfig import *
from cmjGuiLibGrid import * ## 2020Aug03
from collections import defaultdict  ## needed for two dimensional dictionaries
from generalUtilities import generalUtilities  ## this is needed for three dimensional dictionaries
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import time
##            Import the graphing modules
##  Import for PyRoot
import ROOT as _root  ## import to define vectors which are used to save strings
from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH2F, TGraph, TStyle, TTree, TString, TMultiGraph
from ROOT import gROOT, gBenchmark, gRandom, gSystem, gStyle, Double_t
from array import array
##
##
ProgramName = "fiberQueryRoot"
Version = "version2022.01.21"
##
##
cmjPlotDiag = 0  #  plot diagnostic variable... set to non-zero to plot diagnostics....
##
##
## -------------------------------------------------------------
##       A class to set up the main window to drive the
##      python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__cmjDebug = 0
    self.__database_config  = databaseConfig()
    #self.__database_config.setDebugOn()
    self.setupDevelopmentDatabase()  ## set up communications with database
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
##      Initialize this value to a minimum... update later in the program
    self.__numberOfBatches = 20
##      Set maximum numbers of tries to ask the database... sometimes it does not answer
    self.__maxTries = 3
##
    self.__fiberBatchResults = []  # The list of batches that will be histogrammed....
##      Arrays to plot...keep these in scope in the whole class
    self.__fiberId = {}
    self.__fiberProductionDate = {}
    self.__fiberInitialLength = {}
    self.__fiberCurrentLength = {}
    ##
    self.__plotFiberId = []
    self.__plotFiberProductionDate = []
    self.__plotFiberInitialLength =  []
    self.__plotFiberCurrentLength = []
    ##  Vendor Test Measurements
    self.__fiberVendorId = {}
    self.__fiberVendorAttenuation = {}
    self.__fiberVendorAttenuationVoltage256cm = {}
    self.__fiberVendorDiameter = {}
    self.__fiberVendorSigma = {}
    self.__fiberVendorEccentricity = {}
    self.__fiberVendorNumberOfBumps = {}
    self.__fiberVendorNumberOfBumpsKm = {}
    self.__fiberVendorComments = {}
    ##
    self.__plotVendorFiberId = []
    self.__plotFiberVendorProductionDate = []
    self.__plotFiberVendorAttenuation = []
    self.__plotFiberVendorAttenuationVoltage256cm = []
    self.__plotFiberVendorDiameter = []
    self.__plotFiberVendorSigma = []
    self.__plotFiberVendorEccentricity = []
    self.__plotFiberVendorNumberOfBumps = []
    self.__plotFiberVendorNumberOfBumpsKm = []
    self.__plotFiberVendorComments = []
    ## Local Measurements
    self.__fiberLocalId = {}
    self.__fiberLocalTestDate = {}
    self.__fiberLocalDiameter = {}
    self.__fiberLocalAttenuation = {}
    self.__fiberLocalComments = {}
    ##
    self.__plotFiberLocalId = []
    self.__plotFiberLocalTestDate = []
    self.__plotFiberLocalDiameter = []
    self.__plotFiberLocalAttenuation = []
    self.__plotFiberLocalComments = []
##
##      Lists and Dictionaries to plot the local attenuation vs. wavelength
##      The key is a composite of fiberTestDate+fiberId+Wavelength
    self.__localWavelengthTestDate = {}            ## key [testDate+fiberId+wavelength]
    self.__localWavelengthFiberId = {}            ## key [testDate+fiberId+wavelength]
    self.__localWavelength = {}                  ## key [testDate+fiberId+wavelength]
    self.__localWavelengthAttenuationSingleKey = {}      ## key [testDate+fiberId+wavelength]
    self.__localWavelengthFiberId = defaultdict(dict)      ## keys [testDate][]fiberId]
    self.__myMultiDimDictionary = generalUtilities()
    self.__localWavelength = self.__myMultiDimDictionary.nestedDict() ## [testDate][fiberId][wavelength]
    self.__localWavelengthAttenuation = self.__myMultiDimDictionary.nestedDict() ## [testDate][fiberId][wavelength]

##
##      Lists and Dictionaries to plot the local attenuation vs. fiber length
##      This is the local (UVa) ADC counts vs fiber length
##      The key is a composite of fiberTestDate+fiberId+Wavelength
    self.__localFiberAttenuationTestDate = {}            ## key [testDate+fiberId+wavelength]
    self.__localFiberAttenuationFiberId = {}            ## key [testDate+fiberId+wavelength]
    self.__localFiberAttenuationLengthSingleKey = {}                  ## key [testDate+fiberId+wavelength]
    self.__localFiberAttenuationAdcSingleKey = {}      ## key [testDate+fiberId+wavelength]
    self.__localFiberAttenuationId = defaultdict(dict)      ## keys [testDate][]fiberId]
    self.__myMultiDimDictionary = generalUtilities()
    self.__localFiberAttenuationLength = self.__myMultiDimDictionary.nestedDict() ## [testDate][fiberId][wavelength]
    self.__localFiberAttenuationAdc = self.__myMultiDimDictionary.nestedDict() ## [testDate][fiberId][wavelength]
##
##      Lists and Dictionaries to plot the vendor attenuation vs. fiber length
##      This is the vendor (Hamatsu) Voltage (mv) vs fiber length
##      The key is a composite of fiberTestDate+fiberId+Wavelength
    self.__vendorFiberAttenuationTestDate = {}            ## key [testDate+fiberId+wavelength]
    self.__vendorFiberAttenuationFiberId = {}            ## key [testDate+fiberId+wavelength]
    self.__vendorFiberAttenuationLengthSingleKey = {}                  ## key [testDate+fiberId+wavelength]
    self.__vendorFiberAttenuationAdcSingleKey = {}      ## key [testDate+fiberId+wavelength]
    self.__vendorFiberAttenuationId = defaultdict(dict)      ## keys [testDate][]fiberId]
    self.__vendorFiberAttenuationLength = self.__myMultiDimDictionary.nestedDict() ## [testDate][fiberId][wavelength]
    self.__vendorFiberAttenuationAdc = self.__myMultiDimDictionary.nestedDict() ## [testDate][fiberId][wavelength]


##      Define Output Log file... remove this later
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('fiberQuerries')
    self.__mySaveIt.openFile()
    self.__row = 0
    self.__col = 0
    self.__strName = []
    self.__sCount = 0
##
##
##
##      First Column...
    self.__col = 0
    self.__firstRow = 0
##
##      Instruction Box...
    self.__myInstructions = myScrolledText(self)
    self.__myInstructions.setTextBoxWidth(50)
    self.__myInstructions.makeWidgets()
    self.__myInstructions.setText('','Instructions/InstructionsForFiberQuerry2012Jun22.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##      Plot histograms
    self.__secondRow = 2
    self.__col = 1
    self.__buttonWidth = 10
    self.__getValues = Button(self,text='Histograms',command=self.getHistograms,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    #self.__secondRow += 1
    #         Display the date the script is being run
    self.__col = 2
    self.__date = myDate(self,self.__secondRow,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__secondRow,column=self.__col,sticky=E)
##      Third Column...
    self.__row = 0
    self.__col = 2
    self.__logo = mu2eLogo(self,self.__row,self.__col)     # display Mu2e logo!
    self.__logo.grid(row=self.__row,column=self.__col,rowspan=2,sticky=NE)
#         Display the script's version number
    self.__version = myLabel(self,self.__row,self.__col)
    self.__version.setForgroundColor('blue')
    self.__version.setFontAll('Arial',10,'bold')
    self.__version.setWidth(20)
    self.__version.setText(Version)
    self.__version.makeLabel()
    self.__version.grid(row=self.__row,column=self.__col,stick=E)
    self.__row += 1
#         Display the debug level selection
    self.__col = 0
    self.__buttonName = 'Debug Level (0 to 5)'
    self.StringEntrySetup(self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,self.__buttonName,self.__buttonName)
    self.__row += 1

    self.__col = 0
    self.__row += 1
    self.__buttonWidth = 10
##      Add Control Bar at the bottom...
    self.__col = 0
    self.__firstRow = 6
    self.__quitNow = Quitter(self,0,self.__col)
    self.__quitNow.grid(row=self.__firstRow,column=0,sticky=W)
##
## -------------------------------------------------------------------
##      Setup to make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "fiber Tables"
    self.__whichDatabase = 'development'
    if(self.__cmjDebug !=0): print("...multiWindow::getFromDevelopmentDatabase... get to development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
##
## -------------------------------------------------------------------
##      Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Sipm Tables"
    self.__whichDatabase = 'production'
    print("...multiWindow::getFromProductionDatabase... get from production database \n")
    ## cmj2022Jan18 self.__url = self.__database_config.getProductionQueryUrl()
    self.__queryurl = self.__database_config.getProductionQueryUrl() ## cmj2022Jan2018
##
#####################################################################################
##
##  Setup local control: set debug level
##
##
## ===================================================================
##       Local String Entry button
##       Need to setup here to retain local program flow
  def StringEntrySetup(self,row,col,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    print("----- StringEntrySetup--- Enter")
    self.__StringEntry_row = row
    self.__StringEntry_col = col
    self.__StringEntry_labelWidth = 10
    self.__StringEntry_entryWidth = 10
    self.__StringEntry_buttonWidth= 10
    self.__StringEntry_entyLabel = ''
    self.__StringEntry_buttonText = 'Enter'
    self.__StringEntry_buttonName = buttonName
    self.__StringEntry_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__label = Label(self,width=self.__labelWidth,text=self.__StringEntry_buttonName,anchor=W,justify=LEFT)
    self.__label.grid(row=self.__StringEntry_row,column=self.__StringEntry_col,sticky=W)
    self.__ent = Entry(self,width=self.__StringEntry_entryWidth)
    self.__var = StringVar()        # associate string variable with entry field
    self.__ent.config(textvariable=self.__var)
    self.__var.set('')
    self.__ent.grid(row=self.__StringEntry_row,column=self.__StringEntry_col+1,sticky=W)
    self.__ent.focus()
    self.__ent.bind('<Return>',lambda event:self.fetch())
    self.__button = Button(self,text=self.__StringEntry_buttonText,width=self.__StringEntry_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetch)
    self.__button.config(bg='#E3E3E3')
    self.__button.grid(row=self.__StringEntry_row,column=self.__StringEntry_col+2,sticky=W)
  def StringEntryFetch(self):
    self.__StringEntry_result = self.__ent.get()
    self.turnOnDebug(int(self.__StringEntry_result))
    print(("--- StringEntryGet... after Button in getEntry = %s") %(self.__StringEntry_result))
    return self.__StringEntry_result
##
##
##
####################################################################################
####################################################################################
##       Methods to interface with pyroot
## --------------------------------------------------------------
## This method calls the method to get the entries to the database
## and plot Histograms
  def getHistograms(self):
    #self.__tempFibersFromDatabase = []
    #self.__tempFibersFromDatabase = self.getFibersFromDatabase()
    #self.unpackFibers(self.__tempFibersFromDatabase)
    ## Get the vendor measurements of the fibers
    self.__tempVendorFiberMeasurements = []
    self.__tempVendorFiberMeasurements = self.getVendorFiberMeasurementsFromDatabase()
    self.unpackVendorFiberMeasurements(self.__tempVendorFiberMeasurements)
    ## Local Measurements
    self.__tempLocalFiberMeasurements = []
    self.__tempLocalFiberMeasurements = self.getLocalFiberMeasurementsFromDatabase()
    self.unpackLocalFiberMeasurements(self.__tempLocalFiberMeasurements)
    ## Local Attenuation vs Wavelength
    self.__tempResults =[]
    self.__tempResults = self.getLocalAttenuationVsWavelength()
    self.unpackLocalAttenuationVsWavelength(self.__tempResults)
    ## Local ADC counts vs Fiber lengths.
    self.__tempLocalAttenuationResults = []
    self.__tempLocalAttenuationResults =self.getLocalAttenuationLength()
    self.unpackLocalAttenuationVsLength(self.__tempLocalAttenuationResults)

    ## Vendor Votage (mv) vs Fiber lengths.
    self.__tempVendorAttenuationResults = []
    self.__tempVendorAttenuationResults =self.getVendorAttenuationLength()
    self.unpackVendorAttenuationVsLength(self.__tempVendorAttenuationResults)
    ## Plot histograms and make root trees
    self.plotHistograms()
    self.makeRootTrees()
##
##
####################################################################################
####################################################################################
###   Local Attenuation Vs Wavelength Measurements
## --------------------------------------------------------------
##      Make queries to get all locally measured attenuation vs wavelength
  def getLocalAttenuationVsWavelength(self):
    self.__getlocalWavelengthAttenuationValues = DataQuery(self.__queryUrl)
    if(self.__cmjDebug > 2) : print((".... getLocalAttenuationVsWavelength: self.__queryUrl   = %s \n") % (self.__queryUrl))
    self.__localWavelengthAttenuationValues = []
    self.__table = "fiber_local_spect_attenuations"
    self.__fetchThese = "fiber_id,test_timestamp,wavelength_nm,local_attenuation_mm"
    #self.__fetchThese = "fiber_id"
    self.__fetchCondition = "create_time:ge:2017-05-15"
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print("===========> getLocalAttenuationVsWavelength %s %s %s \n" %(self.__database,self.__table,self.__fetchThese))
    #self.__localWavelengthAttenuationValues = self.__getlocalWavelengthAttenuationValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localWavelengthAttenuationValues = self.__getlocalWavelengthAttenuationValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localWavelengthAttenuationValues != -9999) : break
    ## cmj2018Mar26
    if(self.__cmjDebug > 5): print(" getLocalAttenuationVsWavelength: self.__fiberValues = %s \n" %(self.__localWavelengthAttenuationValues))
    self.__localWavelengthAttenuationValuesLength = len(self.__localWavelengthAttenuationValues)
    if(self.__cmjDebug > 1) :
      print("++++++++++++++++++++++++++++++++++++++++++++++")
      print((".... getLocalAttenuationVsWavelength: self.__localWavelengthAttenuationValuesLength = %d ") % (self.__localWavelengthAttenuationValuesLength))
    if(self.__cmjDebug != 0):
      for self.__l in self.__localWavelengthAttenuationValues:
        print(self.__l)
    return self.__localWavelengthAttenuationValues
##
## --------------------------------------------------------------------
##      Unpack the locally measured attenuation vs wavelength
  def unpackLocalAttenuationVsWavelength(self,tempLocalAttenuationVsWavelength):
    if(self.__cmjDebug > 1):
      print("...  unpackLocalAttenuationVsWavelength: Enter\n")
      print(("....unpackLocalAttenuationVsWavelength: len(tempExtrusion) = %d \n") % len(tempLocalAttenuationVsWavelength))
    if(tempLocalAttenuationVsWavelength[0] == -9999):
      print("...  unpackLocalAttenuationVsWavelength: WARNING!!! Fiber Vendor Attenuation vs Wavelength did not unpack! \n") 
      print(("...  unpackLocalAttenuationVsWavelength: tempFiber = %s \n") % (tempLocalAttenuationVsWavelength))
      return
    for self.__record in tempLocalAttenuationVsWavelength:
      self.__item = []
      self.__item = self.__record.rsplit(',')
      if (self.__item[0] != ""):
        self.__tempFiberId = self.__item[0]
        self.__tempFiberTestDate = self.__item[1]
        self.__tempFiberWavelength = float(self.__item[2])
        self.__tempFiberAttenuation = float(self.__item[3])
        if(self.__cmjDebug > 2):  ## diagnostic print statements
          print(("...  unpackLocalAttenuationVsWavelength: self.__record = %s") % (self.__record))
          print(("...  unpackLocalAttenuationVsWavelength: self.__tempFiberId = %s") % (self.__tempFiberId))
          print(("...  unpackLocalAttenuationVsWavelength: self.__tempFiberTestDate = %s") % (self.__tempFiberTestDate))
          print(("...  unpackLocalAttenuationVsWavelength: self.__tempFiberWaveLength = %e") % (self.__tempFiberWavelength))
          print(("...  unpackLocalAttenuationVsWavelength: self.__tempFiberAttenuation = %e") % (self.__tempFiberAttenuation))
      ## Store the information!
      self.__localWavelengthTestDate[self.__tempFiberTestDate] = self.__tempFiberTestDate
      self.__localWavelengthFiberId[self.__tempFiberTestDate][self.__tempFiberId] = self.__tempFiberId
      self.__localWavelength[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberWavelength] = float(self.__tempFiberWavelength)
      self.__localWavelengthAttenuation[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberWavelength] = float(self.__tempFiberAttenuation)
      if(self.__cmjDebug > 2):  ## diagnostic print statements
        print(("...  unpackLocalAttenuationVsWavelength: self.__localWavelengthTestDate[%s] = %s") % (self.__tempFiberTestDate,self.__localWavelengthTestDate[self.__tempFiberTestDate]))
        print(("...  unpackLocalAttenuationVsWavelength: self.__localWavelengthFiberId[%s][%s] = %s") % (self.__tempFiberTestDate,self.__tempFiberId, self.__localWavelengthFiberId[self.__tempFiberTestDate][self.__tempFiberId]))
        print(("...  unpackLocalAttenuationVsWavelength: self.__tempFiberWaveLength[%s][%s][%s] = %e") % (self.__tempFiberTestDate,self.__tempFiberId,self.__tempFiberWavelength,self.__localWavelength[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberWavelength]))
        print(("...  unpackLocalAttenuationVsWavelength: self.__localWavelengthAttenuation[%s][%s][%s] = %e") % (self.__tempFiberTestDate,self.__tempFiberId,self.__tempFiberWavelength,self.__localWavelengthAttenuation[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberWavelength]))
    if(self.__cmjDebug > 0):
      print("... XX unpackLocalAttenuationVsWavelength: Exit\n")
##
##
##
##
####################################################################################
####################################################################################
###   Local Attenuation Lengths (not wavelength) Measurements
##    Local (UVa) measured ADC counts vs fiber length
## --------------------------------------------------------------
##      Make queries to get all locally measured (UVa) ADC counts vs fiber length
  def getLocalAttenuationLength(self):
    self.__getlocalAttenuationValues = DataQuery(self.__queryUrl)
    if(self.__cmjDebug > 1): print((".... getLocalAttenuationLength: self.__queryUrl   = %s \n") % (self.__queryUrl))
    self.__localAttenuationValues = []
    self.__table = "fiber_attenuation_local_lengths"
    self.__fetchThese = "fiber_id,test_timestamp,fiber_distance,fiber_adc"
    #self.__fetchThese = "fiber_id"
    self.__fetchCondition = "create_time:ge:2018-06-01"  ## exclude Steve's test entry
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print("===========> getLocalAttenuationLength %s %s %s \n" %(self.__database,self.__table,self.__fetchThese))
    #self.__localAttenuationValues = self.__getlocalAttenuationValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localAttenuationValues = self.__getlocalAttenuationValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localAttenuationValues != -9999) : break
    ## cmj2018Mar26
    if(self.__cmjDebug > 5): print(".... getLocalAttenuationLength: self.__fiberValues = %s \n" %(self.__localAttenuationValues))
    self.__localAttenuationValuesLength = len(self.__localAttenuationValues)
    if(self.__cmjDebug > 1):
      print("++++++++++++++++++++++++++++++++++++++++++++++")
      print((".... getLocalAttenuationLength: self.__localAttenuationValues = %d ") % (len(self.__localAttenuationValues)))
    if(self.__cmjDebug != 0):
      for self.__l in self.__localAttenuationValues:
        print(self.__l)
    return self.__localAttenuationValues
##
## --------------------------------------------------------------------
##      Unpack the locally measured ADC counts vs fiber length
  def unpackLocalAttenuationVsLength(self,tempLocalAttenuationVsLength):
    if(self.__cmjDebug > 1):
      print("...  unpackLocalAttenuationVsLength: Enter\n")
      print(("....unpackLocalAttenuationVsLength: len(tempExtrusion) = %d \n") % len(tempLocalAttenuationVsLength))
    if(tempLocalAttenuationVsLength[0] == -9999):
      print("...  unpackLocalAttenuationVsLength: WARNING!!! Fiber Vendor Attenuation vs Wavelength did not unpack! \n") 
      print(("...  unpackLocalAttenuationVsLength: tempLocalAttenuationVsLength= %s \n") % (tempLocalAttenuationVsLength))
      return
    for self.__record in tempLocalAttenuationVsLength:
      self.__item = []
      self.__item = self.__record.rsplit(',')
      if (self.__item[0] != ""):
        self.__tempFiberId = self.__item[0]
        self.__tempFiberTestDate = self.__item[1]
        self.__tempFiberLength = float(self.__item[2])
        self.__tempFiberAttenuation = float(self.__item[3])
        if(self.__cmjDebug > 2):  ## diagnostic print statements
          print(("...  unpackLocalAttenuationVsLength: self.__record = %s") % (self.__record))
          print(("...  unpackLocalAttenuationVsLength: self.__tempFiberId = %s") % (self.__tempFiberId))
          print(("...  unpackLocalAttenuationVsLength: self.__tempFiberTestDate = %s") % (self.__tempFiberTestDate))
          print(("...  unpackLocalAttenuationVsLength: self.__tempFiberLength = %e") % (self.__tempFiberLength))
          print(("...  unpackLocalAttenuationVsLength: self.__tempFiberAttenuation = %e") % (self.__tempFiberAttenuation))
      ## Store the information!
      self.__localFiberAttenuationTestDate[self.__tempFiberTestDate] = self.__tempFiberTestDate
      self.__localFiberAttenuationId[self.__tempFiberTestDate][self.__tempFiberId] = self.__tempFiberId
      self.__localFiberAttenuationLength[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength] = float(self.__tempFiberLength)
      self.__localFiberAttenuationAdc[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength] = float(self.__tempFiberAttenuation)
      if(self.__cmjDebug > 2):  ## diagnostic print statements
        print(("...  unpackLocalAttenuationVsLength: self.__localFiberAttenuationTestDate[%s] = %s") % (self.__tempFiberTestDate,self.__localFiberAttenuationTestDate[self.__tempFiberTestDate]))
        print(("...  unpackLocalAttenuationVsLength: self.__localFiberAttenuationId[%s][%s] = %s") % (self.__tempFiberTestDate,self.__tempFiberId, self.__localFiberAttenuationId[self.__tempFiberTestDate][self.__tempFiberId]))
        print(("...  unpackLocalAttenuationVsLength: self.__localFiberAttenuationLength[%s][%s][%s] = %e") % (self.__tempFiberTestDate,self.__tempFiberId,self.__tempFiberLength,self.__localFiberAttenuationLength[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength]))
        print(("...  unpackLocalAttenuationVsLength: self.__localFiberAttenuationAdc[%s][%s][%s] = %e") % (self.__tempFiberTestDate,self.__tempFiberId,self.__tempFiberLength,self.__localFiberAttenuationAdc[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength]))
    if(self.__cmjDebug > 1):
      print("... XX unpackLocalAttenuationVsLength: Exit\n")
##
##
##
##
####################################################################################
####################################################################################
###   Vendor Attenuation Lengths  Measurements
##    Vendor (Hamatsu) measured Voltage (mv) vs fiber length
## --------------------------------------------------------------
##      Make queries to get all locally measured (UVa) ADC counts vs fiber length
  def getVendorAttenuationLength(self):
    self.__getVendorAttenuationValues = DataQuery(self.__queryUrl)
    if(self.__cmjDebug > 2) : print((".... getVendorAttenuationLength: self.__queryUrl   = %s \n") % (self.__queryUrl))
    self.__vendorAttenuationValues = []
    self.__table = "fiber_attenuation_vendor_lengths"
    self.__fetchThese = "fiber_id,fiber_test_date,fiber_distance,fiber_light_output_mv"
    #self.__fetchThese = "fiber_id"
    self.__fetchCondition = "create_time:ge:2018-06-01"  ## exclude Steve's test entry
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print("===========> getVendorAttenuationLength %s %s %s \n" %(self.__database,self.__table,self.__fetchThese))
    #self.__vendorAttenuationValues = self.__getVendorAttenuationValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__vendorAttenuationValues = self.__getlocalAttenuationValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__vendorAttenuationValues != -9999) : break
    ## cmj2018Mar26
    if(self.__cmjDebug > 5): print(".... getVendorAttenuationLength: self.__vendorAttenuationValues = %s \n" %(self.__vendorAttenuationValues))
    self.__vendorAttenuationValuesLength = len(self.__vendorAttenuationValues)
    print("++++++++++++++++++++++++++++++++++++++++++++++")
    print((".... getVendorAttenuationLength: len(self.__vendorAttenuationValues) = %d ") % (len(self.__vendorAttenuationValues)))
    if(self.__cmjDebug != 0):
      for self.__l in self.__vendorAttenuationValues:
        print(self.__l)
    return self.__vendorAttenuationValues
##
## --------------------------------------------------------------------
##      Unpack the Vendor measured Voltage (mv) vs Fiber length
  def unpackVendorAttenuationVsLength(self,tempVendorAttenuationVsLength):
    if(self.__cmjDebug > 1):
      print("...  unpackVendorAttenuationVsLength: Enter\n")
      print(("....unpackVendorAttenuationVsLength: len(tempVendorAttenuationVsLength) = %d \n") % len(tempVendorAttenuationVsLength))
    if(tempVendorAttenuationVsLength[0] == -9999):
      print("...  unpackVendorAttenuationVsLength: WARNING!!! Fiber Vendor Attenuation vs Wavelength did not unpack! \n") 
      print(("...  unpackVendorAttenuationVsLength: tempVendorAttenuationVsLength = %s \n") % (tempVendorAttenuationVsLength))
      return
    for self.__record in tempVendorAttenuationVsLength:
      self.__item = []
      self.__item = self.__record.rsplit(',')
      if (self.__item[0] != ""):
        self.__tempFiberId = self.__item[0]
        self.__tempFiberTestDate = self.__item[1]
        self.__tempFiberLength = float(self.__item[2])
        self.__tempFiberAttenuation = float(self.__item[3])
        if(self.__cmjDebug > 2):  ## diagnostic print statements
          print(("...  unpackVendorAttenuationVsLength: self.__record = %s") % (self.__record))
          print(("...  unpackVendorAttenuationVsLength: self.__tempFiberId = %s") % (self.__tempFiberId))
          print(("...  unpackVendorAttenuationVsLength: self.__tempFiberTestDate = %s") % (self.__tempFiberTestDate))
          print(("...  unpackVendorAttenuationVsLength: self.__tempFiberLength = %e") % (self.__tempFiberLength))
          print(("...  unpackVendorAttenuationVsLength: self.__tempFiberAttenuation = %e") % (self.__tempFiberAttenuation))
      ## Store the information!
      self.__vendorFiberAttenuationTestDate[self.__tempFiberTestDate] = self.__tempFiberTestDate
      self.__vendorFiberAttenuationId[self.__tempFiberTestDate][self.__tempFiberId] = self.__tempFiberId
      self.__vendorFiberAttenuationLength[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength] = float(self.__tempFiberLength)
      self.__vendorFiberAttenuationAdc[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength] = float(self.__tempFiberAttenuation)
      if(self.__cmjDebug > 2):  ## diagnostic print statements
        print(("...  unpackVendorAttenuationVsLength: self.__vendorFiberAttenuationTestDate[%s] = %s") % (self.__tempFiberTestDate,self.__vendorFiberAttenuationTestDate[self.__tempFiberTestDate]))
        print(("...  unpackVendorAttenuationVsLength: self.__vendorFiberAttenuationId[%s][%s] = %s") % (self.__tempFiberTestDate,self.__tempFiberId, self.__vendorFiberAttenuationId[self.__tempFiberTestDate][self.__tempFiberId]))
        print(("...  unpackVendorAttenuationVsLength: self.__vendorFiberAttenuationLength[%s][%s][%s] = %e") % (self.__tempFiberTestDate,self.__tempFiberId,self.__tempFiberLength,self.__vendorFiberAttenuationLength[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength]))
        print(("...  unpackVendorAttenuationVsLength: self.__vendorFiberAttenuationAdc[%s][%s][%s] = %e") % (self.__tempFiberTestDate,self.__tempFiberId,self.__tempFiberLength,self.__vendorFiberAttenuationAdc[self.__tempFiberTestDate][self.__tempFiberId][self.__tempFiberLength]))
    if(self.__cmjDebug > 1):
      print("... XX unpackVendorAttenuationVsLength: Exit\n")
##
##
##
###################################################################################
###################################################################################
###################################################################################
##
##            Vendor supplied measurements    
## -------------------------------------------------------------------
##      Make querries to get all vendor measurements of the fibers from the data base
##
  def getFibersFromDatabase(self):
    self.__getFiberValues = DataQuery(self.__queryUrl)
    print((".... getFibersFromDatabase: self.__queryUrl   = %s \n") % (self.__queryUrl))
    self.__localFiberValues = []
    self.__table = "fibers"
    #elf.__fetchThese = "batch_id,average_ref_counts,stdev_ref_counters,percent_ref_counters,average_light_yield_cnt,stdev_light_yield_cnt,percent_light_yield_cnt,create_time"
    self.__fetchThese = "fiber_id,production_date,initial_length,current_length,fiber_type,vendor_diameter_micron,vendor_light_yield,comments"
    ##self.__fetchThese = "fiber_id,production_date,initial_length,current_length,fiber_type,diameter_micron,diameter_sigma_micron,eccentricty,attenuation_length_cm,attenuation_voltage_at256cm_mv,comments"
    self.__fetchCondition = "create_time:ge:2017-05-15"
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print("===========> getFibersFromDatabase %s %s %s \n" %(self.__database,self.__table,self.__fetchThese))
    #self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localFiberValues != -9999) : break
    ## cmj2018Mar26
    if(self.__cmjDebug > 1): print(" getFibersFromDatabase: self.__fiberValues = %s \n" %(self.__localFiberValues))
    self.__numberOfFibers = len(self.__localFiberValues)
    if(self.__cmjDebug != 0):
      for self.__l in self.__localFiberValues:
        print(self.__l)
    return self.__localFiberValues
##
## --------------------------------------------------------------
##      Unpack the vendor supplied database information for plotting,etc
  def unpackFibers(self,tempFiber):
    if(self.__cmjDebug > 1) : print("...  unpackFibers: Enter\n")
    if(self.__cmjDebug > 2) : print(("... unpackFibers: tempFiber = %s \n") % tempFiber)
    if(tempFiber[0] == -9999):
      print("...  unpackFibers: WARNING!!! Fiber did not unpack! \n") 
      print(("...  unpackFibers: tempFiber = %s \n") % (tempFiber))
      return
    for self.__record in tempFiber:
      self.__item = []
      self.__item = self.__record.rsplit(',')
      if (self.__item[0] != ""):
        self.__tempFiberId = self.__item[0]
        self.__tempFiberProductionDate = self.__item[1]
        self.__tempFiberInitialLength = float(self.__item[2])
        self.__tempFiberCurrentLength = float(self.__item[3])
        self.__tempFiberType = self.__item[4]
        self.__tempFiberDiameter = self.__item[5]
        self.__tempFiberSigma = self.__item[6]
        self.__tempFiberEccentricity = self.__item[7]
        self.__tempFiberAttenuationLength = self.__item[8]
        self.__tempFiberAttenuationVoltage256cm = self.__[9]
        self.__tempComment = self.__item[10]
        if(not self.__item[5]):
          self.__tempFiberVendorDiameter = float(self.__item[5])
        else:
          self.__tempFiberVendorDiameter = float(-9999.99)
        self.__tempFiberVendorLightYield = float(self.__item[6])
        self.__tempFiberVendorComments = self.__item[7]
        if(self.__cmjDebug > 2):  ## diagnostic print statements
          print("unpackFibers ........ New Counter ............ \n")
          print(("... self.__item = %s \n") % self.__item)
          print(("... self.__tempFiberId = %s \n") % self.__tempFiberId)
        self.__fiberId[self.__tempFiberId]     = self.__tempFiberId
        self.__fiberProductionDate[self.__tempFiberId] = self.__tempFiberProductionDate
        self.__fiberInitialLength[self.__tempFiberId]      = float(self.__tempFiberInitialLength)
        self.__fiberCurrentLength[self.__tempFiberId] = float(self.__tempFiberCurrentLength)
        self.__fiberType[self.__tempFiberId] = self.__tempFiberType
        self.__fiberVendorAttenuation[self.__tempFiberId] = float(self.__tempFiberVendorAttenuation)
        self.__fiberVendorComments[self.__tempFiberId] = self.__tempFiberVendorComments
##            Load arrays for root files....vendor
        self.__plotFiberId.append(self.__tempFiberId)
        self.__plotFiberProductionDate.append(self.__tempFiberProductionDate)
        self.__plotFiberInitialLength.append(float(self.__tempFiberInitialLength))
        self.__plotFiberCurrentLength.append(float(self.__tempFiberCurrentLength))
        self.__plotFiberType.append(self.__tempFiberType)
        self.__plotFiberVendorAttenuation.append(float(self.__tempFiberVendorAttenuation))
        self.__plotFiberVendorAttenuationVoltage256cm = float(self.__tempFiberAttenuationVoltage256cm)
        self.__plotFiberVendorDiameter.append(float(self.__tempFiberVendorDiameter))
        self.__plotFiberVendorSigma = float(self.__tempFiberSigma)
        self.__plotFiberVendorEccentricity = float(self.__tempFiberEccentricity)
        #self.__plotFiberVendorLightYield.append(float(self.__tempFiberVendorLightYield))
        self.__plotFiberVendorComments.append(self.__tempFiberVendorComments)
##
    if(self.__cmjDebug > -1):            ## diangonstic print statements
      print(("unpackFibers ........len(self.__plotFiberId) = %d \n") % (len(self.__plotFiberId)))
      print(("unpackFibers ........len(self.__plotFiberProductionDate) = %d \n") % (len(self.__plotFiberProductionDate)))
      print(("unpackFibers ........len(self.__plotFiberInitialLength) = %d \n") % (len(self.__plotFiberInitialLength)))
      print(("unpackFibers ........len(self.__plotFiberType) = %d \n") % (len(self.__plotFiberType)))
      print(("unpackFibers ........len(self.__plotFiberVendorAttenuation) = %d \n") % (len(self.__plotFiberVendorAttenuation)))
      print(("unpackFibers ........len(self.__plotFiberVendorDiameter) = %d \n") % (len(self.__plotFiberVendorDiameter)))
      #print("unpackFibers ........len(self.__plotFiberVendorLightYield) = %d \n") % (len(self.__plotFiberVendorLightYield))
      print(("unpackFibers ........len(self.__plotFiberComments) = %d \n") % (len(self.__plotFiberVendorComments)))
      print("unpackFibers ........ ExtrusionId ............ \n")
      for self.__m in list(self.__fiberId.keys()):
        print(("...... self.__fiberId.keys()     = %s || self.__fiberId[%s] = %s \n")     % (self.__m,self.__m,self.__fiberId[self.__m]))
###################################################################################
###################################################################################
###################################################################################
##
##            Vendor supplied measurements    
## -------------------------------------------------------------------
##      Make querries to get all vendor measurements of the fibers from the data base
##
  def getFibersFromDatabase(self):
    self.__getFiberValues = DataQuery(self.__queryUrl)
    if(self.__cmjDebug > 2): print((".... getFibersFromDatabase: self.__queryUrl   = %s \n") % (self.__queryUrl))
    self.__localFiberValues = []
    self.__table = "fibers"
    #elf.__fetchThese = "batch_id,average_ref_counts,stdev_ref_counters,percent_ref_counters,average_light_yield_cnt,stdev_light_yield_cnt,percent_light_yield_cnt,create_time"
    self.__fetchThese = "fiber_id,production_date,initial_length,current_length,fiber_type,vendor_diameter_micron,vendor_light_yield,comments"
    ##self.__fetchThese = "fiber_id,production_date,initial_length,current_length,fiber_type,diameter_micron,diameter_sigma_micron,eccentricty,attenuation_length_cm,attenuation_voltage_at256cm_mv,comments"
    self.__fetchCondition = "create_time:ge:2017-05-15"
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print("===========> getFibersFromDatabase %s %s %s \n" %(self.__database,self.__table,self.__fetchThese))
    #self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localFiberValues != -9999) : break
    ## cmj2018Mar26
    if(self.__cmjDebug > 1): print(" getFibersFromDatabase: self.__fiberValues = %s \n" %(self.__localFiberValues))
    self.__numberOfFibers = len(self.__localFiberValues)
    if(self.__cmjDebug != 0):
      for self.__l in self.__localFiberValues:
        print(self.__l)
    return self.__localFiberValues
##
###################################################################################
###################################################################################
###################################################################################
##
##            Vendor supplied measurements    
## -------------------------------------------------------------------
##      Make querries to get all vendor measurements of the fibers from the data base
##
  def getVendorFiberMeasurementsFromDatabase(self):
    self.__getFiberValues = DataQuery(self.__queryUrl)
    if(self.__cmjDebug > 2): print((".... getVendorFiberMeasurementsFromDatabase: self.__queryUrl   = %s \n") % (self.__queryUrl))
    self.__localFiberValues = []
    self.__table = "fiber_tests"
    self.__fetchThese = "fiber_id,test_timestamp,measurement,diameter_micron,diameter_sigma_micron,eccentricity,number_of_bumps_spool,number_of_bumps_km,attenuation_length_cm,attenuation_voltage_at256cm_mv,fiber_diameter_mm,light_yield,temperature_degc,comments"
    self.__fetchCondition = "create_time:ge:2017-05-15&measurement:eq:vendor"
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print("===========> getVendorFiberMeasurementsFromDatabase %s %s %s \n" %(self.__database,self.__table,self.__fetchThese))
    #self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localFiberValues != -9999) : break
    ## cmj2018Mar26
    if(self.__cmjDebug > 1): print(" getVendorFiberMeasurementsFromDatabase: self.__fiberValues = %s \n" %(self.__localFiberValues))
    self.__numberOfFibers = len(self.__localFiberValues)
    if(self.__cmjDebug != 0):
      for self.__l in self.__localFiberValues:
        print(self.__l)
    return self.__localFiberValues
##
## --------------------------------------------------------------
##      Unpack the vendor supplied database information for plotting,etc
  def unpackVendorFiberMeasurements(self,tempFiber):
    if(self.__cmjDebug > 1) : print("...  unpackVendorFiberMeasurements: Enter\n")
    if(self.__cmjDebug > 2) : print(("....unpackVendorFiberMeasurements: tempFibers = %s \n") % tempFiber)
    if(tempFiber[0] == -9999):
      print("...  unpackVendorFiberMeasurements: WARNING!!! Fiber did not unpack! \n") 
      print(("... XX unpackVendorFiberMeasurements: tempFiber = %s \n") % (tempFiber))
      return
    for self.__record in tempFiber:
      self.__item = []
      self.__item = self.__record.rsplit(',')
      if (self.__item[0] != ""):
        self.__tempFiberId = self.__item[0]
        self.__tempFiberProductionDate = self.__item[1]
        self.__tempFiberDiameter = self.__item[3]
        self.__tempFiberSigma = self.__item[4]
        self.__tempFiberEccentricity = self.__item[5]
        self.__number_of_bumps = self.__item[6]
        self.__number_of_bumps_km = self.__item[7]
        self.__tempFiberAttenuationLength = self.__item[8]
        self.__tempFiberAttenuationVoltage256cm = self.__item[9]
        self.__tempFiberComment = self.__item[11]
        if(self.__cmjDebug > 2):  ## diagnostic print statements
          print("unpackVendorFiberMeasurements ........ New Counter ............ \n")
          print(("unpackVendorFiberMeasurements ... self.__item = %s \n") % self.__item)
          print(("unpackVendorFiberMeasurements ... self.__tempFiberId = %s \n") % self.__tempFiberId)
        self.__fiberVendorId[self.__tempFiberId]     = self.__tempFiberId
        self.__fiberProductionDate[self.__tempFiberId] = self.__tempFiberProductionDate
        self.__fiberVendorAttenuation[self.__tempFiberId] = float(self.__tempFiberAttenuationLength)
        self.__fiberVendorAttenuationVoltage256cm[self.__tempFiberId] = float(self.__tempFiberAttenuationVoltage256cm)
        self.__fiberVendorDiameter[self.__tempFiberId] = float(self.__tempFiberDiameter)
        self.__fiberVendorSigma[self.__tempFiberId] = float(self.__tempFiberSigma)
        self.__fiberVendorEccentricity[self.__tempFiberId] = float(self.__tempFiberEccentricity)
        self.__fiberVendorNumberOfBumps[self.__tempFiberId] = int(self.__number_of_bumps)
        self.__fiberVendorNumberOfBumpsKm[self.__tempFiberId] = int(self.__number_of_bumps_km)
        self.__fiberVendorComments[self.__tempFiberId] = self.__tempFiberComment 
##            Load arrays for root files....vendor
        self.__plotFiberId.append(self.__tempFiberId)
        self.__plotFiberProductionDate.append(self.__tempFiberProductionDate)
        self.__plotFiberVendorAttenuation.append(float(self.__tempFiberAttenuationLength))
        self.__plotFiberVendorAttenuationVoltage256cm.append(float(self.__tempFiberAttenuationVoltage256cm))
        self.__plotFiberVendorDiameter.append(float(self.__tempFiberDiameter))
        self.__plotFiberVendorSigma.append(float(self.__tempFiberSigma))
        self.__plotFiberVendorEccentricity.append(float(self.__tempFiberEccentricity))
        self.__plotFiberVendorNumberOfBumps.append(int(self.__number_of_bumps))
        self.__plotFiberVendorNumberOfBumpsKm.append(int(self.__number_of_bumps_km))
        self.__plotFiberVendorComments.append(self.__tempFiberComment )
##
    if(self.__cmjDebug > 1):            ## diangonstic print statements
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberId) = %d \n") % (len(self.__plotFiberId)))
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberVendorAttenuation) = %d \n") % (len(self.__plotFiberVendorAttenuation)))
      print(("unpackVendorFiberMeasurements ........len(plotFiberVendorAttenuationVoltage256cm) = %d \n") % (len(self.__plotFiberVendorAttenuation)))
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberVendorAttenuationVoltage256cm) = %d \n") % (len(self.__plotFiberVendorAttenuationVoltage256cm)))

      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberVendorSigma) = %d \n") % (len(self.__plotFiberVendorSigma)))
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberVendorEccentricity) = %d \n") % (len(self.__plotFiberVendorEccentricity)))
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberVendorNumberOfBumps) = %d \n") % (len(self.__plotFiberVendorNumberOfBumps)))
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberVendorNumberOfBumpsKm) = %d \n") % (len(self.__plotFiberVendorNumberOfBumpsKm)))
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberComments) = %d \n") % (len(self.__plotFiberVendorComments)))
      print("unpackVendorFiberMeasurements ........ ExtrusionId ............ \n")
      for self.__m in list(self.__fiberId.keys()):
        print(("...... self.__fiberId.keys()     = %s || self.__fiberId[%s] = %s \n")     % (self.__m,self.__m,self.__fiberId[self.__m]))
##
##
###################################################################################
###################################################################################
###################################################################################
##
##            Local measurements    
## -------------------------------------------------------------------
##      Make querries to get all local measurements of the fibers from the data base
##
  def getLocalFiberMeasurementsFromDatabase(self):
    self.__getFiberValues = DataQuery(self.__queryUrl)
    if(self.__cmjDebug > 2) : print((".... getLocalFiberMeasurementsFromDatabase: self.__queryUrl   = %s \n") % (self.__queryUrl))
    self.__localFiberValues = []
    self.__table = "fiber_tests"
    self.__fetchThese = "fiber_id,test_timestamp,diameter_micron,attenuation_length_cm,comments"
    self.__fetchCondition = "create_time:ge:2017-05-15&measurement:eq:local"
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print("===========> getLocalFiberMeasurementsFromDatabase %s %s %s \n" %(self.__database,self.__table,self.__fetchThese))
    #self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localFiberValues = self.__getFiberValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localFiberValues != -9999) : break
    if(self.__cmjDebug > 1): print(("===========> getLocalFiberMeasurementsFromDatabase/// self_localFiberValues %s \n") % (self.__localFiberValues))
    ## cmj2018Mar26
    if(self.__cmjDebug > 1): print(" getLocalFiberMeasurementsFromDatabase: self.__fiberValues = %s \n" %(self.__localFiberValues))
    self.__numberOfFibers = len(self.__localFiberValues)
    if(self.__cmjDebug != 0):
      for self.__l in self.__localFiberValues:
        print(self.__l)
    return self.__localFiberValues
##
## --------------------------------------------------------------
##      Unpack the vendor supplied database information for plotting,etc
  def unpackLocalFiberMeasurements(self,tempFiber):
    if(self.__cmjDebug > 0):
      print("...  unpackLocalFiberMeasurements: Enter\n")
      print(("....unpackFibers: tempExtrusion = %s \n") % tempFiber)
    if(tempFiber[0] == -9999):
      print("...  unpackLocalFiberMeasurements: WARNING!!! Fiber did not unpack! \n") 
      print(("...  unpackLocalFiberMeasurements: tempFiber = %s \n") % (tempFiber))
      return
    for self.__record in tempFiber:
      self.__item = []
      self.__item = self.__record.rsplit(',')
      if (self.__item[0] != ""):
        self.__tempFiberId = self.__item[0]
        self.__tempFiberProductionDate = self.__item[1]
        if(self.__item[2]!='None'):
          self.__tempFiberDiameter = self.__item[2]
        else:
          self.__tempFiberDiameter = -9999.99
        if(self.__item[3]!='None'):
          self.__tempFiberAttenuationLength = self.__item[3]
        else:
          self.__tempFiberAttenuationLength = -9999.99
        self.__tempFiberComment = self.__item[4]
        if(self.__cmjDebug > 1):  ## diagnostic print statements
          print("unpackLocalFiberMeasurements ........ New Counter ............ \n")
          print(("unpackLocalFiberMeasurements ... self.__item = %s \n") % self.__item)
          print(("unpackLocalFiberMeasurements ... self.__tempFiberId = %s \n") % self.__tempFiberId)
          print(("unpackLocalFiberMeasurements ... self.__tempFiberProductionDate = %s \n") % self.__tempFiberProductionDate)
          print(("unpackLocalFiberMeasurements ... self.__tempFiberDiameter = %s \n") % self.__tempFiberDiameter)
          print(("unpackLocalFiberMeasurements ... self.__tempFiberAttenuationLength = %s \n") % self.__tempFiberAttenuationLength)
          print(("unpackLocalFiberMeasurements ... self.__tempFiberComment = %s \n") % self.__tempFiberComment)
        self.__fiberLocalId[self.__tempFiberId]     = self.__tempFiberId
        self.__fiberLocalTestDate[self.__tempFiberId] = self.__tempFiberProductionDate
        self.__fiberLocalDiameter[self.__tempFiberId] = float(self.__tempFiberDiameter)
        self.__fiberLocalAttenuation[self.__tempFiberId] = float(self.__tempFiberAttenuationLength)
        self.__fiberLocalComments[self.__tempFiberId] = self.__tempFiberComment 
##            Load arrays for root files....vendor
        self.__plotFiberLocalId.append(self.__tempFiberId)
        self.__plotFiberLocalTestDate.append(self.__tempFiberProductionDate)
        self.__plotFiberLocalDiameter.append(float(self.__tempFiberDiameter))
        self.__plotFiberLocalAttenuation.append(float(self.__tempFiberAttenuationLength))
        self.__plotFiberLocalComments.append(self.__tempFiberComment )
##
    if(self.__cmjDebug > 1):            ## diangonstic print statements
      print(("unpackLocalFiberMeasurements ........len(self.__plotFiberId) = %d \n") % (len(self.__plotFiberId)))
      print(("unpackLocalFiberMeasurements ........len(plotFiberLocalDiameter) = %d \n") % (len(self.__plotFiberLocalDiameter)))
      print(("unpackLocalFiberMeasurements ........len(self.__plotFiberLocalAttenuation) = %d \n") % (len(self.__plotFiberLocalAttenuation)))
      print(("unpackVendorFiberMeasurements ........len(self.__plotFiberComments) = %d \n") % (len(self.__plotFiberLocalComments)))
      print("unpackVendorFiberMeasurements ........ ExtrusionId ............ \n")
      for self.__m in list(self.__fiberId.keys()):
        print(("...... self.__fiberId.keys()     = %s || self.__fiberId[%s] = %s \n")     % (self.__m,self.__m,self.__fiberId[self.__m]))

##
##
##############################################################################
##############################################################################
##############################################################################
##
## --------------------------------------------------------------------
##   Plot Histograms with root
##
  def plotHistograms(self):
    self.bookHistograms()
    self.bookVendorMeasurementsHistograms()
    self.bookLocalMeasurementsHistograms()
    self.fillHistograms()
    self.drawVendorMeasurementCanvas()
    self.drawLocalMeasurementCanvas()
##
## --------------------------------------------------------------------
##  A method to book the vendor measurement histograms....
##
  def bookVendorMeasurementsHistograms(self):
    self.__nBins = 100
    #2022Jan18 self.__lowBin = 1.35e3
    #2022Jan18 self.__hiBin  = 1.45e3
    self.__lowBin = 1.35e3
    self.__hiBin  = 1.95e3
    self.__hFiberVendorDiameter = TH1F('self.__hFiberVendorDiameter','Vendor Measured Diameter',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hFiberVendorDiameter.SetFillColor(2)
    self.__nBins = 100
    self.__lowBin = 200.0
    self.__hiBin  = 500.0
    self.__hFiberVendorAttenuationOneMeas = TH1F('self.__hFiberVendorAttenuationOneMeas','Vendor Measured Attenution',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hFiberVendorAttenuationOneMeas.SetFillColor(2)
    self.__nBins = 100
    self.__lowBin = 0.0
    self.__hiBin  = 50.0
    self.__hFiberVendorAttenuation256cm = TH1F('hFiberVendorAttenuation256cm','Vendor Measured Voltage at 256 cm',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hFiberVendorAttenuation256cm.SetFillColor(2)
    self.__hFiberVendorAttenuation256cm.GetXaxis().SetTitle("Voltage (mv)")
    self.__nBins = 100
    self.__lowBin = 0.0
    self.__hiBin  = 20.0
    self.__hFiberVendorSigma = TH1F('self.__hFiberVendorSigma','Vendor Measured Fiber Sigma',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hFiberVendorSigma.SetFillColor(3)
    self.__hFiberVendorSigma.GetXaxis().SetTitle("Diameter Sigma (micron)")
    self.__nBins = 100
    self.__lowBin = 0.0
    self.__hiBin  = 0.01
    self.__hFiberVendorEccentricity = TH1F('self.__hFiberVendorEccentricity','Vendor Measured Fiber Eccentricity',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hFiberVendorEccentricity.SetFillColor(3)
##
## --------------------------------------------------------------------
##  A method to book the local measurement histograms....
##
  def bookLocalMeasurementsHistograms(self):
    self.__nBins = 100
    #cmj2022Jan18 self.__lowBin = 1.35e3
    #cmj2022jan18 self.__hiBin  = 1.45e3
    self.__lowBin = 1.35e3
    self.__hiBin  = 1.95e3
    self.__hFiberLocalDiameter = TH1F('self.__hFiberLocalDiameter','Locally Measured Diameter',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hFiberLocalDiameter.SetFillColor(2)
    self.__nXbins = 100
    self.__xLow = 0.0
    self.__xHi  = 50.0
    self.__nYbins = 1000
    self.__yLow = 0.0
    self.__yHi  = 2.0e4
    self.__hFiberLocalAttenuation = TH2F('self.__hFiberLocalAttenuation','Locally Measured Attenuation',self.__nXbins,self.__xLow,self.__xHi,self.__nYbins,self.__yLow,self.__yHi)
    self.__hFiberLocalAttenuation.SetFillColor(2)

    self.__hFiberVendorAttenuation = TH2F('self.__hFiberVendorAttenuation','Vendor Measured Attenuation',self.__nXbins,self.__xLow,self.__xHi,self.__nYbins,self.__yLow,self.__yHi)
    self.__hFiberVendorAttenuation.SetFillColor(2)

##
## --------------------------------------------------------------------
##  A method to book the histograms....
##
  def bookHistograms(self):
    self.__nBins = 200
    self.__lowBin = 0.0
    self.__hiBin  = 0.200
    self.__hVendorLightYield = TH1F('self.__hVendorLightYield','Vendor Measured Light Yield',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hVendorLightYield.SetFillColor(4)
    self.__nXbin = 60
    self.__Xlow = 400.0
    self.__Xhi = 700.0
    self.__nYbin = 200
    self.__Ylow =  0.0
    self.__Yhi = 30.0
    self.__hlocalWavelengthAttenuation = TH2F("self.__hlocalWavelengthAttenuation","Locally Measeured Attenaution vs. Wavelength",self.__nXbin,self.__Xlow,self.__Xhi,self.__nYbin,self.__Ylow,self.__Yhi)
    self.__hlocalWavelengthAttenuation.GetXaxis().SetTitle("Wavelength (nm)")
##
##
## --------------------------------------------------------------------
##  Fill the histograms!!!
##
  def fillHistograms(self):
    ##  Fill the vendor measurements first!
    for self.__vendorFiber in list(self.__fiberVendorId.keys()):
      self.__hFiberVendorDiameter.Fill(float(self.__fiberVendorDiameter[self.__vendorFiber]))
      self.__hFiberVendorSigma.Fill(float(self.__fiberVendorSigma[self.__vendorFiber]))
      self.__hFiberVendorAttenuationOneMeas.Fill(float(self.__fiberVendorAttenuation[self.__vendorFiber]))
      self.__hFiberVendorAttenuation256cm.Fill(float(self.__fiberVendorAttenuationVoltage256cm[self.__vendorFiber]))
      self.__hFiberVendorEccentricity.Fill(float(self.__fiberVendorEccentricity[self.__vendorFiber]))
    ##  Fill local measurements
    for self.__localFiber in list(self.__fiberLocalId.keys()):
      if(self.__localFiber != '-'):
       self.__hFiberLocalDiameter.Fill(float(self.__fiberLocalDiameter[self.__localFiber]))
       if(self.__cmjDebug > 1): print(("local fiber diameter = %f ") %( float(self.__fiberLocalDiameter[self.__localFiber]) ))
    ##
    for self.__Date in list(self.__localWavelengthTestDate.keys()):
      for self.__Fiber in list(self.__localWavelengthFiberId[self.__Date].keys()):
        for self.__Wavelength in list(self.__localWavelength[self.__Date][self.__Fiber].keys()):
          self.__hlocalWavelengthAttenuation.Fill(float(self.__Wavelength),float(self.__localWavelengthAttenuation[self.__Date][self.__Fiber][self.__Wavelength]))
    ## fill local ADC count vs Fiber length plot
    for self.__Date2 in list(self.__localFiberAttenuationTestDate.keys()):
      for self.__Fiber2 in list(self.__localFiberAttenuationId[self.__Date2].keys()):
        for self.__Length in list(self.__localFiberAttenuationLength[self.__Date2][self.__Fiber2].keys()):
          self.__hFiberLocalAttenuation.Fill(float(self.__Length),float(self.__localFiberAttenuationAdc[self.__Date2][self.__Fiber2][self.__Length]))
    ## fill Vendor Voltage vs Fiber length plot
    for self.__Date3 in list(self.__vendorFiberAttenuationTestDate.keys()):
      for self.__Fiber3 in list(self.__vendorFiberAttenuationId[self.__Date3].keys()):
        for self.__Length3 in list(self.__vendorFiberAttenuationLength[self.__Date3][self.__Fiber3].keys()):
          self.__hFiberVendorAttenuation.Fill(float(self.__Length3),float(self.__vendorFiberAttenuationAdc[self.__Date3][self.__Fiber3][self.__Length3]))
##
##
##
## --------------------------------------------------------------------
##  Draw one canvas for the vendor measurement results....
##  Draw multiple plots in pads onto the canvas
##
##    
  def drawVendorMeasurementCanvas(self):
    #self.__windowTitle = 'Extrusion Batch: '+str(self.__localExtrusionBatch)
    self.__windowTitle = 'Vendor Measurements'
    self.__cX = 200
    self.__cY = 10
    self.__cWidth = 700      ## canvas width
    self.__cHeight = 500      ## canvas height
    self.__c1 = TCanvas('self.__c1',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c1.Divide(3,2)  ## split canvas into pads....
    self.__c1.cd(1)
    self.__hFiberVendorAttenuationOneMeas.Draw()
    self.__c1.cd(2)
    self.__hFiberVendorAttenuation256cm.Draw()
    self.__c1.cd(3)
    self.__hFiberVendorDiameter.Draw()
    self.__c1.cd(4)
    self.__hFiberVendorSigma.Draw()
    self.__c1.cd(5)
    self.__hFiberVendorEccentricity.Draw()
    self.__c1.Print("outputFiles/fibers.png")
    ##
    self.__windowTitle = "Vendor Attenuation vs. Wavelength"
    self.__cY = 60
    self.__c3 = TCanvas('self.__c3',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)
    self.__hFiberVendorAttenuation.Draw()
    self.__c3.SetLogy()
    self.__c3.Print("outputFiles/VendorAttenVsLength.png")
    #self.defineVendorTree()
##
##
##
## --------------------------------------------------------------------
##  Draw one canvas for the vendor measurement results....
##  Draw multiple plots in pads onto the canvas
##
##    
  def drawLocalMeasurementCanvas(self):
    #self.__windowTitle = 'Extrusion Batch: '+str(self.__localExtrusionBatch)
    self.__windowTitle = 'Local Measurements'
    self.__cX = 300
    self.__cY = 10
    self.__cWidth = 700      ## canvas width
    self.__cHeight = 500      ## canvas height
    self.__c10 = TCanvas('self.__c10',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c10.Divide(2,1)  ## split canvas into pads....
    self.__c10.cd(1)
    self.__hFiberLocalDiameter.Draw()
    self.__c10.cd(2)
    self.__hFiberLocalAttenuation.Draw()
    self.__c10.cd(2).SetLogy()
    ##
    self.__windowTitle = "Local Attenuation vs. Wavelength"
    self.__cY = 60
    self.__c11 = TCanvas('self.__c11',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)
    self.__hlocalWavelengthAttenuation.Draw()
    self.__c11.SetLogy()
    self.__c11.Print("outputFiles/AttenuationVsWavelength.png")
    #self.defineLocalMeasurementree()  ## add define root tree for local measurements!!!!
##
## --------------------------------------------------------------------
##  This file defines the output root tree file and saves the root trees
##  in the individual programs....
  def makeRootTrees(self):
    ## Define output file name; tagged with the time
    self.__treeTime = myTime()
    self.__treeTime.getComputerTime()
    self.__saveTreeTime = self.__treeTime.getTimeForSavedFiles()
    self.__outRootTreeFileName = "outputFiles/FiberRootHistograms"+self.__saveTreeTime+".root"
    print(("makeRootTrees: output Root Tree File name = %s \n") % (self.__outRootTreeFileName))
    ## Define the root tree
    self.__rootTreeFile = TFile(self.__outRootTreeFileName,'RECREATE')
    self.defineVendorTree()
    self.defineLocalTree()
    self.defineWavelengthVsAttenuationTree()
    self.defineLocalAttenuationVsLengthTree()
    self.defineVendorAttenuationVsLengthTree()
    self.__rootTreeFile.Write()
    self.__rootTreeFile.Close()
    print(("makeRootTrees: wrote Root Tree File = %s \n") % (self.__outRootTreeFileName))
    
##
## --------------------------------------------------------------------
##  Define Root TTree... Fill it with the arrays defined previously
##      then filled from the database.... then write and save the root 
##      tree file.....
##            This writes a regular root tree!
##  This is the vendor measurements
  def defineVendorTree(self):
##
    self.__vendorRootTree = TTree('Vendor Fiber Measurements','root tree with ntuples') ## define the root tree!
##
    ## numerical values
    self.__arrayNumberOfEntries = array('i',[0])
    self.__arrayFiberVendorDiameter = array('f',[0])
    self.__arrayFiberVendorAttenuation = array('f',[0])
    self.__arrayfiberVendorAttenuationVoltage256cm = array('f',[0])
    self.__arrayfiberVendorSigma = array('f',[0])
    self.__arrayfiberVendorEccentricity = array('f',[0])
    ## save strings
    localFiberId = _root.vector('string')()  ## cmj2022Jan18
    localProductionDate = _root.vector('string')() ## cmj2022Jan18
    #localFiberType = _root.vector('string')()
    localFiberComments = _root.vector('string')() ## cmj2022Jan18
##
##
##      Define the branches
    self.__vendorRootTree.Branch('numberOfEntries',self.__arrayNumberOfEntries,'self.__arrayNumberOfEntries[1]/i')
    self.__vendorRootTree.Branch('fiberId',localFiberId)
    self.__vendorRootTree.Branch('fiberProductionDate',localProductionDate)
    #self.__vendorRootTree.Branch('fiberType',localFiberType)
    self.__vendorRootTree.Branch('fiberComments',localFiberComments)
    self.__vendorRootTree.Branch('fiberVendorDiameter',self.__arrayFiberVendorDiameter,'self.__arrayFiberVendorDiameter[1]/F')
    self.__vendorRootTree.Branch('fiberVendorSigma',self.__arrayfiberVendorSigma,'self.__arrayfiberVendorSigma[1]/F')
    self.__vendorRootTree.Branch('fiberVendorAttenuation',self.__arrayFiberVendorAttenuation,'self.__arrayFiberVendorAttenuation[1]/F')
    self.__vendorRootTree.Branch('fiberVendorAttenuationVolt285cm',self.__arrayfiberVendorAttenuationVoltage256cm,'self.__arrayfiberVendorAttenuationVoltage256cm[1]/F')
    self.__vendorRootTree.Branch('fiberVendorEccentricity',self.__arrayfiberVendorEccentricity,'self.__arrayfiberVendorEccentricity[1]/F')
    ##  Fill root tree arrays...
    for self.__counter in list(self.__fiberVendorId.keys()):
      self.__arrayFiberVendorDiameter[0] = float(self.__fiberVendorDiameter[self.__counter])
      self.__arrayFiberVendorAttenuation[0] = float(self.__fiberVendorAttenuation[self.__counter])
      self.__arrayfiberVendorAttenuationVoltage256cm[0] = float(self.__fiberVendorAttenuationVoltage256cm [self.__counter])
      self.__arrayfiberVendorSigma[0] = float(self.__fiberVendorSigma[self.__counter])
      self.__arrayfiberVendorEccentricity[0] = float(self.__fiberVendorEccentricity[self.__counter])
      ## fill strings
      localFiberId.push_back(self.__counter)
      localProductionDate.push_back(self.__fiberProductionDate[self.__counter])
      localFiberComments.push_back(self.__fiberVendorComments[self.__counter])
      self.__arrayNumberOfEntries[0] = len(self.__plotFiberId)
      self.__vendorRootTree.Fill()            ## fill the root tree here...
    #print("after filling the tree \n")
    #self.__vendorRootTree.Scan("")
    self.__vendorRootTree.Write()
    return
##
## --------------------------------------------------------------------
##  Define Root TTree... Fill it with the arrays defined previously
##      then filled from the database.... then write and save the root 
##      tree file.....
##            This writes a regular root tree!
##  This is the local measurements
  def defineLocalTree(self):
##
    self.__localRootTree = TTree('Local Fiber Measurement','root tree with ntuples') ## define the root tree!
##
##      Define the arrays contained in each branch from previosly loaded list
    ## numerical values
    self.__arrayNumberOfEntries = array('i',[0])
    self.__arrayFiberLocalDiameter = array('f',[0]) 
    self.__arrayFiberLocalAttenuation = array('f',[0])
    ## define string values
    localFiberTestDate = _root.vector('string')()
    localFiberId = _root.vector('string')()
    localFiberComment = _root.vector('string')()
##
##
##      Define the branches
    self.__localRootTree.Branch('numberOfEntriesl',self.__arrayNumberOfEntries,'self.__arrayNumberOfEntries[1]/i')
    self.__localRootTree.Branch('LocalDiameter',self.__arrayFiberLocalDiameter,'self.__arrayFiberLocalDiameter[1]/F')
    self.__localRootTree.Branch('LocalAttenuation',self.__arrayFiberLocalAttenuation,'self.__arrayFiberLocalAttenuation[1]/F')
    self.__localRootTree.Branch('fiberId',localFiberId)
    self.__localRootTree.Branch('testDate',localFiberTestDate)
    self.__localRootTree.Branch('comment',localFiberTestDate)
    ##  Fill root tree arrays...
    for self.__counter in list(self.__fiberLocalId.keys()):
      self.__arrayFiberLocalDiameter[0] = float(self.__fiberLocalDiameter[self.__counter])
      self.__arrayFiberLocalAttenuation[0] = float(self.__fiberLocalAttenuation[self.__counter])
##	Fill the strings...
      if(self.__cmjDebug > 2) :
        print(("...defineLocalTree: self.__counter = %s" ) % (self.__counter))
        print(("...defineLocalTree: self.__fiberLocalTestDate[self.__counter] = %s" ) % (self.__fiberLocalTestDate[self.__counter]))
        print(("...defineLocalTree: self.__fiberLocalComments[self.__counter] = %s" ) % (self.__fiberLocalComments[self.__counter]))
      #localString.push_back(self.__counter)
      localFiberId.push_back(self.__counter)
      localFiberTestDate.push_back(str(self.__fiberLocalTestDate[self.__counter]))
      localFiberComment.push_back(str(self.__fiberLocalComments[self.__counter]))
      self.__localRootTree.Fill()            ## fill the root tree here...
    #print("after filling the tree \n")
    #self.__localRootTree.Scan('','','colsize = 30')
    self.__localRootTree.Write()
    return

##
## --------------------------------------------------------------------
##  Define the Wavelength vs Attenuation Root trees...
##  This method will write a root tree for each test date.
##  This is a lot of root trees, that will be sorted in the root macro script.
  def defineWavelengthVsAttenuationTree(self):
##
    localFiberId = _root.vector('string')()
    localTestDate = _root.vector('string')()
    for self.__n in list(self.__localWavelengthTestDate.keys()):
      for self.__m in list(self.__localWavelengthFiberId[self.__n].keys()):
        self.__localFolderDate = self.__n
        self.__localFolderDate.replace(' ','-')
        self.__localFolderDate.replace(':','-')
        ## define the root tree for the attenuation vs wavelength
        self.__localAttenuationVsWavelengthRootTreeName = 'Fiber-WavelengthVsAtten_'+self.__m+'_'+self.__localFolderDate
        if(self.__cmjDebug > 2): print(('...  defineWavelengthVsAttenuationTree... open root tree:  %s \n') % self.__localAttenuationVsWavelengthRootTreeName )
        self.__localAttenuationVsWavelengthRootTree = TTree(self.__localAttenuationVsWavelengthRootTreeName,'root tree with vectors')
        ## arrays for the attenuation vs wavelength
        #self.__tempNumberOfEntries = len(self.__plotAttenuationVsWavelength_wavelength)
        self.__arrayNumberOfEntries = array('i',[0])
        self.__plotAttenuationVsWavelength_wavelength = []
        self.__plotAttenuationVsWavelength_attenuation = []
        self.__arrayAttenuationVsWavelength_wavelength = array('f',self.__plotAttenuationVsWavelength_wavelength)
        self.__arrayAttenuationVsWavelength_attenuation = array('f',self.__plotAttenuationVsWavelength_attenuation)
        for self.__j in list(self.__localWavelength[self.__n][self.__m].keys()):
          self.__plotAttenuationVsWavelength_wavelength.append(float(self.__localWavelength[self.__n][self.__m][self.__j]))
          self.__plotAttenuationVsWavelength_attenuation.append(float(self.__localWavelengthAttenuation[self.__n][self.__m][self.__j]))
          self.__arrayAttenuationVsWavelength_wavelength.append(float(self.__localWavelength[self.__n][self.__m][self.__j]))
          self.__arrayAttenuationVsWavelength_attenuation.append(float(self.__localWavelengthAttenuation[self.__n][self.__m][self.__j]))
          localFiberId.push_back(self.__n)      # load fiber id string
          localTestDate.push_back(self.__m)   # load wavelength string
          if(self.__cmjDebug > 2) : print(("... defineWavelengthVsAttenuationTree: float(self.__localWavelength[self.__n][self.__m][self.__j]) = %f") % (float(self.__localWavelength[self.__n][self.__m][self.__j])))
        self.__numberOfEntries = len(self.__plotAttenuationVsWavelength_wavelength)
        ## define branches
        self.__numberOfEntries = array('i',self.__numberOfEntries*[0])
        self.__localAttenuationVsWavelengthRootTree.Branch('numberOfEntries',self.__arrayNumberOfEntries,'self.__numberOfEntries/I')
        self.__localAttenuationVsWavelengthRootTree.Branch('fiberId',localFiberId)
        self.__localAttenuationVsWavelengthRootTree.Branch('testDate',localTestDate)
        self.__localAttenuationVsWavelengthRootTree.Branch('wavelength',self.__arrayAttenuationVsWavelength_wavelength,'self.__arrayAttenuationVsWavelength_wavelength[self.__numberOfEntries]/F')
        self.__localAttenuationVsWavelengthRootTree.Branch('attenuation',self.__arrayAttenuationVsWavelength_attenuation,'self.__arrayAttenuationVsWavelength_attenuation[self.__numberOfEntries]/F')
        ##
        self.__arrayNumberOfEntries[0] = len(self.__plotAttenuationVsWavelength_wavelength)
        self.__localAttenuationVsWavelengthRootTree.Fill()
        self.__localAttenuationVsWavelengthRootTree.Write()
    return


##
## --------------------------------------------------------------------
##  Define the Local Attenuation vs Length Root trees...
##  This is the Local (UVa) ADC count vs Fiber length
##  This method will write a root tree for each test date.
##  This is a lot of root trees, that will be sorted in the root macro script.
  def defineLocalAttenuationVsLengthTree(self):
##
    localFiberId = _root.vector('string')()
    localTestDate = _root.vector('string')()
    for self.__n in list(self.__localFiberAttenuationTestDate.keys()):
      for self.__m in list(self.__localFiberAttenuationId[self.__n].keys()):
        self.__localFolderDate = self.__n
        self.__localFolderDate.replace(' ','-')
        self.__localFolderDate.replace(':','-')
        ## define the root tree for the attenuation vs wavelength
        self.__localFiberAttenuationLengthVsAdcRootTree = TTree('Fiber-LocalAttenVsLength_'+self.__m+'_'+self.__localFolderDate,'root tree with vectors; local attenuation')
        ## arrays for the attenuation vs wavelength
        self.__arrayNumberOfEntries = array('i',[0])
        self.__plotLocalFiberAttenuation_length = []
        self.__plotLocalFiberAttenuation_adc = []
        self.__arrayLocalFiberAttenuation_length = array('f',self.__plotLocalFiberAttenuation_length)
        self.__arrayLocalFiberAttenuation_adc = array('f',self.__plotLocalFiberAttenuation_adc)
        for self.__j in list(self.__localFiberAttenuationLength[self.__n][self.__m].keys()):
          self.__plotLocalFiberAttenuation_length.append(float(self.__localFiberAttenuationLength[self.__n][self.__m][self.__j]))
          self.__plotLocalFiberAttenuation_adc.append(float(self.__localFiberAttenuationAdc[self.__n][self.__m][self.__j]))
          self.__arrayLocalFiberAttenuation_length.append(float(self.__localFiberAttenuationLength[self.__n][self.__m][self.__j]))
          self.__arrayLocalFiberAttenuation_adc.append(float(self.__localFiberAttenuationAdc[self.__n][self.__m][self.__j]))
          localFiberId.push_back(self.__m)
          localTestDate.push_back(self.__n)
        self.__numberOfEntries = len(self.__plotLocalFiberAttenuation_length)
        ## define branches
        self.__numberOfEntries = array('i',self.__numberOfEntries*[0])
        self.__localFiberAttenuationLengthVsAdcRootTree.Branch('numberOfEntries',self.__arrayNumberOfEntries,'self.__numberOfEntries/I')
        self.__localFiberAttenuationLengthVsAdcRootTree.Branch('testDate',localTestDate)
        self.__localFiberAttenuationLengthVsAdcRootTree.Branch('fiberId',localFiberId)
        self.__localFiberAttenuationLengthVsAdcRootTree.Branch('fiberLength',self.__arrayLocalFiberAttenuation_length,'self.__arrayLocalFiberAttenuation_length[self.__numberOfEntries]/F')
        self.__localFiberAttenuationLengthVsAdcRootTree.Branch('adcCount',self.__arrayLocalFiberAttenuation_adc,'self.__arrayLocalFiberAttenuation_adc[self.__numberOfEntries]/F')
        self.__arrayNumberOfEntries[0] = len(self.__plotLocalFiberAttenuation_length)
        self.__localFiberAttenuationLengthVsAdcRootTree.Fill()
        self.__localFiberAttenuationLengthVsAdcRootTree.Write()
    return
##
##
## --------------------------------------------------------------------
##  Define the Vendor Attenuation vs Length Root trees...
##  This is the Vendor (Hamamatsu) Voltage (mv) vs Fiber length
##  This method will write a root tree for each test date.
##  This is a lot of root trees, that will be sorted in the root macro script.
  def defineVendorAttenuationVsLengthTree(self):
##
    localFiberId = _root.vector('string')()
    localTestDate = _root.vector('string')()
    for self.__n in list(self.__vendorFiberAttenuationTestDate.keys()):
      if(self.__cmjDebug > 2) : print(("... defineVendorAttenuationVsLengthTree: self.__n = %s") % self.__n)
      for self.__m in list(self.__vendorFiberAttenuationId[self.__n].keys()):
        if(self.__cmjDebug > 2) : print(("... defineVendorAttenuationVsLengthTree: self.__m = %s") % self.__m)
        self.__localFolderDate = self.__n
        self.__localFolderDate.replace(' ','-')
        self.__localFolderDate.replace(':','-')
        ## define the root tree for the attenuation vs wavelength
        self.__vendorFiberAttenuationLengthVsAdcRootTree = TTree('Fiber-VendorAttenVsLength_'+self.__m+'_'+self.__localFolderDate,'root tree with vectors: vendor attenuation')
        ## arrays for the attenuation vs wavelength
        self.__arrayNumberOfEntries = array('i',[0])
        self.__plotVendorFiberAttenuation_length = []        ##print("len(self.__plotAttenuationVsWavelength_wavelength) = %d") %(len(self.__plotAttenuationVsWavelength_wavelength))
        self.__plotVendorFiberAttenuation_adc = []
        self.__arrayVendorFiberAttenuation_length = array('f',self.__plotVendorFiberAttenuation_length)
        self.__arrayVendorFiberAttenuation_adc = array('f',self.__plotVendorFiberAttenuation_adc)
        for self.__j in list(self.__vendorFiberAttenuationLength[self.__n][self.__m].keys()):
          self.__plotVendorFiberAttenuation_length.append(float(self.__vendorFiberAttenuationLength[self.__n][self.__m][self.__j]))
          self.__plotVendorFiberAttenuation_adc.append(float(self.__vendorFiberAttenuationAdc[self.__n][self.__m][self.__j]))
          self.__arrayVendorFiberAttenuation_length.append(float(self.__vendorFiberAttenuationLength[self.__n][self.__m][self.__j]))
          self.__arrayVendorFiberAttenuation_adc.append(float(self.__vendorFiberAttenuationAdc[self.__n][self.__m][self.__j]))
          localFiberId.push_back(self.__m)
          localTestDate.push_back(self.__n)
        self.__numberOfEntries = len(self.__plotVendorFiberAttenuation_length)
        ## define branches
        self.__numberOfEntries = array('i',self.__numberOfEntries*[0])
        self.__vendorFiberAttenuationLengthVsAdcRootTree.Branch('VnumberOfEntries',self.__arrayNumberOfEntries,'self.__numberOfEntries/I')
        self.__vendorFiberAttenuationLengthVsAdcRootTree.Branch('fiberId',localFiberId)
        self.__vendorFiberAttenuationLengthVsAdcRootTree.Branch('testDate',localTestDate)
        self.__vendorFiberAttenuationLengthVsAdcRootTree.Branch('fiberLength',self.__arrayVendorFiberAttenuation_length,'self.__arrayLocalFiberAttenuation_length[self.__numberOfEntries]/F')
        self.__vendorFiberAttenuationLengthVsAdcRootTree.Branch('adcCount',self.__arrayVendorFiberAttenuation_adc,'self.__arrayLocalFiberAttenuation_adc[self.__numberOfEntries]/F')
        self.__arrayNumberOfEntries[0] = len(self.__plotVendorFiberAttenuation_length)
        self.__vendorFiberAttenuationLengthVsAdcRootTree.Fill()
        self.__vendorFiberAttenuationLengthVsAdcRootTree.Write()
    return
#
## --------------------------------------------------------------------
##
  def turnOnDebug(self,tempDebug):
    self.__database_config.setDebugOn()
    self.__cmjDebug = tempDebug
##
## --------------------------------------------------------------------
##
  def turnOnTestMode(self):
    self.__cmjTest = 1
##
##
## --------------------------------------------------------------------
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('--debug',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set test: 0 (off - default), 1 = on')
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  options, args = parser.parse_args()
  print(("'__main__': options.debugMode = %s \n") % (options.debugMode))
  print(("'__main__': options.database  = %s \n") % (options.database))
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry("+100+500")  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.debugMode != 0): myMultiForm.turnOnDebug(options.debugMode)
  if(options.testMode != 0): myMultiForm.turnOnTestMode()
  if(options.database == "development"): myMultiForm.setupDevelopmentDatabase()
  else: myMultiForm.setupProductionDatabase()
  myMultiForm.grid()
  root.mainloop()
