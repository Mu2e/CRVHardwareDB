# -*- coding: utf-8 -*-
##
##  File = "guiFibers.py"
##
##  Derived from File = "guiExtrusions.py"
##
##  Python script to read in the vendor generated files for the 
##	fibers.
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2015Sep23
##
#!/bin/env python
##
##  Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2020Jul09... change hdbClient_v2_0 -> hdbClient_v2_2
##  Modified by cmj2020Jul09... change crvUtilities2018->crvUtilities; cmjGuiLibGrid2018Oct1-> cmjGuiLibGrid2020Jan30
##  Modified by cmj2020Aug03... cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
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
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from cmjGuiLibGrid import *       ## 2020Aug03
from Fibers import *
ProgramName = "guiFibers"
Version = "version2020.12.16"
##
## -------------------------------------------------------------
## 	A class to set up the main window to drive the
##	python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__cmjGuiDebug = 0
    self.__myFibers  = fiber()
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
##
##
##	Dictionary of arrays to hold the Sipm Batch information
    self.__sipmBatch={}
##	Define Output Log file... remove this later
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('fiberQuerries')
    self.__mySaveIt.openFile()
    self.__row = 0
    self.__col = 0
    self.__strName = []
    self.__sCount = 0
##Scatter Plots
##
##
##	First Column...
    self.__col = 0
    self.__firstRow = 0
##
##	Instruction Box...
    self.__myInstructions = myScrolledText(self)
    self.__myInstructions.setTextBoxWidth(60)
    self.__myInstructions.makeWidgets()
    self.__myInstructions.setText('','Instructions/InstructionsForEnterFibers2018Aug3.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__col = 0
    self.__secondRow = 1
    self.__buttonWidth = 30
    self.__getValues = Button(self,text='Get Input File',command=self.openFileDialog,width=self.__buttonWidth,bg='lightblue',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Send the Initial Fiber information from the vendors...
    self.__getValues = Button(self,text='Add Fibers',command=self.startInitialEntries,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
##	Send the vendor fiber measurements...
    self.__secondRow += 1
    self.__getValues = Button(self,text='Vendor Measurement',command=self.sendVendorMeasurements,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
##	Send the locally measured ADC counts vs wavelength measurments...
##	Send the locally measured fiber diameters...
    self.__secondRow += 1
    self.__getValues = Button(self,text='Local Fiber Diameter Measurement',command=self.sendLocalMeasurements,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
##	Send the locally measured attenuation measurments: ADC counts vs length
    self.__secondRow += 1
    self.__getValues = Button(self,text='Local Fiber Attenuation Measurement',command=self.sendLocalAttenuationMeasurements,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
##	Send the locally measured ADC counts vs wavelength measurments...
    self.__secondRow += 1
    self.__getValues = Button(self,text='Local Spectral Measurements',command=self.sendSpecturalMeasurements,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
#    self.__secondRow += 1
###	Setup Debug option
    self.__col = 1
    self.__secondRow = 2
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Test',command=self.__myFibers.turnOffSendToDatabase,width=self.__buttonWidth,bg='orange',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Setup Debug option
    self.__col = 1
    self.__secondRow = 3
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Debug',command=self.turnOnDebug,width=self.__buttonWidth,bg='orange',fg='black')
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
    self.__firstRow = 7
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
    self.__myFibers.openFile(self.__filePath)
##
## --------------------------------------------------------------------
##
  def startInitialEntries(self):
    self.__myFibers.readFiberFileInitial()
    self.__myFibers.sendFiberToDatabase()
##
## --------------------------------------------------------------------
##
  def sendVendorMeasurements(self):
    self.__myFibers.readFiberFileVendor()
    self.__myFibers.sendFiberVendorMeasurementToDatabase()
    self.__myFibers.sendFiberVendorAttenuationToDatabase()
##
## --------------------------------------------------------------------
##
  def sendLocalMeasurements(self):
    self.__myFibers.readLocalMeasurementFile()
    self.__myFibers.sendFiberLocalMeasurementToDatabase()
##
## ---------------------------------------------------------------------
  def sendLocalAttenuationMeasurements(self):
    self.__myFibers.readLocalAttenuationFile()
    self.__myFibers.sendFiberLocalAttenuationMeasurementToDatabase()
##
## ---------------------------------------------------------------------
  def sendSpecturalMeasurements(self):
    self.__myFibers.readWavelengthFile()
    #if(self.__cmjGuiDebug > 0) : self.__myFibers.dumpWavelengthFiberWaveLength()
    self.__myFibers.sendFiberWavelengthMeasurementToDatabase()
##
## --------------------------------------------------------------------
##
  def turnOnDebug(self,tempDebug):
    print("__multiWindow__::turnOnDebug= %s \n") % (tempDebug)
    self.__myFibers.setDebugLevel(tempDebug)
    self.__cmjGuiDebug = 1
## --------------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__myFibers.turnOnSendToDatabase()
## --------------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__myFibers.turnOffSendToDatabase()
## --------------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__myFibers.sendToDevelopmentDatabase()
## --------------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__myFibers.sendToProductionDatabase()
## --------------------------------------------------------------------
  def update(self):
    self.__myFibers.updateMode() ## set dataloader to update mode....
##  
##
##
## --------------------------------------------------------------------
##
##	Run main GUI program here!
##
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 1 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
  parser.add_option('--update',dest='updateMode',type='int',default=0,help='0 or 1 (update)')
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
  if(options.testMode != 0): 
    myMultiForm.turnOffSendToDatabase()
  else:
    myMultiForm.turnOnSendToDatabase()
    if(options.database == "development"): myMultiForm.sendToDevelopmentDatabase()
    else: myMultiForm.sendToProductionDatabase()
  if(options.updateMode != 0) : myMultiForm.update()
  myMultiForm.grid()
  root.mainloop()



