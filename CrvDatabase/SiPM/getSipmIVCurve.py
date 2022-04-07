# -*- coding: utf-8 -*-
##
##  File = "getSipmIVCurve.py"
##  Derived from "getSiPM.py"
##
##  This script gets the IV Curve for SiPM from the database
##
##      A python script to read the Sipm tables in the hardware database
##      and display the overall Sipm status for a selected pack number
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2019Jan30
##  Derived from "goodSipm.py"
##     Add query for SiPM number
##  Modified by cmj2016Jun24.Sipm.py.. Add one more upward level for subdirectory to get to the utilities directory
##                        for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2019Feb28... Change the default database to production.
##  Modified by cmj2020Aug03... cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May11.... replace dataloader with dataloader
##
#!/bin/env python
from tkinter import *         # get widget class
import tkinter as tk
import tkinter.filedialog
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip") ## 2021May11
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul02 add highlight to scrolled list
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *  
from cmjGuiLibGrid import *  ## cmj2020Aug03
from Sipm import *
##
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
import time
import array
##            Import the graphing modules
##  Import for PyRoot
from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH2F, TGraph, TStyle, TTree, TString
from ROOT import gROOT, gBenchmark, gRandom, gSystem, gStyle, Double_t
from array import array
##
ProgramName = "goodSipm.py"
Version = "version2021.2.08"
##
##
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
    self.setupDevelopmentDatabase()  ## set up communications with database
    self.__cmjPlotDiag = 0 ## default... not debug messages printed out
                  ##  Limit number of sipms read in for tests.... set negative to read all
    self.__cmjTest = 0      ## set this to 1 to look at 10 sipm_id's
##      Define Output Log file... remove this later
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('goodSipms')
    self.__mySaveIt.openFile()
##
    self.__sipmIdName = []
    self.__sipmStatus = []
    self.__sipmIdName_dict =  {}
    self.__sipmStatus_dict = {}
    ## set up geometry for GUI
    self.__labelWidth = 10
    self.__entryWidth = 10
    self.__buttonWidth = 5
    self.__packNumber = 0
###
    self.__selectedSipmId = 9999
    self.__selectedSipmIDANumber = "A-NotValid"
    self.__sipmIvsVresults =[]
    ##      Nested Dictionaries to save I vs V data for each sipm, each test
##      The keys to these dictionaries are [sipmMeasureDate][SipmId][binNumber]
    self.__sipmMeasureTestDate_IvsV = {}  ## first key in triple nested dictionary
    self.__sipmId_IvsV = defaultdict(dict) ## second key in triple nested dictionary [sipmMeasureDate][SipmId]
    self.__myMultiDimDictionary = generalUtilities()
    self.__IvsV_current = self.__myMultiDimDictionary.nestedDict()
    self.__IvsV_voltage = self.__myMultiDimDictionary.nestedDict()
    self.__sipmResults = []
    self.__sipmPackNumberResults = {}  ## dictionary to hold pack number: Key SipmId
    self.__sipmIvsVresults =[]
##      Most times the Sipms are tested once, but at different time
###
##
##      Display the Sipm Grid here..
##
    self.__row = 0
    self.__col = 0
    self.__buttonName = 'Waffle Pack'
    self.StringEntrySetup(self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,self.__buttonName,self.__buttonName)
    #self.__WaffelPack.grid(row=self.__row,col=self.__col)
    self.__row = 1
    self.__buttonName2 = 'Sipm Id'
    self.StringEntrySetup2(self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,self.__buttonName2,self.__buttonName2)
##
##  Plot scatter plots
##
    self.__row = 0
    self.__col = 5
    self.__buttonWidth1 = 20
    self.__getValues = Button(self,text='Plot Waffle Pack IV Curve',command=self.plotWafflePackIVcurve,width=self.__buttonWidth1,bg='orange',fg='black')
    self.__getValues.grid(row=self.__row,column=self.__col,sticky=W)
    #self.__WaffelPack.grid(row=self.__row,col=self.__col)
    self.__row = 1
    self.__getValues = Button(self,text='Plot SiPM IV Curve',command=self.plotSipmIVcurve,width=self.__buttonWidth1,bg='orange',fg='black')
    self.__getValues.grid(row=self.__row,column=self.__col,sticky=W)
##
##
##
    #self.SipmQuery.grid(row=self.__row,col=self.__col)
