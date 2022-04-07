# -*- coding: utf-8 -*-
## File = "SipmQuerryRoot.py"
##
##  Modified by cmj2018Mar28... Changed the directory structure and calls DataLoader versions so these could be accounted for.
##	This version uses the old hdbClient_v1_3a
##  Modifed by cmj2018Mar28... Change "crvUtilities2017.zip" to "crvUtilities.zip"
##   Modified by cmj2018May30... Change to hdbClient_v2_0
##	
## Derived from File = "SipmQuerryRoot2017Jul27.py"\
## Derived from File = "SipmQuerry2017Jul22.py"
## Derived from File = "SipmQuerry2017Jul22.py"
## Derived from File = "extrusionQuerry2017Jul22.py"
## Derived from File = "extrusionQuerry2017Jul19.py"
##
##	Use matplotlib to plot graphs
##	Re-arrange the GUI...
##	Inlucde a list box to display all avaialble batches
##	Plot with PyRoot!
##
##  Modified by cmj to add root extras!
##
## Derived from File = "extrusionQuerry2017Jul16.py"
## Derived from File = "extrusionQuerry2017Jul16.py"
## Derived from File = "extrusionQuerry2017Jul15.py"
## Derived from File = "extrusionQuerry2017Jul14.py"
## Derived from File = "extrusionQuerry2017Jul13.py"
##
#!/usr/bin/env python
##
##	A python script that uses a Graphical User Interface
##	to allow querry of the Sipm database and plot 
##	the test results..
##
##	Written by 	Merrill Jenkins
##			Department of Physics
##			University of South Alabama
##
##	Modified by cmj2018May31.... Include new Sipm Measurements types
##  Modified by cmj2018Jul26... Initialize bytearry strings with each event in root tree
##  Modified by cmj2018Oct5... Fix bug... return the Production database Query URL instead of the Write URL
##  Modified by cmj2018Oct9.... Change to hdbClient_v2_2
##  Modified by cmj2020Jun16... Change to cmjGuiLibGrid2019Jan30
##  Modified by cmj2020Jul13... Add progress bar
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##
from Tkinter import *         # get widget class
import Tkinter as tk
from ttk import *             # get tkk widget class (for progess bar)
import sys
from collections import defaultdict  ## needed for two dimensional dictionaries
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul02 add highlight to scrolled list
from DataLoader import *
from databaseConfig import *
from cmjGuiLibGrid import *      ## 2020Aug03
from generalUtilities import generalUtilities  ## this is needed for three dimensional dictionaries
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import time
import array
##		Import the graphing modules
##  Import for PyRoot
from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH2F, TGraph, TStyle, TTree, TString
from ROOT import gROOT, gBenchmark, gRandom, gSystem, gStyle, Double
from array import array
##
##
ProgramName = "SipmQueryRoot"
Version = "version2020.12.16"
##
##
##
##
## -------------------------------------------------------------
## 	A class to set up the main window to drive the
##	python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__database_config  = databaseConfig()
    self.setupDevelopmentDatabase()  ## set up communications with database
    self.__cmjPlotDiag = 0 ## default... not debug messages printed out
			##  Limit number of sipms read in for tests.... set negative to read all
    self.__cmjTest = 0	## set this to 1 to look at 10 sipm_id's
    self.__progressBarCount = tk.DoubleVar()  ## for progress bar
    self.__progressBarCount.set(0)            ## for progress ba
    ## set up geometry for GUI
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
##	Arrays to plot...keep these in scope in the whole class
    self.__sipmMeasureTestDate = {}		## first key of the nested dictionaries
    self.__saveTestType = {} ## dictionary of test types; key sipmMeasureDate
##	Define a series of nested dictionaries to hold various quantities:
##		keys [sipmMeasureDate][sipmId]
    self.__sipmId = defaultdict(dict)         ## second key for nested dictionaries
    self.__sipmNumber = defaultdict(dict)
    self.__testType = defaultdict(dict)
    self.__workerBarCode = defaultdict(dict)
    self.__workStationBarCode = defaultdict(dict)
    self.__biasVoltage = defaultdict(dict)
    self.__darkCount = defaultdict(dict)
    self.__gain = defaultdict(dict)
    self.__temperature = defaultdict(dict)
    self.__breakdown_voltage = defaultdict(dict)
    self.__dark_count_rate = defaultdict(dict)
    self.__current_vs_voltage_condition = defaultdict(dict)
    self.__x_talk = defaultdict(dict)
    self.__led_response = defaultdict(dict)
    self.__data_file_location = defaultdict(dict)
    self.__data_file_name = defaultdict(dict)
    self.__pack_number = defaultdict(dict)
##	Nested Dictionaries to save I vs V data for each sipm, each test
##	The keys to these dictionaries are [sipmMeasureDate][SipmId][binNumber]
    self.__sipmMeasureTestDate_IvsV = {}  ## first key in triple nested dictionary
    self.__sipmId_IvsV = defaultdict(dict) ## second key in triple nested dictionary [sipmMeasureDate][SipmId]
    self.__myMultiDimDictionary = generalUtilities()
    self.__IvsV_current = self.__myMultiDimDictionary.nestedDict()
    self.__IvsV_voltage = self.__myMultiDimDictionary.nestedDict()
##	Most times the Sipms are tested once, but at different times....
##	save all local tests in one root tree with the test date tagged.
    self.__allSipmId = {} ## key [testDate+sipmId[testDate]]
    self.__allSipmMeasureTestDate = {}  ## key [testDate+sipmId[testDate]]
    self.__allTestType = {} # key [testDate+sipmId[testDate]
    self.__allWorkerBarCode = {} ## key [testDate+sipmId[testDate]]
    self.__allWorkStationBarCode = {} ## key [testDate+sipmId[testDate]]
    self.__allBiasVoltage = {} ## key [testDate+sipmId[testDate]]
    self.__allDarkCount = {} ## key [testDate+sipmId[testDate]]
    self.__allGain = {} ## key [testDate+sipmId[testDate]]
    self.__allTemperature = {} ## key [testDate+sipmId[testDate]])
    self.__allBreakdown_voltage = {} ## key [testDate+sipmId[testDate]]
    self.__allDark_count_rate = {} ## key [testDate+sipmId[testDate]]
    self.__allCurrent_vs_voltage_condition = {} ## key [testDate+sipmId[testDate]]
    self.__allX_talk = {} ## key [testDate+sipmId[testDate]]
    self.__allLed_response = {} ## key [testDate+sipmId[testDate]]
    self.__allData_file_location = {} ## key [testDate+sipmId[testDate]]
    self.__allData_file_name = {} ## key [testDate+sipmId[testDate]]
    self.__allPack_number = {} ## key [testDate+sipmId[testDate]]
##	Nested Dictionaries to save I vs V data for each sipm, each test
##	The keys to these dictionaries are [ivsvTestDate+sipmId[testDate]][binNumber]
    self.__All_IvsV_current = defaultdict(dict)
    self.__All_IvsV_voltage = defaultdict(dict)
##
    self.__sipmResults = []
    self.__sipmPackNumberResults = {}  ## dictionary to hold pack number: Key SipmId
    self.__sipmIvsVresults =[]
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
##
##	First Column...
    self.__col = 0
    self.__firstRow = 0
