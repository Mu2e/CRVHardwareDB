# -*- coding: utf-8 -*-
##
##  File = "checkFeb.py"
##	A python script to read the Feb tables in the hardware database
##	and display the Location and type of a FEB
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2020Jul27
##
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##
##
#!/bin/env python
from Tkinter import *         # get widget class
import Tkinter as tk
from ttk import *             # get tkk widget class (for progess bar)
import tkFileDialog
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
    print("...multiWindow::Class multiWindow... Enter \n") 
    self.__sleepTime = 0.1  ##  time interval between database requests
    self.__maxTries = 10  ## maximum number of attempts to retrieve from database
    self.__defaultBackGroundColor = "gray"
    self.__masterFrame = Frame.__init__(self,parent)
    self.__database_config  = databaseConfig()
    self.setupDevelopmentDatabase()  ## set up communications with database
    self.__cmjDebug = 0 ## default... not debug messages printed out
			##  Limit number of sipms read in for tests.... set negative to read all
    self.__cmjTest = 0	## set this to 1 to look at 10 sipm_id's
    self.__sendToDatabase = 1
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
    print("...multiWindow::Class multiWindow:: before self.__setControlBox() \n")
    self.setControlBox()
    print("...multiWindow::Class multiWindow:: before self.__changeLocationFrame() \n")
    self.changeLocationFrame()  ## call the function to setup the change location controls
    ##
    ##-----------------------------------------------------------------------------
  def setControlBox(self):
    if(self.__cmjDebug > 3): print("...multiWindow::setControlBox ---- Enter ----------------- \n")
##	Display the Control Box  Frame here..
    self.__frame0 = tk.LabelFrame(self.__masterFrame,bg=self.__defaultBackGroundColor)
    self.__frame0.grid(row=0,column=0,columnspan=1,sticky=NSEW)
    self.__frame0.config(width=300)
    self.__frame0.config(text="Database Query ---")
    self.__row = 0
    self.__col = 0
    self.__buttonName = 'Feb Id '
    self.StringEntrySetup(self.__frame0,self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName)
    self.__row+=1
    ##
    self.__buttonName1 = 'Location'
    self.__entry1 = self.StringEntrySetup1(self.__frame0,self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName1)
    self.__row+=1
    ##
    self.__buttonName2 = 'Type'
    self.__entry2 = self.StringEntrySetup2(self.__frame0,self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName2)
    self.__row+=1
    ##	Get All Feb's
    self.__getValues = Button(self.__frame0,text='Get All Febs',command=self.getAllFebFromDatabase,width=self.__buttonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__row,column=self.__col,sticky=W)
    self.__row += 1
    ##	Get All Feb's
    #self.__getValues = Button(self.__frame0,text='Location',command=self.getFebInstitutionFromDatabase,width=self.__buttonWidth,bg='green',fg='black')
    #self.__getValues.grid(row=self.__row,column=self.__col,sticky=W)
    #self.__row += 1
    ##
##	Third Column...
    self.__row = 0
    self.__col = 4
    self.__logo = mu2eLogo(self.__frame0,self.__row,self.__col)     # display Mu2e logo!
    self.__logo.grid(row=self.__row,column=self.__col,rowspan=1,columnspan=4,sticky=NE)
    self.__col = 0
    self.__row += 4
    ##
    self.__sipmGrid_row = self.__row
    self.__sipmGrid_col = self.__col
#         Display the date the script is being run
    self.__row += 2
    self.__col = 1
    self.__date = myDate(self.__frame0,self.__row,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__row,column=self.__col,columnspan=2,sticky=E)
    ##  Add program version
    self.__col = 4
    self.__myVersion = myLabel(self.__frame0,self.__row,self.__col,20)
    self.__myVersion.grid(row=self.__row,column=self.__col,columnspan=2,sticky=E)
    self.__myVersion.setText(Version)
    self.__myVersion.setForgroundColor('blue')
    self.__col = 0
    self.__buttonWidth = 10
    ##  Add progress bar
    #self.__progressbarStyle = Style()
    #self.__progressbarStyle.configure("red.Horizontal.TProgressBar",background="red",forground="black")
    #self.__progressbar = Progressbar(self.__frame0,orient=HORIZONTAL,length=200,maximum=300,variable=self.__progressBarCount,mode='determinate')
    self.__progressbar = Progressbar(self.__frame0,orient=HORIZONTAL,length=200,maximum=self.__progressBarMaximum,variable=self.__progressBarCount,mode='determinate')
    self.__progressbar.grid(row=self.__row,column=0,columnspan=5,sticky=W)
    self.__row += 1
