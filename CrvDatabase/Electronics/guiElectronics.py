# -*- coding: utf-8 -*-
##
##  File = "guiElectronics.py"
##  Derived from File = "guiModules.py"
##  Derived from File = "guiDiCounters.py"
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
##	1) Input the initial diCounter information... 
##	 python DiCounters_2016Dec27.p -i 'CounterSpreadSheets/Counter_2016May13.csv'
##	2) Input the image file for the cut
##	 python DiCounters_2016Dec27.py -i 'diCounterSpreadSheets/DiCounter_Tests_2016Dec20.csv' --mode 'image'
##	3) Input the test results
##	 python DiCounters_2016Dec27.py -i 'diCounterSpreadSheets/DiCounter_Tests_2016Dec20.csv' --mode 'measure'
##
##  Modified by cmj 2016Jan7... Add the databaseConfig class to get the URL for 
##		the various databases... change the URL in this class to change for all scripts.
##  Modified by cmj 2016Jan14 to use different directories for support modules...
##		These are located in zip files in the various subdirectories....
##  Modified by cmj2016Jan26.... change the maximum number of columns decoded to use variable.
##				change code to accomodate two hole positions										"pre_production" or "production"
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##  Modified by cmj2017Mar14... Add instructions for use in the call of the script.
##  Modified by cmj2017Mar14... Add test mode option; option to turn off send to database.
##  Modified by cmj2017May31... Add "di-" identifiery for di-counters.
##  Modified by cmj2017Aug2... Change to drive Modules.py
##  Modified by cmj2018Jun8... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2019May16... Change "hdbClient_v2_0" to "hdbClient_v2_2"
##  Modified by cmj2019May23... Add update mode for modules...
##  Modified by cmj2019May23... Change default database to "production"
##  Modified by cmj2020Jul09... crvUtilities2020 -> crvUtilities; cmjGuiLibGrid2018Oct1->cmjGuiLibGrid2019Jan30
##  Modified by cmj2020Jul09.... Changed default database to "development"
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
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

#import ssl		## new for new version of DataLoader
#import random		## new for new version of Dat##  File = "DiCounters_2017Mar13.py"aLoader
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from generalUtilities import generalUtilities
from cmjGuiLibGrid import *       ## 2020Aug03
from Electronics import *

ProgramName = "guiElectronics.py"
Version = "version2020.12.16"

##
## -------------------------------------------------------------
## 	A class to set up the main window to drive the
##	python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__myElectronics  = Electronics()
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
##
##	First Column...
    self.__col = 0
    self.__firstRow = 0
##
##	Instruction Box...
    self.__myInstructions = myScrolledText(self)
    self.__myInstructions.setTextBoxWidth(50)
    self.__myInstructions.makeWidgets()
    self.__myInstructions.setText('','Instructions/InstructionsForGuiElectronics2019May24.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__col = 0
    self.__secondRow = 1
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Get Input File',command=self.openFileDialog,width=self.__buttonWidth,bg='lightblue',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Send initial FEB information into the database
    self.__getValues = Button(self,text='Send Feb Id',command=self.sendFebIds,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
    
    self.__getValues = Button(self,text='Initial',command=self.startInitialEntries,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
    self.__getValues = Button(self,text='Tests',command=self.sendMeasurements,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Setup Debug option
    self.__col = 1
    self.__secondRow = 2
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Test',command=self.__myElectronics.turnOffSendToDatabase,width=self.__buttonWidth,bg='orange',fg='black')
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
    self.__myElectronics.openFile(self.__filePath)
##
## --------------------------------------------------------------------
##
##	Send only the FEB Id's, type and location.
  def sendFebIds(self):
    print("__multiWindow__::sendFebIds..  self.__myElectronics.sendFebIds()")
    self.__myElectronics.readFebId()
##
## --------------------------------------------------------------------
##
  def startInitialEntries(self):
    self.__myElectronics.readFile()
    print("__multiWindow__::startInitialEntries..  self.__myElectronics.sendFrontEndBoardsToDatabase()")
    self.__myElectronics.sendFrontEndBoardsToDatabase()
    print("__multiWindow__::startInitialEntries..  self.__myElectronics.sendFebChipsToDatabase()")
    self.__myElectronics.sendFebChipsToDatabase()
##
## --------------------------------------------------------------------
##
  def sendMeasurements(self):
    self.__myElectronics.readFile()
    self.__myElectronics.sendElectronicsMeasurementsToDatabase()
##
## --------------------------------------------------------------------
##
  def turnOnDebug(self):
    self.__myElectronics.turnOnDebug()
## --------------------------------------------------------------------
  def setDebugLevel(self,tempDebug):
    self.__myElectronics.setDebugLevel(tempDebug)
## --------------------------------------------------------------------
  def setSleeptime(self,tempSleepTime):
    self.__myElectronics.setSleeptime(tempDebug)
## --------------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__myElectronics.turnOnSendToDatabase()
## --------------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__myElectronics.turnOffSendToDatabase()
## --------------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__myElectronics.sendToDevelopmentDatabase()
## --------------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__myElectronics.sendToProductionDatabase()
## --------------------------------------------------------------------
  def updateMode(self):
    print("__multiWindow__::updateMode.... UPDATE MODE!... update entries to database!")
    self.__myElectronics.updateMode()
## --------------------------------------------------------------------
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="development",help='development or production')
  parser.add_option('--update',dest='update',type='string',default="add",help='update to update entries')
  parser.add_option('--debuglevel',dest='debugLevel',type='int',default=0,help='set debug level, default = 0')
  parser.add_option('--sleepTime',dest='sleepTime',type='float',default=1.0,help='set sleep time between database transactions, defalut = 1.0 sec')
  options, args = parser.parse_args()
  print("'__main__': options.debugMode = %s \n") % (options.debugMode)
  print("'__main__': options.testMode  = %s \n") % (options.testMode)
  print("'__main__': options.database  = %s \n") % (options.database)
 
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry("+100+500")  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.update == "update"):  myMultiForm.updateMode()
  if(options.debugMode != 0): myMultiForm.turnOnDebug(options.debugMode)
  if(options.debugLevel != 0): myMultiForm.setDebugLevel(options.debugLevel)
  if(options.sleepTime != 1.0):myMultiForm.setSleeptime(options.sleepTime)
  if(options.testMode != 0): 
    myMultiForm.turnOffSendToDatabase()
  else:
    myMultiForm.turnOnSendToDatabase()
    if(options.database == "development"): myMultiForm.sendToDevelopmentDatabase()
    else: myMultiForm.sendToProductionDatabase()
  myMultiForm.grid()
  root.mainloop()



