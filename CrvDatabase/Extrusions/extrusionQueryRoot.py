# -*- coding: utf-8 -*-
## File = "extrusionQuerryRoot.py"
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
##   Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Jul26... Initialize bytearry strings with each event in root tree
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##                        yellow highlight to selected scrolled list items
##  Modified by cmj2020Jun15... Changeto hdbClient_v2_2
##  Modified by cmj2020Jun16.... Change to cmjGuiLibGrid2019Jan30
##  Modified by cmj2020Jul09.... Changed crvUtilities2018->crvUtilities; changed cmjGuiLibGrid2018Oct1->cmjGuiLibGrid2019Jan30
##  Modified by cmj2020Aug03... cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##  Modified by cmj2022Jan26... finally able to save character strings in root trees using python3
##  Modified by cmj2022Jan26... make production database default
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
from tkinter import *         # get widget class
import sys
##
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *
from databaseConfig import *
from cmjGuiLibGrid import *       ## cmj2020Aug03
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import time
##            Import the graphing modules
##import numpy as np
##import matplotlib.pyplot as plt
##import matplotlib.ticker as mtick
##  Import for PyRoot
import ROOT as _root  ## import to define vectors which are used to save strings
from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH2F, TGraph, TStyle, TTree, TString
from ROOT import gROOT, gBenchmark, gRandom, gSystem, gStyle, Double_t
from array import array
##
##
ProgramName = "extrusionQueryRoot"
Version = "version2022.01.26"
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
    self.__database_config  = databaseConfig()
    #self.__database_config.setDebugOn()  ## 2020Jul09... turn off these debugs!
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
    self.__extrusionBatchResults = []  # The list of batches that will be histogrammed....
##      Arrays to plot...keep these in scope in the whole class
    self.__extrusionId = {}
    self.__extrusionNumber = {}
    self.__lightYield = {}
    self.__base ={}
    self.__height = {}
    self.__holeDiameter1 = {}
    self.__holeDiameter2 = {}
    self.__extrusionLength = {}  ## cmj2020Jun15
    self.__plotExtrusionId = []
    self.__plotLightYieldExtrusionNumber = []
    self.__plotLightYieldExtrusion = []
    self.__plotBase = []
    self.__plotHeight = []
    self.__plotHoleDiameter1 = []
    self.__plotHoleDiameter2 = []
    self.__plotExtrusionLength = [] ## cmj2020Jun15