##      Third Column...
    self.__col = 6
    self.__logo = mu2eLogo(self,self.__row,self.__col)     # display Mu2e logo!
    self.__logo.grid(row=self.__row,column=self.__col,rowspan=2,sticky=NE)
    self.__col = 0
    self.__row += 4
    ##
    self.__sipmGrid_row = self.__row
    self.__sipmGrid_col = self.__col
    self.setSipmIdName()
    self.setSipmStatus()
#         Display the date the script is being run
    self.__row += 5
    self.__col = 2
    self.__date = myDate(self,self.__row,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__row,column=self.__col,sticky=E)
    self.__col = 0
    self.__buttonWidth = 10
##      Add Control Bar at the bottom...
    self.__quitNow = Quitter(self,0,self.__col)
    self.__quitNow.grid(row=self.__row,column=0,sticky=W)
##
## -------------------------------------------------------------------
##      Make querries to data base
#  def setupDevelopmentDatabase(self):
#    self.__database = 'mu2e_hardware_dev'
#    self.__group = "Sipm Tables"
#    self.__whichDatabase = 'development'
#    print("...multiWindow::getFromDevelopmentDatabase... get from development database \n")
#    self.__queryUrl = self.__database_config.getQueryUrl()
#    print("...multiWindow::getFromDevelopmentDatabase... self.__queryUrl = %s \n") % (self.__queryUrl)
##
## -------------------------------------------------------------------
##      Make querries to data base
#  def setupProductionDatabase(self):
#    self.__database = 'mu2e_hardware_prd'
#    self.__group = "Sipm Tables"
#    self.__whichDatabase = 'production'
#    print("...multiWindow::getFromProductionDatabase... get from production database \n")
#    self.__url = self.__database_config.getProductionQueryUrl()
#    print("...multiWindow::getFromProductionDatabase...  self.__queryUrl = %s \n") % (self.__url)
##
## ------------------------------------------------------------------
##  Set the SipmId for each Sipm in a waffle pack
  def setSipmIdName(self):
    for self.__m in range(16):
      self.__sipmIdName.append(str(self.__m))
## ------------------------------------------------------------------
##  Set the Sipm over-all status for each Sipm in a waffle pack
  def setSipmStatus(self):
    self.__testCondition = 0
    self.__green = 'green'
    self.__yellow = 'yellow'
    self.__red = 'red'
    for self.__myElement in range(16):
      self.__sipmStatus.append('white')