##	Add Control Bar at the bottom...
    self.__quitNow = Quitter(self.__frame0,0,self.__col)
    self.__quitNow.grid(row=self.__row,column=0,sticky=W)
    self.update()
    if(self.__cmjDebug > 3): print("...multiWindow::setControlBox ---- Exit ----------------- \n")
##
## -------------------------------------------------------------------
##	Define a frame that contains the controls for changing the
##      the location of an FEB
  def changeLocationFrame(self,):
    ##	Display the Control Box  Frame here..
    ##  Setup the control box frame
    print("...multiWindow:: --------- changeLocationFrame: Enter ----------------- \n") 
    self.__title = 'Change Feb Location  - '
    self.__frame3 = tk.LabelFrame(self.__masterFrame)      ## define frame3 in the master frame
    self.__locationRow = 0
    self.__locationCol = 0
    self.__frame3.grid(row=0,column=1,columnspan=1,sticky=tk.NW)
    self.__frame3.configure(width=300)
    self.__frame3.configure(text=self.__title)
    self.__frame3 = tk.Frame(self.__frame3,bg=self.__defaultBackGroundColor)
    self.__frame3.grid(row=self.__row,column=0,columnspan=3,sticky=NSEW)
    self.__buttonWidth1 = 20
    ##  Setup the display label
    self.__row = 0
    self.__myLocationLabel = myLabel(self.__frame3)
    self.__myLocationLabel.setWidth(20)
    self.__myLocationLabel.setText('Change Feb Location')
    self.__myLocationLabel.setFont('arial')
    self.__myLocationLabel.setFontType('bold')
    self.__myLocationLabel.setBackgroundColor('lightblue')
    self.__myLocationLabel.makeLabel()
    self.__myLocationLabel.grid(row=self.__row,column=0)
    self.__row += 1
    ##  Setup the set Feb Id button
    self.__StringEntryFebId_result = 'none'
    self.__buttonName = 'Feb Id '
    localButtonWidth = 15
    localLabelWidth = 20
    localEntryWidth = 15
    self.StringEntrySetFebId(self.__frame3,self.__row,self.__locationCol,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__row+=1
    ## Setup the new location button
    self.__StringEntryFebLocation_result = 'none'
    self.__frame3 = tk.Frame(self.__frame3,bg=self.__defaultBackGroundColor)
    self.__frame3.grid(row=self.__row,column=0,columnspan=3,sticky=NSEW)
    self.__buttonName = 'New Feb Location '
    self.StringEntrySetFebLocation(self.__frame3,self.__row,self.__locationCol,localLabelWidth,localEntryWidth,localButtonWidth,buttonName=self.__buttonName)
    self.__row+=1
    ##	Change the Feb location when this button is clicked!
    self.__getValues = Button(self.__frame3,text='Change Feb Location',command=self.changeFebLocation,width=localButtonWidth,bg='green',fg='black')
    self.__getValues.grid(row=self.__row,column=self.__locationCol,sticky=W)
    self.update()
    print("...multiWindow:: --------- changeLocationFrame: Exit ----------------- \n")
## 
##
## -------------------------------------------------------------------
##
  def showAllFeb(self):
    if(self.__cmjDebug > 3): print("...multiWindow::showAllFeb ---------  Enter ----------------- \n")
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
    self.update()
    #
    self.__frame2 = tk.Frame(self.__masterFrame)      ## define frame2 in the master frame3in the master frame
    #self.__frame2.grid(row=1,column=5,columnspan=3,sticky=tk.NW)   ## frame2 contains the module cross section and slide bars
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
    self.update()
    ##
    self.__positionBanner0 = []
    self.__positionBanner1 = []
    self.__positionBanner2 = []
    self.__positionBanner3 = []
    self.__positionBanner4 = []
    self.__positionNumber = 0
    ppp = 0
    for mmm in sorted(self.__febId_dict.keys()):
      if(self.__cmjDebug > 5): print(" self.__febId_dict.keys = %s ppp = %d\n") % (mmm, ppp)
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
    if(self.__cmjDebug > 2) : print("bbox1 =%s bbox2 = %s bbox3 = %s  \n")%(self.__bbox[1],self.__bbox[2],self.__bbox[3])
    self.__width = self.__bbox[2]-self.__bbox[1]
    self.__height = self.__bbox[3]-self.__bbox[1]
    self.__COLS = 5  ## define the number of columns in the grid
    self.__ROWS = 8   ## define the number of rows in the grid
    self.__COLS_DISP = 5  ## define the number of columns to display
    self.__ROWS_DISP = 7   ## define the number of rows to display
    self.__deltaWidth=int((self.__width/self.__COLS)*self.__COLS_DISP)   ## define the scrollable region as canvas with COLS_DISP columns displayed
    self.__deltaHeight=int((self.__height/self.__ROWS)*self.__ROWS_DISP) ## define the scrollable region as canvas with ROWS_DISP rows displayed
    self.__canvas1.configure(scrollregion=self.__bbox,width=self.__deltaWidth,height=self.__deltaHeight) ## actually configure the canvas
    print("...multiWindow::showAllFeb:: before self.__changeLocationFrame() \n")
    if(self.__cmjDebug > 1): print("...multiWindow::showAllFeb ---------  Exit ----------------- \n")     
##
## -------------------------------------------------------------------
##
  def getFebFromDatabase(self,tempFebId):
    if(self.__cmjDebug > 1): print("...multiWindow::getFebFromDatabase... Enter \n")
    self.__singleFebResult = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchCondition='feb_id:eq:'+tempFebId.strip()
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 3):
      print("...multiWindow::getFebFromDatabase... self.__tempFebId = %s \n") % (tempFebId)
      print("...multiWindow::getFebFromDatabase... self.__database = %s \n") % (self.__database)
      print("...multiWindow::getFebFromDatabase... self.__table = %s \n") % (self.__table)
      print("...multiWindow::getFebFromDatabase... self.__fetchCondition = xxx%sxxx \n") % (self.__fetchCondition)
      print("...multiWindow::getFebFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese)
    self.__singleFebResult = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition)
    self.storeFebResults(self.__singleFebResult)
    self.showAllFeb()
    if(self.__cmjDebug > 3): print("...multiWindow::getFebFromDatabase... self.__singleFebResult = %s \n") % (self.__singleFebResult)
    if(self.__cmjDebug > 1): print("...multiWindow::getFebFromDatabase... Exit \n")
