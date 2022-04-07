# -*- coding: utf-8 -*-
##
##  File = "checkFeb.py"
##      A python script to read the Feb tables in the hardware database
##      and display the Location and type of a FEB
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2020Jul27
##
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May12... replaced tabs with 6 spaces to convert to python 3
##  Modified by cmj2022Mar23-2022Mar31... add multiple frames and scroll frames to select FEB's
##
##
#!/bin/env python
from tkinter import *         # get widget class
import tkinter as tk
from tkinter.ttk import *             # get tkk widget class (for progess bar)
import tkinter.filedialog
import os
import sys        ## 
import optparse   ## parser module... to parse the command line arguments
import math
from collections import defaultdict
from time import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2018Oct2 add highlight to scrolled list
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from cmjGuiLibGrid import *  ## cmj2020Aug03
from Electronics import *
#import SipmMeasurements
##
ProgramName = "checkFeb.py"
Version = "version2023.03.31"
##
##
## -------------------------------------------------------------
##       A class to set up the main window to drive the
##      python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0, debug = 0):
    self.__cmjDebug = debug ## default... no debug messages printed out
    print(("Program: %s \n")%(ProgramName))
    print(("Version: %s \n") % (Version))
    if(self.__cmjDebug > -1): print("...multiWindow::Class multiWindow... Enter \n") 
    self.__sleepTime = 0.1  ##  time interval between database requests
    self.__maxTries = 10  ## maximum number of attempts to retrieve from database
    self.__defaultBackGroundColor = "gray"
    self.__masterFrame = Frame.__init__(self,parent)
    self.__writePassword = ""
    self.__database_config  = databaseConfig()
    #self.setupDevelopmentDatabase()  ## set up communications with database
    self.setupProductionDatabase()  ## set up communications with database
    self.__sendToDatabase = 1
    if(self.__cmjDebug > 3): print("...multiWindow::combineFrames:: before self.addFebFrame() \n")
    self.__StringEntryFebId_result = 'xxxxaaaa'
    ##
    self.__febId_dict = {}
    self.__febType_dict={}
    self.__febLocation_dict={}
    self.__febComment_dict={}
    self.__febFirmwareRelease_dict = {}
    ##
    self.__progressBarCount = tk.DoubleVar()  ## for progress bar
    self.__progressBarCount.set(0)            ## for progress bar
    self.__progressBarMaximum = 300
    ## set up geometry for GUI
    self.__gridWidth = int(15)
    self.__labelWidth = self.__gridWidth
    self.__entryWidth = self.__gridWidth
    self.__buttonWidth = self.__gridWidth
    self.__row = 0
    self.__col = 0
    ## Get the list of FEB's once and use this list in the various control frames
    self.__tempFebResults = []
    self.__tempFebResults = self.getAllFebsFromDatabase()  ## get the list of Feb Id's from the database
    if(self.__cmjDebug > 3) : print((("self.__tempFebResults = %s \n") % (self.__tempFebResults )))
    self.__myOptions = []
    for self.__m in self.__tempFebResults:
      self.__temp = self.__m.rsplit(",",8)
      self.__myOptions.append(self.__temp[0])
    ## Get the list of FEB's once and use this list in the various control frames 
    if(self.__cmjDebug > 10): 
      print(("...multiWindow:: self.__writePassword = %s \n") %(self.__writePassword))
      print("...multiWindow::Class multiWindow:: before self.setControlBox() \n")
    ##
    ##  Control Frame in upper left hand corner
    self.__comboRow = 0
    self.__comboCol = 0
    self.setControlBox()
    ##  Query Frame... below Control box: lower left hand corner
    self.__comboRow = 1
    self.__comboCol = 0
    self.queryFrame()
    ##  Change location frame: upper right hand corner
    self.__comboRow = 0
    self.__comboCol = 1    
    self.changeLocationFrame()
    ##  Add FEB frame: lower right hand corner
    self.__comboRow = 1
    self.__comboCol = 1
    self.addFebFrame()
    if(self.__cmjDebug > 2): print("...multiWindow::Class multiWindow... Exit \n")
##
##
##
##-----------------------------------------------------------------------------
## Define the Control box frame that is contained in the masterFrame
## This frame has the Mu2e logo, program version, date, debug boxes and
## the progress bar.
##
  def setControlBox(self):
    if(self.__cmjDebug > 2): print("...multiWindow::setControlBox... Enter \n")
##      Display the Control Box  Frame here..
    self.__frame0 = tk.LabelFrame(self.__masterFrame,bg=self.__defaultBackGroundColor)
    self.__frame0.grid(row=self.__comboRow,column=self.__comboCol,columnspan=4,sticky=NSEW)
    self.__frame0.config(width=300)
    self.__frame0.config(text="FEB Database Management Script ---")
    self.__row = 0
    self.__col = 0
##  Setup a debug level window...
    localButtonWidth = 15
    localLabelWidth = 20
    localEntryWidth = 15
    self.__StringEntryFebLocation_result = 'none'
    self.__frame0.grid(row=self.__row,column=0,sticky=NSEW)
    self.__buttonName = 'Set debug level: '
    self.__buttonText1 = 'Enter 0 - 5'
    #self.__StringEntryChangeFebLocation = myStringEntry2(self.__frame0)
    #self.__StringEntryChangeFebLocation.StringEntrySetup(self.__frame0,self.__row,0,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.StringEntrySetDebugLevel(self.__frame0,self.__row,0,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName,buttonText=self.__buttonText1)
    self.__row += 1
##      Third Column...
    self.__row = 0
    self.__col = 10
    self.__logo = mu2eLogo(self.__frame0,self.__row,self.__col)     # display Mu2e logo!
    self.__logo.grid(row=self.__row,column=self.__col,rowspan=3,sticky=NE)
    self.__col = 1
    self.__row += 4
    ##
    self.__sipmGrid_row = self.__row
    self.__sipmGrid_col = self.__col
#         Display the date the script is being run
    #self.__row = 0
    self.__col = 0
    self.__date = myDate(self.__frame0,self.__row,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__row,column=self.__col,columnspan=2,sticky=W)
    ##  Add program version
    self.__row += 1
    self.__col = 0
    self.__myVersion = myLabel(self.__frame0,self.__row,self.__col,20)
    self.__myVersion.grid(row=self.__row,column=self.__col,columnspan=2,sticky=W)
    self.__myVersion.setText(Version)
    self.__myVersion.setForgroundColor('blue')
    self.__col = 0
    self.__buttonWidth = 10
    self.__row += 1
    self.__progressbar = Progressbar(self.__frame0,orient=HORIZONTAL,length=200,maximum=self.__progressBarMaximum,variable=self.__progressBarCount,mode='determinate')
    self.__progressbar.grid(row=self.__row,column=0,columnspan=5,sticky=W)
    self.__row += 1
##      Add Control Bar at the bottom...
    self.__quitNow = Quitter(self.__frame0,0,self.__col)
    self.__quitNow.grid(row=self.__row,column=0,sticky=W)
#    self.queryFrame()
    self.update()
    if(self.__cmjDebug > 2): print("...multiWindow::setControlBox... Exit \n")
##
## -------------------------------------------------------------------
##  Define the queryFrame that is contained in the masterFrame
##  This contains a scroll window to select FEB's and three options
##  to string entry for FebId, Feb type, Feb location, or all Feb's
##  After selection, the FebId, Feb Type, Location, Comment and Firmware release
##  are printed out in another frame.
##
  def queryFrame(self):
    if(self.__cmjDebug > 2): print("...multiWindow::queryFrame... Enter \n") 
    self.__title = 'Query an FEB  - '
    self.__frame5 = tk.LabelFrame(self.__masterFrame)      ## define frame3 in the master frame
    self.__locationRow5 = 0
    self.__locationCol5 = 0
    self.__frame5.grid(row=self.__comboRow,column=self.__comboCol,columnspan=1,sticky=tk.NW)
    self.__frame5.configure(width=300)
    self.__frame5.configure(text=self.__title)
    self.__frame5 = tk.Frame(self.__frame5,bg=self.__defaultBackGroundColor)
    self.__frame5.grid(row=self.__locationRow5,column=self.__locationCol5,columnspan=3,sticky=NSEW)
    ##  Setup the display label
    self.__row = 0
    self.__myLocationLabel = myLabel(self.__frame5)
    self.__myLocationLabel.setWidth(20)
    self.__myLocationLabel.setText('Find an FEB Location, etc ---')
    self.__myLocationLabel.setFont('arial')
    self.__myLocationLabel.setFontType('bold')
    self.__myLocationLabel.setBackgroundColor('lightblue')
    self.__myLocationLabel.makeLabel()
    self.__myLocationLabel.grid(row=self.__row,column=0,sticky=W)
    self.__locationRow5 += 1
    ##
    ##  Setup the change Feb_Id Scroll Window
    ##  Followed by the  button to implment the choice.
    ##  These two are paired.... begin
    self.__myScrolledListQuery = ScrolledList(self.__frame5,self.__myOptions)  ## self.__myScrolledQuery.fetchList()  will return a list of all double clicked fields.
    self.__myScrolledListQuery.grid(row=self.__locationRow5,column=self.__locationCol5,sticky=W,rowspan=4)
    ##   Setup Button to select FebId ....
    self.__locationRow5 = 0
    self.__locationCol5 = 2
    self.__buttonWidth = 10
    self.__getValues = Button(self.__frame5,text='Select FEB',command=self.loadFebQueryRequest,width=self.__buttonWidth,bg='violet',fg='black')
    self.__getValues.grid(row=self.__locationRow5,column=self.__locationCol5,sticky=W)
    ##  These two are paired.... end
    ##
    ## FebId button... string entry... redundant: select an individual Feb by its Id... enter string.
    self.__locationRow5 += 1
    self.__buttonWidth1 = 20
    self.__buttonName = 'Feb Id '
    self.__buttonText3 = 'Enter: feb-NT+Numb'
    tempResult = ''
    self.StringEntrySetup(self.__frame5,self.__locationRow5,self.__locationCol5,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName,buttonText=self.__buttonText3)
    ## 
    ## Location Query... string entry
    self.__locationRow5 +=1
    self.__buttonName1 = 'Location'
    self.__entry1 = self.StringEntrySetup1(self.__frame5,self.__locationRow5,self.__locationCol5,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName1)
    self.__locationRow5 +=1
    ##
    ## Type of FEB... string entry
    self.__buttonName2 = 'Type'
    self.__entry2 = self.StringEntrySetup2(self.__frame5,self.__locationRow5,self.__locationCol5,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName2)
    self.__locationRow5 +=1
    ##
    ##  Get All Feb's... string entry
    self.__getValues = Button(self.__frame5,text='Get All Febs',command=self.getAllFebFromDatabase,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__locationRow5,column=self.__locationCol5,sticky=W)
    self.__locationRow5  += 1
    self.update()  ## write these out to frame5
    if(self.__cmjDebug > 2): print("...multiWindow::queryFrame... Exit \n")