##
##	Instruction Box...
    self.__myInstructions = myScrolledText(self)
    self.__myInstructions.setTextBoxWidth(50)
    self.__myInstructions.makeWidgets()
    self.__myInstructions.setText('','Instructions/InstructionsForSipmRootQuerry2017Jun28.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__strName.append("Sipm PO")
    self.__labelWidth = 15
    self.__SipmBatchStr = myStringEntry(self,self.__firstRow,self.__col,self.__mySaveIt)
    self.__SipmBatchStr.setEntryText(self.__strName[self.__sCount])
    self.__SipmBatchStr.setLabelWidth(self.__labelWidth)
    self.__SipmBatchStr.setEntryWidth(self.__entryWidth)
    self.__SipmBatchStr.setButtonWidth(self.__buttonWidth)
    self.__SipmBatchStr.makeEntry()
    self.__SipmBatchStr.grid(row=self.__firstRow,column=self.__col,stick=W,columnspan=2)
    self.__firstRow += 1
##	Add list box to first columnspan
##	This sequence presents a list box filled with the
##	available batches.  A left double click appends a
##	another comma separated batch...
##	Click the "Batches button" to load the list of batches
    self.__tempBatchResults = []
    self.__tempBatchResults = self.getSipmsBatchesFromDatabase()
    if(self.__cmjPlotDiag != 0) : print("self.__tempBatchResults = %s \n") % (self.__tempBatchResults)
    self.__myOptions = []
    for self.__m in self.__tempBatchResults:
      self.__temp = self.__m.rsplit(",",8)
      self.__myOptions.append(self.__temp[0])
    self.__myScrolledList = ScrolledList(self,self.__myOptions)
    self.__myScrolledList.grid(row=self.__firstRow,column=self.__col,sticky=W,rowspan=4)
##	New Row
##	Add button to get available batches...
##	Enter the request for batches to be histogrammed.
##	A single batch or a string of comma separated multiple batches
##	may be selected for histogramming.
    self.__col = 1
    self.__secondRow = 2
    self.__buttonWidth = 10
    self.__getValues = Button(self,text='Batches',command=self.loadSipmBatchRequest,width=self.__buttonWidth,bg='lightblue',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Plot scatter plots
    self.__getValues = Button(self,text='Scatter Plots',command=self.getScatterPlots,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Plot histograms
    self.__getValues = Button(self,text='Histograms',command=self.getHistograms,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Third Column...
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
#         Display the date the script is being run
    self.__date = myDate(self,self.__row,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__row,column=self.__col,sticky=E)
    self.__col = 0
    self.__row += 1
    self.__buttonWidth = 10
    ##  Add progress bar
    #self.__progressbarStyle = Style()
    #self.__progressbarStyle.configure("red.Horizontal.TProgressBar",background="red",forground="black")
    #self.__progressbar = Progressbar(self.__frame0,orient=HORIZONTAL,length=200,maximum=300,variable=self.__progressBarCount,mode='determinate')
    self.__row = 6
    tempSipmRows = 100*self.countTheSimps()
    self.__progressbarStyle = Style()
    self.__progressbarStyle.theme_use('clam')
    #self.__progressbarStyle.configure("green.Horizontal.TProgressbar",background="green")
    #self.__progressbar = Progressbar(self,style="green.Horizontal.TProgressBar",orient=HORIZONTAL,length=500,maximum=tempSipmRows,variable=self.__progressBarCount,mode='determinate')
    self.__progressbar = Progressbar(self,orient=HORIZONTAL,length=500,maximum=10000,variable=self.__progressBarCount,mode='determinate')
    self.__progressbar.grid(row=self.__row,column=0,columnspan=10,sticky=W)
##	Add Control Bar at the bottom...
    self.__col = 0
    self.__firstRow = 7
    self.__quitNow = Quitter(self,0,self.__col)
    self.__quitNow.grid(row=self.__firstRow,column=0,sticky=W)
##
## -------------------------------------------------------------------
##	Make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Sipm Tables"
    self.__whichDatabase = 'development'
    print("...multiWindow::getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
##
## -------------------------------------------------------------------
##	Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Sipm Tables"
    self.__whichDatabase = 'production'
    print("...multiWindow::getFromProductionDatabase... get from production database \n")
    self.__url = self.__database_config.getProductionQueryUrl()
## ---------------------------------------------------------------------------
##  Get the total number of rows for the progress bar... 
##  In the future update this to get the number of rows with 
##  the selected batchs
  def countTheSimps(self):
    self.__getDatabaseValue = DataQuery(self.__queryUrl)
    self.__tables = "sipms"
    if(self.__cmjPlotDiag > 2) : print("...multiWindow::countTheSipms: self.__database = %s self.__tables = %s \n") % (self.__database, self.__tables)
    self.__SipmRows = self.__getDatabaseValue.query(self.__database,self.__tables,'count(*)')
    if(self.__cmjPlotDiag > 2) : print("...multiWindow::countTheSipms::Query Results:")
    for self.__SipmRow in self.__SipmRows:
      print(self.__SipmRow)
    if(self.__cmjPlotDiag > 1): print("...multiWindow::countExtrusion__:countTheSipms:: number of rows = %s ") % self.__SipmRows
    tempSipmRows = float(self.__SipmRows[0])
    return(tempSipmRows)
##
## -------------------------------------------------------------------
##	Load batches requested from batch window
##	This it the list of batches that will be histogrammed...
  def loadSipmBatchRequest(self):
    if(self.__cmjPlotDiag != 0):
      print ("... loadSipmBatchRequest ")
      print ("... loadSipmBatchRequest:mySaveIt.getStrEntry = %s ") % (self.__mySaveIt.getStrEntry("Sipm Batch"))
      print ("... loadSipmBatchRequest:self.__myScrolledList.fetchList() = %s \n") %(self.__myScrolledList.fetchList())
    if(self.__mySaveIt.getStrEntry('Sipm Batch') != "NULL"):
      if(self.__cmjPlotDiag > 0):
	print "from mySaveIt \n"
	print ("... mySaveIt.getStrEntry = %s \n") % (self.__mySaveIt.getStrEntry("Sipm Batch"))
      self.__sipmBatchRequest = self.__mySaveIt.getStrEntry('Sipm Batch').rsplit(",",self.__numberOfBatches)
    elif (self.__myScrolledList.fetchList() != "NULL"):
      if(self.__cmjPlotDiag > 0) : print ("from myScrolledList")
      self.__sipmBatchRequest = self.__myScrolledList.fetchList().rsplit(",",self.__numberOfBatches)
    else:
      print "error: enter a correct batch name!!! \n"
      return
    if(self.__cmjPlotDiag != 0): print ("... loadSipmBatchRequest len(self.__sipmBatchRequest) = %d ") % (len(self.__sipmBatchRequest))
    for self.__localSipmBatch in self.__sipmBatchRequest:
      self.getSipmsFromDatabase(self.__localSipmBatch) 
      self.getSipmsPackNumberFromDatabase(self.__localSipmBatch)
      self.getIvsVforSipm(self.__localSipmBatch)
    self.unpackSipms()
    self.unpackSipmIvsV()
    return
##
## -------------------------------------------------------------------
##	Make querries to get all sipm batches to data base
  def getSipmsBatchesFromDatabase(self):
    if(self.__cmjPlotDiag > 0): print("... multiWindow::getSipmBatchesFromDatabase \n") 
    self.__getSipmBatchValues = DataQuery(self.__queryUrl)
    self.__localSipmBatchValues = []
    self.__table = "sipm_batches"
    self.__fetchThese = "po_number"
    self.__fetchCondition = 'date_received:gt:2015-08-15'  ## works!!!
    self.__numberReturned = 0
    if(self.__cmjPlotDiag > 0):
      print (".... getSipmsBatchesFromDatabase: self.__queryUrl   = %s \n") % (self.__queryUrl)
      print (".... getSipmsBatchesFromDatabase: self.__table                = %s \n") % (self.__table)
      print (".... getSipmsBatchesFromDatabase: self.__fetchThese           = %s \n") % (self.__fetchThese)
      print (".... getSipmsBatchesFromDatabase: self.__fetchCondition       = %s \n") % (self.__fetchCondition)
    self.__localSipmBatchValues = self.__getSipmBatchValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjPlotDiag > 1): 
	print (".... getSipmsBatchesFromDatabase: self.__getSipmBatchValues   = %s \n") % (self.__getSipmBatchValues)
	print (".... getSipmsBatchesFromDatabase: self.__table                = %s \n") % (self.__table)
	print (".... getSipmsBatchesFromDatabase: self.__fetchThese           = %s \n") % (self.__fetchThese)
	print (".... getSipmsBatchesFromDatabase: self.__fetchCondition       = %s \n") % (self.__fetchCondition)
	print (".... getSipmsBatchesFromDatabase: self.__localSipmBatchValues = %s \n") % (self.__localSipmBatchValues)
    self.__numberOfBatches = len(self.__localSipmBatchValues)
    xx = self.__progressBarCount.get()  ## get current count value for progress bar
    self.__progressBarCount.set(xx+10)  ## increment that value
    self.update() ## update the progress bar...
    if(self.__cmjPlotDiag > 1):
      for self.__l in self.__localSipmBatchValues:
	print self.__l
    return self.__localSipmBatchValues
##
## -------------------------------------------------------------------
##	Make querries to data base to get the sipm information
  def getSipmsFromDatabase(self,tempBatch):
    self.__singleSipmNumber = []
    self.__singleSipmNumber = self.getSipmNumberFromPo(tempBatch)  ## get list of Sipms with same PO
    if(self.__cmjPlotDiag > 4) : 
      print (" ------------------------------------------------------------ ")
      print (".... getSipmsFromDatabase: List of Sipms with PO Number = %s \n") %(tempBatch)
      print (".... getSipmsFromDatabase: len(self.__singleSipmNumber) = %d ") % (len(self.__singleSipmNumber))
      for self.__l in sorted(self.__singleSipmNumber):
	print (".... getSipmsFromDatabase: self.__l  = %s ") % (self.__l)
    self.__getSipmValues = DataQuery(self.__queryUrl)
    self.__table = "sipm_measure_tests"
    self.__fetchThese = "sipm_id,measure_test_date,test_type,worker_barcode,workstation_barcode,"
    self.__fetchThese += "bias_voltage,dark_count,gain,temp_degc,breakdown_voltage,dark_count_rate,"
    self.__fetchThese += "current_vs_voltage_condition,x_talk,led_response,data_file_location,"
    self.__fetchThese += "data_file_name"
    ## loop over all SipmId's with the sampe PO number
    for self.__localSipmNumber in self.__singleSipmNumber:
      if(self.__localSipmNumber != "NULL" and self.__localSipmNumber != ''):
	print(".... getSipmsFromDatabase: get sipm_id  = %s") % (self.__localSipmNumber)
	self.__localSipmResult = []
	self.__fetchCondition = "sipm_id:eq:"+str(self.__localSipmNumber)
	if (self.__cmjPlotDiag > 4):
	  print(".... getSipmsFromDatabase: self.__table  = %s \n") % (self.__table)
	  print(".... getSipmsFromDatabase: self.__fetchThese  = %s \n") % (self.__fetchThese)
	  print(".... getSipmsFromDatabase: self.__fetchCondition = %s \n") % (self.__fetchCondition)
	##  This call returns a list with the database entries for all lines with the same sipm_id plus other
	##   list members that are either white characters, quotations or forward slashes.. They must be
	##   filtered out before sending them to the "unpackSipms" member function....
	self.__localSipmResult = self.__getSipmValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
	self.__singleSipmLine = []
	if(self.__cmjPlotDiag > 4): print(".... getSipmsFromDatabase: len(self.__localSipmResult) = %d, self.__localSipmResult  = %s \n") % (len(self.__localSipmResult),self.__localSipmResult)
	self.__mcount = 0
	self.__ncount = 0
	for self.__mline in sorted(self.__localSipmResult):
	  xx = self.__progressBarCount.get()  ## get current count value for progress bar
	  self.__progressBarCount.set(xx+10)  ## increment that value
	  self.update() ## update the progress bar...
	  if(self.__cmjPlotDiag > 5): print(".... getSipmsFromDatabase: (self.__singleSipmLine, all) ncount = %d,  len(self.__mline) = %d,  self.__mline  = %s \n") % (self.__ncount,len(self.__mline),self.__mline)
	  if(len(self.__mline) > 4):
	    self.__singleSipmLine.append(self.__mline.rsplit(','))
	    if(self.__cmjPlotDiag > 2): print(".... getSipmsFromDatabase: (self.__singleSipmLine, filtered) mcount = %d, self.__mline  = %s \n") % (self.__mcount,self.__mline)
	    self.__sipmResults.append(self.__mline)
	    self.__mcount += 1
	  self.__ncount += 1
    return

##
##  Get Sipm Information from database to populate the root tree!
##  This function is called by all list selections
##
## -------------------------------------------------------------------
##	Make querries to data base to get the sipm information
  def getSipmsPackNumberFromDatabase(self,tempBatch):
    self.__singleSipmNumber = []
    self.__singleSipmNumber = self.getSipmNumberFromPo(tempBatch)  ## get list of Sipms with same PO
    if(self.__cmjPlotDiag > 4) : 
      print (" ------------------------------------------------------------ ")
      print (".... getSipmsPackNumberFromDatabase: List of Sipms with PO Number = %s \n") %(tempBatch)
      print (".... getSipmsPackNumberFromDatabase: len(self.__singleSipmNumber) = %d ") % (len(self.__singleSipmNumber))
      for self.__l in sorted(self.__singleSipmNumber):
	print (".... getSipmsPackNumberFromDatabase: self.__l  = %s ") % (self.__l)
    self.__getSipmValues = DataQuery(self.__queryUrl)
    self.__table = "sipms"
    #self.__fetchThese = "sipm_id,measure_test_date,test_type,bias_voltage,dark_count,gain,temp_degc"
    self.__fetchThese = "sipm_id,pack_number"
    ## loop over all SipmId's with the sampe PO number
    self.__sipmIdCount = 0
    for self.__localSipmNumber in self.__singleSipmNumber:
      if(self.__localSipmNumber != "NULL" and self.__localSipmNumber != ''):
	self.__sipmIdCount += 1
	print(".... getSipmsPackNumberFromDatabase: get sipm_id  = %s") % (self.__localSipmNumber)
	self.__localSipmResult = []
	#self.__fetchCondition = "sipm_id:eq:"+str(self.__localSipmNumber)+"&"+"test_type:eq:vendor"
	self.__fetchCondition = "sipm_id:eq:"+str(self.__localSipmNumber)
	if (self.__cmjPlotDiag > 4):
	  print(".... getSipmsPackNumberFromDatabase: self.__table  = %s \n") % (self.__table)
	  print(".... getSipmsPackNumberFromDatabase: self.__fetchThese  = %s \n") % (self.__fetchThese)
	  print(".... getSipmsPackNumberFromDatabase: self.__fetchCondition = %s \n") % (self.__fetchCondition)
	##  This call returns a list with the database entries for all lines with the same sipm_id plus other
	##   list members that are either white characters, quotations or forward slashes.. They must be
	##   filtered out before sending them to the "unpackSipms" member function....
	if(self.__cmjPlotDiag == 0):
	  self.__localSipmResult = self.__getSipmValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
	else:
	  print(".... getSipmsPackNumberFromDatabase	WARNING: LIMIT TO 5 CALLS!!!!!!")
	  self.__localSipmResult = self.__getSipmValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese,limit=5)
	  if (self.__sipmIdCount > 4) : break
	self.__singleSipmLine = []
	if(self.__cmjPlotDiag > 4): print(".... getSipmsPackNumberFromDatabase: len(self.__localSipmResult) = %d, self.__localSipmResult  = %s \n") % (len(self.__localSipmResult),self.__localSipmResult)
	self.__mcount = 0
	self.__ncount = 0
	for self.__mline in sorted(self.__localSipmResult):
	  if (self.__mline != ''):
	    xx = self.__progressBarCount.get()  ## get current count value for progress bar
	    self.__progressBarCount.set(xx+10)  ## increment that value
	    self.update() ## update the progress bar...
	    self.__tempList = []
	    self.__tempList = self.__mline.rsplit(',')
	    #print(".................... self.__mline = %s") % (self.__mline)
	    #print(".................... self.__tempList = %s") % (self.__tempList)
	    self.__sipmPackNumberResults[self.__tempList[0]] = self.__tempList[1]  ## self.__tempList[0] = SipmId, self.__tempList[1] = packnumber
    return

##
## -------------------------------------------------------------------
##	Make querries about to the data base to get the locally measured I vs V curves
  def getIvsVforSipm(self,tempBatch):
    print(" ------------------------------------------------------------- ")
    print(".... getIvsVforSipm: tempBatch = %s") % (tempBatch)
    self.__singleSipmNumber = []
    self.__singleSipmNumber = self.getSipmNumberFromPo(tempBatch)  ## get list of Sipms with same PO
    if(self.__cmjPlotDiag > 4) : 
      print (" ------------------------------------------------------------ ")
      print (".... getIvsVforSipm: List of Sipms with PO Number = %s \n") %(tempBatch)
      print (".... getIvsVforSipm: len(self.__singleSipmNumber) = %d ") % (len(self.__singleSipmNumber))
      for self.__l in sorted(self.__singleSipmNumber):
	print (".... getSipmsFromDatabase: self.__l  = %s ") % (self.__l)
    self.__getSipmIvsVvalues = DataQuery(self.__queryUrl)
    self.__table = "sipm_current_vs_voltages"
    self.__fetchThese = "sipm_id,measure_test_date,point,voltage,current"
    ## loop over all SipmId's with the sampe PO number
    for self.__localSipmNumber in self.__singleSipmNumber:
      if(self.__localSipmNumber != "NULL"):
	print(".... getIvsVforSipm: get sipm_id  = %s") % (self.__localSipmNumber)
	self.__localSipmIvsVresult = []
	self.__fetchCondition = "sipm_id:eq:"+str(self.__localSipmNumber)
	if (self.__cmjPlotDiag > 4):
	  print(".... getIvsVforSipm: self.__table  = %s \n") % (self.__table)
	  print(".... getIvsVforSipm: self.__fetchThese  = %s \n") % (self.__fetchThese)
	  print(".... getIvsVforSipm: self.__fetchCondition = %s \n") % (self.__fetchCondition)
	##  This call returns a list with the database entries for all lines with the same sipm_id plus other
	##   list members that are either white characters, quotations or forward slashes.. They must be
	##   filtered out before sending them to the "unpackSipms" member function....
	self.__localSipmIvsVresult = self.__getSipmIvsVvalues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
	self.__singleSipmIvsVline = []
	if(self.__cmjPlotDiag > 4): print(".... getIvsVforSipm: len(self.__localSipmIvsVresult) = %d, self.__localSipmIvsVresult  = %s \n") % (len(self.__localSipmIvsVresult),self.__localSipmIvsVresult)
	self.__mcount = 0
	self.__ncount = 0
	for self.__mline in sorted(self.__localSipmIvsVresult):
	  xx = self.__progressBarCount.get()  ## get current count value for progress bar
	  self.__progressBarCount.set(xx+10)  ## increment that value
	  self.update() ## update the progress bar...
	  if(self.__cmjPlotDiag > 0): print(".... getIvsVforSipm: (self.__singleSipmIvsVline, all) ncount = %d,  len(self.__mline) = %d,  self.__mline  = %s \n") % (self.__ncount,len(self.__mline),self.__mline)
	  if(len(self.__mline) > 0):
	    self.__singleSipmIvsVline.append(self.__mline.rsplit(','))
	    if(self.__cmjPlotDiag > 0): print(".... getIvsVforSipm: (self.__singleSipmIvsVline, filtered) mcount = %d, self.__mline  = %s \n") % (self.__mcount,self.__mline)
	    self.__sipmIvsVresults.append(self.__mline)
	    self.__mcount += 1
	  self.__ncount += 1
    return
##
##
## --------------------------------------------------------------
##  This  method is specialized to the Sipms... and will have to be
##	repeated for other types of tables... The PO-number is associated
##	with Sipm numbers in the "sipm" table.  Once a PO-number is selected
##	a  list of all Sipms must be made with that PO-Number.  The
##	following method makes that list....
  def getSipmNumberFromPo(self,tempBatch):
    self.__sipmList = []
    self.__getSipmNumbers = DataQuery(self.__queryUrl)
    self.__table = "sipms"
    self.__fetchThese = "sipm_id"
    self.__fetchCondition = "po_number:eq:"+str(tempBatch)
    if (self.__cmjPlotDiag > 1):
      print(".... getSipmNumberFromPo: tempBatch  = %s \n") % (tempBatch)
      print(".... getSipmNumberFromPo: self.__table  = %s \n") % (self.__table)
      print(".... getSipmNumberFromPo: self.__fetchThese  = %s \n") % (self.__fetchThese)
      print(".... getSipmNumberFromPo: self.__fetchCondition = %s \n") % (self.__fetchCondition)
    if(self.__cmjTest == 1):
      self.__sipmList = self.__getSipmNumbers.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese,limit=10)
    else:
      self.__sipmList = self.__getSipmNumbers.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjPlotDiag > 1):
      for self.__l in self.__sipmList:
	print(".... getSipmNumberFromPo: self.__sipmId = %s \n") % (self.__l)
    return self.__sipmList
## --------------------------------------------------------------
## This method calls the method to get the entries to the database
## and plot scatter plots
  def getScatterPlots(self):
    if(self.__cmjPlotDiag != 0): print("....getScatterPlots: Enter getScatterPlots \n")
    self.plotScatterPlots()
    if(self.__cmjPlotDiag != 0): print("....getScatterPlots: Exit getScatterPlots \n")
    return
## --------------------------------------------------------------
## This method calls the method to get the entries to the database
## and plot Histograms
  def getHistograms(self):
    if(self.__cmjPlotDiag != 0): print("....getHistograms: Enter getHistograms \n")
    #self.plotHistograms()
    self.__treeTime = myTime()
    self.__treeTime.getComputerTime()
    self.__saveTreeTime = self.__treeTime.getTimeForSavedFiles()
    self.__outRootTreeFileName = "outputFiles/SipmRootHistograms"+self.__saveTreeTime+".root"
    self.__rootTreeFile = TFile(self.__outRootTreeFileName,'RECREATE')
    print ("XXXXXXXXXXX getHistograms:: Root Tree File name = %s \n") % (self.__outRootTreeFileName)
    self.bookHistograms()
    self.fillHistograms()
    self.drawCanvas() 
    #self.defineSipmMeasurementRootTree()  ## define and write root trees for sipm measurments!
    self.defineSipmIvsVMeasurementRootTree()  ## define the root trees that contain the I vs V measurment.
    #self.defineAllLocalSipmMeasurementRootTree()
    #self.defineAllVendorSipmMeasurementRootTree()
    self.defineAllMeasurementRootTree()
    self.__rootTreeFile.Close()
    if(self.__cmjPlotDiag != 0): print("....getHistograms: Exit getHistograms \n")
    return
##
##    
## --------------------------------------------------------------
##	Unpack the database information for each Sipm, each test,
##		use save this information to plot in a histogramm
##		and to save in a root tree
  def unpackSipms(self):
    if(self.__cmjPlotDiag > 2): print("XXXXXXXXXXX entered unpackSipms \n")
    if(self.__cmjPlotDiag > 2): print (".... unpackSipms: self.__sipmResults  = %s \n") % (self.__sipmResults)
    print(".... unpackSipms: self.__sipmResults  = %d \n") % len(self.__sipmResults)
    ## self.__sipmResults is a list that has all occurances of a given sipm_id... this includes
    ## an entry for each test date (and test type like vendor or measured).... 
    for self.__record in sorted(self.__sipmResults):
      self.__new_Sipm_Id_Marker = 0
      if(self.__cmjPlotDiag > 2): print("....unpackSipms: self.__record =  %s , len(self.__record) = %d \n") % (self.__record, len(self.__record))
      for self.__item in sorted(self.__record):
	xx = self.__progressBarCount.get()  ## get current count value for progress bar
	self.__progressBarCount.set(xx+10)  ## increment that value
	self.update() ## update the progress bar...
	if(self.__cmjPlotDiag > 3): print("....unpackSipms: self.__record = %s, len(self.__record) = %d \n") %(self.__record, len(self.__record))
	self.__item = str(self.__record).rsplit(',')     ##
	if(self.__cmjPlotDiag > 3): print("....unpackSipms: self.__item = %s, len(self.__item) = %d \n") %(self.__item, len(self.__item))
	if (len(self.__item) > 2):
	  self.__tempSipmId 	= self.__item[0][2:]
	  self.__tempNumber	= self.__tempSipmId[22:]
	  self.__tempSipmTestDate = self.__item[1]
	  self.__tempTestType   = self.__item[2]
	  self.__tempWorkerBarCode = self.__item[3]
	  self.__tempWorkStationBarCode = self.__item[4]
	  self.__tempBiasVoltage  = self.__item[5]
	  self.__tempDarkCount	= self.__item[6]
	  self.__tempGain		= self.__item[7]
	  #self.__tempString = str(self.__item[8])
	  #self.__tempTemperature	= float(self.__tempString[0:len(self.__tempString)-1])
	  self.__tempTemperature = float(self.__item[8])
	  self.__tempBreakdownVolt = self.__item[9]
	  self.__tempDarkCountRate = self.__item[10]
	  self.__tempCurrentVsVoltageCond = self.__item[11]
	  self.__tempXTalk = self.__item[12]
	  self.__tempLedResponse = self.__item[13]
	  self.__tempPackNumber = self.__sipmPackNumberResults[self.__item[0]]
	  self.__tempDataFileLocation = self.__item[14]
	  self.__tempDataFileName = self.__item[15]
	  if(self.__new_Sipm_Id_Marker == 0):	## let user know what the script is doing
	    print("...unpackSipms::  unpack sipm_id = %s ") % (self.__tempSipmId)
	    self.__new_Sipm_Id_Marker = 1
	  if(self.__cmjPlotDiag > 2):  ## diagnostic print statements
	    print("unpackSipms ........ New Counter ............ \n")
	    print("... self.__item = %s ") % self.__item
	    print("... self.__tempSipmId = %s ") % self.__tempSipmId
	    print("... self.__tempNumber = %s ") % self.__tempNumber
	    print("... self.__tempSipmTestDate = %s ") % self.__tempSipmTestDate
	    print("... self.__tempTestType = %s ") % self.__tempTestType
	    print("... self.__tempWorkerBarCode = %s ") % self.__tempWorkerBarCode
	    print("... self.__tempWorkStationBarCode = %s ") % self.__tempWorkStationBarCode
	    print("... self.__tempBiasVoltage = %s ") % self.__tempBiasVoltage
	    print("... self.__tempDarkCount = %s ") % self.__tempDarkCount
	    print("... self.__tempGain = %s ") % self.__tempGain
	    print("... self.__tempTemperature = %s ") % self.__tempTemperature
	    print("... self.__tempBreakDownVolt = %s ") % self.__tempBreakdownVolt
	    print("... self.__tempDarkCountRate = %s ") % self.__tempDarkCountRate
	    print("... self.__tempCurrentVsVoltageCond = %s ") % self.__tempCurrentVsVoltageCond
	    print("... self.__tempXTalk = %s ") % self.__tempXTalk
	    print("... self.__tempLedResponse = %s ") % self.__tempLedResponse
	    print("... self.__tempPackNumber = %s ") % self.__tempPackNumber
	    print("... self.__tempDataFileLocation = %s ") % self.__tempDataFileLocation
	    print("... self.__tempDataFileName = %s \n") % self.__tempDataFileName
	  self.__sipmId[self.__tempSipmTestDate][self.__tempSipmId]     	= self.__tempSipmId
	  self.__sipmNumber[self.__tempSipmTestDate][self.__tempSipmId] 	= float(self.__tempNumber)
	  self.__sipmMeasureTestDate[self.__tempSipmTestDate] = self.__tempSipmTestDate
	  self.__saveTestType[self.__tempSipmTestDate] = self.__tempTestType
	  self.__testType[self.__tempSipmTestDate][self.__tempSipmId]      = self.__tempTestType
	  self.__biasVoltage[self.__tempSipmTestDate][self.__tempSipmId]	= self.__tempBiasVoltage
	  self.__darkCount[self.__tempSipmTestDate][self.__tempSipmId]	= self.__tempDarkCount
	  self.__gain[self.__tempSipmTestDate][self.__tempSipmId]		= self.__tempGain
	  self.__temperature[self.__tempSipmTestDate][self.__tempSipmId]	= self.__tempTemperature
	  ##
	  if(self.__tempWorkerBarCode != 'None') :
	    self.__workerBarCode[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempWorkerBarCode
	  else:
	    self.__workerBarCode[self.__tempSipmTestDate][self.__tempSipmId] = 'not_given'

	  if(self.__tempWorkStationBarCode != 'None') :
	    self.__workStationBarCode[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempWorkStationBarCode
	  else:
	    self.__workStationBarCode[self.__tempSipmTestDate][self.__tempSipmId] = 'not_given'

	  if(self.__tempBreakdownVolt != 'None') : 
	    self.__breakdown_voltage[self.__tempSipmTestDate][self.__tempSipmId] = float(self.__tempBreakdownVolt)
	  else: 
	    self.__breakdown_voltage[self.__tempSipmTestDate][self.__tempSipmId] = -9999.99

	  if(self.__tempDarkCountRate != 'None') :
	    self.__dark_count_rate[self.__tempSipmTestDate][self.__tempSipmId] = float(self.__tempDarkCountRate)
	  else:
	    self.__dark_count_rate[self.__tempSipmTestDate][self.__tempSipmId] = -9999.99

	  if(self.__tempCurrentVsVoltageCond != 'None') :
	    self.__current_vs_voltage_condition[self.__tempSipmTestDate][self.__tempSipmId] = float(self.__tempCurrentVsVoltageCond)
	  else:
	    self.__current_vs_voltage_condition[self.__tempSipmTestDate][self.__tempSipmId] = -9999.99

	  if(self.__tempXTalk != 'None') :
	    self.__x_talk[self.__tempSipmTestDate][self.__tempSipmId] = float(self.__tempXTalk)
	  else:
	    self.__x_talk[self.__tempSipmTestDate][self.__tempSipmId] = -9999.99

	  if(self.__tempLedResponse != 'None') :
	    self.__led_response[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempLedResponse
	  else:
	    self.__led_response[self.__tempSipmTestDate][self.__tempSipmId] = -9999.99

	  if(self.__tempPackNumber != 'None'):
	    self.__pack_number[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempPackNumber
	  else:
	    self.__pack_number[self.__tempSipmTestDate][self.__tempSipmId] = 'none_given'

	  if(self.__tempDataFileLocation != 'None') :
	    self.__data_file_location[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempDataFileLocation
	  else:
	    self.__data_file_location[self.__tempSipmTestDate][self.__tempSipmId] = 'none_given'

	  if(self.__tempDataFileName != 'None') :
	    self.__data_file_name[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempDataFileName
	  else:
	    self.__data_file_name[self.__tempSipmTestDate][self.__tempSipmId] =  'none_given'
    if(self.__cmjPlotDiag > 1):		## diangonstic print statements
      print("unpackSipms ........ SipmId ............ \n")
      for self.__n in self.__sipmMeasureTestDate.keys():
	print("...... self.__sipmMeasureTestDate[%s]	= %s ")      % (self.__n,self.__sipmMeasureTestDate[self.__n])
	for self.__m in sorted(self.__sipmId[self.__n].keys()):
	    print("...... self.__sipmId[%s][%s]	= %s \n")     % (self.__n,self.__m,self.__sipmId[self.__n][self.__m])
	    print("...... self.__sipmNumber[%s][%s]	= %s ") % (self.__n,self.__m,self.__sipmNumber[self.__n][self.__m])
	    print("...... self.__testType[%s][%s]	= %s ")      % (self.__n,self.__m,self.__testType[self.__n][self.__m])
	    print("...... self.__workerBarCode[%s][%s]= %s ")      % (self.__n,self.__m,self.__workerBarCode[self.__n][self.__m])
	    print("...... self.__workStationBarCode[%s][%s]	= %s \n")      % (self.__n,self.__m,self.__workStationBarCode[self.__n][self.__m])
	    print("...... self.__biasVoltage[%s][%s]	= %s ")	% (self.__n,self.__m,self.__biasVoltage[self.__n][self.__m])
	    print("...... self.__darkCount[%s][%s]	= %s ")      % (self.__n,self.__m,self.__darkCount[self.__n][self.__m])
	    print("...... self.__gain[%s][%s] 	= %s ")      % (self.__n,self.__m,self.__gain[self.__n][self.__m])
	    print("...... self.__sipmId.keys()      = %s || self.__temperature[%s]	= %s ")      % (self.__m,self.__m,self.__temperature[self.__m])

	    print("...... self.__breakdown_voltage[%s[%s]	= %s \n")      % (self.__n,self.__m,self.__breakdown_voltage[self.__n][self.__m])
	    print("...... self.__dark_count_rate[%s][%s]	= %s \n")      % (self.__n,self.__m,self.__dark_count_rate[self.__n][self.__m])
	    print("...... self.__current_vs_voltage_condition[%s][%s]	= %s ")      % (self.__n,self.__m,self.__current_vs_voltage_condition[self.__n][self.__m])
	    print("...... self.__x_talk[%s][%s]	= %s \n")      % (self.__n,self.__m,self.__x_talk[self.__n][self.__m])
	    print("...... self.__led_response[%s][%s]	= %s ")      % (self.__n,self.__m,self.__led_response[self.__n][self.__m])
	    print("...... self.__data_file_location[%s][%s]	= %s \n")      % (self.__n,self.__m,self.__data_file_location[self.__n][self.__m])
	    print("...... self.__data_file_name[%s][%s]	= %s ")      % (self.__n,self.__m,self.__data_file_name[self.__n][self.__m])
      #
    if(self.__cmjPlotDiag > 2): print("XXXXXXXXXXX exit unpackSipms \n")
    return
##
##    
## --------------------------------------------------------------
  def unpackSipmIvsV(self):
    if(self.__cmjPlotDiag > 2): print("XXXXXXXXXXX entered unpackSipmIvsV \n")
    if(self.__cmjPlotDiag > 2): print (".... unpackSipmIvsV: self.__sipmResults  = %s \n") % (self.__sipmResults)
    print(".... unpackSipmIvsV: self.__sipmResults  = %d \n") % len(self.__sipmIvsVresults)
    ## self.__sipmResults is a list that has all occurances of a given sipm_id... this includes
    ## an entry for each test date (and test type like vendor or measured).... 
    for self.__record in sorted(self.__sipmIvsVresults):
      if(self.__cmjPlotDiag > 2): print("....unpackSipmIvsV: self.__record =  %s , len(self.__record) = %d \n") % (self.__record, len(self.__record))
      for self.__item in sorted(self.__record):
	if(self.__cmjPlotDiag > 3): print("....unpackSipmIvsV: self.__record = %s, len(self.__record) = %d \n") %(self.__record, len(self.__record))
	self.__item = str(self.__record).rsplit(',')     ##
	if(self.__cmjPlotDiag > 3): print("....unpackSipmIvsV: self.__item = %s, len(self.__item) = %d \n") %(self.__item, len(self.__item))
	if (len(self.__item) > 2):
	  self.__tempSipmId = self.__item[0]
	  self.__tempSipmTestDate = self.__item[1]
	  self.__tempSipmIvsV_Bin = self.__item[2]
	  self.__tempSipmIvsV_Voltage = self.__item[3]
	  self.__tempSipmIvsV_Current = self.__item[4]
	  if(self.__cmjPlotDiag > 4):
	    print(".... unpackSipmIvsV: self.__tempSipmId = %s") % (self.__tempSipmId)
	    print(".... unpackSipmIvsV: self.__tempSipmTestDate = %s") % (self.__tempSipmTestDate)
	    print(".... unpackSipmIvsV: self.__tempSipmIvsV_Bin = %s") % (self.__tempSipmIvsV_Bin)
	    print(".... unpackSipmIvsV: self.__tempSipmIvsV_Voltage = %s") % (self.__tempSipmIvsV_Voltage)
	    print(".... unpackSipmIvsV: self.__tempSipmIvsV_Current = %s") % (self.__tempSipmIvsV_Current)
	self.__sipmMeasureTestDate_IvsV[self.__tempSipmTestDate] = self.__tempSipmTestDate
	self.__sipmId_IvsV[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempSipmId
	self.__IvsV_voltage[self.__tempSipmTestDate][self.__tempSipmId][self.__tempSipmIvsV_Bin] = self.__tempSipmIvsV_Voltage
	self.__IvsV_current[self.__tempSipmTestDate][self.__tempSipmId][self.__tempSipmIvsV_Bin] = self.__tempSipmIvsV_Current
    return
##
##
##
################################################################################################
################################################################################################
################################################################################################
##
##		Root part of the program
##
## --------------------------------------------------------------------
##   Plot scatter plots for sipms
##	Use Root!
  def plotScatterPlots(self):
    print (".... plotScatterPlots:Begin Scatter Plots\n")
    self.__windowTitle = "PO-Number "+str(self.__sipmBatchRequest)
    self.__c2 = TCanvas('self.__c2',self.__windowTitle,200,10,800,700)
    self.__c2.SetFillColor(0)
    self.__c2.Divide(2,3)
    self.__n = len(self.__plotSipmNumber)
    self.__sipmNumberArray = array('f')
    self.__biasVoltageArray = array('f')
    self.__darkCountArray = array('f') 
    self.__gainArray = array('f')
    self.__temperatureArray = array('f') 
    for i in range(self.__n):
      self.__sipmNumberArray.append(self.__plotSipmNumber[i])
      self.__biasVoltageArray.append(float(self.__plotBiasVoltage[i]))
      self.__darkCountArray.append(float(self.__plotDarkCount[i]))
      self.__gainArray.append(float(self.__plotGain[i]))
      self.__temperatureArray.append(float(self.__plotTemperature[i]))
#	First pad... Bais Voltage
    self.__c2.cd(1)
    self.__graph1 = TGraph(self.__n,self.__sipmNumberArray,self.__biasVoltageArray)
    self.__graph1.SetLineWidth(0)
    self.__graph1.SetMarkerColor(4)
    self.__graph1.SetMarkerStyle(21)
    self.__graph1.SetTitle('Bias Voltage')
    self.__graph1.GetXaxis().SetTitle('Sipm Number')
    self.__graph1.GetYaxis().SetTitle('Counts')
    self.__graph1.Draw()
#	Second pad Dark Current
    self.__c2.cd(2)
    self.__graph2 = TGraph(self.__n,self.__sipmNumberArray,self.__darkCountArray)
    self.__graph2.SetLineWidth(0)
    self.__graph2.SetMarkerColor(4)
    self.__graph2.SetMarkerStyle(21)
    self.__graph2.SetTitle('Dark Current')
    self.__graph2.GetXaxis().SetTitle('Sipm Number')
    self.__graph2.GetYaxis().SetTitle('Dark Current (Amps)')
    self.__graph2.Draw()
#	Third pad Gain Measurement
    self.__c2.cd(3)
    self.__graph3 = TGraph(self.__n,self.__sipmNumberArray,self.__gainArray)
    self.__graph3.SetLineWidth(0)
    self.__graph3.SetMarkerColor(4)
    self.__graph3.SetMarkerStyle(21)
    self.__graph3.SetTitle('Gain')
    self.__graph3.GetXaxis().SetTitle('Sipm Number')
    self.__graph3.GetYaxis().SetTitle('Gain (Counts)')
    self.__graph3.Draw()
#	Fourth pad: Temperature
    self.__c2.cd(5)
    self.__graph4 = TGraph(self.__n,self.__sipmNumberArray,self.__temperatureArray)
    self.__graph4.SetLineWidth(0)
    self.__graph4.SetMarkerColor(4)
    self.__graph4.SetMarkerStyle(21)
    self.__graph4.SetTitle('Diameter 1 Measurement')
    self.__graph4.GetXaxis().SetTitle('Extrusion Number')
    self.__graph4.GetYaxis().SetTitle('Diameter 1 (mm)')
    self.__graph4.Draw()
#	Draw canvas
    self.__c2.Modified()
    self.__c2.Update()
    #sleep(5)

    ## Save graphics
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "logFiles/SipmPlotsRoot"+self.__saveTime+".png"
    self.__c2.SaveAs(self.__outFileName)
    return
##
##
## --------------------------------------------------------------------
##  A method to book the histograms....
##  Use Root!
##
  def bookHistograms(self):
    gStyle.SetOptStat("nemruoi");  ## Print statistitics... page 32 root manual.. reset defaul
    gStyle.SetOptDate(1);          ## Print date on plots
    gStyle.SetOptFit(1111);        ## show parameters, errors and chi2... page 72 root manual
    self.__nBiasVoltageBins = 100
    self.__lowBiasVoltageBins = 45.0
    self.__hiBiasVoltageBins  = 65.0
    #self.__myStyle = TStyle('self.__myStyle','self.__myStyle')
    #self.__myStyle.SetTitleSize(0.3,"t")
    #gROOT.SetStyle(self.__myStyle)
    self.__hBiasVoltage = TH1F('self.__hBiasVoltage','Bias Voltage',self.__nBiasVoltageBins,self.__lowBiasVoltageBins,self.__hiBiasVoltageBins)
    self.__hBiasVoltage.SetFillColor(2)
    self.__hBiasVoltage.GetXaxis().SetTitle('Bias Voltage (Volts)')
    self.__hBiasVoltage.GetYaxis().SetTitle('Counts per 0.1 Volt')
    self.__hBiasVoltage.GetXaxis().SetLabelSize(0.08)
    self.__hBiasVoltage.GetYaxis().SetLabelSize(0.08)
    self.__nBinsDarkCurrent = 100
    self.__lowBinDarkCurrent = 0.0
    self.__hiBinDarkCurrent  = 0.2
    self.__hDarkCurrent = TH1F('self.__hDarkCurrent','Dark Current',self.__nBinsDarkCurrent,self.__lowBinDarkCurrent,self.__hiBinDarkCurrent)
    self.__hDarkCurrent.SetFillColor(4)
    self.__hDarkCurrent.GetXaxis().SetTitle('Dark Current (Amps)')
    self.__hDarkCurrent.GetYaxis().SetTitle('Counts per 0.002 Amps')
    self.__hDarkCurrent.GetXaxis().SetLabelSize(0.08)
    self.__hDarkCurrent.GetYaxis().SetLabelSize(0.08)
    self.__nBinsGain = 100
    self.__lowBinGain = 0.0
    self.__hiBinGain  = 50.0
    self.__hGain = TH1F('self.__hGain','Gain Measurement',self.__nBinsGain,self.__lowBinGain,self.__hiBinGain)
    self.__hGain.SetFillColor(4)
    self.__hGain.GetXaxis().SetTitle('Gain (Counts)')
    self.__hGain.GetYaxis().SetTitle('Counts per 0.002 Counts')
    self.__hGain.GetXaxis().SetLabelSize(0.08)
    self.__hGain.GetYaxis().SetLabelSize(0.08)
    self.__nBins = 100
    self.__lowBin = 20.0
    self.__hiBin  = 28.0
    self.__hTemperature = TH1F('self.__hTemperature','Temperature Measurement',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hTemperature.SetFillColor(3)
    self.__hTemperature.GetXaxis().SetTitle('Temerature ^oC')
    self.__hTemperature.GetYaxis().SetTitle('Counts per 0.08 ^oC')
    self.__hTemperature.GetXaxis().SetLabelSize(0.08)
    self.__hTemperature.GetYaxis().SetLabelSize(0.08)
    self.__nBins = 100
    self.__lowBin = 10.0
    self.__hiBin  = 60.0
    self.__hVendorBiasVoltage = TH1F('self.__hVendorBiasVoltage','Vendor Bias Voltage',self.__nBiasVoltageBins,self.__lowBiasVoltageBins,self.__hiBiasVoltageBins)
    self.__hVendorBiasVoltage.SetFillColor(2)
    self.__hVendorBiasVoltage.GetXaxis().SetTitle('Bias Voltage (Volts)')
    self.__hVendorBiasVoltage.GetYaxis().SetTitle('Counts per 0.1 Volt')
    self.__hVendorBiasVoltage.GetXaxis().SetLabelSize(0.08)
    self.__hVendorBiasVoltage.GetYaxis().SetLabelSize(0.08)
    self.__lowBin = 0.0
    self.__hiBin  = 0.2
    self.__hVendorDarkCurrent = TH1F('self.__hVendorDarkCurrent','Vendor Dark Current',self.__nBinsDarkCurrent,self.__lowBinDarkCurrent,self.__hiBinDarkCurrent)
    self.__hVendorDarkCurrent.SetFillColor(4)
    self.__hVendorDarkCurrent.GetXaxis().SetTitle('Dark Current (Amps)')
    self.__hVendorDarkCurrent.GetYaxis().SetTitle('Counts per 0.002 Amps')
    self.__hVendorDarkCurrent.GetXaxis().SetLabelSize(0.08)
    self.__hVendorDarkCurrent.GetYaxis().SetLabelSize(0.08)
    self.__lowBin = 0.0
    self.__hiBin  = 2.0
    self.__hVendorGain = TH1F('self.__hVendorGain','Vendor Gain Measurement',self.__nBinsGain,self.__lowBinGain,self.__hiBinGain)
    self.__hVendorGain.SetFillColor(4)
    self.__hVendorGain.GetXaxis().SetTitle('Gain (Counts)')
    self.__hVendorGain.GetYaxis().SetTitle('Counts per 0.002 Counts')
    self.__hVendorGain.GetXaxis().SetLabelSize(0.08)
    self.__hVendorGain.GetYaxis().SetLabelSize(0.08)
    self.__nBinsTemp = 100
    self.__lowBinTemp = 20.0
    self.__hiBinTemp  = 28.0
    self.__hVendorTemperature = TH1F('self.__hVendorTemperature','Vendor Temperature Measurement',self.__nBinsTemp,self.__lowBinTemp,self.__hiBinTemp)
    self.__hVendorTemperature.SetFillColor(3)
    self.__hVendorTemperature.GetXaxis().SetTitle('Temerature ^oC')
    self.__hVendorTemperature.GetYaxis().SetTitle('Counts per 0.08 ^oC')
    self.__hVendorTemperature.GetXaxis().SetLabelSize(0.08)
    self.__hVendorTemperature.GetYaxis().SetLabelSize(0.08)
    self.__nBins = 100
    self.__lowBin = 10.0
    self.__hiBin  = 60.0
    self.__localXLabelSize = 0.06
    self.__localYlabelSize = 0.06
    self.__hlocalBiasVoltage = TH1F('self.__hlocalBiasVoltage','Local Bias Voltage',self.__nBiasVoltageBins,self.__lowBiasVoltageBins,self.__hiBiasVoltageBins)
    self.__hlocalBiasVoltage.SetFillColor(2)
    self.__hlocalBiasVoltage.GetXaxis().SetTitle('Bias Voltage (Volts)')
    self.__hlocalBiasVoltage.GetYaxis().SetTitle('Counts per 0.1 Volt')
    self.__hlocalBiasVoltage.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hlocalBiasVoltage.GetYaxis().SetLabelSize(self.__localYlabelSize)
    self.__localXLabelSize = 0.04
    self.__localYlabelSize = 0.06
    self.__lowBin = 0.0
    self.__hiBin  = 0.2
    self.__hlocalDarkCurrent = TH1F('self.__hlocalDarkCurrent','Local Dark Current',self.__nBinsDarkCurrent,self.__lowBinDarkCurrent,self.__hiBinDarkCurrent)
    self.__hlocalDarkCurrent.SetFillColor(4)
    self.__hlocalDarkCurrent.GetXaxis().SetTitle('Dark Current (Amps)')
    self.__hlocalDarkCurrent.GetYaxis().SetTitle('Counts per 0.002 Amps')
    self.__hlocalDarkCurrent.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hlocalDarkCurrent.GetYaxis().SetLabelSize(self.__localYlabelSize)
    self.__localXLabelSize = 0.06
    self.__localYlabelSize = 0.06
    self.__lowBin = 0.0
    self.__hiBin  = 2.0
    self.__hlocalGain = TH1F('self.__hlocalGain','Local Gain Measurement',self.__nBinsGain,self.__lowBinGain,self.__hiBinGain)
    self.__hlocalGain.SetFillColor(4)
    self.__hlocalGain.GetXaxis().SetTitle('Gain (Counts)')
    self.__hlocalGain.GetYaxis().SetTitle('Counts per 0.002 Counts')
    self.__hlocalGain.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hlocalGain.GetYaxis().SetLabelSize(self.__localYlabelSize)
    self.__lowBin = 20.0
    self.__hiBin  = 28.0
    self.__hlocalTemperature = TH1F('self.__hlocalTemperature','Local Temperature Measurement',self.__nBinsTemp,self.__lowBinTemp,self.__hiBinTemp)
    self.__hlocalTemperature.SetFillColor(3)
    self.__hlocalTemperature.GetXaxis().SetTitle('Temerature ^oC')
    self.__hlocalTemperature.GetYaxis().SetTitle('Counts per 0.08 ^oC')
    self.__hlocalTemperature.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hlocalTemperature.GetYaxis().SetLabelSize(self.__localYlabelSize)
    self.__nBinsBreakdown = 100
    self.__lowBinBreakdown = 50.0
    self.__hiBinBreakdown  = 60.0
    self.__hLocalBreakdownVoltage = TH1F('self.__hLocalBreakdownVoltage','Local Breakdown Voltage Measurement',self.__nBinsBreakdown,self.__lowBinBreakdown,self.__hiBinBreakdown)
    self.__hLocalBreakdownVoltage.SetFillColor(6)
    self.__hLocalBreakdownVoltage.GetXaxis().SetTitle('Breakdown Voltage')
    self.__hLocalBreakdownVoltage.GetYaxis().SetTitle('Counts')
    self.__hLocalBreakdownVoltage.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hLocalBreakdownVoltage.GetYaxis().SetLabelSize(self.__localYlabelSize)
    self.__nBinsCurrentVsVoltage = 100
    self.__lowBinCurrentVsVoltage = 50.0
    self.__hiBinCurrentVsVoltage  = 60.0
    self.__hLocalCurrentVsVoltageCondition = TH1F('self.__hLocalCurrentVsVoltageCondition','Local Current vs Voltage Condition',self.__nBinsCurrentVsVoltage,self.__lowBinCurrentVsVoltage,self.__hiBinCurrentVsVoltage)
    self.__hLocalCurrentVsVoltageCondition.SetFillColor(6)
    self.__hLocalCurrentVsVoltageCondition.GetXaxis().SetTitle('Current vs Voltage')
    self.__hLocalCurrentVsVoltageCondition.GetYaxis().SetTitle('Counts')
    self.__hLocalCurrentVsVoltageCondition.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hLocalCurrentVsVoltageCondition.GetYaxis().SetLabelSize(self.__localYlabelSize)
    self.__nBinsXTalk = 100
    self.__lowBinXTalk = 0.0
    self.__hiBinXTalk  = 10.0
    self.__hLocalXTalk = TH1F('self.__hLocalXTalk','Local Cross Talk',self.__nBinsXTalk,self.__lowBinXTalk,self.__hiBinXTalk)
    self.__hLocalXTalk.SetFillColor(7)
    self.__hLocalXTalk.GetXaxis().SetTitle('X Talk')
    self.__hLocalXTalk.GetYaxis().SetTitle('Counts')
    self.__hLocalXTalk.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hLocalXTalk.GetYaxis().SetLabelSize(self.__localYlabelSize)

    ## Define I vs V Curves
    self.__hIvsV = TH1F('self.__hIvsV','All SiPMs: IvsV',5000,0.0,5.0)
    #self.__hTemperature.SetFillColor(3)
    self.__hIvsV.GetXaxis().SetTitle('Voltage (Volts)')
    self.__hIvsV.GetYaxis().SetTitle('Current (#mu Amps)')
    self.__hIvsV.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__hIvsV.GetYaxis().SetLabelSize(self.__localYlabelSize)

    ## plot the I vs V curves
    self.__h2_IvsVFrame = TH2F('self.__h2_IvsVFrame','All SiPMs I vs V!',1000,0.0,100.0,100,0.0,5.0)
    self.__h2_IvsVFrame.GetXaxis().SetTitle('Voltage (Volts)')
    self.__h2_IvsVFrame.GetYaxis().SetTitle('Current (#mu Amps)')
    self.__h2_IvsVFrame.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__h2_IvsVFrame.GetYaxis().SetLabelSize(self.__localYlabelSize)
    return

##
## --------------------------------------------------------------------
##  Fill the histograms!!!
##  Obviously, use Root!
##
  def fillHistograms(self):
    self.__h_IvsVFrame = TH2F('self.__h_IvsVFrame','All SiPMs I vs V!',2,0.0,100.0,2,0.0,5.0)
    self.__h_IvsVFrame.GetXaxis().SetTitle('Voltage (V)')
    self.__h_IvsVFrame.GetYaxis().SetTitle('Current (Amps)')
    self.__c1000 = TCanvas( 'self.__c1000', 'I vs V Curves', 500, 700, 700, 500 )
    self.__h_IvsVFrame.Draw()
    self.__t_graphs = []
    self.__npoint = int(100)
    for self.__testDate in self.__sipmMeasureTestDate.keys():
      for self.__event in self.__sipmId[self.__testDate].keys():
	if(self.__cmjPlotDiag > 6): print("...__multiWindow__fillHistograms... self.__testDate = %s , self.__event = %s ") % (self.__testDate,self.__event)
	self.__hBiasVoltage.Fill(float(self.__biasVoltage[self.__testDate][self.__event]))
	self.__hDarkCurrent.Fill(float(self.__darkCount[self.__testDate][self.__event]))
	self.__hGain.Fill(float(self.__gain[self.__testDate][self.__event]))
	self.__hTemperature.Fill(float(self.__temperature[self.__testDate][self.__event])) 

 ## combine all local measurement dates into single root tree.
	self.__newKey = self.__testDate+self.__event
	if(self.__cmjPlotDiag > 6): print("...__multiWindow__fillHistograms... self.__testDate = %s , self.__event = %s ||| new key = xxxx%sxxxx") % (self.__testDate,self.__event,self.__newKey)
	self.__allSipmId[self.__newKey] = self.__event
	self.__allSipmMeasureTestDate[self.__newKey] = self.__testDate
	self.__allTestType[self.__newKey] = self.__testType[self.__testDate][self.__event]
	self.__allWorkerBarCode[self.__newKey] = self.__workerBarCode[self.__testDate][self.__event]
	self.__allWorkStationBarCode[self.__newKey] = self.__workStationBarCode[self.__testDate][self.__event]
	self.__allBiasVoltage[self.__newKey] = float(self.__biasVoltage[self.__testDate][self.__event])
	self.__allDarkCount[self.__newKey] = float(self.__darkCount[self.__testDate][self.__event])
	#print("...__multiWindow__fillHistograms... self.__allLocalDarkCount[%s] = %s ") % (self.__event,self.__allLocalDarkCount[self.__event])
	self.__allGain[self.__newKey] = float(self.__gain[self.__testDate][self.__event])
	self.__allTemperature[self.__newKey] = float(self.__temperature[self.__testDate][self.__event])
	self.__allBreakdown_voltage[self.__newKey] = float(self.__breakdown_voltage[self.__testDate][self.__event])
	self.__allDark_count_rate[self.__newKey] = float(self.__dark_count_rate[self.__testDate][self.__event])
	self.__allCurrent_vs_voltage_condition[self.__newKey] = float(self.__current_vs_voltage_condition[self.__testDate][self.__event])
	self.__allX_talk[self.__newKey] = float(self.__x_talk[self.__testDate][self.__event])
	self.__allLed_response[self.__newKey] = float(self.__led_response[self.__testDate][self.__event])
	self.__allData_file_location[self.__newKey] = self.__data_file_location[self.__testDate][self.__event]
	self.__allData_file_name[self.__newKey] = self.__data_file_name[self.__testDate][self.__event]
	#self.__allPack_number[self.__newKey] =  self.__pack_number[self.__testDate][self.__event]
	## plot histograms with the vendor information, only....
	if(self.__testType[self.__testDate][self.__event] == 'vendor'):
	  self.__hVendorBiasVoltage.Fill(float(self.__biasVoltage[self.__testDate][self.__event]))
	  self.__hVendorDarkCurrent.Fill(float(self.__darkCount[self.__testDate][self.__event]))
	  self.__hVendorGain.Fill(float(self.__gain[self.__testDate][self.__event]))
	  self.__hVendorTemperature.Fill(float(self.__temperature[self.__testDate][self.__event]))
	## plot histograms with the local measurements, only
	if(self.__testType[self.__testDate][self.__event] == 'measured'):
	  self.__hlocalBiasVoltage.Fill(float(self.__biasVoltage[self.__testDate][self.__event]))
	  self.__hlocalDarkCurrent.Fill(float(self.__darkCount[self.__testDate][self.__event]))
	  self.__hlocalGain.Fill(float(self.__gain[self.__testDate][self.__event]))
	  self.__hlocalTemperature.Fill(float(self.__temperature[self.__testDate][self.__event]))
	  self.__hLocalBreakdownVoltage.Fill(float(self.__breakdown_voltage[self.__testDate][self.__event]))
	  self.__hLocalCurrentVsVoltageCondition.Fill(float(self.__breakdown_voltage[self.__testDate][self.__event]))
	  self.__hLocalXTalk.Fill(float(self.__x_talk[self.__testDate][self.__event]))
	  self.__hLocalCurrentVsVoltageCondition.Fill(float(self.__current_vs_voltage_condition[self.__testDate][self.__event]))
    self.__markerColor = 2;
    for self.__n in self.__sipmMeasureTestDate_IvsV.keys():
      for self.__m in self.__sipmId_IvsV[self.__n].keys():
	self.__arrayVoltage = array('d')
	self.__arrayCurrent = array('d')
	for self.__j in self.__IvsV_voltage[self.__n][self.__m].keys():
	  self.__h2_IvsVFrame.Fill(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]),float(self.__IvsV_current[self.__n][self.__m][self.__j]))
	  if(float(self.__IvsV_current[self.__n][self.__m][self.__j]) > 5.0) : continue
	  if(float(self.__IvsV_current[self.__n][self.__m][self.__j]) < 0.0) : continue
	  self.__arrayCurrent.append(float(self.__IvsV_current[self.__n][self.__m][self.__j]))
	  self.__arrayVoltage.append(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]))
	  self.__hIvsV.Fill(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]),float(self.__IvsV_current[self.__n][self.__m][self.__j]))
	self.__t_graphs.append(TGraph(self.__npoint,self.__arrayVoltage,self.__arrayCurrent))
    print("XXXX fillHistograms:: len(self.__t_graphs) = %d ") % len(self.__t_graphs)
    for self.__newGraph in self.__t_graphs:
      #self.__newGraph.GetXaxis().SetTitle('Votage (V)')
      #self.__newGraph.GetYaxis().SetTitle('Current (Amps)')
      self.__newGraph.Draw('P')
      self.__c1000.Update()
## Save graphics
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "logFiles/SipmIvsV"+self.__saveTime+".png"
    self.__c1000.SaveAs(self.__outFileName)
    return
##
##
## --------------------------------------------------------------------
##  Use Root... Draw one canvas....
##  Draw multiple plots in pads 
##   onto the canvas
##
##    
  def drawCanvas(self):
    self.__windowTitle = "PO-Number "+str(self.__sipmBatchRequest)
    self.__cX = 200
    self.__cY = 10
    self.__cWidth = 700	 ## canvas width
    self.__cHeight = 500 ## canvas height
    self.__c1 = TCanvas('self.__c1',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c1.Divide(2,3)  ## split canvas into pads....
    self.__c1.cd(1)
    self.__hBiasVoltage.Draw()
    self.__c1.cd(2)
    self.__hDarkCurrent.Draw()
    self.__c1.cd(3)
    self.__hGain.Draw()
    self.__c1.cd(4)
    self.__hTemperature.Draw()
    self.__c1.cd(5)
    self.__h2_IvsVFrame.Draw()
    ## Save graphics
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "outputFiles/graphics2018Aug20/SipmRootHistograms"+self.__saveTime+".png"
    self.__c1.SaveAs(self.__outFileName)
    ## vendor measurments
    self.__windowTitle = "PO-Number "+"Vendor Measurements"
    self.__cX += 100
    self.__cY += 100
    self.__cWidth = 700
    self.__cHeight = 500
    self.__cVendor = TCanvas('self.__cVendor',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)
    self.__cVendor.Divide(2,2)  ## split canvas into pads....
    self.__cVendor.cd(1)
    self.__hVendorBiasVoltage.Draw()
    self.__cVendor.cd(2)
    self.__hVendorDarkCurrent.Draw()
    self.__cVendor.cd(3)
    self.__hVendorGain.Draw()
    self.__cVendor.cd(4)
    self.__hVendorTemperature.Draw()
    ## Save graphics
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "outputFiles/graphics2018Aug20/SipmRootHistograms-VendorMeasurements"+self.__saveTime+".png"
    self.__cVendor.SaveAs(self.__outFileName)

    ## local measurments
    self.__windowTitle = "PO-Number "+"Local Measurements"
    self.__cX += 100
    self.__cY += 100
    self.__cWidth = 1200
    self.__cHeight = 500
    self.__cLocal = TCanvas('self.__cLocal',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)
    self.__cLocal.Divide(4,2)  ## split canvas into pads....
    self.__cLocal.cd(1)
    self.__hlocalBiasVoltage.Draw()
    self.__cLocal.cd(2)
    self.__hlocalDarkCurrent.Draw()
    self.__cLocal.cd(3)
    self.__hlocalGain.Draw()
    self.__cLocal.cd(4)
    self.__hlocalTemperature.Draw()
    self.__cLocal.cd(5)
    self.__hLocalBreakdownVoltage.Draw()
    self.__cLocal.cd(6)
    self.__hLocalCurrentVsVoltageCondition.Draw()
    self.__cLocal.cd(7)
    self.__hLocalXTalk.Draw()
    self.__cLocal.cd(8)
    self.__h2_IvsVFrame.Draw()
    self.__cLocal.SetLogy()
    ## Save graphics
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "outputFiles/graphics2019Feb20/SipmRootHistograms-LocalMeasurements"+self.__saveTime+".png"
    self.__cLocal.SaveAs(self.__outFileName)

    self.__windowTitle = "PO-Number "+"I vs V Linear"
    self.__cWidth = 700	 ## canvas width
    self.__cHeight = 500 ## canvas height
    self.__cX += 100
    self.__cY += 100
    self.__cIvsVLinear = TCanvas('self.__cIvsVLinear',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)
    self.__h2_IvsVFrame.Draw()
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "outputFiles/graphics2018Aug20/SipmRootHistograms-IvsV-Linear"+self.__saveTime+".png"
    self.__cIvsVLinear.SaveAs(self.__outFileName)

    self.__windowTitle = "PO-Number "+"I vs V Log"
    self.__cWidth = 700	 ## canvas width
    self.__cHeight = 500 ## canvas height
    self.__cX += 100
    self.__cY += 100
    self.__cIvsVLog = TCanvas('self.__cIvsVLog',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)
    self.__h2_IvsVFrame.Draw()
    self.__cIvsVLog.SetLogy()
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "outputFiles/graphics2018Aug26/SipmRootHistograms-IvsV-Log"+self.__saveTime+".png"
    self.__cIvsVLog.SaveAs(self.__outFileName)

##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##
##
## --------------------------------------------------------------------
##  Define a Root TTree with all SiPM measurements... local and vendor... 
##
##  The keys are the concatonation of testDate+simpId[testDate]
##  The root tree contains vendor and local measurments.  Their identification
##   is contained in the testType array that can be used to sort them with
##   a root macro file...
##
##	then filled from the database.... then write and save the root 
##	tree file.....
##  Use Root...
  def defineAllMeasurementRootTree(self):
    if(self.__cmjPlotDiag > 0): print("XXXXXXXXXXX __multiWindow__defineAllMeasurementRootTree:: entered \n")
    ## Define output file name; tagged with the time
    self.__tempSipmId = bytearray(30)
    self.__tempSipmTestDate = bytearray(30)
    self.__tempSipmTestType = bytearray(30)
    self.__tempWorkerBarCode = bytearray(120)
    self.__tempWorkStationBarCode = bytearray(120)
    self.__tempDataFileLocation = bytearray(120)
    self.__tempDataFileName = bytearray(120)
    self.__tempPackNumber = bytearray(120)
    ######self.__numberOfEntries = len(self.__plotSipmNumber)
    self.__arrayAllNumberOfEntries= array('i',[0])
    self.__arrayAllPlotSipmNumber = array('f',[0])
    self.__arrayAllPlotBiasVoltage = array('f',[0])
    self.__arrayAllPlotDarkCount = array('f',[0])
    self.__arrayAllPlotGain = array('f',[0])
    self.__arrayAllPlotTemperature = array('f',[0])
    #
    self.__arrayAllPlotBreakDownVoltage = array('f',[0])
    self.__arrayAllPlotDarkCountRate = array('f',[0])
    self.__arrayAllPlotCurrentVsVoltageCondition = array('f',[0])
    self.__arrayAllPlotXTalk = array('f',[0])
    self.__arrayAllPlotLedResponse = array('f',[0])
##
##
##	List to load into root tree....
    self.__allPlotSipmId = []
    self.__allPlotSipmNumber = []
    self.__allPlotSipmMeasureTestDate = []
##
##   Define the root tree for all combined  measurements...
##   We assume that these measurements were done once, but at defineAllVendorSipmMeasurementRootTree
##    different times...
    self.__allRootTree = TTree('AllSipmMeasurements','root tree with ntuples')
##	Define the branches...
##	First define a folder with the test date
    if(self.__cmjPlotDiag > 2): print("XXXXXXXXXXX __multiWindow__defineAllMeasurementRootTree:: len( self.__sipmMeasureTestDate) = %d") % (len(self.__sipmMeasureTestDate))
    ##
    self.__allRootTree.Branch('numberOfEntries',self.__arrayAllNumberOfEntries,'AllNumberOfEntries[1]/I')
    self.__allRootTree.Branch('sipmId',self.__tempSipmId,'tempSipmId[30]/C')
    self.__allRootTree.Branch('sipmTestDate',self.__tempSipmTestDate,'tempSipmTestDate[30]/C')
    self.__allRootTree.Branch('sipmTestType',self.__tempSipmTestType,'tempSipmTestType[30]/C')
    #
    self.__allRootTree.Branch('workerBarCode',self.__tempWorkerBarCode,'tempWorkerBarCode[120]/C')
    self.__allRootTree.Branch('workstationBarCode',self.__tempWorkStationBarCode,'tempWorkStationBarCode[120]/C')
    self.__allRootTree.Branch('dataFileLocation',self.__tempDataFileLocation,'tempDataFileLocation[120]/C')
    self.__allRootTree.Branch('dataFileName',self.__tempDataFileName,'tempDataFileName[120]/C')
    self.__allRootTree.Branch('packNumber',self.__tempPackNumber,'tempPackNumber[120]/C')
    #
    self.__allRootTree.Branch('biasVoltage',self.__arrayAllPlotBiasVoltage,'allBiasVoltage[1]/F')
    self.__allRootTree.Branch('darkCount',self.__arrayAllPlotDarkCount,'allDarkCount[1]/F')
    self.__allRootTree.Branch('gain',self.__arrayAllPlotGain,'allGain[1]/F')
    self.__allRootTree.Branch('temperature',self.__arrayAllPlotTemperature,'allTemperature[1]/F')
    #
    self.__allRootTree.Branch('breakDownVolt',self.__arrayAllPlotBreakDownVoltage,'allBreakDownVolt[1]/F')
    self.__allRootTree.Branch('darkCountRate',self.__arrayAllPlotDarkCountRate,'allDarkCountRate[1]/F')
    self.__allRootTree.Branch('currentVsVoltCond',self.__arrayAllPlotCurrentVsVoltageCondition,'allCurrentVsVoltCond[1]/F')
    self.__allRootTree.Branch('xTalk',self.__arrayAllPlotXTalk,'allX_Talk[1]/F')
    self.__allRootTree.Branch('ledResponse',self.__arrayAllPlotLedResponse,'allLedResponse[1]/F')
    for self.__m in self.__allSipmId.keys() :		## load the arrays to be plotted.
      self.__allPlotSipmId.append(self.__m)
      #print("XXXXXXXXXXX __multiWindow__defineAllMeasurementRootTree:: self.__m = %s ") % (self.__m)
      self.__arrayAllPlotBiasVoltage[0] = float(self.__allBiasVoltage[self.__m])
      self.__arrayAllPlotDarkCount[0] = float(self.__allDarkCount[self.__m])
      self.__arrayAllPlotGain[0] = float(self.__allGain[self.__m])
      self.__arrayAllPlotTemperature[0] = float(self.__allTemperature[self.__m])
      ##
      self.__arrayAllPlotBreakDownVoltage[0] = float(self.__allBreakdown_voltage[self.__m])
      self.__arrayAllPlotDarkCountRate[0] = float(self.__allDark_count_rate[self.__m])
      self.__arrayAllPlotCurrentVsVoltageCondition[0] = float(self.__allCurrent_vs_voltage_condition[self.__m])
      self.__arrayAllPlotXTalk[0] = float(self.__allX_talk[self.__m])
      self.__arrayAllPlotLedResponse[0] = float(self.__allLed_response[self.__m])
##	There has to be a better way to do this...
##	But amaziningly, there is no easy way to take a 
##	string and convert it into a character!...
##	And the Root trees need a character array to 
##	be read by a root macro later!
      ## first initialize character arrays!
      for n in range(0,29):
	self.__tempSipmId[n] = 0
	self.__tempSipmTestDate[n] = 0
	self.__tempSipmTestType[n] = 0
      for n in range(0,119):
	self.__tempWorkerBarCode[n] = 0
	self.__tempWorkStationBarCode[n] = 0
	self.__tempDataFileLocation[n] = 0
	self.__tempDataFileName[n] = 0
	self.__tempPackNumber[n] = 0
      m = 0		## SipmId
      for self.__character in self.__allSipmId[self.__m]:
	self.__tempSipmId[m] = self.__character
	m += 1
      m = 0		## Mesurement Date
      for self.__character in self.__allSipmMeasureTestDate[self.__m]:
	self.__tempSipmTestDate[m] = self.__character
	m += 1
      m = 0		## Test Type
      for self.__character in self.__allTestType[self.__m]:
	self.__tempSipmTestType[m] = self.__character
	m += 1
      m = 0		## Worker bar code
      for self.__character in self.__allWorkerBarCode[self.__m]:
	self.__tempWorkerBarCode[m] = self.__character
	m += 1
      m = 0		## Worker bar code
      for self.__character in self.__allWorkStationBarCode[self.__m]:
	self.__tempWorkStationBarCode[m] = self.__character
	m += 1
      m = 0		## Worker bar code
      for self.__character in self.__allData_file_location[self.__m]:
	self.__tempDataFileLocation[m] = self.__character
	m += 1
      m = 0		## Worker bar code
      for self.__character in self.__allData_file_name[self.__m]:
	self.__tempDataFileName[m] = self.__character
	m += 1
      m = 0		## Pack Number
      try:
	for self.__character in self.__allPack_number[self.__m]:
	  self.__tempPackNumber[m] = self.__character
	  m += 1    
      except:
	self.__none = 'none'
	for self.__character in self.__none:
	  self.__tempPackNumber[m] = self.__character
      #self.__TestType = self.__saveTestType[self.__n]
	  ## Add stuff here to fill the branches one at a time.....
      ## from  File = "DiCountersRootQuery.py"  line 394
      self.__arrayAllNumberOfEntries[0] = len(self.__allPlotSipmId)
      self.__allRootTree.Fill()		## fill the root tree here...
    self.__rootTreeFile.Write()	## write a tree for all  measurements!
    print("XXXXXXXXXXX __multiWindow__defineAllSipmMeasurementRootTree::  writeAllRootTree: 'AllSipmMeasurements'") 
    if(self.__cmjPlotDiag > 1): print("XXXXXXXXXXX __multiWindow__defineAllSipmMeasurementRootTree::len(self.__allPlotSipmId) = %d \n") %(len(self.__allPlotSipmId))
    if(self.__cmjPlotDiag > 0): print("XXXXXXXXXXX __multiWindow__defineAllSipmMeasurementRootTree:: exit \n")
    return
##
##
## --------------------------------------------------------------------
##  Define a Root TTree for each SiPM I vs V measurement...
  def defineSipmIvsVMeasurementRootTree(self):
    self.__tempSipmId = bytearray(30)
    self.__tempSipmTestDate = bytearray(120)
    for self.__n in self.__sipmMeasureTestDate_IvsV.keys():
      #print("XXXXXXXXXXX defineSipmIvsVMeasurementRootTree::  self.__sipmId_IvsV[%s] = %s") % (self.__n, self.__sipmId_IvsV[self.__n])
      for self.__m in self.__sipmId_IvsV[self.__n].keys():
	self.__localFolderDate = self.__n
	self.__localFolderDate.replace(' ','-')
	self.__localFolderDate.replace(':','-')
	self.__localRootTree = TTree('SipmIvsV-'+self.__localFolderDate,'root tree for IvsV')
	#if(self.__cmjPlotDiag > 2): print("XXXXXXXXXXX defineSipmIvsVMeasurementRootTree:: self.__localFolderDate = %s") % (self.__localTestType,self.__localFolderDate)
	self.__tempNumberOfEntries = int(0)
	self.__plotIvsV_current = []
	self.__plotIvsV_voltage = []
	self.__arrayIvsV_current = array('f',self.__plotIvsV_current)
	self.__arrayIvsV_voltage = array('f',self.__plotIvsV_voltage)
	for self.__j in self.__IvsV_voltage[self.__n][self.__m].keys():
	  #print("XXXXXXXXXXX defineSipmIvsVMeasurementRootTree:: self.__IvsV_voltage[%s][%s][%s] = %s, self.__IvsV_current[%s][%s][%s] = %s ") % (self.__n,self.__m,self.__j,self.__IvsV_voltage[self.__n][self.__m][self.__j],self.__n,self.__m,self.__j,self.__IvsV_current[self.__n][self.__m][self.__j])
	  self.__plotIvsV_current.append(float(self.__IvsV_current[self.__n][self.__m][self.__j]))
	  self.__plotIvsV_voltage.append(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]))

	  self.__arrayIvsV_current.append(float(self.__IvsV_current[self.__n][self.__m][self.__j]))
	  self.__arrayIvsV_voltage.append(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]))
	self.__numberOfEntries = len(self.__plotIvsV_voltage)
	#print("XXXXXXXXXXX defineSipmIvsVMeasurementRootTree::  len(self.__plotIvsV_voltage) = %d") % (len(self.__plotIvsV_voltage))
	self.__arrayNumberOfEntries = array('i',self.__numberOfEntries*[0])
	## Place each test date and test_type in its own root tree.
	self.__localRootTree.Branch('numberOfEntries',self.__arrayNumberOfEntries,'numberOfEntries/I')
	self.__localRootTree.Branch('sipm_current',self.__arrayIvsV_current,'self.__arrayIvsV_current[numberOfEntries]/F')
	self.__localRootTree.Branch('sipm_voltage',self.__arrayIvsV_voltage,'self.__arrayIvsV_voltage[numberOfEntries]/F')
	self.__arrayNumberOfEntries[0] = len(self.__plotIvsV_voltage)
	self.__localRootTree.Fill()		## fill the root tree
	self.__localRootTree.Write()		## write the root tree to the output file
    return
