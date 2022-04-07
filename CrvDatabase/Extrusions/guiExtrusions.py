# -*- coding: utf-8 -*-
##
##  File = "guiExtrusions.py"
##  Derived from File = "guiExtrusions_2017Jul11.py"
##  Derived from File = "guiExtrusions_2017Jul7.py"
##  Derived from File = "Extrusions.py"
##  Derived from File = "Extrusions_2017Feb2.py"
##  Derived from File = "Extrusions_2016Jun24.py"
##  Derived from File = "Extrusions_2016May24.py"
##  Derived from File = "Extrusions_2016May24.py"
##  Derived from File = "Extrusions_2016May22.py"
##  Derived from File = "Extrusions_2016May17.py"
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
##      python Extrusion_2016Jan27.py -i 'LY_Mu2e-5x2-060414-rev-CmjAmended_2016Jan7.csv'
##
##  Modified by cmj 2016Jan7... Add the databaseConfig class to get the URL for 
##            the various databases... change the URL in this class to change for all scripts.
##  Modified by cmj 2016Jan14 to use different directories for support modules...
##            These are located in zip files in the various subdirectories....
##  Modified by cmj2016Jan26.... change the maximum number of columns decoded to use variable.
##                        change code to accomodate two hole positions
##  Modifed by cmj2016May22.... Add the counter type which contains one of the values: "test", "prototype" 
##                                                            "pre_production" or "production"
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##                        for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2017Feb2... Add instructions for use in the call of the script.
##  Modified by cmj2017Feb2... Add test mode option; option to turn off send to database.
##  Modified by cmj2018Mar01... Choose hdbClient_v1_3 dataloader
##  Modified by cmj2018Apr27... Change to hdbClient_v2_0
##  Modified by cmj2018Jun6.... change default datatbase to PRODUCTION
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##                        yellow highlight to selected scrolled list items
##  Modified by cmj2020Jul09.... Changed crvUtilities2018->crvUtilities; changed cmjGuiLibGrid2018Oct1->cmjGuiLibGrid2019Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##
##
sendDataBase = 0  ## zero... don't send to database
#
from tkinter import *         # get widget class
import tkinter as tk
import tkinter.filedialog
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2020Jul09
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from cmjGuiLibGrid import *       ## cmj2020Aug03
from Extrusions import *
ProgramName = "guiExtrusions"
Version = "version2020.05.12"

##############################################################################################
##############################################################################################
##
## -------------------------------------------------------------
##       A class to set up the main window to drive the
##      python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__myExtrusions  = extrusion()
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
##      Arrays to plot...keep these in scope in the whole class
    self.__sipmId = {}
    self.__sipmNumber = {}
    self.__testType = {}
    self.__biasVoltage ={}
    self.__darkCurrent = {}
    self.__gain = {}
    self.__temperature = {}
    self.__sipmResults = []
    self.__plotSipmId = []
    self.__plotSipmNumber = []
    self.__plotTestType = []
    self.__plotBiasVoltage = []
    self.__plotDarkCurrent = []
    self.__plotGain = []
    self.__plotTemperature = []
##      Dictionary of arrays to hold the Sipm Batch information
    self.__sipmBatch={}
##      Define Output Log file... remove this later
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('sipmQuerries')
    self.__mySaveIt.openFile()
    self.__row = 0
    self.__col = 0
    self.__strName = []
    self.__sCount = 0
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
    self.__myInstructions.setText('','Instructions/InstructionsForEnterExtrusions2017Jul7.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__col = 0
    self.__secondRow = 1
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Get Input File',command=self.openFileDialog,width=self.__buttonWidth,bg='lightblue',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##      Send initial Sipm information: PO number, batches recieved and vendor measurements...
    self.__getValues = Button(self,text='Add Extrusions',command=self.startInitialEntries,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##
##      Send initial Sipm information: PO number, batches recieved and vendor measurements...
    self.__getValues = Button(self,text='Add Extrusions - only',command=self.extrusionsOnly,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##
###      Setup Debug option
    self.__col = 1
    self.__secondRow = 2
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Test',command=self.__myExtrusions.turnOffSendToDatabase,width=self.__buttonWidth,bg='orange',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###      Setup Debug option
    self.__col = 1
    self.__secondRow = 3
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Debug',command=self.turnOnDebug,width=self.__buttonWidth,bg='orange',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###      Third Column...
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
##      Add Control Bar at the bottom...
    self.__col = 0
    self.__firstRow = 6
    self.__quitNow = Quitter(self,0,self.__col)
    self.__quitNow.grid(row=self.__firstRow,column=0,sticky=W)
##sendMeasurements
##
## --------------------------------------------------------------------
##
##      Open up file dialog....
  def openFileDialog(self):
    self.__filePath=tkinter.filedialog.askopenfilename()
    print((("__multiWindow__::openDialogFile = %s \n") % (self.__filePath)))
    self.__myExtrusions.openFile(self.__filePath)
##
## --------------------------------------------------------------------
##
  def startInitialEntries(self):
    self.__myExtrusions.readFile()
    self.__myExtrusions.sendStatisticsToDatabase()
    self.__myExtrusions.sendReferenceCounterToDatabase()
    self.__myExtrusions.sendExtrusionsToDatabase()
##
## --------------------------------------------------------------------
##
  def extrusionsOnly(self):
    self.__myExtrusions.readFile()
    self.__myExtrusions.sendExtrusionsToDatabase()
##
## --------------------------------------------------------------------
##
  def turnOnDebug(self):
    self.__myExtrusions.turnOnDebug(1)
## --------------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__myExtrusions.turnOnSendToDatabase()
## --------------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__myExtrusions.turnOffSendToDatabase()
## --------------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__myExtrusions.sendToDevelopmentDatabase()
## --------------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__myExtrusions.sendToProductionDatabase()
##  
##
##
## --------------------------------------------------------------------
##
##      Run main GUI program here!
##
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('-d',dest='debugMode',type='int',default=0,help='set debug: 0 (off - default), 1 = on')
  parser.add_option('-t',dest='testMode',type='int',default=0,help='set to test mode (do not send to database): 1')
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  options, args = parser.parse_args()
  print((("'__main__': options.debugMode = %s \n") % (options.debugMode)))
  print((("'__main__': options.testMode  = %s \n") % (options.testMode)))
  print((("'__main__': options.database  = %s \n") % (options.database)))
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
  myMultiForm.grid()
  root.mainloop()