##
## ------------------------------------------------------------------
##  Set the status grid...
  def setStatusGrid(self,row,col):
    self.__row0 = row  ## row 0... build row by incrementind column
    self.__col0 = col
    self.__borderWidth = 2
    self.__borderStyle = 'solid'
    self.__grid_width = int(30)
    self.__square00=myLabel(self,self.__row0,self.__col0,self.__grid_width)
    self.__square00.setText(self.__sipmIdName[0])
    self.__square00.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square00.setBackgroundColor(self.__sipmStatus[0])
    #self.__square00.makeLabel()
    self.__square00.grid(row=self.__row0,column=self.__col0)
    self.__col1 = self.__col0 + 1
    self.__square01=myLabel(self,self.__row0,self.__col1,self.__grid_width)
    self.__square01.setText(self.__sipmIdName[1])
    self.__square01.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square01.setBackgroundColor(self.__sipmStatus[1])
    #self.__square01.makeLabel()
    self.__square01.grid(row=self.__row0,column=self.__col1)
    self.__col2 = self.__col0 + 2
    self.__square02=myLabel(self,self.__row0,self.__col2,self.__grid_width)
    self.__square02.setText(self.__sipmIdName[2])
    self.__square02.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square02.setBackgroundColor(self.__sipmStatus[2])
    #self.__square02.makeLabel()
    self.__square02.grid(row=self.__row0,column=self.__col2)
    self.__col3 = self.__col0 + 3
    self.__square03=myLabel(self,self.__row0,self.__col3,self.__grid_width)
    self.__square03.setText(self.__sipmIdName[3])
    self.__square03.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square03.setBackgroundColor(self.__sipmStatus[3])
    #self.__square03.makeLabel()
    self.__square03.grid(row=self.__row0,column=self.__col3)
    self.__row0 += 1  ## row 1... build row by incrementind column
    self.__col0 = 0
    self.__square10=myLabel(self,self.__row0,self.__col0,self.__grid_width)
    self.__square10.setText(self.__sipmIdName[4])
    self.__square10.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square10.setBackgroundColor(self.__sipmStatus[4])
    #self.__square10.makeLabel()
    self.__square10.grid(row=self.__row0,column=self.__col0)
    self.__col1 = self.__col0 + 1
    self.__square11=myLabel(self,self.__row0,self.__col1,self.__grid_width)
    self.__square11.setText(self.__sipmIdName[5])
    self.__square11.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square11.setBackgroundColor(self.__sipmStatus[5])
    #self.__square11.makeLabel()
    self.__square11.grid(row=self.__row0,column=self.__col1)
    self.__col2 = self.__col0 + 2
    self.__square12=myLabel(self,self.__row0,self.__col2,self.__grid_width)
    self.__square12.setText(self.__sipmIdName[6])
    self.__square12.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square12.setBackgroundColor(self.__sipmStatus[6])
    #self.__square12.makeLabel()
    self.__square12.grid(row=self.__row0,column=self.__col2)
    self.__col3 = self.__col0 + 3
    self.__square13=myLabel(self,self.__row0,self.__col3,self.__grid_width)
    self.__square13.setText(self.__sipmIdName[7])
    self.__square13.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square13.setBackgroundColor(self.__sipmStatus[7])
    #self.__square13.makeLabel()
    self.__square13.grid(row=self.__row0,column=self.__col3)
    self.__row0 += 1  ## row 2... build row by incrementind column
    self.__col0 = 0
    self.__square20=myLabel(self,self.__row0,self.__col0,self.__grid_width)
    self.__square20.setText(self.__sipmIdName[8])
    self.__square20.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square20.setBackgroundColor(self.__sipmStatus[8])
    #self.__square20.makeLabel()
    self.__square20.grid(row=self.__row0,column=self.__col0)
    self.__col1 = self.__col0 + 1
    self.__square21=myLabel(self,self.__row0,self.__col1,self.__grid_width)
    self.__square21.setText(self.__sipmIdName[9])
    self.__square21.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square21.setBackgroundColor(self.__sipmStatus[9])
    #self.__square21.makeLabel()
    self.__square21.grid(row=self.__row0,column=self.__col1)
    self.__col2 = self.__col0 + 2
    self.__square22=myLabel(self,self.__row0,self.__col2,self.__grid_width)
    self.__square22.setText(self.__sipmIdName[10])
    self.__square22.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square22.setBackgroundColor(self.__sipmStatus[10])
    #self.__square22.makeLabel()
    self.__square22.grid(row=self.__row0,column=self.__col2)
    self.__col3 = self.__col0 + 3
    self.__square23=myLabel(self,self.__row0,self.__col3,self.__grid_width)
    self.__square23.setText(self.__sipmIdName[11])
    self.__square23.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square23.setBackgroundColor(self.__sipmStatus[11])
    #self.__square23.makeLabel()
    self.__square23.grid(row=self.__row0,column=self.__col3)
    self.__row0 += 1  ## row 3... build row by incrementind column
    self.__col0 = 0
    self.__square30=myLabel(self,self.__row0,self.__col0,self.__grid_width)
    self.__square30.setText(self.__sipmIdName[12])
    self.__square30.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square30.setBackgroundColor(self.__sipmStatus[12])
    #self.__square30.makeLabel()
    self.__square30.grid(row=self.__row0,column=self.__col0)
    self.__col1 = self.__col0 + 1
    self.__square31=myLabel(self,self.__row0,self.__col1,self.__grid_width)
    self.__square31.setText(self.__sipmIdName[13])
    self.__square31.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square31.setBackgroundColor(self.__sipmStatus[13])
    #self.__square31.makeLabel()
    self.__square31.grid(row=self.__row0,column=self.__col1)
    self.__col2 = self.__col0 + 2
    self.__square32=myLabel(self,self.__row0,self.__col2,self.__grid_width)
    self.__square32.setText(self.__sipmIdName[14])
    self.__square32.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square32.setBackgroundColor(self.__sipmStatus[14])
    #self.__square32.makeLabel()
    self.__square32.grid(row=self.__row0,column=self.__col2)
    self.__col3 = self.__col0 + 3
    self.__square33=myLabel(self,self.__row0,self.__col3,self.__grid_width)
    self.__square33.setText(self.__sipmIdName[15])
    self.__square33.setBorder(self.__borderWidth,self.__borderStyle)
    self.__square33.setBackgroundColor(self.__sipmStatus[15])
    #self.__square33.makeLabel()
    self.__square33.grid(row=self.__row0,column=self.__col3)