##    
## -------------------------------------------------------------------
##
  def getFebInstitutionFromDatabase(self,tempLocation):
    if(self.__cmjDebug > 1): print("...multiWindow::getFebInstitutionFromDatabase... Enter \n")
    self.__allFebResults = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchCondition='location:eq:'+tempLocation.strip()
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 3):
      print("...multiWindow::getFebInstitutionFromDatabase... self.__tempLocation = %s \n") % (tempLocation)
      print("...multiWindow::getFebInstitutionFromDatabase... self.__database = %s \n") % (self.__database)
      print("...multiWindow::getFebInstitutionFromDatabase... self.__table = %s \n") % (self.__table)
      print("...multiWindow::getFebInstitutionFromDatabase... self.__fetchCondition = xxx%sxxx \n") % (self.__fetchCondition)
      print("...multiWindow::getFebInstitutionFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese)
    self.__allFebResults = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjDebug > 3): print("...multiWindow::getFebInstitutionFromDatabase... self.__allFebResults = %s \n") % (self.__allFebResults)
    self.storeFebResults(self.__allFebResults)
    self.showAllFeb()
    if(self.__cmjDebug > 1): print("...multiWindow::getFebInstitutionFromDatabase... Exit \n")
    ## -------------------------------------------------------------------
##
  def getFebTypeFromDatabase(self,tempType):
    if(self.__cmjDebug > 1): print("...multiWindow::getFebTypeFromDatabase... Enter \n")
    self.__allFebResults = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchCondition='feb_type:eq:'+tempType.strip()
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 3):
      print("...multiWindow::getFebTypeFromDatabase... self.__tempType = %s \n") % (tempType)
      print("...multiWindow::getFebTypeFromDatabase... self.__database = %s \n") % (self.__database)
      print("...multiWindow::getFebTypeFromDatabase... self.__table = %s \n") % (self.__table)
      print("...multiWindow::getFebTypeFromDatabase... self.__fetchCondition = xxx%sxxx \n") % (self.__fetchCondition)
      print("...multiWindow::getFebTypeFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese)
    self.__allFebResults = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
    if(self.__cmjDebug > 3): print("...multiWindow::getFebTypeFromDatabase... self.__allFebResults = %s \n") % (self.__allFebResults)
    self.storeFebResults(self.__allFebResults)
    self.showAllFeb()
    if(self.__cmjDebug > 1): print("...multiWindow::getFebTypeFromDatabase... Exit \n")
    ##
## -------------------------------------------------------------------
##
  def getAllFebFromDatabase(self):
    if(self.__cmjDebug > 1): print("...multiWindow::getAllFebFromDatabase... Enter \n")
    self.__allFebResults = []
    self.__getFebValues = DataQuery(self.__queryUrl)
    self.__table = "front_end_boards"
    self.__fetchThese='feb_id,feb_type,location,comments,firmware_version'
    if(self.__cmjDebug > 3):
      print("...multiWindow::getAllFebFromDatabase... self.__database = %s \n") % (self.__database)
      print("...multiWindow::getAllFebFromDatabase... self.__table = %s \n") % (self.__table)
      print("...multiWindow::getAllFebFromDatabase... self.__fetchThese = %s \n") % (self.__fetchThese)
    self.__allFebResults = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,None)
    if(self.__cmjDebug > 3): print("...multiWindow::getAllFebFromDatabase... self.__allFebResults = %s \n") % (self.__allFebResults)
    self.storeFebResults(self.__allFebResults)
    self.showAllFeb()
    if(self.__cmjDebug > 1): print("...multiWindow::getAllFebFromDatabase... Exit \n")
     ##
