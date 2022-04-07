# -*- coding: utf-8 -*-
##
##  File = "guiSipm.py"
##  Derivef from File = "guiSipm2017Oct2-OLD.py"
##  Derived from File = 'guiSipm2017Jul10.py"
##  Derived from File = "enterSipmSpreadSheet_2017Jun23.py"
##  Derived from File = "readSipmSpreadSheet_2017Jun23.py"
##  Derived from File = "readSipmSpreadSheet_2016Jun27.py"
##  Derived from File = "readSipmSpreadSheet_2015Jun24.py"
##  Derived from File = "readSipmSpreadSheet_2015Jan20.py"
##  Derived from File = "readSipmSpreadSheet_2015Jan14.py"
##
##  Program to read a comma-separated data file and enter SiPM values into
##  the QA database.  Here the delimeter is a comma.
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2015Sep23
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##
#!/bin/env pytho##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2016Jun24... Read and include SiPM Type...
##  Modified by cmj2017Jun23... Add new crvUtilities library that contains a scrollList
##  To enter the locally measured quantities into the database:
##	python Sipm.py -i "SiPMSpreadSheets/Sipms_151224_S13360-2050VE_data_2016Jun27TEST.csv" -m 5
##  Modified by cmj2017Oct2... Use the file Sipm.py as the source of the sipm interface so only one set of code needs to be
##				maintainted.
##   Modified by cmj2018Apr27... Change to hdbClient_v2_0
##
##  Modified by cmj2018Jul13.... add update mode for database switch.
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2018Oct9.... Change to hdbClient_v2_2
##  Modified by cmj2019Jan24... Allow multiple selection of files for either the tests or loading to the 
##				database.
##  Modified by cmj2019May14... The previous version became missing after a the previous version (guiSipm2019Jan24.py)
##				was not used to produce the current version... this is now added in.
##  Modified by cmj2020Jun16... Use cmjGuiLibGrid2019Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16..M. replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May11... replace dataloader3.zip with dataloader.zip
##
##
##  To run this script:
##	python readSipmSpreadSheet_2016Jun27.py -i "Sipms_151224_S13360-2050VE_data_2016Jun27TEST.csv" 
##
#
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
ProgramName = "guiSipm.py"
Version = "version2021.05.12"
##
##
##
##############################################################################################
##############################################################################################
##  Entry point to program if this file is executed...
##if __name__ == '__main__':
#  def oldBeging(self):
#  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
#  parser.add_option('-i',dest='inputCvsFile',type='string',default="SiPM_2016Jan4.csv",help="Name of cvs extrution spread sheet file")
#  options, args = parser.parse_args()
#  inputSipmFile = options.inputCvsFile
#  print ("\nRunning %s \n") % (ProgramName)
#  print ("%s \n") % (Version)
#  print "inputSipmFile = %s " % inputSipmFile
#  mySipm = sipm()sys.path.append("../../Utilities/hdbClient_v1_3a/Dataloader.zip")
#  mySipm.turnOnDebug()
#  mySipm.openFile(inputSipmFile)
#  mySipm.readFile()
#  mySipm.turnOnSendToDatabase()
#  #mySipm.turnOffSendToDatabase()
#  #mySipm.sendToProductionDatabase()  ######## SEND TO PRODUCTION DATABASE!!!!
#  mySipm.sendToDevelopmentDatabase()
#  proceed0 = 0   ## set this to zero to start process..
#  proceed1 = 1
#  proceed2 = 1
#  proceed3 = 1
#  proceed4 = 1
#  proceed5 = 1
#  proceed6 = 1
#  if(proceed0 == 0): proceed1 = mySipm.sendPoNumberToDatabase()
#  if(proceed1 == 0): proceed2 = mySipm.sendReceivedPoToDatabase()
#  if(proceed2 == 0): proceed3  = mySipm.sendSipmIdsToDatabase()
#  if(proceed3 == 0): proceed4 = mySipm.sendSipmVendMeasToDatabase()
#  if(proceed4 == 0): proceed5 = mySipm.sendSipmLocalMeasToDatabase()
#  if(proceed5 == 0): print("readSipmSpreadSheet wrote all elements to database \n")
##
#  print("Finished running %s \n") % (ProgramName)
##
##	Interactive GUI
##
## -------------------------------------------------------------
## 	A class to set up the main window to drive the
##	python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    Frame.__init__(self,parent)
    self.__mySipm  = sipm()
    self.__mySipm.sendToDevelopmentDatabase()  ## set up communications with database
    self.__labelWidth = 25
    self.__entryWidth = 20
    self.__buttonWidth = 5
    self.__maxRow = 2