##
## ===================================================================
##      Local String Entry button
##      Need to setup here to retain local program flow
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
    self.getSipmsFromWafflePack(self.__StringEntry_result)
    print(("--- StringEntryGet... after Button in getEntry = %s") %(self.__StringEntry_result))
    return self.__StringEntry_result
##  Second one for the SipmId
##
## ===================================================================
##      Local String Entry button
##      Need to setup here to retain local program flow
  def StringEntrySetup2(self,row,col,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    print("----- StringEntrySetup2 -- Enter")
    self.__StringEntry_row2 = row
    self.__StringEntry_col2 = col
    self.__StringEntry_labelWidth2 = 10
    self.__StringEntry_entryWidth2 = 10
    self.__StringEntry_buttonWidth2 = 10
    self.__StringEntry_entyLabel2 = ''
    self.__StringEntry_buttonText2 = 'Enter'
    self.__StringEntry_buttonName2 = buttonName
    self.__StringEntry_result2 = 'xxxxaaaa'
    self.__entryLabel2 = '' 
    self.__label2 = Label(self,width=self.__StringEntry_labelWidth2,text=self.__StringEntry_buttonName2,anchor=W,justify=LEFT)
    self.__label2.grid(row=self.__StringEntry_row2,column=self.__StringEntry_col2,sticky=W)
    self.__ent2 = Entry(self,width=self.__StringEntry_entryWidth2)
    self.__var2 = StringVar()        # associate string variable with entry field
    self.__ent2.config(textvariable=self.__var2)
    self.__var2.set('')
    self.__ent2.grid(row=self.__StringEntry_row2,column=self.__StringEntry_col2+1,sticky=W)
    self.__ent2.focus()
    self.__ent2.bind('<Return>',lambda event:self.fetch())
    self.__button2 = Button(self,text=self.__StringEntry_buttonText2,width=self.__StringEntry_buttonWidth2,anchor=W,justify=LEFT,command=self.StringEntryFetch2)
    self.__button2.config(bg='#E3E3E3')
    self.__button2.grid(row=self.__StringEntry_row2,column=self.__StringEntry_col2+2,sticky=W)
  def StringEntryFetch2(self):
    self.__StringEntry_result2 = self.__ent2.get()
    self.__selectedSipmId = 'CrvSipm-S14283(ES2)_'+self.__StringEntry_result2
    self.__selectedSipmIDANumber=self.__StringEntry_result2
    print(("----- StringEntrySetup2 -- self.__selectedSipmId = %s")  % (self.__selectedSipmId))
    self.getWafflePackFromSipms(self.__StringEntry_result2)
    print(("--- StringEntryGet2... after Button in getEntry2 = %s") %(self.__StringEntry_result2))
    return self.__StringEntry_result2
## ===================================================================   
##
## -------------------------------------------------------------------
##      Make querries to data base for Sipm Status
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Sipm Tables"
    self.__whichDatabase = 'development'
    print("...multiWindow::getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
##
## -------------------------------------------------------------------
##      Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Sipm Tables"
    self.__whichDatabase = 'production'
    print("...multiWindow::getFromProductionDatabase... get from production database \n")
    self.__url = self.__database_config.getProductionQueryUrl()
## --------------------------------------------------------------------
##      Make querries to get all sipm batches to data base
  def getSipmsFromWafflePack(self,packNumber):
    if(self.__cmjPlotDiag > 0): print("... multiWindow::getSipmsFromWafflePack \n") 
    self.__getSipmBatchValues = DataQuery(self.__queryUrl)
    self.__localSipmBatchValues = []
    self.__table = "sipms"
    self.__fetchThese = "sipm_id,sipm_signoff"
    self.__fetchCondition = 'pack_number:eq:'+packNumber  ## works!!!
    self.__numberReturned = 0
    if(self.__cmjPlotDiag > 1):
      print((".... getSipmsFromWafflePack: self.__queryUrl   = %s \n") % (self.__queryUrl))
      print((".... getSipmsFromWafflePack: self.__table                = %s \n") % (self.__table))
      print((".... getSipmsFromWafflePack: self.__fetchThese           = %s \n") % (self.__fetchThese))
      print((".... getSipmsFromWafflePack: self.__fetchCondition       = %s \n") % (self.__fetchCondition))
    self.__localSipmBatchValues = self.__getSipmBatchValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjPlotDiag > 2): 
      print((".... getSipmsFromWafflePack: self.__getSipmBatchValues   = %s \n") % (self.__getSipmBatchValues))
      print((".... getSipmsFromWafflePack: self.__table                = %s \n") % (self.__table))
      print((".... getSipmsFromWafflePack: self.__fetchThese           = %s \n") % (self.__fetchThese))
      print((".... getSipmsFromWafflePack: self.__fetchCondition       = %s \n") % (self.__fetchCondition))
      print((".... getSipmsFromWafflePack: self.__localSipmBatchValues = %s \n") % (self.__localSipmBatchValues))
    self.__numberOfBatches = len(self.__localSipmBatchValues)
    if(self.__cmjPlotDiag > 2) : print(('len(self.__localSipmBatchValues) = %d') % (self.__numberOfBatches))
    self.__sipmChannel = 0
    for self.__mmm in sorted(self.__localSipmBatchValues):
      if(self.__cmjPlotDiag> 0): print(("self.__mmm = xxx%sxxx") % (self.__mmm))
      if(self.__mmm == '') : continue
      self.__tempElement = []
      self.__tempElement = self.__mmm.rsplit(',')
      self.__sipmIdName[self.__sipmChannel] = self.__tempElement[0]
      self.__sipmStatus[self.__sipmChannel] = self.__tempElement[1]
      if(self.__tempElement[1] == 'None') : self.__sipmStatus[self.__sipmChannel] = 'white'
      if(self.__tempElement[1] == "not tested"): self.__sipmStatus[self.__sipmChannel] = 'gray'
      self.__sipmChannel += 1
      if(self.__cmjPlotDiag> 2):  print(("self.__tempElement[0] = %s self.__tempElement[1] = %s") % (self.__tempElement[0],self.__tempElement[1] ))
    self.setSipmIdName()
    self.setSipmStatus()
    self.setStatusGrid(self.__sipmGrid_row,self.__sipmGrid_col)
    return self.__localSipmBatchValues
  ## --------------------------------------------------------------------
##      Make querries to get all sipm batches to data base
  def getWafflePackFromSipms(self,sipmNumber):
    if(self.__cmjPlotDiag > 0): print("... multiWindow::getSipmsFromWafflePack \n") 
    self.__getWaffelPackValues = DataQuery(self.__queryUrl)
    self.__localWaffelPackValues = []
    self.__table = "sipms"
    #self.__fetchThese = "sipm_id,sipm_signoff"
    #self.__fetchCondition = 'pack_number:eq:'+packNumber  ## works!!!
    self.__fetchThese2 = "pack_number"
    self.__fetchCondition2 = 'sipm_id:eq:CrvSipm-S14283(ES2)_'+sipmNumber  ## works!!!
    self.__numberReturned2 = 0
    if(self.__cmjPlotDiag > 1):
      print((".... getSipmsFromWafflePack: self.__queryUrl   = %s \n") % (self.__queryUrl))
      print((".... getSipmsFromWafflePack: self.__table                = %s \n") % (self.__table))
      print((".... getSipmsFromWafflePack: self.__fetchThese2          = %s \n") % (self.__fetchThese2))
      print((".... getSipmsFromWafflePack: self.__fetchCondition2      = %s \n") % (self.__fetchCondition2))
    self.__localWaffelPackValues = self.__getWaffelPackValues.query(self.__database,self.__table,self.__fetchThese2,self.__fetchCondition2,'-'+self.__fetchThese2)
    if(self.__cmjPlotDiag > 2): 
      print((".... getSipmsFromWafflePack: self.__localWaffelPackValues   = %s \n") % (self.__localWaffelPackValues))
      print((".... getSipmsFromWafflePack: self.__table                = %s \n") % (self.__table))
      print((".... getSipmsFromWafflePack: self.__fetchThese 2          = %s \n") % (self.__fetchThese2))
      print((".... getSipmsFromWafflePack: self.__fetchCondition2       = %s \n") % (self.__fetchCondition2))
      print((".... getSipmsFromWafflePack: self.__localWaffelPackValues = %s \n") % (self.__localWaffelPackValues))
    self.__localSipmPackNumber = self.__localWaffelPackValues[0]
    print((".... getSipmsFromWafflePack: self.__localSipmPackNumber = %s") % (self.__localSipmPackNumber))
#    if(self.__cmjPlotDiag > 2) : print('len(self.__localSipmBatchValues) = %d') % (self.__numberOfBatches)
#    self.__sipmChannel = 0
#    for self.__mmm in sorted(self.__localSipmBatchValues):
#      if(self.__cmjPlotDiag> 0): print("self.__mmm = xxx%sxxx") % (self.__mmm)
#      if(self.__mmm == '') : continue
#      self.__tempElement = []
#      self.__tempElement = self.__mmm.rsplit(',')
#      self.__sipmIdName[self.__sipmChannel] = self.__tempElement[0]
#      self.__sipmStatus[self.__sipmChannel] = self.__tempElement[1]
#      if(self.__tempElement[1] == 'None') : self.__sipmStatus[self.__sipmChannel] = 'white'
#      if(self.__tempElement[1] == "not tested"): self.__sipmStatus[self.__sipmChannel] = 'gray'
#      self.__sipmChannel += 1
#      if(self.__cmjPlotDiag> 2):  print("self.__tempElement[0] = %s self.__tempElement[1] = %s") % (self.__tempElement[0],self.__tempElement[1] )
#    self.setSipmIdName()
#    self.setSipmStatus()
#    self.setStatusGrid(self.__sipmGrid_row,self.__sipmGrid_col)
    self.__packLabel = Label(self,width=30,text='Panel Number = '+self.__localSipmPackNumber,anchor=W,justify=LEFT)
    self.__packLabel.grid(row=4,column=0,sticky=W)
    self.getSipmsFromWafflePack(self.__localSipmPackNumber)
    return self.__localSipmPackNumber
### *************************************************************
###            -- Plot IV curves
###
### --------------------------------- Single Sipm  ---------
  def plotSipmIVcurve(self) :
    self.__localSipmNumber = self.__selectedSipmId
    self.__getSipmIvsVvalues = DataQuery(self.__queryUrl)
    self.__table = "sipm_current_vs_voltages"
    self.__fetchThese = "sipm_id,measure_test_date,point,voltage,current"
    if(self.__localSipmNumber != "NULL"):
      print((".... plotSipmIVcurve: get sipm_id  = %s") % (self.__localSipmNumber))
      self.__localSipmIvsVresult = []
      self.__fetchCondition = "sipm_id:eq:"+str(self.__localSipmNumber)
      if (self.__cmjPlotDiag > -1): 
        print((".... plotSipmIVcurve: self.__table  = %s \n") % (self.__table))
        print((".... plotSipmIVcurve: self.__fetchThese  = %s \n") % (self.__fetchThese))
        print((".... plotSipmIVcurve: self.__fetchCondition = %s \n") % (self.__fetchCondition))
      ##  This call returns a list with the database entries for all lines with the same sipm_id plus other
      ##   list members that are either white characters, quotations or forward slashes.. They must be
      ##   filtered out before sending them to the "unpackSipms" member function....
      self.__localSipmIvsVresult = self.__getSipmIvsVvalues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
      self.__singleSipmIvsVline = []
      if(self.__cmjPlotDiag > -1): print((".... plotSipmIVcurvexx: len(self.__localSipmIvsVresult) = %d, self.__localSipmIvsVresult  = %s \n") % (len(self.__localSipmIvsVresult),self.__localSipmIvsVresult))
      self.__mcount = 0
      self.__ncount = 0
      for self.__mline in sorted(self.__localSipmIvsVresult):
        if(self.__cmjPlotDiag > -1): 
          print((".... plotSipmIVcurve: (self.__singleSipmIvsVline, all) ncount = %d,  len(self.__mline) = %d,  self.__mline  = %s \n") % (self.__ncount,len(self.__mline),self.__mline))
        if(len(self.__mline) > 0):
          self.__singleSipmIvsVline.append(self.__mline.rsplit(','))
          if(self.__cmjPlotDiag > -1): 
            print((".... plotSipmIVcurve: (self.__singleSipmIvsVline, filtered) mcount = %d, self.__mline  = %s \n") % (self.__mcount,self.__mline))
            self.__sipmIvsVresults.append(self.__mline)
            self.__mcount += 1
      self.__ncount += 1
    self.unpackSipmIvsV()
    self.plotSipmIVPlot()
    return
### --------------------------------------------------------
## --------------------------------------------------------------
  def unpackSipmIvsV(self):
    if(self.__cmjPlotDiag > -1): print("XXXXXXXXXXX entered unpackSipmIvsV \n")
    if(self.__cmjPlotDiag > -1): print((".... unpackSipmIvsV: self.__sipmResults  = %s \n") % (self.__sipmResults))
    print((".... unpackSipmIvsV: self.__sipmResults  = %d \n") % len(self.__sipmIvsVresults))
    ## self.__sipmResults is a list that has all occurances of a given sipm_id... this includes
    ## an entry for each test date (and test type like vendor or measured).... 
    for self.__record in sorted(self.__sipmIvsVresults):
      if(self.__cmjPlotDiag > 2): print(("....unpackSipmIvsV: self.__record =  %s , len(self.__record) = %d \n") % (self.__record, len(self.__record)))
      for self.__item in sorted(self.__record):
        if(self.__cmjPlotDiag > 3): print(("....unpackSipmIvsV: self.__record = %s, len(self.__record) = %d \n") %(self.__record, len(self.__record)))
        self.__item = str(self.__record).rsplit(',')     ##
        if(self.__cmjPlotDiag > 3): print(("....unpackSipmIvsV: self.__item = %s, len(self.__item) = %d \n") %(self.__item, len(self.__item)))
        if (len(self.__item) > 2):
          self.__tempSipmId = self.__item[0]
          self.__tempSipmTestDate = self.__item[1]
          self.__tempSipmIvsV_Bin = self.__item[2]
          self.__tempSipmIvsV_Voltage = self.__item[3]
          self.__tempSipmIvsV_Current = self.__item[4]
          if(self.__cmjPlotDiag > -1):
            print((".... unpackSipmIvsV: self.__tempSipmId = %s") % (self.__tempSipmId))
            print((".... unpackSipmIvsV: self.__tempSipmTestDate = %s") % (self.__tempSipmTestDate))
            print((".... unpackSipmIvsV: self.__tempSipmIvsV_Bin = %s") % (self.__tempSipmIvsV_Bin))
            print((".... unpackSipmIvsV: self.__tempSipmIvsV_Voltage = %s") % (self.__tempSipmIvsV_Voltage))
            print((".... unpackSipmIvsV: self.__tempSipmIvsV_Current = %s") % (self.__tempSipmIvsV_Current))
        self.__sipmMeasureTestDate_IvsV[self.__tempSipmTestDate] = self.__tempSipmTestDate
        self.__sipmId_IvsV[self.__tempSipmTestDate][self.__tempSipmId] = self.__tempSipmId
        self.__IvsV_voltage[self.__tempSipmTestDate][self.__tempSipmId][self.__tempSipmIvsV_Bin] = self.__tempSipmIvsV_Voltage
        self.__IvsV_current[self.__tempSipmTestDate][self.__tempSipmId][self.__tempSipmIvsV_Bin] = self.__tempSipmIvsV_Current
    return
### --------------------------------------------------------
  def plotSipmIVPlot(self):
    ## Define I vs V Curves
    self.__localXLabelSize = 0.06
    self.__localYlabelSize = 0.06
    #self.__hIvsV = TH1F('self.__hIvsV','All SiPMs: IvsV',5000,0.0,5.0)
    #self.__hTemperature.SetFillColor(3)
    #self.__hIvsV.GetXaxis().SetTitle('Voltage (Volts)')
    #self.__hIvsV.GetYaxis().SetTitle('Current (#mu Amps)')
    #self.__hIvsV.GetXaxis().SetLabelSize(self.__localXLabelSize)
    #self.__hIvsV.GetYaxis().SetLabelSize(self.__localYlabelSize)
#
#    ## plot the I vs V curves
    self.__IvsVTitle = "I vs V Sipm: "+self.__selectedSipmIDANumber
    self.__h2_IvsVFrame = TH2F('self.__h2_IvsVFrame',self.__IvsVTitle,1000,0.0,100.0,100,0.0,5.0)
    self.__h2_IvsVFrame.GetXaxis().SetTitle('Voltage (Volts)')
    self.__h2_IvsVFrame.GetYaxis().SetTitle('Current (#mu Amps)')
    self.__h2_IvsVFrame.GetXaxis().SetLabelSize(self.__localXLabelSize)
    self.__h2_IvsVFrame.GetYaxis().SetLabelSize(self.__localYlabelSize)
#    ##
    self.__markerColor = 2;
    self.__h2_IvsVFrame.SetMarkerColor(2)
    self.__h2_IvsVFrame.SetMarkerSize(0.5)
    self.__h2_IvsVFrame.SetMarkerStyle(21)
    print(("...plotSipmIVPlot len(self.__sipmMeasureTestDate_IvsV.keys()) = %d") % (len(list(self.__sipmMeasureTestDate_IvsV.keys()))))
    for self.__n in list(self.__sipmMeasureTestDate_IvsV.keys()):
      print(("...plotSipmIVPlot len(self.__sipmId_IvsV[self.__n].keys()) = %d") % (len(list(self.__sipmId_IvsV[self.__n].keys()))))
      for self.__m in list(self.__sipmId_IvsV[self.__n].keys()):
        self.__arrayVoltage = array('d')
        self.__arrayCurrent = array('d')
        print(("...plotSipmIVPlot len(self.__IvsV_voltage[self.__n][self.__m].keys()) = %d") % (len(list(self.__IvsV_voltage[self.__n][self.__m].keys()))))
        for self.__j in list(self.__IvsV_voltage[self.__n][self.__m].keys()):
          self.__h2_IvsVFrame.Fill(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]),float(self.__IvsV_current[self.__n][self.__m][self.__j]))
          if(float(self.__IvsV_current[self.__n][self.__m][self.__j]) > 5.0) : continue
          if(float(self.__IvsV_current[self.__n][self.__m][self.__j]) < 0.0) : continue
          self.__arrayCurrent.append(float(self.__IvsV_current[self.__n][self.__m][self.__j]))
          self.__arrayVoltage.append(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]))
          #self.__hIvsV.Fill(float(self.__IvsV_voltage[self.__n][self.__m][self.__j]),float(self.__IvsV_voltage[self.__n][self.__m][self.__j]))
          tempVoltage = float(self.__IvsV_voltage[self.__n][self.__m][self.__j])
          tempCurrent = float(self.__IvsV_current[self.__n][self.__m][self.__j])
          print(("... plotSipmIVPlot: self._arrayVoltage[%s,%s,%s] = %f self._arrayCurrent [%s,%s,%s] = %f ") % (self.__n,self.__m,self.__j,tempVoltage,self.__n,self.__m,self.__j,tempCurrent))
    #self.__newGraph = TGraph(self.__npoint,self.__arrayVoltage,self.__arrayCurrent))
    self.__windowTitle = "I vs V xxx"
    self.__cWidth = 700       ## canvas width
    self.__cHeight = 500 ## canvas height
    self.__cX = 100
    self.__cY = 200
    self.__cIvsVLog = TCanvas('self.__cIvsVLog',self.__windowTitle,self.__cX,self.__cY,self.__cWidth,self.__cHeight)
    self.__h2_IvsVFrame.Draw()
    self.__cIvsVLog.SetLogy()
    #self.__cIvsVLog.Update()
    self.__graphicsTime = myTime()
    self.__graphicsTime.getComputerTime()
    self.__saveTime = self.__graphicsTime.getTimeForSavedFiles()
    self.__outFileName = "outputFiles/SipmRootHistograms-IvsV-Log"+self.__selectedSipmIDANumber+self.__saveTime+".png"
    self.__cIvsVLog.SaveAs(self.__outFileName)
#    return
### --------------------------------- Single Sipm  ---------
  def plotWafflePackIVcurve(self,tempWafflePack) :
    return
### *************************************************************
## ------------------------------------------------------------------
##  Set the debug mode 
  def setDebugMode(self,tempDebug):
    self.__cmjPlotDiag = tempDebug
    print((".... etDebugMode = %s") % (self.__cmjPlotDiag))
##
##
## -------------------------------------------------------------------
##
##
## --------------------------------------------------------------------
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  parser.add_option('--update',dest='update',type='string',default="add",help='update to update entries')
  options, args = parser.parse_args()
  print(("'__main__': options.debugMode = %s \n") % (options.debugMode))
  print(("'__main__': options.testMode  = %s \n") % (options.testMode))
  print(("'__main__': options.database  = %s \n") % (options.database))
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry("+100+500")  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.database == "production"):
    myMultiForm.setupProductionDatabase()
  else:
    myMultiForm.setupDevelopmentDatabase()
  if(options.debugMode != 0): myMultiForm.setDebugMode(options.debugMode)
##
  myMultiForm.grid()
  root.mainloop()