## -------------------------------------------------------------------
##
  def storeFebResults(self,tempFebResults):
    if(self.__cmjDebug > 0): print("...multiWindow::storeFebResults... Enter \n")
    for nn in tempFebResults:
      self.__item=[]
      self.__item = nn.rsplit(',')
      if(len(self.__item) > 1): 
	if(self.__cmjDebug > 5): print("self.__item = %s") % (self.__item)
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
    if(self.__cmjDebug > 5):    #self.__singleFebResult = self.__getFebValues.query(self.__database,self.__table,self.__fetchThese,self.__fetchCondition,'-'+self.__fetchThese)
      for mm in self.__febId_dict.keys():
	print("...multiWindow::storeFebResults... self.__febId_dict[%s] = %s self.__febType_dict[%s] = %s self.__febLocation_dict[%s] = %s self.__febComment_dict[%s] =  %s self.__febFirmwareRelease_dict[%s] =  %s") % (mm,self.__febId_dict[mm],mm,self.__febType_dict[mm],mm,self.__febLocation_dict[mm],mm,self.__febComment_dict[mm],mm,self.__febComment_dict[mm],mm,self.__febFirmwareRelease_dict[mm])
    if(self.__cmjDebug > 0): print("...multiWindow::storeFebResults... Exit \n")