##	Arrays to plot...keep these in scope in the whole class
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
##Scatter Plots
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
    self.__myInstructions.setText('','Instructions/InstructionsForGuiSipms2017Jul7.txt')
    self.__myInstructions.grid(row=self.__firstRow,column=self.__col,columnspan=2)
    self.__firstRow += 1
##
    self.__col = 0
    self.__secondRow = 1
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Get Input File',command=self.openFileDialogMultipleFiles,width=self.__buttonWidth,bg='lightblue',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Send initial Sipm information: PO number, batches recieved and vendor measurements...
    self.__getValues = Button(self,text='Enter Purchase Order',command=self.sendInitialToDatabase,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Send Vendor measurment information
    self.__getValues = Button(self,text='Enter Vendor Measurements',command=self.sendVendorInformation,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
##	Send Local measurment information
    self.__getValues = Button(self,text='Enter Local Measurements',command=self.sendLocalInformation,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Shift columns... add enter iv curves
##	Send Local measurment information
    self.__col = 1
    self.__secondRow = 1
    self.__getValues = Button(self,text='Enter IV Measurements',command=self.sendLocalIVInformation,width=self.__buttonWidth,bg='yellow',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Special buttons to add pack number after the Sipms were added
##	Send Pack number to the database.
    self.__col = 1
    self.__secondRow = 2
    self.__getValues = Button(self,text='Enter Pack# (special)',command=self.sendPackNumberToDatabase,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Setup Debug option
    self.__col = 1
    self.__secondRow = 3
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Test',command=self.__mySipm.turnOffSendToDatabase,width=self.__buttonWidth,bg='orange',fg='black')
    self.__getValues.grid(row=self.__secondRow,column=self.__col,sticky=W)
    self.__secondRow += 1
###	Setup Debug option
    self.__col = 1
    self.__secondRow = 4
    self.__buttonWidth = 20
    self.__getValues = Button(self,text='Turn on Debug',command=self.__mySipm.turnOnDebug,width=self.__buttonWidth,bg='orange',fg='black')
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
#         Display the debug level selection
    self.__col = 0
    self.__row = 8
    self.__buttonName = 'Debug Level (0 to 5)'
    self.StringEntrySetup(self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,self.__buttonName,self.__buttonName)
    self.__col = 0
    self.__row += 1
    self.__buttonWidth = 10
##	Add Control Bar at the bottom...
    self.__col = 0
    self.__firstRow = 9
    self.__quitNow = Quitter(self,0,self.__col)
    self.__quitNow.grid(row=self.__firstRow,column=0,sticky=W)
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
## --------------------------------------------------------------------
##
##	Open up file dialog....Loca
  def openFileDialog(self):
    self.__filePath=tkinter.filedialog.askopenfilename()
    print(("__multiWindow__::openDialogFile = %s \n") % (self.__filePath))
    self.__mySipm.openFile(self.__filePath)
    self.__mySipm.turnOnSendToDatabase()
##
##
## --------------------------------------------------------------------
##
##	Open up file dialog....Locate multiple files in a string
## cmj2019May14 
  def openFileDialogMultipleFiles(self):
    self.__multipleFilePath=tkinter.filedialog.askopenfilenames()  ## add an "s" at the end to get the string for several files
    #print("__multiWindow__::openFileDialogMultipleFiles = %s \n") % (self.__multipleFilePath)
    self.__multipleFileNames = list(self.__multipleFilePath)
    for self.__myFile in self.__multipleFileNames:
      print(("__multiWindow__::openFileDialogMultipleFiles = %s \n") % (self.__myFile))
##
## ------------------------------------------------------------------
##	Send initial information to database
  def sendInitialToDatabase(self):
    ## cmj2019May14 self.__mySipm.readFile('initial')
    for self.__myFile in self.__multipleFileNames:						  ## cmj2019May14
      print(("__multiWindow__::sendInitialToDatabase... load from file: %s \n") % (self.__myFile))  ## cmj2019May14
      self.__mySipm.readFile('initial',self.__myFile)
      self.__mySipm.sendPoNumberToDatabase()
      self.__mySipm.sendReceivedPoToDatabase()
      self.__mySipm.sendSipmIdsToDatabase()
##
## ------------------------------------------------------------------
##	Send pack number to database
##      This is a special case for the first two batches
  def sendPackNumberToDatabase(self):
    ##cmj2019May14 self.__mySipm.readFile('packnumber')
    for self.__myFile in self.__multipleFileNames:							## cmj2019May14
      print(("__multiWindow__::sendPackNumberToDatabase... load from file: %s \n") % (self.__myFile))	## cmj2019May14
      self.__mySipm.readFile('packnumber',self.__myFile)
      self.__mySipm.sendPackNumberToDatabase()
##
## ------------------------------------------------------------------
##	Send Vendor information to database
##
  def sendVendorInformation(self):
    ##cmj2019May14 self.__mySipm.readFile('vendor')
    for self.__myFile in self.__multipleFileNames:							## cmj2019May14
      print(("__multiWindow__::sendVendorInformation... load from file: %s \n") % (self.__myFile)) 	## cmj2019May14
      self.__mySipm.readFile('vendor',self.__myFile)
      self.__mySipm.sendSipmVendorMeasToDatabase()
##
## ------------------------------------------------------------------
##	Send locally measured information to database
##
  def sendLocalInformation(self):
    for self.__myFile in self.__multipleFileNames:						##cmj2019May14 
      print(("__multiWindow__::sendLocalInformation... load from file: %s \n") % (self.__myFile)) ##cmj2019May14 
      self.__mySipm.readFile('local',self.__myFile)						##cmj2019May14 
    ##cmj2019May14 self.__mySipm.readFile('local')
      self.__mySipm.sendSipmLocalMeasToDatabase()
##
## ------------------------------------------------------------------
##	Send IV information to database
##
  def sendLocalIVInformation(self):
    ##cmj2019May14 self.__mySipm.readIVfile()
    for self.__myFile in self.__multipleFileNames:
      print(("__multiWindow__::sendLocalIVInformation... load from file: %s \n") % (self.__myFile))
      self.__mySipm.readIVfile(self.__myFile)
      self.__mySipm.sendIvMeasurmentsTodatabase()
##
## --------------------------------------------------------------------
##
  def turnOnDebug(self,tempDebug):
    self.__mySipm.setDebugLevel(tempDebug)
## --------------------------------------------------------------------
  def turnOnSendToDatabase(self):
    self.__mySipm.turnOnSendToDatabase()
## --------------------------------------------------------------------
  def turnOffSendToDatabase(self):
    self.__mySipm.turnOffSendToDatabase()
## --------------------------------------------------------------------
  def sendToDevelopmentDatabase(self):
    self.__mySipm.sendToDevelopmentDatabase()
## --------------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__mySipm.sendToProductionDatabase()  
## --------------------------------------------------------------------
  def updateMode(self):
    print("__multiWindow__::updateMode.... UPDATE MODE!... update entries to database!")
    self.__mySipm.updateMode()
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
  if(options.update == "update"): myMultiForm.updateMode()
  if(options.debugMode != 0): myMultiForm.turnOnDebug(options.debugMode)
  if(options.testMode != 0): 
    myMultiForm.turnOffSendToDatabase()
  else:
    myMultiForm.turnOnSendToDatabase()
    myMultiForm.sendToProductionDatabase()
    if(options.database == "development"): myMultiForm.sendToDevelopmentDatabase()
    else: myMultiForm.sendToProductionDatabase()
  myMultiForm.grid()
  root.mainloop()