##
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################



##
##
## --------------------------------------------------------------------
##  Define a PyRoot TTree... Fill it with the arrays defined previously
##	then filled from the database.... then write and save the root 
##	tree file.....
##  Use Root...
  def definePyRootTree(self):
    if(self.__cmjPlotDiag > 0): print("XXXXXXXXXXX entered definePyRootTree \n")
    ## Define output file name; tagged with the time
    self.__treeTime = myTime()
    self.__treeTime.getComputerTime()
    self.__saveTreeTime = self.__treeTime.getTimeForSavedFiles()
    self.__outRootTreeFileName = "outputFiles/SipmRootHistograms"+self.__saveTreeTime+".root"
    print ("out Root Tree File name = %s \n") % (self.__outRootTreeFileName)
    ## Define the root tree
    self.__rootTreeFile = TFile(self.__outRootTreeFileName,'RECREATE')
    self.__localRootTree = TTree('SipmMeasurement','root tree with ntuples')
    ## Define the branches in the root tree... load previously loaded lists.
##
##
##	Define the arrays contained in each branch from previosly loaded list
    self.__numberOfEntries = len(self.__plotSipmNumber)
    self.__arrayNumberOfEntries= array('i',self.__numberOfEntries*[0])
    self.__arrayPlotSipmNumber = array('f',self.__plotSipmNumber)
    #self.__arrayPlotTestType = array('c',self.__plotTestType)
    self.__arrayPlotBiasVoltage = array('f',self.__plotBiasVoltage)
    self.__arrayPlotDarkCurrent = array('f',self.__plotDarkCount)
    self.__arrayPlotGain = array('f',self.__plotGain)
    self.__arrayPlotTemperature = array('f',self.__plotTemperature)