##
## -------------------------------------------------------------------
##  
##	Change the FEB location
##
  def changeFebLocation(self):
    if(self.__cmjDebug > 1): print("...multiWindow::changeFebLocation --------- changeFebLocation: Enter ----------------- \n")
    self.__group = "Electronic Tables"
    self.__frontEndBoardsTable = "front_end_boards"
    self.__frontEndBoardLocation = {}
    self.__frontEndBoardLocation['feb_id'] = self.__StringEntryFebId_result
    self.__frontEndBoardLocation['location']=self.__StringEntryFebLocation_result
    print("...multiWindow::storeFebResults... self.__writeUrl =%s \n") % (self.__writeUrl)
    print("...multiWindow::storeFebResults... self.__writePassword = %s \n") % (self.__writePassword) 
    if(self.__cmjDebug > -1): 
	print ("...multiWindow::storeFebResults... changeFebLocation: self.__StringEntryFebId_result = %s, self.__StringEntryFebLocation_result = %s \n") % (self.__StringEntryFebId_result,self.__StringEntryFebLocation_result)
    if self.__sendToDatabase != 0:
      print "send Change Feb Location to database!"
      self.__myDataLoader1 = DataLoader(self.__writePassword,self.__writeUrl,self.__group,self.__frontEndBoardsTable)
      if(self.__cmjDebug > -1): print("...multiWindow::storeFebResults... sendFrontEndBoardsToDatabase: update")
      self.__myDataLoader1.addRow(self.__frontEndBoardLocation,'update')	##cmj2019May23... update existing line
      (self.__retVal,self.__code,self.__text) = self.__myDataLoader1.send()	## send it to the data base!
      print "self.__text = %s" % self.__text
      sleep(self.__sleepTime)
      if self.__retVal:							## sucess!  data sent to database
	  print "...multiWindow::changeFebLocation... Electronics FEB "+self.__StringEntryFebId_result+"  Transmission Success!!!"
	  print self.__text
      elif self.__password == '':
	  print('...multiWindow::changeFebLocation: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')()
      else:
	  print "...multiWindow::changeFebLocation:  Electronics FEB "+self.__StringEntryFebId_result+"  Transmission: Failed!!!"
	  print self.__code
	  print self.__text 
    if(self.__cmjDebug > 1): print("...multiWindow::changeFebLocation --------- changeFebLocation: Enter ----------------- \n")
    return 0  ## success