##
## -------------------------------------------------------------------
##  Define a frame that is contained in the masterFrame that has these
##  controls for changing the the location of an FEB or its Firmware.
##  There is a scroll frame and button to select the FebId, then two 
##  string entries to insert the new Feb location or change the Feb_Id
##  firmware, then two buttons to actuate the change.
##
  def changeLocationFrame(self):
    ##  Display the Location Frame....
    if(self.__cmjDebug > 2): print("...multiWindow::changeLocationFrame... Enter \n") 
    self.__title = 'Change Feb Location... or Update the Firmware  - '
    self.__frame3 = tk.LabelFrame(self.__masterFrame)      ## define frame3 in the master frame
    self.__locationRow3 = 0
    self.__locationCol3 = 0
    self.__frame3.grid(row=self.__comboRow,column=self.__comboCol,columnspan=2,sticky=tk.NW)
    self.__frame3.configure(width=300)
    self.__frame3.configure(text=self.__title)
    self.__frame3 = tk.Frame(self.__frame3,bg=self.__defaultBackGroundColor)
    self.__frame3.grid(row=self.__locationRow3,column=self.__locationCol3,columnspan=3,sticky=NSEW)
    self.__buttonWidth1 = 20
    ##  Setup the display label
    self.__locationRow3= 0
    self.__myLocationLabel = myLabel(self.__frame3)
    self.__myLocationLabel.setWidth(20)
    self.__myLocationLabel.setText('Change Feb Location')
    self.__myLocationLabel.setFont('arial')
    self.__myLocationLabel.setFontType('bold')
    self.__myLocationLabel.setBackgroundColor('lightblue')
    self.__myLocationLabel.makeLabel()
    self.__myLocationLabel.grid(row=self.__locationRow3,column=self.__locationCol3,sticky=W)
    self.__locationRow3 += 1
    ##
    ##  Define the dimensions of buttons in this frame.
    localButtonWidth = 15
    localLabelWidth = 20
    localEntryWidth = 15
    ##
    ##  Setup the change Feb_Id Scroll Window
    ##  Followed by the  button to implment the choice.
    ##  These two are paired.... begin
    self.__changeFebScrolledList = FebScrolledList(self.__frame3,self.__myOptions)
    self.__changeFebScrolledList.grid(row=self.__locationRow3,column=self.__locationCol3,sticky=W,rowspan=4)
    ## Setup Button to select FebId
    self.__locationCol3 = 1
    self.__buttonWidth = 10
    self.__getValues = Button(self.__frame3,text='Select FEB',command=self.loadFebIdChangeRequest,width=self.__buttonWidth,bg='violet',fg='black')
    self.__getValues.grid(row=self.__locationRow3,column=self.__locationCol3,sticky=W)
    self.__locationRow3 += 1
    ##  These two are paired.... end
    ##
    ##  Setup the Change FEB location Window... paired with "self.__getValues" button
    self.__StringEntryFebLocation_result = 'none'
    self.__frame3.grid(row=self.__locationRow3,column=1,sticky=NSEW)
    self.__buttonName = 'New Feb Location '
    self.__StringEntryChangeFebLocation = myStringEntry2(self.__frame3)
    self.__StringEntryChangeFebLocation.StringEntrySetup(self.__frame3,self.__locationRow3,1,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    ##
    ## Setup the change FEB Firmware button... paired with "self.__updateFirm" button
    self.__locationRow3 += 1
    self.__StringEntryFebFirmware_result = 'N/A'
    self.__buttonName = 'Firmware '
    self.StringEntrySetFebFirmware(self.__frame3,self.__locationRow3,1,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__frame3.grid(row=self.__locationRow3,column=1,sticky=NSEW)
    self.__buttonName = 'Change FEB Firmware '
    self.__StringEntryChangeFebFirmware = myStringEntry2(self.__frame3)
    self.__StringEntryChangeFebFirmware.StringEntrySetup(self.__frame3,self.__locationRow3,1,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__locationRow3+=1
    ##
    ## Setup the change Comment button... paired with "self.__updateComment" button
    self.__locationRow3 += 1
    self.__StringEntryFebComment_result = 'N/A'
    self.__frame3.grid(row=self.__locationRow3,column=1,sticky=NSEW)
    self.__buttonName = 'Change FEB Comment '
    self.__StringEntryChangeFebComment = myStringEntry2(self.__frame3)
    self.__StringEntryChangeFebComment.StringEntrySetup(self.__frame3,self.__locationRow3,1,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__locationRow3+=1
    ##
    ##  Setup the change the Feb location when this button is clicked!
    self.__getValues = Button(self.__frame3,text='Change Feb Location',command=self.changeFebLocation,width=localButtonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__locationRow3,column=0,sticky=W)
    ##
    ##  Setup the change the Feb firmware when this button is clicked!
    self.__updateFirm = Button(self.__frame3,text='Update Firmware',command=self.changeFirmware,width=localButtonWidth,bg='green',fg='black')
    self.__updateFirm.grid(row=self.__locationRow3,column=1,sticky=W)
    ##
    ##  Setup the change the Feb firmware when this button is clicked!
    self.__updateComment = Button(self.__frame3,text='Update Comment',command=self.changeComment,width=localButtonWidth,bg='green',fg='black')
    self.__updateComment.grid(row=self.__locationRow3,column=2,sticky=W)
    ##
    self.update()  ## update -- i.e. write these into self.__frame3
    if(self.__cmjDebug > 2): print("...multiWindow::changeLocationFrame... Exit \n")
##
## ---------------------------------------------------------------------------------------
##  Define a frame that is contained in the masterFrame that allows entry of a new FEB
##  Along with its locatin, type and firmware version.  A button at the end affects these
##  changes.
  def addFebFrame(self):
    if(self.__cmjDebug > 2): print("...multiWindow::addFebFrame... Enter \n")
    self.__title = 'Add Feb ... or Update the Firmware - '
    self.__frame4 = tk.LabelFrame(self.__masterFrame)      ## define frame4 in the master frame
    self.__locationRow4 = 0
    self.__locationCol4 = 0
    self.__frame4.grid(row=self.__comboRow,column=self.__comboCol,columnspan=3,sticky=tk.NW) ## define location in masterFrame
    self.__frame4.configure(width=300)
    self.__frame4.configure(text=self.__title)
    self.__frame4 = tk.Frame(self.__frame4,bg=self.__defaultBackGroundColor)
    self.__frame4.grid(row=self.__row,column=0,columnspan=3,sticky=NSEW)
    self.__buttonWidth1 = 20
    ##  Setup the display label
    self.__locationRow4 = 0
    self.__myLocationLabel = myLabel(self.__frame4)
    self.__myLocationLabel.setWidth(20)
    self.__myLocationLabel.setText('Add New FEB')
    self.__myLocationLabel.setFont('arial')
    self.__myLocationLabel.setFontType('bold')
    self.__myLocationLabel.setBackgroundColor('lightblue')
    self.__myLocationLabel.makeLabel()
    self.__myLocationLabel.grid(row=self.__locationRow4,column=0,sticky=tk.NW)
    self.__locationRow4 += 1
    if(self.__cmjDebug > 10): print(("...multiWindow::addFebFrame... self.__writePassword = %s \n") %(self.__writePassword))
    self.__StringEntryFebId_result = 'none'
    self.__buttonName = 'Add: Feb Id '
    localButtonWidth = 15
    localLabelWidth = 20
    localEntryWidth = 15
    self.__locationRow4 += 1
    self.__locationCol4 = 0
    ## Setup the Add FEB string entry
    self.__StringEntryNewFeb_result = 'none'
    self.__frame4.grid(row=self.__locationRow4,column=self.__locationCol4,columnspan=3,sticky=NSEW)
    self.__buttonName = 'New FEB Id '
    self.__buttonText2 = 'Enter: feb-NT+Numb'
    self.StringEntrySetFebId(self.__frame4,self.__locationRow4,self.__locationCol4,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName,buttonText=self.__buttonText2)
    self.__locationRow4 += 1   
    ## Setup the New FEB Type string entry
    self.__StringEntryFebType_result = 'none'
    self.__frame4.grid(row=self.__locationRow4,column=0,columnspan=3,sticky=NSEW)
    self.__buttonName = 'FEB Type '
    self.StringEntrySetFebType(self.__frame4,self.__locationRow4,self.__locationCol4,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__locationRow4 += 1   
    ## Setup the new FEB Firmware string entry
    self.__StringEntryFebFirmware_result = 'N/A'
    self.__frame4.grid(row=self.__locationRow4,column=0,columnspan=3,sticky=NSEW)
    self.__buttonName = 'Firmware '
    self.StringEntrySetFebFirmware(self.__frame4,self.__locationRow4,self.__locationCol4,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__locationRow4 += 1
    ## Setup the new Feb Location string entry
    self.__StringEntryFebLocation_result = 'none'
    self.__frame4.grid(row=self.__locationRow4,column=1,columnspan=3,sticky=NSEW)
    self.__buttonName = 'Feb Location '
    self.StringEntrySetFebLocation(self.__frame4,self.__locationRow4,self.__locationCol4,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__locationRow4 += 1
    ## Setup the add Comment button...
    self.__StringEntryFebNewComment_result = 'N/A'
    self.__frame4.grid(row=self.__locationRow4,column=1,sticky=NSEW)
    self.__buttonName = 'FEB Comment '
    self.__StringEntryNewFebComment = myStringEntry2(self.__frame4)
    self.__StringEntryNewFebComment.StringEntrySetup(self.__frame4,self.__locationRow4,self.__locationCol4,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__locationRow4 += 1
    ##      Change the Feb location when this button is clicked!
    self.__getValues = Button(self.__frame4,text='Add Feb',command=self.addFeb,width=localButtonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__locationRow4,column=0,sticky=W)  
    self.update()
    if(self.__cmjDebug > 2): print("...multiWindow::addFebFrame... Exit \n")
## 
##
## -------------------------------------------------------------------
## A frame that is contained (actually ammended) to the masterFrame
## once the "Get All Feb" button is clicked in the "Query an FEB" frame.
## The result is to write out for each FEB in the database:
## FebId, FebType, Location, Comments and Firmware release.
##
  def showAllFeb(self):
    if(self.__cmjDebug > 2): print("...multiWindow::showAllFeb...  Enter \n")
    self.__frame02 = tk.LabelFrame(self.__masterFrame)      ## define frame2 in the master frame in the master frame
    self.__borderWidth = 1
    self.__borderStyle = 'solid'
    self.__row = 0
    self.__col = 0
    self.__textList = []
    self.__bannerGridWidth = 20
    self.__bannerRow = 0
    self.__frame02.grid(row=10,column=0,columnspan=3,sticky=tk.NW)   ## frame2 contains the banner
    self.__frame02.configure(width=500)
    self.__frame02.configure(text="Febs")
    self.__myTitle0 = myLabel(self.__frame02,0,0,int(self.__bannerGridWidth))
    self.__myTitle0.setText('Feb Id')
    self.__myTitle0.setBorder(self.__borderWidth,self.__borderStyle)
    self.__myTitle0.setBackgroundColor(self.__defaultBackGroundColor)
    self.__myTitle0.setFontSize('12')
    self.__myTitle0.grid(row=0,column=0,columnspan=1)
    #
    self.__myTitle1 = myLabel(self.__frame02,0,0,int(self.__bannerGridWidth))
    self.__myTitle1.setText('Feb Type')
    self.__myTitle1.setBorder(self.__borderWidth,self.__borderStyle)
    self.__myTitle1.setBackgroundColor(self.__defaultBackGroundColor)
    self.__myTitle1.setFontSize('12')
    self.__myTitle1.grid(row=0,column=1,columnspan=1)
    #
    self.__myTitle2 = myLabel(self.__frame02,0,0,int(self.__bannerGridWidth))
    self.__myTitle2.setText('Location')
    self.__myTitle2.setBorder(self.__borderWidth,self.__borderStyle)
    self.__myTitle2.setBackgroundColor(self.__defaultBackGroundColor)
    self.__myTitle2.setFontSize('12')
    self.__myTitle2.grid(row=0,column=2,columnspan=1)
    #
    self.__myTitle3 = myLabel(self.__frame02,0,0,int(self.__bannerGridWidth))
    self.__myTitle3.setText('Comment')
    self.__myTitle3.setBorder(self.__borderWidth,self.__borderStyle)
    self.__myTitle3.setBackgroundColor(self.__defaultBackGroundColor)
    self.__myTitle3.setFontSize('12')
    self.__myTitle3.grid(row=0,column=3,columnspan=1)
    #
    self.__myTitle4 = myLabel(self.__frame02,0,0,int(self.__bannerGridWidth))
    self.__myTitle4.setText('Firmware Release')
    self.__myTitle4.setBorder(self.__borderWidth,self.__borderStyle)
    self.__myTitle4.setBackgroundColor(self.__defaultBackGroundColor)
    self.__myTitle4.setFontSize('12')
    self.__myTitle4.grid(row=0,column=4,columnspan=1)
    #self.update()
    #
    self.__frame2 = tk.Frame(self.__masterFrame)      ## define frame2 in the master frame3in the master frame
    self.__frame2.grid(row=11,column=0,columnspan=3,sticky=tk.NW)   ## frame2 contains the module cross section and slide bars
    self.__frame2.configure(width=500)
    #self.__frame2.configure(text=self.__title)
    self.__canvas1 = tk.Canvas(self.__frame2,bg="gray")
    self.__canvas1.grid(row=0,column=0,columnspan=5)
    self.__canvas1.configure(width=790,height=320)
    ## define the vertical slide bar 
    self.__vScrollBar = tk.Scrollbar(self.__frame2,orient=tk.VERTICAL,command=self.__canvas1.yview)
    self.__vScrollBar.grid(row=0,column=5,sticky=NS)
    self.__canvas1.configure(yscrollcommand=self.__vScrollBar.set)
    ## define the horizontal slide bar
    self.__hScrollBar = tk.Scrollbar(self.__frame2,orient=tk.HORIZONTAL,command=self.__canvas1.xview)
    self.__hScrollBar.grid(row=1,column=0,sticky=EW)
    self.__canvas1.configure(xscrollcommand=self.__hScrollBar.set)
    ## Define the grid frame to contain the scroll bar window
    self.__moduleGridFrame=tk.LabelFrame(self.__canvas1,bg="gray",bd=2)
    self.__moduleGridFrame.configure(width=780,height=220)
    #self.update()
    ##
    self.__positionBanner0 = []
    self.__positionBanner1 = []
    self.__positionBanner2 = []
    self.__positionBanner3 = []
    self.__positionBanner4 = []
    self.__positionNumber = 0
    ppp = 0
    for mmm in sorted(self.__febId_dict.keys()):
      if(self.__cmjDebug > 5): print((" self.__febId_dict.keys = %s ppp = %d\n") % (mmm, ppp))
      self.__col = 0
      self.__text = self.__febId_dict[mmm]
      self.__positionBanner0.append(myLabel(self.__moduleGridFrame,self.__bannerRow,self.__col,int(self.__bannerGridWidth)))
      self.__positionBanner0[ppp].setText(str(self.__text))
      self.__positionBanner0[ppp].setBorder(self.__borderWidth,self.__borderStyle)
      self.__positionBanner0[ppp].setBackgroundColor(self.__defaultBackGroundColor)
      self.__positionBanner0[ppp].setFontSize('12')
      self.__positionBanner0[ppp].grid(row=self.__row,column=self.__col,columnspan=1)
      self.__col += 1
      ##
      self.__text = self.__febType_dict[mmm]
      self.__positionBanner1.append(myLabel(self.__moduleGridFrame,self.__bannerRow,self.__col,int(self.__bannerGridWidth)))
      self.__positionBanner1[ppp].setText(str(self.__text))
      self.__positionBanner1[ppp].setBorder(self.__borderWidth,self.__borderStyle)
      self.__positionBanner1[ppp].setBackgroundColor(self.__defaultBackGroundColor)
      self.__positionBanner1[ppp].setFontSize('12')
      self.__positionBanner1[ppp].grid(row=self.__row,column=self.__col,columnspan=1)
      self.__col += 1
      ##
      self.__text = self.__febLocation_dict[mmm]
      self.__positionBanner2.append(myLabel(self.__moduleGridFrame,self.__bannerRow,self.__col,int(self.__bannerGridWidth)))
      self.__positionBanner2[ppp].setText(str(self.__text))
      self.__positionBanner2[ppp].setBorder(self.__borderWidth,self.__borderStyle)
      self.__positionBanner2[ppp].setBackgroundColor(self.__defaultBackGroundColor)
      self.__positionBanner2[ppp].setFontSize('12')
      self.__positionBanner2[ppp].grid(row=self.__row,column=self.__col,columnspan=1)
      self.__col +=1
      ##
      self.__text = self.__febComment_dict[mmm]
      self.__positionBanner3.append(myLabel(self.__moduleGridFrame,self.__bannerRow,self.__col,int(self.__bannerGridWidth)))
      self.__positionBanner3[ppp].setText(str(self.__text))
      self.__positionBanner3[ppp].setBorder(self.__borderWidth,self.__borderStyle)
      self.__positionBanner3[ppp].setBackgroundColor(self.__defaultBackGroundColor)
      self.__positionBanner3[ppp].setFontSize('12')
      self.__positionBanner3[ppp].grid(row=self.__row,column=self.__col,columnspan=1)
      self.__col +=1
      ##
      self.__text = self.__febFirmwareRelease_dict[mmm]
      self.__positionBanner4.append(myLabel(self.__moduleGridFrame,self.__bannerRow,self.__col,int(self.__bannerGridWidth)))
      self.__positionBanner4[ppp].setText(str(self.__text))
      self.__positionBanner4[ppp].setBorder(self.__borderWidth,self.__borderStyle)
      self.__positionBanner4[ppp].setBackgroundColor(self.__defaultBackGroundColor)
      self.__positionBanner4[ppp].setFontSize('12')
      self.__positionBanner4[ppp].grid(row=self.__row,column=self.__col,columnspan=1)
      self.__col +=1
      ##
      self.__row += 1
      ppp+=1
      xx = self.__progressBarCount.get()  ## get current count for self.__width progress bar
      self.__progressBarCount.set(xx+10)  ## increment the count
      self.update()  ## update the progress bar...
    self.update()
    self.__canvas1.create_window((0,0),window=self.__moduleGridFrame,anchor=tk.NW)  ## make window to hold the canvas
    self.__moduleGridFrame.update_idletasks() ## Make box information (below) available 
    self.__bbox = self.__canvas1.bbox(tk.ALL) ## Get the dimensions of the bounding box holding the canvas
    if(self.__cmjDebug > 2) : print(("bbox1 =%s bbox2 = %s bbox3 = %s  \n")%(self.__bbox[1],self.__bbox[2],self.__bbox[3]))
    self.__width = self.__bbox[2]-self.__bbox[1]
    self.__height = self.__bbox[3]-self.__bbox[1]
    self.__COLS = 5  ## define the number of columns in the grid
    self.__ROWS = 8   ## define the number of rows in the grid
    self.__COLS_DISP = 5  ## define the number of columns to display
    self.__ROWS_DISP = 7   ## define the number of rows to display
    self.__deltaWidth=int((self.__width/self.__COLS)*self.__COLS_DISP)   ## define the scrollable region as canvas with COLS_DISP columns displayed
    self.__deltaHeight=int((self.__height/self.__ROWS)*self.__ROWS_DISP) ## define the scrollable region as canvas with ROWS_DISP rows displayed
    self.__canvas1.configure(scrollregion=self.__bbox,width=self.__deltaWidth,height=self.__deltaHeight) ## actually configure the canvas
    if(self.__cmjDebug > 2): print("...multiWindow::showAllFeb... Exit \n")     
##
## -------------------------------------------------------------------
##  Make querries to get all extrusion batches to data base
##  This function gets all Feb id's from the database to be used
##  in the scroll
##
  def getAllFebsFromDatabase(self):
    if(self.__cmjDebug > 2): print("...multiWindow::getAllFebsFromDatabase... Enter \n")
    self.__getAllFebValues = DataQuery(self.__queryUrl)
    self.__localFebIdsValues = []
    self.__table = "front_end_boards"
    self.__fetchThese = "feb_id"
    self.__fetchCondition = "create_time:ge:2017-05-15"
    self.__numberReturned = 0
    if(self.__cmjDebug > 1): print(("...multiWindow::getAllFebsFromDatabase %s %s %s \n" %(self.__database,self.__table,self.__fetchThese)))
    ## cmj2018Mar26
    for n in range(0,self.__maxTries):            ## sometimes the datagbase does not answer.. give it a few tries!
      self.__localFebIdsValues = self.__getAllFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,"-"+self.__fetchThese)
      if (self.__localFebIdsValues != -9999) : break
    ## cmj2018Mar26
    if(self.__cmjDebug > 1): print(("...multiWindow::getAllFebsFromDatabase: self.__extrusionBatchValues = %s \n") %(self.__localFebIdsValues))
    self.__numberOfBatches = len(self.__localFebIdsValues)
    if(self.__cmjDebug != 0):
      for self.__l in self.__localFebIdsValues:
        print((self.__l))
    if(self.__cmjDebug > 2): print("...multiWindow::getAllFebsFromDatabase... Exit \n")
    return self.__localFebIdsValues
##
## -------------------------------------------------------------------
##      Load the Feb Id requeseted from the query scroll list
##  
  def loadFebIdChangeRequest(self):
    if(self.__cmjDebug > 2): print("...multiWindow::loadFebIdChangeRequest... Enter \n")
    if(self.__cmjDebug > 3): print(("...multiWindow::loadFebIdChangeRequest.... self.__myScrolledList.fetchList = %s \n") % (self.__changeFebScrolledList.fetchList()))
    self.__StringEntryFebId_result = self.__changeFebScrolledList.fetchList();
    if(self.__cmjDebug > 3): print(("...multiWindow::loadFebIdChangeRequest.... self.__StringEntryFebId_result = %s \n") % (self.__changeFebScrolledList.fetchList()))
    if(self.__cmjDebut > 2): print("...multiWindow::loadFebIdChangeRequest... Exit \n")
    return
  ##
## -------------------------------------------------------------------
##  Load the Feb Id requeseted from the query scroll list
##  This function calls "getFebFromDatabase" that queries 
##  the database to get the information stored for 
##  the requested Feb_Id's
##  
  def loadFebQueryRequest(self):
    if(self.__cmjDebug > 2): print("...multiWindow::loadFebQueryRequest... Enter \n")
    if(self.__cmjDebug > 3): print(("...multiWindow::loadFebQueryRequest.... self.__myScrolledList.fetchList = %s \n") % (self.__myScrolledListQuery.fetchList()))
    tempString = self.__StringEntryFebId_result = self.__myScrolledListQuery.fetchList()  ## fetch the list of FebId's selected
    tempList = []
    tempList = tempString.rsplit(",")
    for febId in tempList:
      self.getFebFromDatabase(febId)
      if(self.__cmjDebug > 3): print(("...multiWindow::loadFebQueryRequest.... febId = %s \n") % (febId))
    if(self.__cmjDebug > 2): print("...multiWindow::loadFebQueryRequest... Exit \n")
    return
##
## -------------------------------------------------------------------
## This function actually queries the database for the a requested Feb_Id 
## supplied and loads the results into a list that containse the 
## FebId, feb_type, locatoin, comments and firmware version
##
  def getFebFromDatabase(self,tempFebId):
    if(self.__cmjDebug > 2): print("...multiWindow::getFebFromDatabase... Enter \n")
    self.__singleFebResult = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchCondition='feb_id:eq:'+tempFebId.strip()
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 5):
      print(("...multiWindow::getFebFromDatabase... self.__tempFebId = %s \n") % (tempFebId))
      print(("...multiWindow::getFebFromDatabase... self.__database = %s \n") % (self.__database))
      print(("...multiWindow::getFebFromDatabase... self.__table = %s \n") % (self.__table))
      print(("...multiWindow::getFebFromDatabase... self.__fetchCondition = xxx%sxxx \n") % (self.__fetchCondition))
      print(("...multiWindow::getFebFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese))
    self.__singleFebResult = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition)
    self.storeFebResults(self.__singleFebResult)
    self.showAllFeb()
    if(self.__cmjDebug > 3): print(("...multiWindow::getFebFromDatabase... self.__singleFebResult = %s \n") % (self.__singleFebResult))
    if(self.__cmjDebug > 1): print("...multiWindow::getFebFromDatabase... Exit \n")
##    
## -------------------------------------------------------------------
## This function actually queries the database for a selected institution
## to get the feb_Id, feb_type, location, comments and firmware version.
  def getFebInstitutionFromDatabase(self,tempLocation):
    if(self.__cmjDebug > 2): print("...multiWindow::getFebInstitutionFromDatabase... Enter \n")
    self.__allFebResults = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchCondition='location:eq:'+tempLocation.strip()
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 5):
      print(("...multiWindow::getFebInstitutionFromDatabase... self.__tempLocation = %s \n") % (tempLocation))
      print(("...multiWindow::getFebInstitutionFromDatabase... self.__database = %s \n") % (self.__database))
      print(("...multiWindow::getFebInstitutionFromDatabase... self.__table = %s \n") % (self.__table))
      print(("...multiWindow::getFebInstitutionFromDatabase... self.__fetchCondition = xxx%sxxx \n") % (self.__fetchCondition))
      print(("...multiWindow::getFebInstitutionFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese))
    self.__allFebResults = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjDebug > 3): print(("...multiWindow::getFebInstitutionFromDatabase... self.__allFebResults = %s \n") % (self.__allFebResults))
    self.storeFebResults(self.__allFebResults)
    self.showAllFeb()
    if(self.__cmjDebug > 2): print("...multiWindow::getFebInstitutionFromDatabase... Exit \n")
## -------------------------------------------------------------------
##  This function actually querries the database for a selected Feb type
## to get the feb_Id, feb_type, location, comments and firmware version.
  def getFebTypeFromDatabase(self,tempType):
    if(self.__cmjDebug > 2): print("...multiWindow::getFebTypeFromDatabase... Enter \n")
    self.__allFebResults = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchCondition='feb_type:eq:'+tempType.strip()
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 5):
      print(("...multiWindow::getFebTypeFromDatabase... self.__tempType = %s \n") % (tempType))
      print(("...multiWindow::getFebTypeFromDatabase... self.__database = %s \n") % (self.__database))
      print(("...multiWindow::getFebTypeFromDatabase... self.__table = %s \n") % (self.__table))
      print(("...multiWindow::getFebTypeFromDatabase... self.__fetchCondition = xxx%sxxx \n") % (self.__fetchCondition))
      print(("...multiWindow::getFebTypeFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese))
    self.__allFebResults = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjDebug > 3): print(("...multiWindow::getFebTypeFromDatabase... self.__allFebResults = %s \n") % (self.__allFebResults))
    self.storeFebResults(self.__allFebResults)
    self.showAllFeb()
    if(self.__cmjDebug > 2): print("...multiWindow::getFebTypeFromDatabase... Exit \n")
    ##
## -------------------------------------------------------------------
## This function actually querries the database to get FebId's 
## for all Feb's in the database to produce a list for the 
## FebId's in the scroll lists
  def getAllFebFromDatabase(self):
    if(self.__cmjDebug > 2): print("...multiWindow::getAllFebFromDatabase... Enter \n")
    self.__allFebResults = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 5):
      print(("...multiWindow::getAllFebFromDatabase... self.__database = %s \n") % (self.__database))
      print(("...multiWindow::getAllFebFromDatabase... self.__table = %s \n") % (self.__table))
      print(("...multiWindow::getAllFebFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese))
    self.__allFebResults = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,None)
    if(self.__cmjDebug > 3): print(("...multiWindow::getAllFebFromDatabase... self.__allFebResults = %s \n") % (self.__allFebResults))
    self.storeFebResults(self.__allFebResults)
    self.showAllFeb()
    if(self.__cmjDebug > 2): print("...multiWindow::getAllFebFromDatabase... Exit \n")
     ##
## -------------------------------------------------------------------
## This function stores the Feb results from the querries into 
## a dictionaries FebId, FebType, FebLocation, FebFirmware type
## where the key is the Feb_Id.
  def storeFebResults(self,tempFebResults):
    if(self.__cmjDebug > 2): print("...multiWindow::storeFebResults... Enter \n")
    for nn in tempFebResults:
      self.__item=[]
      self.__item = nn.rsplit(',')
      if(len(self.__item) > 1): 
        if(self.__cmjDebug > 5): print(("self.__item = %s") % (self.__item))
        tempFebId = self.__item[0]
        tempFebType = self.__item[1]
        tempFebLocation = self.__item[2]
        tempFebComment = self.__item[3]
        tempFirmWareRelease = self.__item[4]
        self.__febId_dict[tempFebId]=tempFebId
        self.__febType_dict[tempFebId]=tempFebType
        self.__febLocation_dict[tempFebId]=tempFebLocation
        if(tempFebComment == 'None'):
          self.__febComment_dict[tempFebId] = " "
        else:
          self.__febComment_dict[tempFebId] = tempFebComment
        if(tempFirmWareRelease == 'None'):
          self.__febFirmwareRelease_dict[tempFebId] = 'N/A'
        else :
          self.__febFirmwareRelease_dict[tempFebId] = tempFirmWareRelease
        xx = self.__progressBarCount.get()  ## get current count for progress bar
        self.__progressBarCount.set(xx+10)  ## increment the count
        self.update()  ## update the progress bar...
    if(self.__cmjDebug > 5):
      for mm in list(self.__febId_dict.keys()):
        print(("...multiWindow::storeFebResults... self.__febId_dict[%s] = %s \n") % (mm,self.__febId_dict[mm]))
        print(("...multiWindow::storeFebResults... self.__febType_dict[%s] = %s \n") % (mm,self.__febType_dict[mm]))
        print(("...multiWindow::storeFebResults... self.__febLocation_dict[%s] = %s \n") % (mm,self.__febLocation_dict[mm]))
        print(("...multiWindow::storeFebResults... self.__febComment_dict[%s] = %s \n") % (mm,self.__febComment_dict[mm]))
        print(("...multiWindow::storeFebResults... self.__febFirmwareRelease_dict[%s] = %s \n") % (mm,self.__febFirmwareRelease_dict[mm]))       
    if(self.__cmjDebug > 2): print("...multiWindow::storeFebResults... Exit \n")
##
## ------------------------------------------------------------------- 
##  This function changes the FEB location in the Database
##  for an Feb_Id that already exist in the database
##  using the "update" feature.
  def changeFebLocation(self):
    if(self.__cmjDebug > 1): print("...multiWindow::changeFebLocation... Enter  \n")
    self.__group = "Electronic Tables"
    self.__frontEndBoardsTable = "front_end_boards"
    self.__frontEndBoardLocation = {}
    self.__frontEndBoardLocation['feb_id'] = self.__StringEntryFebId_result
    self.__frontEndBoardLocation['location']=self.__StringEntryChangeFebLocation.fetchResult()
    if(self.__cmjDebug > 10): 
      print(("...multiWindow::changeFebLocation... self.__writeUrl = %s \n") % (self.__writeUrl))
      print(("...multiWindow::changeFebLocation... self.__writePassword = %s \n") % (self.__writePassword)) 
    if(self.__cmjDebug > -1): 
      print(("...multiWindow::changeFebLocation... changeFebLocation: self.__StringEntryFebId_result = %s, self.__StringEntryFebLocation_result = %s \n") % (self.__StringEntryFebId_result,self.__StringEntryFebLocation_result))
    if self.__sendToDatabase != 0:
      print("send Change Feb Location to database!")
      self.__myDataLoader1 = DataLoader(self.__writePassword,self.__writeUrl,self.__group,self.__frontEndBoardsTable)
      if(self.__cmjDebug > -1): print("...multiWindow::changeFebLocation... sendFrontEndBoardsToDatabase: update")
      self.__myDataLoader1.addRow(self.__frontEndBoardLocation,'update')      ##cmj2019May23... update existing line
      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()      ## send it to the data base!
      print("self.__text = %s" % self.__text)
      sleep(self.__sleepTime)
      if self.__retVal:                                          ## sucess!  data sent to database
        print("...multiWindow::changeFebLocation... Electronics FEB "+self.__StringEntryFebId_result+"  Transmission Success!!!")
        print(self.__text)
      elif self.__password == '':
        print(('...multiWindow::changeFebLocation: Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
      else:
        print("...multiWindow::changeFebLocation:  Electronics FEB "+self.__StringEntryFebId_result+"  Transmission: Failed!!!")
        print(self.__code)
        print(self.__text) 
    if(self.__cmjDebug > 1): print("...multiWindow::changeFebLocation... Exit  \n")
    return 0  ## success
##
## -------------------------------------------------------------------
##    Add a new FEB to the database
##    Add new FEB Board (i.e. Feb Id to database)
  def addFeb(self):
    if(self.__cmjDebug > 1): print("...multiWindow::addFeb... Enter \n")
    self.__group = "Electronic Tables"
    self.__frontEndBoardsTable = "front_end_boards"
    self.__addNewFeb = {}
    self.__addNewFeb['feb_id'] = self.__StringEntryFebId_result
    self.__addNewFeb['feb_type'] = self.__StringEntryFebType_result
    self.__addNewFeb['firmware_version'] = self.__StringEntryFebFirmware_result
    self.__addNewFeb['location'] = self.__StringEntryFebLocation_result
    self.__addNewFeb['comments'] = self.__StringEntryNewFebComment.fetchResult()
    self.__addNewFeb['module_position'] = -1
    if(self.__cmjDebug > 10): 
      print(("...multiWindow::addFeb... self.__writeUrl =%s \n") % (self.__writeUrl))
      print(("...multiWindow::addFeb... self.__writePassword = %s \n") % (self.__writePassword)) 
    if(self.__cmjDebug > -1): 
      print(("...multiWindow::addFeb... self.__StringEntryFebId_result = %s \n") % (self.__StringEntryFebId_result))
    if self.__sendToDatabase != 0:
      print("Add New Feb Id to database!")
      self.__myDataLoader1 = DataLoader(self.__writePassword,self.__writeUrl,self.__group,self.__frontEndBoardsTable)
      if(self.__cmjDebug > -1): print("...multiWindow::addFeb... sendFrontEndBoardsToDatabase: update")
      self.__myDataLoader1.addRow(self.__addNewFeb,'insert')      ##cmj2019May23... update existing line
      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()      ## send it to the data base!
      print("self.__text = %s" % self.__text)
      sleep(self.__sleepTime)
      if self.__retVal:                                          ## sucess!  data sent to database
        print("...multiWindow::addFeb... Electronics FEB "+self.__StringEntryFebId_result+"  Transmission Success!!!")
        print(self.__text)
      elif self.__writePassword == '':
        print(('...multiWindow::addFEB.... Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
      else:
        print("...multiWindow::addFeb:  Electronics FEB "+self.__StringEntryFebId_result+"  Transmission: Failed!!!")
        print(self.__code)
        print(self.__text) 
    if(self.__cmjDebug > 1): print("...multiWindow::addFeb... Exit \n")
    return 0  ## success  
##
## -------------------------------------------------------------------
##    This function adds Firmware Version for the new FEB...
##    The Feb_Id is already entered.... The Firmware is changed 
##    with the update feature (to an existing Feb_Id record)
##
  def changeFirmware(self):
    if(self.__cmjDebug > 1): print("...multiWindow::changeFirmware... Enter \n")
    self.__group = "Electronic Tables"
    self.__frontEndBoardsTable = "front_end_boards"
    self.__updateFirm = {}
    self.__updateFirm['feb_id'] = self.__StringEntryFebId_result
    #self.__updateFirm['feb_type'] = self.__StringEntryFebType_result
    self.__updateFirm['firmware_version'] = self.__StringEntryChangeFebFirmware.fetchResult()
    self.__updateFirm['module_position'] = -1
    if(self.__cmjDebug > 10): 
      print(("...multiWindow::changeFirmware... self.__writeUrl =%s \n") % (self.__writeUrl))
      print(("...multiWindow::changeFirmware... self.__writePassword = %s \n") % (self.__writePassword)) 
    if(self.__cmjDebug > -1): 
      print(("...multiWindow::changeFirmware... self.__StringEntryFebId_result = %s \n") % (self.__StringEntryFebId_result))
    if self.__sendToDatabase != 0:
      print("Add New Feb Id to database!")
      self.__myDataLoader1 = DataLoader(self.__writePassword,self.__writeUrl,self.__group,self.__frontEndBoardsTable)
      if(self.__cmjDebug > -1): print("...multiWindow::changeFirmware... sendFrontEndBoardsToDatabase: update")
      self.__myDataLoader1.addRow(self.__updateFirm,'update')      ##cmj2019May23... update existing line
      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()      ## send it to the data base!
      print("self.__text = %s" % self.__text)
      sleep(self.__sleepTime)
      if self.__retVal:                                          ## sucess!  data sent to database
        print("...multiWindow::changeFirmware... Electronics FEB "+self.__StringEntryFebId_result+"  Transmission Success!!!")
        print(self.__text)
      elif self.__writePassword == '':
        print(('...multiWindow::addFEB.... Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
      else:
        print("...multiWindow::changeFirmware:  Electronics FEB "+self.__StringEntryFebId_result+"  Transmission: Failed!!!")
        print(self.__code)
        print(self.__text) 
    if(self.__cmjDebug > 1): print("...multiWindow::changeFirmware... Exit \n")
    return 0  ## success
  
  
##
## -------------------------------------------------------------------
##    This function adds Firmware Version for the new FEB...
##    The Feb_Id is already entered.... The Firmware is changed 
##    with the update feature (to an existing Feb_Id record)
##
  def changeComment(self):
    if(self.__cmjDebug > 1): print("...multiWindow::changeComment... Enter \n")
    self.__group = "Electronic Tables"
    self.__frontEndBoardsTable = "front_end_boards"
    self.__updateFirm = {}
    self.__updateFirm['feb_id'] = self.__StringEntryFebId_result
    self.__updateFirm['comments'] = self.__StringEntryChangeFebComment.fetchResult()
    self.__updateFirm['module_position'] = -1
    if(self.__cmjDebug > 10): 
      print(("...multiWindow::changeComment... self.__writeUrl =%s \n") % (self.__writeUrl))
      print(("...multiWindow::changeComment... self.__writePassword = %s \n") % (self.__writePassword)) 
    if(self.__cmjDebug > -1): 
      print(("...multiWindow::changeComment... self.__StringEntryFebId_result = %s \n") % (self.__StringEntryFebId_result))
    if self.__sendToDatabase != 0:
      print("Add New Feb Id to database!")
      self.__myDataLoader1 = DataLoader(self.__writePassword,self.__writeUrl,self.__group,self.__frontEndBoardsTable)
      if(self.__cmjDebug > -1): print("...multiWindow::changeComment... sendFrontEndBoardsToDatabase: update")
      self.__myDataLoader1.addRow(self.__updateFirm,'update')      ##cmj2019May23... update existing line
      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()      ## send it to the data base!
      print("self.__text = %s" % self.__text)
      sleep(self.__sleepTime)
      if self.__retVal:                                          ## sucess!  data sent to database
        print("...multiWindow::changeComment... Electronics FEB "+self.__StringEntryFebId_result+"  Transmission Success!!!")
        print(self.__text)
      elif self.__writePassword == '':
        print(('...multiWindow::addFEB.... Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
      else:
        print("...multiWindow::changeComment:  Electronics FEB "+self.__StringEntryFebId_result+"  Transmission: Failed!!!")
        print(self.__code)
        print(self.__text) 
    if(self.__cmjDebug > 1): print("...multiWindow::changeComment... Exit \n")
    return 0  ## success
  
##  
#######################################################################################
####################################################################################### 
##
## -------------------------------------------------------------------
##      Make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Electronic Tables"
    self.__whichDatabase = 'development'
    print("...multiWindow::getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
    self.__writeUrl = self.__database_config.getWriteUrl()
    self.__writePassword = self.__database_config.getElectronicsKey()
    if(self.__cmjDebug > 10):
      print(("...multiWindow::setupDevelopmentDatabase: self.__queryUrl = %s \n")% (self.__queryUrl))
      print(("...multiWindow::setupDevelopmentDatabase: self.__writeUrl = %s \n")% (self.__writeUrl))
      print(("...multiWindow::setupDevelopmentDatabase: self.__writePassword = %s \n")% (self.__writePassword))
##
## -------------------------------------------------------------------
##      Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Electronic Tables"
    self.__whichDatabase = 'production'
    print("...multiWindow::getFromProductionDatabase... get from production database \n")
    self.__queryUrl = self.__database_config.getProductionQueryUrl()
    self.__writeUrl = self.__database_config.getProductionWriteUrl()
    self.__writePassword = self.__database_config.getElectronicsProductionKey()
    if(self.__cmjDebug > 10):
      print(("...multiWindow::setupProductionDatabase: self.__queryUrl = %s \n")% (self.__queryUrl))
      print(("...multiWindow::setupProductionDatabase: self.__writeUrl = %s \n")% (self.__writeUrl))
      print(("...multiWindow::setupProductionDatabase: self.__writePassword = %s \n")% (self.__writePassword))
##
## -------------------------------------------------------------------
  def setDebugLevel(self,tempDebugLevel):
    self.__cmjDebug = tempDebugLevel
    print(("...multiWindow::getFromProductionDatabase... Set Debug Level to = %s \n") % (self.__cmjDebug))   
    ##
## ------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow is to call the "self.getFebFromDatabase()" method when the 
##  "Enter" button is pressed.
  def StringEntrySetup(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup... Enter \n")
    self.__LocalFrame = tempFrame
    self.__StringEntry_row = tempRow
    self.__StringEntry_col = tempCol
    self.__StringEntry_labelWidth = self.__gridWidth
    self.__StringEntry_entryWidth = self.__gridWidth
    self.__StringEntry_buttonWidth= self.__gridWidth
    self.__StringEntry_entyLabel = ''
    self.__StringEntry_buttonText = buttonText
    self.__StringEntry_buttonName = buttonName
    self.__StringEntry_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__label = Label(self.__LocalFrame,width=self.__labelWidth,text=self.__StringEntry_buttonName,anchor=W,justify=LEFT)
    self.__label.grid(row=self.__StringEntry_row,column=self.__StringEntry_col,sticky=W)
    self.__ent = Entry(self.__LocalFrame,width=self.__StringEntry_entryWidth)
    self.__var = StringVar()        # associate string variable with entry field
    self.__ent.config(textvariable=self.__var)
    self.__var.set('')
    self.__ent.grid(row=self.__StringEntry_row,column=self.__StringEntry_col+1,sticky=W)
    self.__ent.focus()
    self.__ent.bind('<Return>',lambda event:self.fetch())
    self.__button = Button(self.__LocalFrame,text=self.__StringEntry_buttonText,width=self.__StringEntry_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetch)
    self.__button.config(bg='#E3E3E3')
    self.__button.grid(row=self.__StringEntry_row,column=self.__StringEntry_col+2,sticky=W)
  def StringEntryFetch(self):
    self.__StringEntry_result = self.__ent.get()
    self.__button.config(bg='yellow')
    self.getFebFromDatabase(self.__StringEntry_result)   ## write result to new frame
    if (self.__buttonName=='Type'): self.getFebTypeFromDatabase(self.__StringEntry_result)
    if(self.__cmjDebug > 3):
      print(("...multiWindow::StringEntrySetup... self.__StringEntry_result = %s \n") %(self.__StringEntry_result))
      print("...multiWindow::StringEntrySetup... StringEntrySetup: Exit \n")
    return self.__StringEntry_result
## ------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow is to call the "self.getFebInstitutionFromDatabase()" method when the 
##  "Enter" button is pressed.
  def StringEntrySetup1(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup1... StringEntrySetup1: Enter \n")
    self.__LocalFrame1 = tempFrame
    self.__StringEntry1_row = tempRow
    self.__StringEntry1_col = tempCol
    self.__StringEntry1_labelWidth = self.__gridWidth
    self.__StringEntry1_entryWidth = self.__gridWidth
    self.__StringEntry1_buttonWidth= self.__gridWidth
    self.__StringEntry1_entyLabel = ''
    self.__StringEntry1_buttonText = 'Enter'
    self.__StringEntry1_buttonName = buttonName
    self.__StringEntry1_result = 'xxxxaaaa'
    self.__entryLabel1 = '' 
    self.__label1 = Label(self.__LocalFrame1,width=self.__labelWidth,text=self.__StringEntry1_buttonName,anchor=W,justify=LEFT)
    self.__label1.grid(row=self.__StringEntry1_row,column=self.__StringEntry1_col,sticky=W)
    self.__ent1 = Entry(self.__LocalFrame1,width=self.__StringEntry1_entryWidth)
    self.__var1 = StringVar()        # associate string variable with entry field
    self.__ent1.config(textvariable=self.__var1)
    self.__var1.set('')
    self.__ent1.grid(row=self.__StringEntry1_row,column=self.__StringEntry1_col+1,sticky=W)
    self.__ent1.focus()
    self.__ent1.bind('<Return>',lambda event:self.fetch())
    self.__button1 = Button(self.__LocalFrame1,text=self.__StringEntry1_buttonText,width=self.__StringEntry1_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetch1)
    self.__button1.config(bg='#E3E3E3')
    self.__button1.grid(row=self.__StringEntry1_row,column=self.__StringEntry1_col+2,sticky=W)
  def StringEntryFetch1(self):
    self.__StringEntry1_result = self.__ent1.get()
    self.__button1.config(bg='yellow')
    if (self.__buttonName1=='Location') : self.getFebInstitutionFromDatabase(self.__StringEntry1_result)
    if(self.__cmjDebug > 3): 
      print(("...multiWindow::StringEntrySetup1... self.__StringEntry1 = %s self.__buttonName1 = %s \n") %(self.__StringEntry1_result,self.__buttonName1))
      print("...multiWindow::StringEntrySetup1... StringEntrySetup1: Exit \n")
    return self.__StringEntry1_result
##
## ------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow is to call the "self.getFebTypeFromDatabase()" method when the 
##  "Enter" button is pressed.
## Get the Feb Type for the Feb_Id is selected.
  def StringEntrySetup2(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup2... Enter \n")
    self.__LocalFrame2 = tempFrame
    self.__StringEntry2_row = tempRow
    self.__StringEntry2_col = tempCol
    self.__StringEntry2_labelWidth = self.__gridWidth
    self.__StringEntry2_entryWidth = self.__gridWidth
    self.__StringEntry2_buttonWidth= self.__gridWidth
    self.__StringEntry2_entyLabel = ''
    self.__StringEntry2_buttonText = 'Enter'
    self.__StringEntry2_buttonName = buttonName
    self.__StringEntry2_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__label = Label(self.__LocalFrame2,width=self.__labelWidth,text=self.__StringEntry2_buttonName,anchor=W,justify=LEFT)
    self.__label.grid(row=self.__StringEntry2_row,column=self.__StringEntry2_col,sticky=W)
    self.__ent2 = Entry(self.__LocalFrame2,width=self.__StringEntry2_entryWidth)
    self.__var2 = StringVar()        # associate string variable with entry field
    self.__ent2.config(textvariable=self.__var2)
    self.__var2.set('')
    self.__ent2.grid(row=self.__StringEntry2_row,column=self.__StringEntry2_col+1,sticky=W)
    self.__ent2.focus()
    self.__ent2.bind('<Return>',lambda event:self.fetch())
    self.__button2 = Button(self.__LocalFrame2,text=self.__StringEntry2_buttonText,width=self.__StringEntry2_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetch2)
    self.__button2.config(bg='#E3E3E3')
    self.__button2.grid(row=self.__StringEntry2_row,column=self.__StringEntry2_col+2,sticky=W)
  def StringEntryFetch2(self):
    self.__StringEntry2_result = self.__ent2.get()
    self.__button2.config(bg='yellow')
    if (self.__buttonName2=='Type'): self.getFebTypeFromDatabase(self.__StringEntry2_result)
    if(self.__cmjDebug > 3):
      print(("...multiWindow::StringEntrySetup2... self.__StringEntry2_result = %s \n") %(self.__StringEntry2_result))
      print("...multiWindow::StringEntrySetup2... Exit \n")
    return self.__StringEntry2_result
##
## ------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow load the string result into "self.__StringEntryFebId_result"
##  variable after the  "Enter" button is pressed.
##  Get the Feb_Id you want
  def StringEntrySetFebId(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebId... StringEntrySetFebId: Enter \n")
    self.__LocalFrame2 = tempFrame
    self.__StringEntryFebId_row = tempRow
    self.__StringEntryFebId_col = tempCol
    self.__StringEntryFebId_labelWidth = self.__gridWidth
    self.__StringEntryFebId_entryWidth = self.__gridWidth
    self.__StringEntryFebId_buttonWidth= self.__gridWidth
    self.__StringEntryFebId_entyLabel = ''
    self.__StringEntryFebId_buttonText = buttonText
    self.__StringEntryFebId_buttonName = buttonName
    stringEntryFebId_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__labelFebId = Label(self.__LocalFrame2,width=self.__labelWidth,text=self.__StringEntryFebId_buttonName,anchor=W,justify=LEFT)
    self.__labelFebId.grid(row=self.__StringEntryFebId_row,column=self.__StringEntryFebId_col,sticky=W)
    self.__entFebId = Entry(self.__LocalFrame2,width=self.__StringEntryFebId_entryWidth)
    self.__varFebId = StringVar()        # associate string variable with entry field
    self.__entFebId.config(textvariable=self.__varFebId)
    self.__varFebId.set('')
    self.__entFebId.grid(row=self.__StringEntryFebId_row,column=self.__StringEntryFebId_col+1,sticky=W)
    self.__entFebId.focus()
    self.__entFebId.bind('<Return>',lambda event:self.fetch())
    self.__buttonFebId = Button(self.__LocalFrame2,text=self.__StringEntryFebId_buttonText,width=self.__StringEntryFebId_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetchFebId)
    self.__buttonFebId.config(bg='#E3E3E3')
    self.__buttonFebId.grid(row=self.__StringEntryFebId_row,column=self.__StringEntryFebId_col+2,sticky=W)
  def StringEntryFetchFebId(self):
    self.__StringEntryFebId_result = self.__entFebId.get()
    stringEntryFebId_result = self.__StringEntryFebId_result
    self.__buttonFebId.config(bg='yellow')
    if(self.__cmjDebug > 3):
      print(("...multiWindow::StringEntrySetFebId... self.__stringEntryFebId_result = %s \n") %(self.__stringEntryFebId_result))
      print("...multiWindow::StringEntrySetFebId... StringEntrySetFebId: Exit  \n")
    return stringEntryFebId_result  
##
## ------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow load the string result into "self.__StringEntryFebLocation_result"
##  variable after the  "Enter" button is pressed.
##  Get the FebLocation whose location you want to change
  def StringEntrySetFebLocation(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebLocation... StringEntrySetFebLocation: Enter  \n")
    self.__LocalFrame2 = tempFrame
    self.__StringEntryFebLocation_row = tempRow
    self.__StringEntryFebLocation_col = tempCol
    self.__StringEntryFebLocation_labelWidth = self.__gridWidth
    self.__StringEntryFebLocation_entryWidth = self.__gridWidth
    self.__StringEntryFebLocation_buttonWidth= self.__gridWidth
    self.__StringEntryFebLocation_entyLabel = ''
    self.__StringEntryFebLocation_buttonText = buttonText
    self.__StringEntryFebLocation_buttonName = buttonName
    self.__StringEntryFebLocation_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__labelFebLocation = Label(self.__LocalFrame2,width=self.__labelWidth,text=self.__StringEntryFebLocation_buttonName,anchor=W,justify=LEFT)
    self.__labelFebLocation.grid(row=self.__StringEntryFebLocation_row,column=self.__StringEntryFebLocation_col,sticky=W)
    self.__entFebLocation = Entry(self.__LocalFrame2,width=self.__StringEntryFebLocation_entryWidth)
    self.__varFebLocation = StringVar()        # associate string variable with entry field
    self.__entFebLocation.config(textvariable=self.__varFebLocation)
    self.__varFebLocation.set('')
    self.__entFebLocation.grid(row=self.__StringEntryFebLocation_row,column=self.__StringEntryFebLocation_col+1,sticky=W)
    self.__entFebLocation.focus()
    self.__entFebLocation.bind('<Return>',lambda event:self.fetch())
    self.__buttonFebLocation = Button(self.__LocalFrame2,text=self.__StringEntryFebLocation_buttonText,width=self.__StringEntryFebLocation_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetchFebLocation)
    self.__buttonFebLocation.config(bg='#E3E3E3')
    self.__buttonFebLocation.grid(row=self.__StringEntryFebLocation_row,column=self.__StringEntryFebLocation_col+2,sticky=W)
  def StringEntryFetchFebLocation(self):
    self.__StringEntryFebLocation_result = self.__entFebLocation.get()
    self.__buttonFebLocation.config(bg='yellow')
    print(("self.__StringEntryFebLocation_result = %s \n") % (self.__StringEntryFebLocation_result))
    if(self.__cmjDebug > 3): 
      print(("..multiWindow::StringEntrySetFebLocation... StringEntrySetFebLocation = %s \n") %(self.__StringEntryFebLocation_result))
      print("...multiWindow::StringEntrySetFebLocation... Exit  \n")
    return self.__StringEntryFebLocation_result   
##
## ------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow load the string result into "self.__StringEntryFebType_result"
##  variable after the  "Enter" button is pressed.
##  Get the FebType (pre-production, production, etc) whose type you want to change
  def StringEntrySetFebType(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebLocation... Enter \n")
    self.__LocalFrame2 = tempFrame
    self.__StringEntryFebType_row = tempRow
    self.__StringEntryFebType_col = tempCol
    self.__StringEntryFebType_labelWidth = self.__gridWidth
    self.__StringEntryFebType_entryWidth = self.__gridWidth
    self.__StringEntryFebType_buttonWidth= self.__gridWidth
    self.__StringEntryFebType_entyLabel = ''
    self.__StringEntryFebType_buttonText = 'Enter'
    self.__StringEntryFebType_buttonName = buttonName
    self.__StringEntryFebType_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__labelFebType = Label(self.__LocalFrame2,width=self.__labelWidth,text=self.__StringEntryFebType_buttonName,anchor=W,justify=LEFT)
    self.__labelFebType.grid(row=self.__StringEntryFebType_row,column=self.__StringEntryFebType_col,sticky=W)
    self.__entFebType = Entry(self.__LocalFrame2,width=self.__StringEntryFebType_entryWidth)
    self.__varFebType = StringVar()        # associate string variable with entry field
    self.__entFebType.config(textvariable=self.__varFebType)
    self.__varFebType.set('')
    self.__entFebType.grid(row=self.__StringEntryFebType_row,column=self.__StringEntryFebType_col+1,sticky=W)
    self.__entFebType.focus()
    self.__entFebType.bind('<Return>',lambda event:self.fetch())
    self.__buttonFebType = Button(self.__LocalFrame2,text=self.__StringEntryFebType_buttonText,width=self.__StringEntryFebType_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetchFebType)
    self.__buttonFebType.config(bg='#E3E3E3')
    self.__buttonFebType.grid(row=self.__StringEntryFebType_row,column=self.__StringEntryFebType_col+2,sticky=W)
  def StringEntryFetchFebType(self):
    self.__StringEntryFebType_result = self.__entFebType.get()
    self.__buttonFebType.config(bg='yellow')
    print(("self.__StringEntryFebType_result = %s \n") % (self.__StringEntryFebType_result))
    if(self.__cmjDebug):
      print(("...multiWindow::StringEntrySetFebType... self.__StringEntryFebType_result = %s") %(self.__StringEntryFebType_result))
      print("...multiWindow::StringEntrySetFebType... StringEntrySetFebType: Exit  \n")
    return self.__StringEntryFebType_result  
##
## ------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow load the string result into "self.__cmjDebug"
##  variable after the  "Enter" button is pressed.
##  Change the debug level... return an integer result
  def StringEntrySetDebugLevel(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    print("...multiWindow::StringEntrySetFebLocation... Enter \n")
    self.__LocalFrame2 = tempFrame
    self.__StringDebugLevel_row = tempRow
    self.__StringDebugLevel_col = tempCol
    self.__StringDebugLevel_labelWidth = self.__gridWidth
    self.__StringDebugLevel_entryWidth = self.__gridWidth
    self.__StringDebugLevel_buttonWidth= self.__gridWidth
    self.__StringDebugLevel_entyLabel = ''
    self.__StringDebugLevel_buttonText = buttonText
    self.__StringDebugLevel_buttonName = buttonName
    self.__StringDebugLevel_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__labelDebugLevel = Label(self.__LocalFrame2,width=self.__labelWidth,text=self.__StringDebugLevel_buttonName,anchor=W,justify=LEFT)
    self.__labelDebugLevel.grid(row=self.__StringDebugLevel_row,column=self.__StringDebugLevel_col,sticky=W)
    self.__entDebugLevel = Entry(self.__LocalFrame2,width=self.__StringDebugLevel_entryWidth)
    self.__varDebugLevel = StringVar()        # associate string variable with entry field
    self.__entDebugLevel.config(textvariable=self.__varDebugLevel)
    self.__varDebugLevel.set('')
    self.__entDebugLevel.grid(row=self.__StringDebugLevel_row,column=self.__StringDebugLevel_col+1,sticky=W)
    self.__entDebugLevel.focus()
    self.__entDebugLevel.bind('<Return>',lambda event:self.fetch())
    self.__buttonDebugLevel = Button(self.__LocalFrame2,text=self.__StringDebugLevel_buttonText,width=self.__StringDebugLevel_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetchDebugLevel)
    self.__buttonDebugLevel.config(bg='#E3E3E3')
    self.__buttonDebugLevel.grid(row=self.__StringDebugLevel_row,column=self.__StringDebugLevel_col+2,sticky=W)
  def StringEntryFetchDebugLevel(self):
    self.__StringDebugLevel_result = self.__entDebugLevel.get()
    self.__cmjDebug = int(self.__StringDebugLevel_result)
    self.__buttonDebugLevel.config(bg='yellow')
    print(("...multiWindow::StringEntrySetFebLocation... Set Debug level to = %s \n") % (self.__StringDebugLevel_result))
    if(self.__cmjDebug > 11): print("...multiWindow::StringEntrySetDebugLevel... StringEntrySetDebugLevel: Exit  \n")
    return int(self.__StringDebugLevel_result)
  
  
##
## -------------------------------------------------------------------
## ===================================================================
##    Local String Entry button
##  Need to setup here to retain local program flow
##  The local program flow load the string result into "self.__StringEntryFebFirmware_result"
##  variable after the  "Enter" button is pressed.
##  Get the FebFirmware version you want to change
  def StringEntrySetFebFirmware(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebLocation --------- StringEntrySetFebLocation: Enter ----------------- \n")
    self.__LocalFrame2 = tempFrame
    self.__StringEntryFebFirmware_row = tempRow
    self.__StringEntryFebFirmware_col = tempCol
    self.__StringEntryFebFirmware_labelWidth = self.__gridWidth
    self.__StringEntryFebFirmware_entryWidth = self.__gridWidth
    self.__StringEntryFebFirmware_buttonWidth= self.__gridWidth
    self.__StringEntryFebFirmware_entyLabel = ''
    self.__StringEntryFebFirmware_buttonText = 'Enter'
    self.__StringEntryFebFirmware_buttonName = buttonName
    self.__StringEntryFebFirmware_result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__labelFebFirmware = Label(self.__LocalFrame2,width=self.__labelWidth,text=self.__StringEntryFebFirmware_buttonName,anchor=W,justify=LEFT)
    self.__labelFebFirmware.grid(row=self.__StringEntryFebFirmware_row,column=self.__StringEntryFebFirmware_col,sticky=W)
    self.__entFebFirmware = Entry(self.__LocalFrame2,width=self.__StringEntryFebFirmware_entryWidth)
    self.__varFebFirmware = StringVar()        # associate string variable with entry field
    self.__entFebFirmware.config(textvariable=self.__varFebFirmware)
    self.__varFebFirmware.set('')
    self.__entFebFirmware.grid(row=self.__StringEntryFebFirmware_row,column=self.__StringEntryFebFirmware_col+1,sticky=W)
    self.__entFebFirmware.focus()
    self.__entFebFirmware.bind('<Return>',lambda event:self.fetch())
    self.__buttonFebFirmware = Button(self.__LocalFrame2,text=self.__StringEntryFebFirmware_buttonText,width=self.__StringEntryFebFirmware_buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetchFebFirmware)
    self.__buttonFebFirmware.config(bg='#E3E3E3')
    self.__buttonFebFirmware.grid(row=self.__StringEntryFebFirmware_row,column=self.__StringEntryFebFirmware_col+2,sticky=W)
  def StringEntryFetchFebFirmware(self):
    self.__StringEntryFebFirmware_result = self.__entFebFirmware.get()
    self.__buttonFebFirmware.config(bg='yellow')
    print(("self.__StringEntryFebFirmware_result = %s \n") % (self.__StringEntryFebFirmware_result))
    print(("--- StringEntrySetFebFirmware... after Button in StringEntrySetFebFirmware = %s") %(self.__StringEntryFebFirmware_result))
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebFirmware --------- StringEntrySetFebFirmware: Exit ----------------- \n")
    return self.__StringEntryFebFirmware_result
##
## -------------------------------------------------------------------
## ===================================================================
##    Local scroll list
## Need to setup here to retain local program flow.
## Produce the scroll list and return a single "Feb_Id" selected
## by a "double click" of an element in the displayed list. 
  def FEBScrollList(self,tempFrame,options,tempWidth=20):
    self.__localFrame10 = tempFrame
    self.__localFrame10.pack(expand=YES,fill=BOTH)
    self.makeWidgets(options, tempWidth)
    self.__recordSelection = ""
  def handleList2(self,event):        # Run on double left clidk  
    index = self.listbox.curselection()    # on list double-click
    label = self.listbox.get(index)      # fetch selection text
    self.listbox.itemconfig(index,bg="yellow")  ## cmj2018Oct1.. selected color.
    self.runCommand2(label)        # and call action here
  def makeWidgets(self,options,tempWidth):        # or get (ACTIVE)
    sbar = Scrollbar(self)
    list = Listbox(self,relief=SUNKEN,width=tempWidth)
    sbar.config(command=list.yview)      # cross link sbar and list...
    list.config(yscrollcommand=sbar.set)    # move one moves the other
    sbar.pack(side=RIGHT,fill = Y)      # pack first = clip last
    list.pack(side=LEFT, expand=YES,fill=BOTH)  # list clipped first
    pos = 0
    for label in options:        # Add to list box
      list.insert(pos,label)      # Set event handler
      pos += 1
    list.config(selectmode=SINGLE, setgrid = 1)
    list.bind('<Double-1>',self.handleList2)    # double left click
    #list.bind('<Single-1>',self.handleList1)    # single left click
    self.listbox=list        
  def runCommand2(self,selection):
    self.__recordSelection = self.__recordSelection+selection+","  ## build output string...
    return selection
  def fetchList(self):          # Offer an accessor to get the list selected  
    self.__StringEntryFebId_result = selection
    return
##
##
##
##
###########################################################################
###########################################################################
###########################################################################
###########################################################################
##
##   A class to construct a scrollList
##  This class will return the text of a double clicked entry
##  that are double clicked....
##   There is a fetching accessor function to get the final string
##  after all selections are made.
##   The selections are passed as a list when the class is called.
## Produce the scroll list and return a single "Feb_Id" selected
## by a "double click" of an element in the displayed list.
##
class FebScrolledList(Frame):
  def __init__(self,parent,options,tempWidth=20):
    Frame.__init__(self,parent)
    ##cmj2022Apr5 self.pack(expand=YES,fill=BOTH)
    self.makeWidgets(options,tempWidth)
    self.__recordSelection = ""
    self.__cmjDebug = 0
  def handleList2(self,event):        # Run on double left clidk  
    index = self.listbox.curselection()    # on list double-click
    label = self.listbox.get(index)      # fetch selection text
    self.listbox.itemconfig(index,bg="yellow")  ## cmj2018Oct1.. selected color.
    self.runCommand2(label)        # and call action here
    return label
  def makeWidgets(self,options,tempWidth):        # or get (ACTIVE)
    sbar = Scrollbar(self)
    list = Listbox(self,relief=SUNKEN,width=tempWidth)
    sbar.config(command=list.yview)      # cross link sbar and list...
    list.config(yscrollcommand=sbar.set)    # move one moves the other
    sbar.pack(side=RIGHT,fill = Y)      # pack first = clip last
    list.pack(side=LEFT, expand=YES,fill=BOTH)  # list clipped first
    pos = 0
    for label in options:        # Add to list box
      list.insert(pos,label)      # Set event handler
      pos += 1
    list.config(selectmode=SINGLE, setgrid = 1)
    list.bind('<Double-1>',self.handleList2)    # double left click
    #list.bind('<Single-1>',self.handleList1)    # single left click
    self.listbox=list        
  def runCommand2(self,selection):
    if(self.__cmjDebug > 5): print(("***FebScollList:: - double left click- You selected:"),(selection))
    self.__recordSelection = selection
    if(self.__cmjDebug > 5): print(("***FebScollList:: self.__recordSelection: %s \n")%(self.__recordSelection))
    return selection
  def fetchList(self):          # Offer an accessor to get the list selected
    if(self.__cmjDebug > 5): print(("***FebScrollList:fetchList: %s \n")%(self.__recordSelection))
    return self.__recordSelection 
##
##
##
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
##
## ===================================================================
##      Local String Entry button class
##      Need to setup here to retain local program flow
class myStringEntry2(Frame):
  def __init__(self,parent):
    Frame.__init__(self,parent)
    #self.pack(expand=YES,fill=BOTH)
    #self.__recordSelection = ""
    self.__cmjDebug = 1
  def StringEntrySetup(self,tempFrame,tempRow,tempCol,labelWidth=10,entryWidth=10,buttonWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...myStringEntry2::StringEntrySetup --------- StringEntrySetup: Enter ----------------- \n")
    self.__LocalFrame = tempFrame
    self.__row = tempRow
    self.__col = tempCol
    self.__labelWidth = labelWidth
    self.__entryWidth = entryWidth
    self.__buttonWidth= buttonWidth
    self.__entyLabel = ''
    self.__buttonText = buttonText
    self.__buttonName = buttonName
    self.__result = 'xxxxaaaa'
    self.__entryLabel = '' 
    self.__label = Label(self.__LocalFrame,width=self.__labelWidth,text=self.__buttonName,anchor=W,justify=LEFT)
    self.__label.grid(row=self.__row,column=self.__col,sticky=W)
    self.__ent = Entry(self.__LocalFrame,width=self.__entryWidth)
    self.__var = StringVar()        # associate string variable with entry field
    self.__ent.config(textvariable=self.__var)
    self.__var.set('')
    self.__ent.grid(row=self.__row,column=self.__col+1,sticky=W)
    self.__ent.focus()
    self.__ent.bind('<Return>',lambda event:self.fetch())
    self.__button = Button(self.__LocalFrame,text=self.__buttonText,width=self.__buttonWidth,anchor=W,justify=LEFT,command=self.StringEntryFetch)
    self.__button.config(bg='#E3E3E3')
    self.__button.grid(row=self.__row,column=self.__col+2,sticky=W)
  def StringEntryFetch(self):
    self.__StringEntry_result = self.__ent.get()
    self.__button.config(bg='yellow')
    print(("...myStringEntry2::self.__StringEntry_result = %s \n") % (self.__StringEntry_result))
    print(("...myStringEntry2::--- StringEntryGet... after Button in getEntry = %s") %(self.__StringEntry_result))
    if(self.__cmjDebug > 3): print("...myStringEntry2::StringEntrySetup --------- StringEntrySetup: Exit ----------------- \n")
    return self.__StringEntry_result
  def fetchResult(self):
    return self.__StringEntry_result
##
##
##
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
##
##
## ===================================================================
## -------------------------------------------------------------------
##   Launch the script here!
## --------------------------------------------------------------------
## ===================================================================
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('--debuglevel',dest='debugLevel',type='int',default=0,help='set debug: 0 (off - default), 1, 2, 3, ... ,10')
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  ##
  options, args = parser.parse_args()
  print(("'__main__': options.database  = %s \n") % (options.database))
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry('1150x550+100+50')  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  print(("__main__ = options.database = %s \n")%(options.database))
  #myMultiForm.setupProductionDatabase()
  #if(options.database == "production"):
  #  myMultiForm.setupProductionDatabase()
  #else:
  #  print("__main__ before setupDevelopmentDatabase \n")
  #  myMultiForm.setupDevelopmentDatabase()
##
  if(options.debugLevel != 0): myMultiForm.setDebugLevel(options.debugLevel)
  myMultiForm.grid()  ## define GUI
  root.mainloop()     ## run the GUI