##
##
##	Define the branches
    self.__localRootTree.Branch('numberOfEntries',self.__arrayNumberOfEntries,'numberOfEntries/I')
    self.__localRootTree.Branch('sipmNumber',self.__arrayPlotSipmNumber,'sipmNumber[numberOfEntries]/F')
    self.__localRootTree.Branch('biasVoltage',self.__arrayPlotBiasVoltage,'biasVoltage[numberOfEntries]/F')
    self.__localRootTree.Branch('darkCurrent',self.__arrayPlotDarkCurrent,'darkCurrent[numberOfEntries]/F')
    self.__localRootTree.Branch('gain',self.__arrayPlotGain,'gain[numberOfEntries]/F')
    self.__localRootTree.Branch('temperature',self.__arrayPlotTemperature,'temperature[numberOfEntries]/F')
    self.__arrayNumberOfEntries[0] = len(self.__plotSipmNumber)
    self.__localRootTree.Fill()		## fill the root tree here...
    print("len(self.__arrayPlotSipmNumber) = %d \n") %(len(self.__arrayPlotSipmNumber))
    self.__rootTreeFile.Write()
    self.__rootTreeFile.Close()
    if(self.__cmjPlotDiag > 0): print("XXXXXXXXXXX exit definePyRootTree \n")
    return  
##
## --------------------------------------------------------------------
##
  def turnOnDebug(self,tempDebug):
    self.__database_config.setDebugOn()
    self.__cmjPlotDiag = tempDebug
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
  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
  options, args = parser.parse_args()
  print("'__main__': options.debugMode = %s \n") % (options.debugMode)
  print("'__main__': options.database  = %s \n") % (options.database)
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