#######################################################################################
####################################################################################### 
##
## -------------------------------------------------------------------
##	Make querries to data base
  def setupDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__group = "Electronic Tables"
    self.__whichDatabase = 'development'
    print("...multiWindow::getFromDevelopmentDatabase... get from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
    self.__writeUrl = self.__database_config.getWriteUrl()
    self.__writePassword = self.__database_config.getElectronicsKey()
##
## -------------------------------------------------------------------
##	Make querries to data base
  def setupProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__group = "Electronic Tables"
    self.__whichDatabase = 'production'
    print("...multiWindow::getFromProductionDatabase... get from production database \n")
    self.__url = self.__database_config.getProductionQueryUrl()
    self.__writeUrl = self.__database_config.getProductionWriteUrl()
    self.__writePassword = self.__database_config.getElectronicsProductionKey()
##
## -------------------------------------------------------------------
  def setDebugLevel(self,tempDebugLevel):
    self.__cmjDebug = tempDebugLevel
    print("...multiWindow::getFromProductionDatabase... Set Debug Level to = %s \n") % (self.__cmjDebug)   
    ##
## ------------------------------------------------------------------
##
## ===================================================================
##	Local String Entry button
##	Need to setup here to retain local program flow
  def StringEntrySetup(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup --------- StringEntrySetup: Enter ----------------- \n")
    self.__LocalFrame = tempFrame
    self.__StringEntry_row = tempRow
    self.__StringEntry_col = tempCol
    self.__StringEntry_labelWidth = self.__gridWidth
    self.__StringEntry_entryWidth = self.__gridWidth
    self.__StringEntry_buttonWidth= self.__gridWidth
    self.__StringEntry_entyLabel = ''
    self.__StringEntry_buttonText = 'Enter'
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
    #self.getFebFromDatabase(self.__StringEntry_result)
    print("self.__StringEntry_result = %s \n") % (self.__StringEntry_result)
    self.getFebFromDatabase(self.__StringEntry_result)
    if (self.__buttonName=='Type'): self.getFebTypeFromDatabase(self.__StringEntry_result)
    print("--- StringEntryGet... after Button in getEntry = %s") %(self.__StringEntry_result)
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup --------- StringEntrySetup: Exit ----------------- \n")
    return self.__StringEntry_result
##
## ===================================================================
##	Local String Entry button
##	Need to setup here to retain local program flow
  def StringEntrySetup1(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup1 --------- StringEntrySetup1: Enter ----------------- \n")
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
    if(self.__cmjDebug > 4): print("self.__StringEntry1_result = %s \n") % (self.__StringEntry1_result)
    if (self.__buttonName1=='Location') : self.getFebInstitutionFromDatabase(self.__StringEntry1_result)
    if(self.__cmjDebug > 4): print("--- StringEntryGet1... after Button in getEntry = %s  Button Name = %s") %(self.__StringEntry1_result,self.__buttonName1)
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup1 --------- StringEntrySetup1: Exit ----------------- \n")
    return self.__StringEntry1_result
  ##
## ===================================================================
##	Local String Entry button
##	Need to setup here to retain local program flow
  def StringEntrySetup2(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup2 --------- StringEntrySetup2: Enter ----------------- \n")
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
    #self.getFebFromDatabase(self.__StringEntry2_result)
    print("self.__StringEntry2_result = %s \n") % (self.__StringEntry2_result)
    if (self.__buttonName2=='Type'): self.getFebTypeFromDatabase(self.__StringEntry2_result)
    print("--- StringEntryGet2... after Button in getEntry = %s") %(self.__StringEntry2_result)
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetup2 --------- StringEntrySetup2: Enter ----------------- \n")
    return self.__StringEntry2_result
  
##  
##  
## ===================================================================
##	Local String Entry button
##	Need to setup here to retain local program flow
##	Get the FebId whose location you want to change
  def StringEntrySetFebId(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebId --------- StringEntrySetFebId: Enter ----------------- \n")
    self.__LocalFrame2 = tempFrame
    self.__StringEntryFebId_row = tempRow
    self.__StringEntryFebId_col = tempCol
    self.__StringEntryFebId_labelWidth = self.__gridWidth
    self.__StringEntryFebId_entryWidth = self.__gridWidth
    self.__StringEntryFebId_buttonWidth= self.__gridWidth
    self.__StringEntryFebId_entyLabel = ''
    self.__StringEntryFebId_buttonText = 'Enter'
    self.__StringEntryFebId_buttonName = buttonName
    self.__StringEntryFebId_result = 'xxxxaaaa'
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
    self.__buttonFebId.config(bg='yellow')
    #self.getFebFromDatabase(self.__StringEntryFebId_result)
    print("self.__StringEntryFebId_result = %s \n") % (self.__StringEntryFebId_result)
    #if (self.__buttonName=='Feb Id'): self.__febIdChangeLocation
    print("--- StringEntrySetFebId... after Button in StringEntrySetFebId = %s") %(self.__StringEntryFebId_result)
    if(self.__cmjDebug > 1): print("...multiWindow::StringEntrySetFebId --------- StringEntrySetFebId: Exit ----------------- \n")
    return self.__StringEntryFebId_result  
## ===================================================================
##	Local String Entry button
##	Need to setup here to retain local program flow
##	Get the FebId whose location you want to change
  def StringEntrySetFebLocation(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebLocation --------- StringEntrySetFebLocation: Enter ----------------- \n")
    self.__LocalFrame2 = tempFrame
    self.__StringEntryFebLocation_row = tempRow
    self.__StringEntryFebLocation_col = tempCol
    self.__StringEntryFebLocation_labelWidth = self.__gridWidth
    self.__StringEntryFebLocation_entryWidth = self.__gridWidth
    self.__StringEntryFebLocation_buttonWidth= self.__gridWidth
    self.__StringEntryFebLocation_entyLabel = ''
    self.__StringEntryFebLocation_buttonText = 'Enter'
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
    #self.getFebFromDatabase(self.__StringEntryFebLocation_result)
    print("self.__StringEntryFebLocation_result = %s \n") % (self.__StringEntryFebLocation_result)
    #if (self.__buttonName=='Location'): self.__febIdChangeLocation = self.__StringEntryFebLocation_result
    print("--- StringEntrySetFebLocation... after Button in StringEntrySetFebLocation = %s") %(self.__StringEntryFebLocation_result)
    if(self.__cmjDebug > 3): print("...multiWindow::StringEntrySetFebLocation --------- StringEntrySetFebLocation: Exit ----------------- \n")
    return self.__StringEntryFebLocation_result 
  
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
  print("'__main__': options.database  = %s \n") % (options.database)
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry('1150x550+100+50')  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.database == "production"):
    myMultiForm.setupProductionDatabase()
  else:
    myMultiForm.setupDevelopmentDatabase()
##
  if(options.debugLevel != 0): myMultiForm.setDebugLevel(options.debugLevel)
  myMultiForm.grid()  ## define GUI
  root.mainloop()     ## run the GUI