##      Define Output Log file... remove this later
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('extrusionQuerries')
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
    self.__myInstructions.setText('','Instructions/InstructionsForExtrusionQuerry2018Mar26.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__strName.append("Extrusion Batch")
    self.__labelWidth = 15
    self.__ExtrusionBatchStr = myStringEntry(self,self.__firstRow,self.__col,self.__mySaveIt)
    self.__ExtrusionBatchStr.setEntryText(self.__strName[self.__sCount])
    self.__ExtrusionBatchStr.setLabelWidth(self.__labelWidth)
    self.__ExtrusionBatchStr.setEntryWidth(self.__entryWidth)
    self.__ExtrusionBatchStr.setButtonWidth(self.__buttonWidth)
    self.__ExtrusionBatchStr.makeEntry()
    self.__ExtrusionBatchStr.grid(row=self.__firstRow,column=self.__col,stick=W,columnspan=2)
    self.__firstRow += 1
##      Add list box to first columnspan
##      This sequence presents a list box filled with the
##      available batches.  A left double click appends a
##      another comma sepparated batch...
##      Click the "Batches button" to load the list of batches
    self.__tempBatchResults = []
    self.__tempBatchResults = self.getExtrusionsBatchesFromDatabase()
    if(cmjPlotDiag != 0) : print((("self.__tempBatchResults = %s \n") % (self.__tempBatchResults)))
    self.__myOptions = []
    for self.__m in self.__tempBatchResults:
      self.__temp = self.__m.rsplit(",",8)
      self.__myOptions.append(self.__temp[0])
    self.__myScrolledList = ScrolledList(self,self.__myOptions)
    self.__myScrolledList.grid(row=self.__firstRow,column=self.__col,sticky=W,rowspan=4)
##      New Row
##      Add button to get available batches...
##      Enter the request for batches to be histogrammed.
##      A single batch or a string of comma separated multiple batches
##      may be selected for histogramming.
    self.__col = 1
    self.__secondRow = 2
    self.__buttonWidth = 10
    self.__getValues = Button(self,text='Batches',command=self.loadExtrusionBatchRequest,width=self.__buttonWidth,bg='lightblue',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##      Plot scatter plots
    self.__getValues = Button(self,text='Scatter Plots',command=self.getScatterPlots,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##      Plot histograms
    self.__getValues = Button(self,text='Histograms',command=self.getHistograms,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
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
#         Display the date the script is being run
    self.__date = myDate(self,self.__row,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__row,column=self.__col,sticky=E)
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
##      Make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Extrusion Tables"
    self.__whichDatabase = 'development'
    if(cmjPlotDiag !=0): print("...multiWindow::getFromDevelopmentDatabase... get to development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
## -------------------------------------------------------------------
##      Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Extrusion Tables"
    self.__whichDatabase = 'production'
    if(cmjPlotDiag !=0): print("...multiWindow::getFromProductionDatabase... get to production database \n")
    self.__queryUrl = self.__database_config.getProductionQueryUrl()
##
## -------------------------------------------------------------------
##      Load batches requested from batch window
##      This it the list of batches that will be histogrammed...
  def loadExtrusionBatchRequest(self):
    if(cmjPlotDiag != 0):
      print("... loadExtrusionBatchRequest \n")
      print((("... mySaveIt.getStrEntry = %s \n") % (self.__mySaveIt.getStrEntry("Extrusion Batch"))))
    if(self.__mySaveIt.getStrEntry('Extrusion Batch') != "NULL"):
      print("from mySaveIt \n")
      print((("... mySaveIt.getStrEntry = %s \n") % (self.__mySaveIt.getStrEntry("Extrusion Batch"))))
      self.__extrusionBatchRequest = self.__mySaveIt.getStrEntry('Extrusion Batch').rsplit(",",self.__numberOfBatches)
    elif (self.__myScrolledList.fetchList() != ""):
      print ("from myScrolledList")
      self.__extrusionBatchRequest = self.__myScrolledList.fetchList().rsplit(",",self.__numberOfBatches)
    else:
      print("error: enter a correct batch name!!! \n")
    if(cmjPlotDiag != 0):
      print((("... loadExtrusionBatchRequest: len(self.__extrusionBatchRequest) = %d \n") %(len(self.__extrusionBatchRequest))))
      print((("... loadExtrusionBatchRequest: self.__extrusionBatchRequest = %s \n") %(self.__extrusionBatchRequest)))
    for self.__localExtrusionBatch in self.__extrusionBatchRequest:
      if(self.__localExtrusionBatch != ''):
        if(cmjPlotDiag != 0): print((("get string?? %s \n") %(self.__localExtrusionBatch)))
        self.__tempExtrusion = []
        self.__tempExtrusion = self.getExtrusionsFromDatabase(self.__localExtrusionBatch) 
        if(cmjPlotDiag != 0): print("XXXXXX: loadExtrusionBatchRequest... Calling unpackExtrusions  \n")
        self.unpackExtrusions(self.__tempExtrusion)
    return
##
## -------------------------------------------------------------------
##      Make querries to get all extrusion batches to data base
  def getExtrusionsBatchesFromDatabase(self):
    self.__getExtrusionBatchValues = DataQuery(self.__queryUrl)
    #print (".... getExtrusionsBatchesFromDatabase: self.__queryUrl   = %s \n") % (self.__queryUrl)
    self.__localExtrusionBatchValues = []
    self.__table = "extrusion_batches"
    self.__fetchThese = "batch_id,average_ref_counts,stdev_ref_counters,percent_ref_counters,average_light_yield_cnt,stdev_light_yield_cnt,percent_light_yield_cnt,create_time"
    self.__fetchCondition = "create_time:ge:2017-05-15"
    self.__numberReturned = 0
    if(cmjPlotDiag > 1): print(("===========> getExtrusionsBatchesFromDatabase %s %s %s \n" %(self.__database,self.__table,self.__fetchThese)))
    #self.__localExtrusionBatchValues = self.__getExtrusionBatchValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese,limit=10,echoUrl=True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localExtrusionBatchValues = self.__getExtrusionBatchValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localExtrusionBatchValues != -9999) : break
    ## cmj2018Mar26
    if(cmjPlotDiag > 1): print((" getExtrusionsBatchesFromDatabase: self.__extrusionBatchValues = %s \n" %(self.__localExtrusionBatchValues)))
    self.__numberOfBatches = len(self.__localExtrusionBatchValues)
    if(cmjPlotDiag != 0):
      for self.__l in self.__localExtrusionBatchValues:
        print((self.__l))
    return self.__localExtrusionBatchValues
##
## -------------------------------------------------------------------
##      Make querries about extrusions to data base
  def getExtrusionsFromDatabase(self,tempBatch):
    self.__getExtrusionValues = DataQuery(self.__queryUrl)
    self.__extrusionResults = []
    self.__table = "extrusions"
    self.__fetchThese = "extrusion_id,light_yield,base_mm,height_mm,hole_diameter_1_mm,hole_diameter_2_mm,comments,length_mm" ## cmj2020Jun15
    self.__fetchCondition = "batch_id:eq:"+str(tempBatch)
    self.__numberReturned = 0
    #self.__extrusionResults = self.__getExtrusionValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese,True)
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            # sometimes the database does not answer... give it a few tries!
      self.__extrusionResults = self.__getExtrusionValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,self.__fetchThese)
      if(cmjPlotDiag > 1): print((("XXXXXXXgetExtrusionsFromDatabase: WARNING!!!  loop over tries to database: n = %s  %s \n") % (n, self.__extrusionResults)))
      if (self.__extrusionResults[0] != -9999) : break
    ## cmj2018Mar26
    if(cmjPlotDiag != 0):
      for self.__l in self.__extrusionResults:
        print((self.__l))
    return self.__extrusionResults
## --------------------------------------------------------------
## This method calls the method to get the entries to the database
## and plot scatter plots
  def getScatterPlots(self):
    self.plotScatterPlots()
## --------------------------------------------------------------
## This method calls the method to get the entries to the database
## and plot Histograms
  def getHistograms(self):
    self.plotHistograms()
##
##    
## --------------------------------------------------------------
##      Unpack the database information for plotting,etc
  def unpackExtrusions(self,tempExtrusion):
    if(cmjPlotDiag != 0):
      print("XXXXXXX unpackExtrusions: Enter\n")
      print((("....unpackExtrusions: tempExtrusion = %s \n") % tempExtrusion))
    if(tempExtrusion[0] == -9999):
      print("XXXXXXX unpackExtrusions: WARNING!!! Extrusion did not unpack! \n") 
      print((("XXXXXXX unpackExtrusions: tempExtrusion = %s \n") % (tempExtrusion)))
      return
    for self.__record in tempExtrusion:
      self.__item = []
      self.__item = self.__record.rsplit(',',8)  ## cmj2020Jun15
      if (self.__item[0] != ""):
        self.__tempExtrusionId = self.__item[0]
        if(cmjPlotDiag > 0):
          print((("XXXXXXX unpackExtruions: self.__tempExtrusionId = %s \n") % (self.__tempExtrusionId)))
          print((("XXXXXXX unpackExtruions: self.__tempExtrusionId[0:2] = %s \n") % (self.__tempExtrusionId[0:2])))
          print((("XXXXXXX unpackExtruions: self.__tempExtrusionId[0:12] = %s \n") % (self.__tempExtrusionId[0:12])))
          print((("XXXXXXX unpackExtruions: self.__tempExtrusionId[0:8] = %s \n") % (self.__tempExtrusionId[0:8])))
        if(self.__tempExtrusionId[0:2] == "RD"):
          self.__tempNumber      = self.__tempExtrusionId[2:]
        elif (self.__tempExtrusionId[0:12] == "Mu2e_CRVscin"):
          self.__tempNumber = self.__tempExtrusionId[12:]
        elif (self.__tempExtrusionId[0:8] == "Mu2e-CRV"):
          self.__tempNumber = self.__tempExtrusionId[8:]
        else:
          print("XXXXXXX unpackExtrusions: Scintillator Counter Format problem!!!\n")
          print((("XXXXXXX unpackExtruions: self.__tempExtrusionId = %s \n") % (self.__tempExtrusionId)))
          print("XXXXXXX unpackExtrusions: Inform maintance expert!!!\n")
          print("XXXXXXX unpackExtrusions: --EXIT SCIPT -- LOOK AT HOW COUNTERS ARE NAMED!!!!\n")
          sys.exit()  ## exit script... inform maintance expert
        self.__tempLightYield  = self.__item[1]
        self.__tempBase       = self.__item[2]
        self.__tempHeight      = self.__item[3]
        self.__tempHoleDia1      = self.__item[4]
        self.__tempHoleDia2      = self.__item[5]
        self.__tempExtrusionLength = self.__item[7]   ## cmj2020Jun15
        if(cmjPlotDiag != 0):  ## diagnostic print statements
          print("unpackExtrusions ........ New Counter ............ \n")
          print((("... self.__item = %s \n") % self.__item))
          print((("... self.__tempExtrusionId = %s \n") % self.__tempExtrusionId))
        self.__extrusionId[self.__tempExtrusionId]     = self.__tempExtrusionId
        self.__extrusionNumber[self.__tempNumber] = self.__tempNumber
        self.__lightYield[self.__tempNumber]      = self.__tempLightYield
        self.__base[self.__tempNumber]      = self.__tempBase
        self.__height[self.__tempNumber]      = self.__tempHeight
        self.__holeDiameter1[self.__tempNumber]      = self.__tempHoleDia1
        self.__holeDiameter2[self.__tempNumber]      = self.__tempHoleDia2
        self.__extrusionLength[self.__tempNumber]      = self.__tempExtrusionLength ## cmj2020Jun15
##            Load arrays for root files....
        self.__plotExtrusionId.append(self.__tempNumber)
      ## cmj2018Mar26
        try:
          self.__plotLightYieldExtrusionNumber.append(float(self.__tempNumber))
        except ValueError:
          print((('XXXXXXX unpackExtrusions: Skip counter: %s \n') % (self.__tempNumber)))
          continue  ## go to the next extrusion!
        ## cmj2018Mar26
        self.__plotLightYieldExtrusion.append(float(self.__lightYield[self.__tempNumber]))
        self.__plotBase.append(float(self.__base[self.__tempNumber]))
        self.__plotHeight.append(float(self.__height[self.__tempNumber]))
        self.__plotHoleDiameter1.append(float(self.__holeDiameter1[self.__tempNumber]))
        self.__plotHoleDiameter2.append(float(self.__holeDiameter2[self.__tempNumber]))
        self.__plotExtrusionLength.append(float(self.__extrusionLength[self.__tempNumber]))
##
    if(cmjPlotDiag != 0):            ## diangonstic print statements
      print((("unpackExtrusions ........len(self.__plotExtrusionId) = %d \n") % (len(self.__plotExtrusionId))))
      print((("unpackExtrusions ........len(self.__plotLightYieldExtrusionNumber) = %d \n") % (len(self.__plotLightYieldExtrusionNumber))))
      print((("unpackExtrusions ........len(self.__plotLightYieldExtrusion) = %d \n") % (len(self.__plotLightYieldExtrusion))))
      print((("unpackExtrusions ........len(self.__plotBase) = %d \n") % (len(self.__plotBase))))
      print((("unpackExtrusions ........len(self.__plotHeight) = %d \n") % (len(self.__plotHeight))))
      print((("unpackExtrusions ........len(self.__holeDiameter1) = %d \n") % (len(self.__holeDiameter1))))
      print((("unpackExtrusions ........len(self.__holeDiameter2) = %d \n") % (len(self.__plotHoleDiameter2))))
      print((("unpackExtrusions ........len(self.__extrusionLength) = %d \n") % (len(self.__extrusionLength))))
      print("unpackExtrusions ........ ExtrusionId ............ \n")
      for self.__m in list(self.__extrusionId.keys()):
        print((("...... self.__extrusionId.keys()     = %s || self.__extrusionId[%s] = %s \n")     % (self.__m,self.__m,self.__extrusionId[self.__m])))
      print("unpackExtrusions ........ ExtrusionNumber ............ \n")
      for self.__m in list(self.__extrusionNumber.keys()):
        print((("...... self.__extrusionNumber.keys() = %s || self.__extrusionNumber[%s] = %s \n") % (self.__m,self.__m,self.__extrusionNumber[self.__m])))
      print("unpackExtrusions ........ lightYield ............ \n")
      for self.__m in list(self.__lightYield.keys()):
        print((("...... self.__lightYield.keys()      = %s || self.__lightYield[%s] = %s \n")      % (self.__m,self.__m,self.__lightYield[self.__m])))
      for self.__m in list(self.__extrusionLength.keys()):
        print((("...... self.__extrusionLength.keys()      = %s || self.__extrusionLength[%s] = %s \n")      % (self.__m,self.__m,self.__extrusionLength[self.__m])))
    if(cmjPlotDiag != 0): print("XXXXXXX unpackExtrusions: Exit\n")
##
##
## --------------------------------------------------------------------
##   Plot scatter plots
  def plotScatterPlots(self):
    #self.__windowTitle = 'Extrusion Batch: '+str(self.__localExtrusionBatch)
    self.__windowTitle = 'Extrusion: '+str(self.__mySaveIt.getStrEntry('Extrusion Batch'))
    self.__c2 = TCanvas('self.__c2',self.__windowTitle,200,10,800,700)
    self.__c2.SetFillColor(0)
#    self.__c2.SetGrid()
    self.__c2.Divide(2,3)
    self.__n = len(self.__plotLightYieldExtrusionNumber)
    self.__extrusionNumberArray = array('f')
    self.__lightYieldArray = array('f')
    self.__baseArray = array('f') 
    self.__heightArray = array('f')
    self.__diameter1Array = array('f') 
    self.__diameter2Array = array('f')
    for i in range(self.__n):
      self.__extrusionNumberArray.append(self.__plotLightYieldExtrusionNumber[i])
      self.__lightYieldArray.append(float(self.__plotLightYieldExtrusion[i]))
      self.__baseArray.append(float(self.__plotBase[i]))
      self.__heightArray.append(float(self.__plotHeight[i]))
      self.__diameter1Array.append(float(self.__plotHoleDiameter1[i]))
      self.__diameter2Array.append(float(self.__plotHoleDiameter2[i]))
#      First pad... light yield
    self.__c2.cd(1)
    self.__graph1 = TGraph(self.__n,self.__extrusionNumberArray,self.__lightYieldArray)
    #self.__graph1.SetLineColor(2)
    self.__graph1.SetLineWidth(0)
    self.__graph1.SetMarkerColor(4)
    self.__graph1.SetMarkerStyle(21)
    self.__graph1.SetTitle('Light Yield')
    self.__graph1.GetXaxis().SetTitle('Extrusion Number')
    self.__graph1.GetYaxis().SetTitle('Counts')
    self.__graph1.Draw()
#      Third pad  base width  measurment
    self.__c2.cd(3)
    self.__graph2 = TGraph(self.__n,self.__extrusionNumberArray,self.__baseArray)
    self.__graph2.SetLineWidth(0)
    self.__graph2.SetMarkerColor(4)
    self.__graph2.SetMarkerStyle(21)
    self.__graph2.SetTitle('Base Measurement')
    self.__graph2.GetXaxis().SetTitle('Extrusion Number')
    self.__graph2.GetYaxis().SetTitle('Base (mm)')
    self.__graph2.Draw()
#      Forth pad height measurment
    self.__c2.cd(4)
    self.__graph3 = TGraph(self.__n,self.__extrusionNumberArray,self.__heightArray)
    self.__graph3.SetLineWidth(0)
    self.__graph3.SetMarkerColor(4)
    self.__graph3.SetMarkerStyle(21)
    self.__graph3.SetTitle('Height Measurement')
    self.__graph3.GetXaxis().SetTitle('Extrusion Number')
    self.__graph3.GetYaxis().SetTitle('Height (mm)')
    self.__graph3.Draw()
#      Fifth pad: Diameter 1
    self.__c2.cd(5)
    self.__graph4 = TGraph(self.__n,self.__extrusionNumberArray,self.__diameter1Array)
    self.__graph4.SetLineWidth(0)
    self.__graph4.SetMarkerColor(4)
    self.__graph4.SetMarkerStyle(21)
    self.__graph4.SetTitle('Diameter 1 Measurement')
    self.__graph4.GetXaxis().SetTitle('Extrusion Number')
    self.__graph4.GetYaxis().SetTitle('Diameter 1 (mm)')
    self.__graph4.Draw()
#      Sixth pad: Diameter 2
    self.__c2.cd(6)
    self.__graph5 = TGraph(self.__n,self.__extrusionNumberArray,self.__diameter2Array)
    self.__graph5.SetLineWidth(0)
    self.__graph5.SetMarkerColor(4)
    self.__graph5.SetMarkerStyle(21)
    self.__graph5.SetTitle('Diameter 2 Measurement')
    self.__graph5.GetXaxis().SetTitle('Extrusion Number')
    self.__graph5.GetYaxis().SetTitle('Diameter 2 (mm)')
    self.__graph5.Draw()
#      Draw canvas
    self.__c2.Modified()
    self.__c2.Update()
    sleep(5)
##
##
## --------------------------------------------------------------------
##   Plot scatter plots
  def plotScatterPlotsOld(self):
    self.__nBins = int(len(self.__plotLightYieldExtrusionNumber))
    self.__lowBin = min(self.__plotLightYieldExtrusionNumber)
    self.__hiBin = max(self.__plotLightYieldExtrusionNumber)
    self.__pLightYield = TH1F('self.__hLightYield','Light Yeild',self.__nBins,self.__lowBin,self.__hiBin)
    self.__pLightYield.SetMarkerStyle(20)
    self.__pLightYield.SetMarkerColor(4)
    for self.__event in list(self.__lightYield.keys()):
      self.__pLightYield.Fill(float(self.__event),float(self.__lightYield[self.__event]))
    self.__c2 = TCanvas('self.__c2','Plots',200,10,700,500)
    self.__pLightYield.Draw("P")
    self.__c2.Update()
    sleep(5)
    
    return
##
##
##
##
##
## --------------------------------------------------------------------
##   Plot Histograms with root
##
  def plotHistograms(self):
    self.bookHistograms()
    self.fillHistograms()
    self.drawCanvas()
##
## --------------------------------------------------------------------
##  A method to book the histograms....
##
  def bookHistograms(self):
    self.__labelSize = float(0.05)
    self.__titleSize = float(0.05)
    self.__nBins = 100
    self.__lowBin = 1.0e6
    self.__hiBin  = 5.0e6
    self.__hLightYield = TH1F('self.__hLightYield','Light Yeild',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hLightYield.GetXaxis().SetTitle('ADC')
    self.__hLightYield.GetYaxis().SetTitle('Counts')
    self.__hLightYield.GetXaxis().SetLabelSize(self.__labelSize)
    self.__hLightYield.GetXaxis().SetTitleSize(self.__titleSize)
    self.__hLightYield.SetFillColor(2)
    self.__lowBin = 4.8e1
    self.__hiBin  = 5.8e1
    self.__hBase = TH1F('self.__hBase','Base Measurement',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hBase.SetFillColor(4)
    self.__lowBin = 15.0
    self.__hiBin  = 25.0
    self.__hHeight = TH1F('self.__hHeight','Height Measurement',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hHeight.SetFillColor(4)
    self.__lowBin = 2.0
    self.__hiBin  = 3.0
    self.__hDiameter1 = TH1F('self.__hDiameter1','Diameter 1 Measurement',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hDiameter1.SetFillColor(3)
    self.__lowBin = 2.0
    self.__hiBin  = 3.0
    self.__hDiameter2 = TH1F('self.__hDiameter2','Diameter 2 Measurement',self.__nBins,self.__lowBin,self.__hiBin)
    self.__hDiameter2.SetFillColor(3)
##
## --------------------------------------------------------------------
##  Fill the histograms!!!
##
  def fillHistograms(self):
    for self.__event in list(self.__lightYield.keys()):
      self.__hLightYield.Fill(float(self.__lightYield[self.__event]))
      self.__hBase.Fill(float(self.__base[self.__event]))
      self.__hHeight.Fill(float(self.__height[self.__event]))
      self.__hDiameter1.Fill(float(self.__holeDiameter1[self.__event]))
      self.__hDiameter2.Fill(float(self.__holeDiameter2[self.__event])) 
##
##
## --------------------------------------------------------------------
##  Draw one canvas....
##  Draw multiple plots in pads 
##   onto the canvas
##
##    
  def drawCanvas(self):
    #self.__windowTitle = 'Extrusion Batch: '+str(self.__localExtrusionBatch)
    self.__windowTitle = 'Extrusion: '+str(self.__mySaveIt.getStrEntry('Extrusion Batch'))
    self.__cX = 200
    self.__cY = 10
    self.__cWidth = 700      ## canvas width
    self.__cHeight = 500      ## canvas height
    self.__c1 = TCanvas('self.__c1',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)  
    self.__c1.Divide(2,3)  ## split canvas into pads....
    self.__c1.cd(1)
    self.__hLightYield.Draw()
    self.__c1.cd(3)
    self.__hBase.Draw()
    self.__c1.cd(4)
    self.__hHeight.Draw()
    self.__c1.cd(5)
    self.__hDiameter1.Draw()
    self.__c1.cd(6)
    self.__hDiameter2.Draw()
    self.__c1.Modified()
    self.__c1.Update()
    self.defineTree()
    #sleep(5)

##
##
## --------------------------------------------------------------------
##  Define Root TTree... Fill it with the arrays defined previously
##      then filled from the database.... then write and save the root 
##      tree file.....
##            This writes a regular root tree!
##  Use Root...
  def defineTree(self):
    ## Define output file name; tagged with the time
    self.__treeTime = myTime()
    self.__treeTime.getComputerTime()
    self.__saveTreeTime = self.__treeTime.getTimeForSavedFiles()
    self.__outRootTreeFileName = "outputFiles/ExtrusionRootHistograms"+self.__whichDatabase+self.__saveTreeTime+".root"
    print((("out Root Tree File name = %s \n") % (self.__outRootTreeFileName)))
    ## Define the root tree
    self.__rootTreeFile = TFile(self.__outRootTreeFileName,'RECREATE')
    self.__localRootTree = TTree('Extrusion','root tree with ntuples')
##
##
##      Define the arrays contained in each branch from previosly loaded list
    self.__arrayPlotExtrusionNumber = array('f',[0])
    ####self.__arrayPlotTestType = array('c',self.__plotTestType)
    self.__arrayPlotLightYield = array('f',[0])
    self.__arrayPlotBase = array('f',[0])
    self.__arrayPlotHeight = array('f',[0])
    self.__arrayPlotHoleDiameter1 = array('f',[0])
    self.__arrayPlotHoleDiameter2 = array('f',[0])
    self.__arrayPlotExtrusionLength = array('f',[0])
##
##
##      Define the branches
    self.__localRootTree.Branch('extrusionNumber',self.__arrayPlotExtrusionNumber,'self.__arrayPlotExtrusionNumber[1]/F')
    self.__localRootTree.Branch('lightYield',self.__arrayPlotLightYield,'self.__arrayPlotLightYield[1]/F')
    self.__localRootTree.Branch('base',self.__arrayPlotBase,'self.__arrayPlotBase[1]/F')
    self.__localRootTree.Branch('height',self.__arrayPlotHeight,'self.__arrayPlotHeight[1]/F')
    self.__localRootTree.Branch('diameter1',self.__arrayPlotHoleDiameter1,'self.__arrayPlotHoleDiameter1[1]/F')
    self.__localRootTree.Branch('diameter2',self.__arrayPlotHoleDiameter2,'self.__arrayPlotHoleDiameter2[1]/F')
    self.__localRootTree.Branch('extrLength',self.__arrayPlotExtrusionLength,'self.__arrayPlotExtrusionLength[1]/F')  ## cmj2020Jun15
    #print("before filling the tree \n")
    #print(" self.__extrusionNumber = %s \n") % (self.__extrusionNumber)
    for self.__counter in list(self.__extrusionNumber.keys()):
      #print(" ExtrusionNumber = %s \n") % (self.__extrusionNumber[self.__counter])
      try:
        self.__arrayPlotExtrusionNumber[0] = float(self.__extrusionNumber[self.__counter])
      except:
        print((("-----> defineTree:: self.__extrusionNumber[%s] = %s not float... excluded from tree\n") % (self.__counter,self.__extrusionNumber[self.__counter])))
        continue
      self.__arrayPlotLightYield[0] = float(self.__lightYield[self.__counter])
      self.__arrayPlotBase[0] = float(self.__base[self.__counter])
      self.__arrayPlotHeight[0] = float(self.__height[self.__counter])
      self.__arrayPlotHoleDiameter1[0] = float(self.__holeDiameter1[self.__counter])
      self.__arrayPlotHoleDiameter2[0] = float(self.__holeDiameter2[self.__counter])
      self.__arrayPlotExtrusionLength[0] = float(self.__extrusionLength[self.__counter])
      self.__localRootTree.Fill()            ## fill the root tree here...
    #print("after filling the tree \n")
    #self.__localRootTree.Scan("")
    self.__rootTreeFile.Write()
    self.__rootTreeFile.Close()
    return
##
##
## --------------------------------------------------------------------
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  options, args = parser.parse_args()
  print((("'__main__': options.database  = %s \n") % (options.database)))
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry("+100+500")  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.database == "development"): myMultiForm.setupDevelopmentDatabase()
  else: myMultiForm.setupProductionDatabase()
  myMultiForm.grid()
  root.mainloop()
