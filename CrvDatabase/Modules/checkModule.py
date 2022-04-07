# -*- coding: utf-8 -*-
##
##	A python script to read the Sipm tables in the hardware database
##	and display the overall Sipm status for a selected pack number
##
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2019Jan30
##  Modified by cmj2016Jun24.Sipm.py.. Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##	Modified by cmj2019Feb28... Change the default database to production.
##   Modified by cmj2020Jul14... Add Progress bar
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
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
from Modules import *
#import SipmMeasurements
##
ProgramName = "checkModule.py"
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
    self.__sleepTime = 0.1  ##  time interval between database requests
    self.__maxTries = 10  ## maximum number of attempts to retrieve from database
    self.__defaultBackGroundColor = "gray"
    self.__masterFrame = Frame.__init__(self,parent)
    self.__database_config  = databaseConfig()
    self.setupDevelopmentDatabase()  ## set up communications with database
    self.__cmjDebug = 0 ## default... not debug messages printed out
			##  Limit number of sipms read in for tests.... set negative to read all
    self.__cmjTest = 0	## set this to 1 to look at 10 sipm_id's
    self.__progressBarCount = tk.DoubleVar()  ## for progress bar
    self.__progressBarCount.set(0)            ## for progress bar
##	Define Output Log file... remove this later
    self.__mySaveIt = saveResult()
    self.__mySaveIt.setOutputFileName('checkModule')
    self.__mySaveIt.openFile()
##
    self.__sipmIdName = []
    self.__sipmStatus = []
    self.__sipmIdName_dict =  {}
    self.__sipmStatus_dict = {}
    ## set up geometry for GUI
    self.__gridWidth = int(8)
    self.__labelWidth = self.__gridWidth
    self.__entryWidth = self.__gridWidth
    self.__buttonWidth = self.__gridWidth
    #self.__packNumber = 0
    self.__moduleDiCounterId_dict = defaultdict(dict)  	## Nested dictionary to hold the diCounerId at
							## position and layer in a module 
							## (keys: [layer][position]
							## layer ranges from top to bottom: layer1, layer2, layer3, layer4
							## position 0, 1, 2, 3, 4, 5, 6, 7
    self.__moduleCmb_top_dict = defaultdict(dict)  	## Nested dictionary to hold the top Cmb_id at
							## position and layer in a module 
							## (keys: [layer][position]
							## layer ranges from top to bottom: layer1, layer2, layer3, layer4
							## position 0, 1, 2, 3, 4, 5, 6, 7
    self.__moduleCmb_bot_dict = defaultdict(dict)  	## Nested dictionary to hold the bottom Cmb_id at
							## position and layer in a module 
							## (keys: [layer][position]
							## layer ranges from top to bottom: layer1, layer2, layer3, layer4
							## position 0, 1, 2, 3, 4, 5, 6, 7 
    self.__moduleSmb_top_dict = defaultdict(dict)  	## Nested dictionary to hold the top Smb_id at
							## position and layer in a module 
							## (keys: [layer][position]
							## layer ranges from top to bottom: layer1, layer2, layer3, layer4
							## position 0, 1, 2, 3, 4, 5, 6, 7
    self.__moduleSmb_bot_dict = defaultdict(dict)  	## Nested dictionary to hold the bottom Smb_id at
							## position and layer in a module 
							## (keys: [layer][position]
							## layer ranges from top to bottom: layer1, layer2, layer3, layer4
							## position 0, 1, 2, 3, 4, 5, 6, 7
    self.__moduleSipmSignOff_dict = {} ## Dictionary to hold the Sipm Signoff status: key SipmId
    self.__nestedDirectory = generalUtilities()
    self.__moduleSipmId_top_nest_dict = self.__nestedDirectory.nestedDict()  ## A nested dictionary to hold a dictionary that holds the
								## current the SipmId at the top some location on the di-counter
								## the keys are [layer][[position][sipmPosition]]	
								## position 0, 1, 2, 3, 4, 5, 6, 7
    self.__moduleSipmId_bot_nest_dict = self.__nestedDirectory.nestedDict()  ## A nested dictionary to hold a dictionary that holds the
								## current the SipmId at the bottom some location on the di-counter
								## the keys are [layer][[position][sipmPosition]]	
								## position 0, 1, 2, 3, 4, 5, 6, 7
    self.__sipmSignoffStatus_color='black'
##
##	Display the Control Box  Frame here..
    self.__frame0 = tk.Frame(self.__masterFrame,bg=self.__defaultBackGroundColor)
    self.__frame0.grid(row=0,column=0,columnspan=3,sticky=NSEW)
##
    self.__row = 0
    self.__col = 0
    self.__checkBoxChoices_dict = {"top":1,"bottom":0}
    #self.__myChoice = "top"
    ## Check boxes.... for top and bottom
    self.__ModuleSideselection = "top"  ## default
    self.myRowCheck(self.__frame0,self.__ModuleSideselection,self.__row,self.__col)
    self.initializeCheckList(self.__checkBoxChoices_dict)
    self.setText("Module Side Selection")
    self.makeChecks()
    #self.tempSelection = self.__checkBox.getCheckBoxSelection()
    self.__row += 3
    self.__col = 0
    if(self.__cmjDebug > 0) : print("self.__ModuleSideselection = %s \n") % (self.__ModuleSideselection)
    self.__buttonName = 'Module '
    self.StringEntrySetup(self.__frame0,self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName)
##	Third Column...
    self.__row = 0
    self.__col = 6
    self.__logo = mu2eLogo(self.__frame0,self.__row,self.__col)     # display Mu2e logo!
    self.__logo.grid(row=self.__row,column=self.__col,rowspan=4,columnspan=4,sticky=NE)
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
    self.__col = 5
    self.__myVersion = myLabel(self.__frame0,self.__row,self.__col,20)
    self.__myVersion.grid(row=self.__row,column=self.__col,columnspan=5,sticky=E)
    self.__myVersion.setText(Version)
    self.__myVersion.setForgroundColor('blue')
    self.__col = 0
    self.__buttonWidth = 10
    ##  Add progress bar
    #self.__progressbarStyle = Style()
    #self.__progressbarStyle.configure("red.Horizontal.TProgressBar",background="red",forground="black")
    #self.__progressbar = Progressbar(self.__frame0,orient=HORIZONTAL,length=200,maximum=300,variable=self.__progressBarCount,mode='determinate')
    self.__progressbar = Progressbar(self.__frame0,orient=HORIZONTAL,length=200,maximum=1000,variable=self.__progressBarCount,mode='determinate')
    self.__progressbar.grid(row=self.__row,column=0,columnspan=5,sticky=W)
    self.__row += 1
##	Add Control Bar at the bottom...
    self.__quitNow = Quitter(self.__frame0,0,self.__col)
    self.__quitNow.grid(row=self.__row,column=0,sticky=W)
##  
## -------------------------------------------------------------------
##  Define a frame to hold a graphic of the module side
##  This function is called from the checkbox function:
##  	self.changeTestState()
  def modulePicture(self):
    self.__frame3 = tk.Frame(self.__masterFrame,bg=self.__defaultBackGroundColor)
    self.__frame3.grid(row=0,column=4,columnspan=4,sticky=tk.NSEW)
    self.__frame3.configure(width=2000)
    text=self.__titleModulePicture = 'CRV Module - '+self.__StringEntry_result+' --- '+self.__ModuleSideselection+' Side'
    if(self.__ModuleSideselection == 'top') : self.__crvPicture=PhotoImage(file='../graphics/CrvSideA-Med2-2020.gif')
    elif(self.__ModuleSideselection == 'bottom') : self.__crvPicture=PhotoImage(file='../graphics/CrvSideB-Med2-2020.gif')
    self.__canvas_frame3 = tk.Canvas(self.__frame3,bg="gray")
    self.__imageScale_canvas = 1.0
    self.__canvas_frame3.config(width=self.__crvPicture.width()*self.__imageScale_canvas,height=self.__crvPicture.height()*self.__imageScale_canvas)
    self.__canvas_frame3.create_image(2,2,image=self.__crvPicture,anchor=NW)
    self.__canvas_frame3.grid(row=self.__row,column=self.__col)
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
##
## -------------------------------------------------------------------
  def setDebugLevel(self,tempDebugLevel):
    self.__cmjDebug = tempDebugLevel
    print("...multiWindow::getFromProductionDatabase... Set Debug Level to = %s \n") % (self.__cmjDebug)
##
## ------------------------------------------------------------------
##  Returns a color string for a Sipm Signoff status
  def getSipmSignoffStatus(self,tempStatus):
    self.__sipmSignoffStatus_color = 'white'
    if(tempStatus == 'green') : self.__sipmSignoffStatus_color = 'green'
    elif(tempStatus == 'yellow'): self.__sipmSignoffStatus_color = 'yellow'
    elif(tempStatus == 'red'): self.__sipmSignoffStatus_color = 'red'
    elif(tempStatus == 'purple'): self.__sipmSignoffStatus_color = 'purple'
    return self.__sipmSignoffStatus_color
##
## -----------------------------------------------------------------
  def setStatusGrid2(self,tempSide):
    self.__localSide = tempSide
    if(self.__cmjDebug > 1) : print("setStatusGrid2... self.__localSide %s \n") % (self.__localSide)
    ## define the frame that holds the legend on the left hand side.
    self.__frame1 = tk.LabelFrame(self.__masterFrame) ## define frame to contain legend to the left
    self.__frame1.grid(row=1,column=0,sticky=tk.NSEW)
    self.__frame1.configure(width=15,text=" ")
    self.__frame1.configure(text='Legend')
    self.__smbTitle=[]
    self.__cmbTitle=[]
    self.__dicounterTitle = []
    self.__sipmTitle = []
    self.__row += 1
    self.__tempRow = self.__row
    self.__borderWidth = 1
    self.__borderStyle = 'solid'
    self.__defaultBackGroundColor = "gray"
    self.__legendWidth = 20
          #
    self.__positionText = 'Position'
    self.__positionTitle=(myLabel(self.__frame1,self.__tempRow,0,int(self.__legendWidth)))
    self.__positionTitle.setText(self.__positionText)
    self.__positionTitle.setBorder(self.__borderWidth,self.__borderStyle)
    self.__positionTitle.setBackgroundColor(self.__defaultBackGroundColor)
    self.__positionTitle.setFontSize('12')
    self.__positionTitle.grid(row=self.__tempRow,column=0)
    self.__tempRow += 1
    for nn in range(0,4):
      #
      self.__smbText = 'Layer '+str(nn+1)+' Smb'
      self.__smbTitle.append(myLabel(self.__frame1,self.__tempRow,0,int(self.__legendWidth)))
      self.__smbTitle[nn].setText(self.__smbText)
      self.__smbTitle[nn].setBorder(self.__borderWidth,self.__borderStyle)
      self.__smbTitle[nn].setBackgroundColor(self.__defaultBackGroundColor)
      self.__smbTitle[nn].setFontSize('12')
      self.__smbTitle[nn].grid(row=self.__tempRow,column=0)
      #
      self.__cmbText = '        Cmb'
      self.__cmbTitle.append(myLabel(self.__frame1,self.__tempRow+1,0,int(self.__legendWidth)))
      self.__cmbTitle[nn].setText(self.__cmbText)
      self.__cmbTitle[nn].setBorder(self.__borderWidth,self.__borderStyle)
      self.__cmbTitle[nn].setBackgroundColor(self.__defaultBackGroundColor)
      self.__cmbTitle[nn].setFontSize('12')
      self.__cmbTitle[nn].grid(row=self.__tempRow+1,column=0)
      #
      self.__dicounterText = '        DiCounter'
      self.__dicounterTitle.append(myLabel(self.__frame1,self.__tempRow+2,0,int(self.__legendWidth)))
      self.__dicounterTitle[nn].setText(self.__dicounterText)
      self.__dicounterTitle[nn].setBorder(self.__borderWidth,self.__borderStyle)
      self.__dicounterTitle[nn].setBackgroundColor(self.__defaultBackGroundColor)
      self.__dicounterTitle[nn].setFontSize('12')
      self.__dicounterTitle[nn].grid(row=self.__tempRow+2,column=0)
      #
      self.__sipmText = '        Sipm'
      self.__sipmTitle.append(myLabel(self.__frame1,self.__tempRow+3,0,int(self.__legendWidth)))
      self.__sipmTitle[nn].setText(self.__sipmText)
      self.__sipmTitle[nn].setBorder(self.__borderWidth,self.__borderStyle)
      self.__sipmTitle[nn].setBackgroundColor(self.__defaultBackGroundColor)
      self.__sipmTitle[nn].setFontSize('12')
      self.__sipmTitle[nn].grid(row=self.__tempRow+3,column=0)
      self.__tempRow +=4
      xx = self.__progressBarCount.get()  ## get current count value for progress bar
      self.__progressBarCount.set(xx+10)  ## increment that value
      self.update() ## update the progress bar...
    ##
    ##  -- Define the frame with the module cross section of the module and slide bars
    self.__sideAB = ' -- Side A --'
    if(self.__ModuleSideselection == 'bottom') : self.__sideAB = ' -- Side B--'
    self.__title = 'CRV Module - '+self.__StringEntry_result+' --- '+self.__ModuleSideselection+' Side'+self.__sideAB
    self.__frame2 = tk.LabelFrame(self.__masterFrame)      ## define frame2 in the master frame3in the master frame
    self.__frame2.grid(row=1,column=1,columnspan=5,sticky=tk.NW)   ## frame2 constains the module cross section and slide bars
    self.__frame2.configure(text=self.__title)
    self.__canvas1 = tk.Canvas(self.__frame2,bg="gray")
    self.__canvas1.grid(row=0,column=0)
    self.__canvas1.configure(width=4000,height=520)
    ## define the vertical slide bar 
    self.__vScrollBar = tk.Scrollbar(self.__frame2,orient=tk.VERTICAL,command=self.__canvas1.yview)
    self.__vScrollBar.grid(row=0,column=1,sticky=NS)
    self.__canvas1.configure(yscrollcommand=self.__vScrollBar.set)
    ## define the horizontal slide bar
    self.__hScrollBar = tk.Scrollbar(self.__frame2,orient=tk.HORIZONTAL,command=self.__canvas1.xview)
    self.__hScrollBar.grid(row=1,column=0,sticky=EW)
    self.__canvas1.configure(xscrollcommand=self.__hScrollBar.set)
    ##  Define the grid to contain the module cross section, with the slide bars around it.
    self.__moduleGridFrame=tk.LabelFrame(self.__canvas1,bg="gray",bd=2)
    self.__moduleGridFrame.configure(width=3900,height=500)
    self.__row0 = self.__sipmGrid_row  ## row 0... build row by incrementind column
    self.__col0 = self.__sipmGrid_col
    self.__borderWidth = 1
    self.__borderStyle = 'solid'
    self.__smbColor = 'yellow'
    self.__cmbColor = "orange"
    self.__diCounterColor = "lightblue"
    self.__sipmColor = "pink"
    self.__missingColor = "white"
    self.__absorberColor = "tan"
    self.__reflectorColor = "silver"
    self.__layer_list = ['layer1','layer2','layer3','layer4']
    self.__position_list_top = ['0','1','2','3','4','5','6','7']
    self.__position_list_bot = ['7','6','5','4','3','2','1','0']
    self.__sipm_position_list_top = ['a1','a2','a3','a4']
    self.__sipm_position_list_bot = ['b1','b2','b3','b4']
    self.__cmb = defaultdict(dict)  	## Nested dictionary to hold the bottom cmb_squares at
					## position and layer in a module 
					## (keys: [layer][position]
    self.__smb = defaultdict(dict)  	## Nested dictionary to hold the bottom cmb_squares at
					## position and layer in a module 
					## (keys: [layer][position]
    self.__di = defaultdict(dict)  	## Nested dictionary to hold the bottom cmb_squares at
					## position and layer in a module 
					## (keys: [layer][position]
    self.__sipm_nest_dict = self.__nestedDirectory.nestedDict()  ## A nested dictionary to hold a dictionary that holds the
								## current the Sipm at some location on the di-counter
								## the keys are [layer][[position][sipmPosition]]	
								## position 0, 1, 2, 3, 4, 5, 6, 7
    self.__tempColumn = self.__col0
    self.__tempRow = 2
    ##  Print position banner
    self.__positionBanner = []
    self.__positionNumber = 0
    for ppp in range(0,8):
      if(self.__localSide == 'top') : self.__tempPosition = int(self.__position_list_top[ppp])+1
      elif(self.__localSide == 'bottom') : self.__tempPosition = int(self.__position_list_bot[ppp])+1
      self.__positionBanner.append(myLabel(self.__moduleGridFrame,self.__tempRow,self.__tempColumn,int(4*self.__gridWidth)))
      self.__positionBanner[ppp].setText(str(self.__tempPosition))
      self.__positionBanner[ppp].setBorder(self.__borderWidth,self.__borderStyle)
      self.__positionBanner[ppp].setBackgroundColor(self.__defaultBackGroundColor)
      self.__positionBanner[ppp].setFontSize('12')
      self.__positionBanner[ppp].grid(row=self.__tempRow,column=self.__tempColumn,columnspan=4)
      self.__tempColumn += 4
    self.__tempColumn = self.__col0
    self.__tempRow += 1
    for mm in range(0,4):
      xx = self.__progressBarCount.get()  ## get current count for progress bar
      self.__progressBarCount.set(xx+10)  ## increment the count
      self.update()  ## update the progress bar...
      mmm = self.__layer_list[mm]
      for nn in range(0,8):
	if(self.__localSide == 'top') : nnn = self.__position_list_top[nn]
	elif(self.__localSide == 'bottom') : nnn = self.__position_list_bot[nn]
	
	##-------------+++
	##   --- smb ---
	self.__smb[mmm][nnn] = myLabel(self.__moduleGridFrame,self.__tempRow+1,self.__tempColumn,int(4*self.__gridWidth))
	if(self.__localSide == 'top') : 
	  try:
	    if(self.__moduleSmb_top_dict[mmm][nnn].find('REFLECTOR') != -1):
	      self.__smb[mmm][nnn].setText('REFLECTOR')
	      self.__smb[mmm][nnn].setBackgroundColor(self.__reflectorColor)
	    elif (self.__moduleSmb_top_dict[mmm][nnn].find('ABSORBER') != -1):
	      self.__smb[mmm][nnn].setText('ABSORBER')
	      self.__smb[mmm][nnn].setBackgroundColor(self.__absorberColor)
	    else:
	      self.__smb[mmm][nnn].setText(self.__moduleSmb_top_dict[mmm][nnn])
	      self.__smb[mmm][nnn].setBackgroundColor(self.__smbColor)
	  except:
	    self.__smb[mmm][nnn].setText('N/A')
	    self.__smb[mmm][nnn].setBackgroundColor(self.__missingColor)
	elif(self.__localSide == 'bottom') : 
	  try:
	    tempSmb = str(self.__moduleSmb_bot_dict[mmm][nnn])
	    if(tempSmb.find('REFLECTOR') != -1) :
	      self.__smb[mmm][nnn].setText('REFLECTOR')
	      self.__smb[mmm][nnn].setBackgroundColor(self.__reflectorColor)
	    elif (tempSmb.find('ABSORBER') != -1):
	      self.__smb[mmm][nnn].setText('ABSORBER')
	      self.__smb[mmm][nnn].setBackgroundColor(self.__absorberColor)
	    else:
	      self.__smb[mmm][nnn].setText(tempSmb)
	      self.__smb[mmm][nnn].setBackgroundColor(self.__smbColor)
	  except:
	    self.__smb[mmm][nnn].setText('N/A')
	    self.__smb[mmm][nnn].setBackgroundColor(self.__missingColor)
	self.__smb[mmm][nnn].setBorder(self.__borderWidth,self.__borderStyle)
	self.__smb[mmm][nnn].grid(row=self.__tempRow,column=self.__tempColumn,columnspan=4)
	##-------------+++
	
	##    ---- cmb ----
	self.__cmb[mmm][nnn] = myLabel(self.__moduleGridFrame,self.__tempRow,self.__tempColumn,int(4*self.__gridWidth))
	if(self.__localSide == 'top') : 
	  try:
	    if(self.__moduleCmb_top_dict[mmm][nnn].find('REFLECTOR') != -1):
	      self.__cmb[mmm][nnn].setText('REFLECTOR')
	      self.__cmb[mmm][nnn].setBackgroundColor(self.__reflectorColor)
	    elif(self.__moduleCmb_top_dict[mmm][nnn].find('ABSORBER') != -1):
	      self.__cmb[mmm][nnn].setText('ABSORBER')
	      self.__cmb[mmm][nnn].setBackgroundColor(self.__absorberColor)
	    else:
	      self.__cmb[mmm][nnn].setText(self.__moduleCmb_top_dict[mmm][nnn])
	      self.__cmb[mmm][nnn].setBackgroundColor(self.__cmbColor)
	  except:
	    self.__cmb[mmm][nnn].setText('N/A')
	    self.__cmb[mmm][nnn].setBackgroundColor(self.__missingColor)
	elif(self.__localSide == 'bottom') : 
	  try:
	    if(self.__moduleCmb_bot_dict[mmm][nnn].find('REFLECTOR') != -1):
	     self.__cmb[mmm][nnn].setText('REFLECTOR')
	     self.__cmb[mmm][nnn].setBackgroundColor(self.__reflectorColor) 
	    elif(self.__moduleCmb_bot_dict[mmm][nnn].find('ABSORBER') != -1):
	     self.__cmb[mmm][nnn].setText('ABSORBER')
	     self.__cmb[mmm][nnn].setBackgroundColor(self.__absorberColor)
	    else:
	      self.__cmb[mmm][nnn].setText(self.__moduleCmb_bot_dict[mmm][nnn])
	      self.__cmb[mmm][nnn].setBackgroundColor(self.__cmbColor)
	  except:
	    self.__cmb[mmm][nnn].setText('N/A')
	    self.__cmb[mmm][nnn].setBackgroundColor(self.__missingColor)
	self.__cmb[mmm][nnn].setBorder(self.__borderWidth,self.__borderStyle)
	self.__cmb[mmm][nnn].setFontSize('12')
	self.__cmb[mmm][nnn].grid(row=self.__tempRow+1,column=self.__tempColumn,columnspan=4)

	##  --- diCounters ---
	self.__di[mmm][nnn] = myLabel(self.__moduleGridFrame,self.__tempRow+2,self.__tempColumn,int(4*self.__gridWidth))
	try:
	  self.__di[mmm][nnn].setText(self.__moduleDiCounterId_dict[mmm][nnn])
	  self.__di[mmm][nnn].setBackgroundColor(self.__diCounterColor)
	except:
	  self.__di[mmm][nnn].setText('N/A')
	  self.__di[mmm][nnn].setBackgroundColor(self.__missingColor)
	self.__di[mmm][nnn].setBorder(self.__borderWidth,self.__borderStyle)
	self.__di[mmm][nnn].grid(row=self.__tempRow+2,column=self.__tempColumn,columnspan=4)
	##  -- Sipms ---
	self.__sipmColumn = int(0)
	for pp in range(0,4):
	  if(self.__localSide == 'top') : ppp = self.__sipm_position_list_top[pp]
	  elif(self.__localSide == 'bottom') : ppp = self.__sipm_position_list_bot[pp]
	  self.__sipm_nest_dict[mmm][nnn][ppp] = myLabel(self.__moduleGridFrame,self.__tempRow+3,int(self.__tempColumn)+int(self.__sipmColumn),self.__gridWidth)
	  if(self.__localSide == 'top') : 
	    tempSipmId=str(self.__moduleSipmId_top_nest_dict[mmm][nnn][ppp])
	    if(tempSipmId.find('N/A') != -1):
	      self.__sipm_nest_dict[mmm][nnn][ppp].setText('N/A')
	    elif (tempSipmId.find('defaultdict') != -1):
	      self.__sipm_nest_dict[mmm][nnn][ppp].setText('N/A')
	    else:
	      self.__sipm_nest_dict[mmm][nnn][ppp].setText(self.__moduleSipmId_top_nest_dict[mmm][nnn][ppp])
	  elif(self.__localSide == 'bottom') :
	    tempSipmId = str(self.__moduleSipmId_bot_nest_dict[mmm][nnn][ppp])
	    if (tempSipmId.find('N/A') != -1):
	      self.__sipm_nest_dict[mmm][nnn][ppp].setText('N/A')
	    elif (tempSipmId.find('defaultdict') !=-1 ):
	      self.__sipm_nest_dict[mmm][nnn][ppp].setText('N/A')
	    else:
	      self.__sipm_nest_dict[mmm][nnn][ppp].setText(self.__moduleSipmId_bot_nest_dict[mmm][nnn][ppp])
	  self.__sipm_nest_dict[mmm][nnn][ppp].setBorder(self.__borderWidth,self.__borderStyle)
	  self.__tempSipmId2 = '#N/A'
	  if(self.__localSide == 'top') : self.__tempSipmId2 = self.__moduleSipmId_top_nest_dict[mmm][nnn][ppp]
	  if(self.__localSide == 'bottom') : self.__tempSipmId2 = self.__moduleSipmId_bot_nest_dict[mmm][nnn][ppp]
	  if(self.__tempSipmId2[0] == 'A') : self.__tempColor = self.__moduleSipmSignOff_dict[self.__tempSipmId2]
	  else : self.__tempColor = 'white'
	  self.__sipm_nest_dict[mmm][nnn][ppp].setBackgroundColor(self.getSipmSignoffStatus(self.__tempColor))
	  self.__sipm_nest_dict[mmm][nnn][ppp].setFontSize('6')
	  self.__sipm_nest_dict[mmm][nnn][ppp].grid(row=self.__tempRow+3,column=int(self.__tempColumn)+int(self.__sipmColumn))
	  self.__sipmColumn += 1
	##
	self.__tempColumn += 4
      self.__tempColumn = self.__col0
      self.__tempRow += 4
    self.__canvas1.create_window((0,0),window=self.__moduleGridFrame,anchor=tk.NW)  ## make window to hold the canvas
    self.__moduleGridFrame.update_idletasks() ## Make box information (below) available 
    self.__bbox = self.__canvas1.bbox(tk.ALL) ## Get the dimensions of the bounding box holding the canvas
    if(self.__cmjDebug > 2) : print("bbox1 =%s bbox2 = %s bbox3 = %s  \n")%(self.__bbox[1],self.__bbox[2],self.__bbox[3])
    self.__width = self.__bbox[2]-self.__bbox[1]
    self.__height = self.__bbox[3]-self.__bbox[1]
    self.__COLS = 36  ## define the number of columns in the grid
    self.__ROWS = 8   ## define the number of rows in the grid
    self.__COLS_DISP = 16  ## define the number of columns to display
    self.__ROWS_DISP = 8   ## define the number of rows to display
    self.__deltaWidth=int((self.__width/self.__COLS)*self.__COLS_DISP)   ## define the scrollable region as canvas with COLS_DISP columns displayed
    self.__deltaHeight=int((self.__height/self.__ROWS)*self.__ROWS_DISP) ## define the scrollable region as canvas with ROWS_DISP rows displayed
    self.__canvas1.configure(scrollregion=self.__bbox,width=self.__deltaWidth,height=self.__deltaHeight) ## actually configur the canvas
##
## ------------------------------------------------------------------
##
## ===================================================================
##	Local String Entry button
##	Need to setup here to retain local program flow
  def StringEntrySetup(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
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
    self.getDiCountersInModule(self.__StringEntry_result)
    print("--- StringEntryGet... after Button in getEntry = %s") %(self.__StringEntry_result)
    return self.__StringEntry_result
## -----------------------------------------------------------------------------------
##    A class to add a row of  check boxes
  def myRowCheck(self,tempFrame, localSaveResults,myRow=0,myCol=0):
    self.__localFrame = tempFrame
    self.__checkTestSet = {} 
    self.__save_it = localSaveResults
    self.__checkText = 'Check Boxes'
    self.__row = myRow
    self.__col = myCol
  def initializeCheckList(self,tempEntry):
    self.__selection = ""
    self.__checkTestSet = tempEntry
    self.__tempVar = {}
    if (self.__cmjDebug > 8):
      for temp in sorted(self.__checkTestSet.keys()):
	print ('--- myRowCheck::initializeCheckList... keys = %s selfcheckTestSet = %s') % (temp,self.__checkTestSet[temp])
  def makeChecks(self):
    self.__label = Label(self.__localFrame,text=self.__checkText,anchor=W,justify=LEFT)
    self.__label.grid(row=self.__row,column=self.__col,sticky=W,columnspan=len(self.__checkTestSet)-1)
    if (self.__cmjDebug > 8):
      print '--- myRowCheck::initializeCheckList... self.__row = %d self.__col = %d' % (self.__row,self.__col)
    self.__row =+ 2
    for self.__key in sorted(self.__checkTestSet.keys()):
      self.__var  = IntVar()
      self.__var.set('0')             # initialize all boxes unchecked
      self.__checkbutton = Checkbutton(self.__localFrame,text=self.__key,variable=self.__var,command=self.__checkTestSet[self.__key])
      self.__checkbutton.grid(row=self.__row,column=self.__col,sticky=W)
      self.__col += 1
      if (self.__cmjDebug > 8):
	print '--- myRowCheck::initializeCheckList... self.__var.get() = %s ' % self.__var.get()
      self.__tempVar[self.__key] = self.__var
    self.__button1 = Button(self.__localFrame,text='Enter',command=(lambda :self.changeTestState(self.__key)))
    self.__button1.config(bg='#E3E3E3')
    self.__button1.grid(row=self.__row,column=self.__col,sticky=W)
  def setText(self,tempText):             # Set the check box group name
    self.__checkText=tempText
##        A method to change the state of the check buttons....
##             that is record which check button is selected or "checked"
  def changeTestState(self,tempKey):
    if (self.__cmjDebug > 6):
      print '--- myRowCheck::changeTestState... self.__tempVar.. Before Change'
      for nn in sorted(self.__tempVar.keys()):
	print ('--- myRowCheck::changeTestState... keys = %s  tempVar = %s') % (nn,self.__tempVar[nn].get())
      for nn in sorted(self.__checkTestSet.keys()):
	print ('--- myRowCheck::changeTestState... self.__checkTestSet.. keys = %s Value = %s')%(nn,self.__checkTestSet[nn])
	## Load checkbox values into a dictionary whose values are integers
    for mmm in sorted(self.__checkTestSet.keys()):
      self.__checkTestSet[mmm] = self.__tempVar[mmm].get()
    if (self.__cmjDebug > 7): 
      print '**************** self.__tempVar[mmm].get() %s ' % self.__tempVar[mmm]
    if (self.__cmjDebug > 7):
      print '--- myRowCheck::changeTestState... self.__checkTestSet after change'
      for mm in sorted(self.__checkTestSet.keys()):
	print '--- myRowCheck::changeTestState... self.__checkTestSet:  keys = %s Value = %s'%(mm,self.__checkTestSet[mm])
    self.__button1.config(bg='yellow')
    for mmm in sorted(self.__checkTestSet.keys()):
      if (self.__cmjDebug > 7):print("mmm = %s self.__checkTestSet[mmm]= %s ") %(mmm,self.__checkTestSet[mmm])
      if (self.__checkTestSet[mmm] == 1) :
	self.__ModuleSideselection = mmm
	break
    self.modulePicture()
    print("self.__ModuleSideselection = %s \n") % (self.__ModuleSideselection)
    return
     ##  Allow the user to get the new selection.
  def getCheckBoxSelection(self):
    return self.__selection
  def reset(self):                   # a method to reset the checkboxes for next counter
      if (self.__cmjDebug > 7): print '--- myRowCheck::reset... self.__vars  '  
      for mm in sorted(self.__checkTestSet.keys()):
	self.__checkTestSet[mm] = 0
      for nn in sorted(self.__tempVar.keys()):
	self.__tempVar[nn].set('0')        # reset the integer variable
	self.__button1.config(bg='#E3E3E3')
               
## ===================================================================   
##
## -------------------------------------------------------------------
##	Make querries to data base for Sipm Status
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
## --------------------------------------------------------------------
## --------------------------------------------------------------------
##	Make querries to get all sipm batches to data base
  def getDiCountersInModule(self,moduleNumber):
    if(self.__cmjDebug > 0): print("... multiWindow::getDiCountersInModule\n") 
    self.__getDiCounterValues = DataQuery(self.__queryUrl)  ## first table for diCounters
    self.__getCmbSmbValues = DataQuery(self.__queryUrl)     ##  second table for Cmb
    self.__getSipmValues = DataQuery(self.__queryUrl)  ##  Third table for Sipms
    self.__localDataBaseLine1_list = []
    self.__localDataBaseLine2_list = []
    self.__localDataBaseLine3_list = []
    self.__localDiCounterValues_list = []
    self.__localDiCounterLayer_list = []
    self.__localDiCounterPosition_list = []
    self.__table1 = 'di_counters'
    self.__fetchThese1 = "di_counter_id,module_layer,layer_position"
    self.__fetchCondition1 = 'module_id:eq:'+'crvmod-'+moduleNumber  ## works!!!
    #
    self.__table2 = 'counter_mother_boards'
    self.__fetchThese2 = "di_counter_id,cmb_id,smb_id,di_counter_end"
    self.__numberReturned2 = 0
    ## 
    self.__table3 = 'sipms'
    self.__fetchThese3 = 'cmb_id,cmb_position,sipm_id,sipm_signoff'
    for n in range(0,self.__maxTries):
      #print (".... getDiCountersInModule: Query Try: n = %s \n") % (n)
      try: 
	self.__localDataBaseLine1_list = self.__getDiCounterValues.query(self.__database,self.__table1,self.__fetchThese1,self.__fetchCondition1,'-'+self.__fetchThese1)
	sleep(self.__sleepTime)  ## give time for database to answer
	break ## exit loop
      except:
	print(".... getDiCountersInModule: ****************** Database Query Error ***********************\n")
	print (".... getDiCountersInModule: self.__localDataBaseLine1_list = self.__getDiCounterValues.query \n")
	print (".... getDiCountersInModule: self.__table1                = %s \n") % (self.__table1)
	print (".... getDiCountersInModule: self.__fetchThese1           = %s \n") % (self.__fetchThese1)
	print (".... getDiCountersInModule: self.__fetchCondition1       = %s \n") % (self.__fetchCondition1)
	print (".... getDiCountersInModule: self.__localDataBaseLine1_list = %s \n") % (self.__localDataBaseLine1_list)
	if(n == self.__maxTries-1) :print(".... getDiCountersInModule: ***** Database Read Error Error ********** n > self.__maxTries = %s \n") % (self.__maxTries)
    if(self.__cmjDebug > 3): 
	print (".... getDiCountersInModule: ================================================ \n") 
	print (".... getDiCountersInModule: self.__table1                = %s \n") % (self.__table1)
	print (".... getDiCountersInModule: self.__fetchThese1           = %s \n") % (self.__fetchThese1)
	print (".... getDiCountersInModule: self.__fetchCondition1       = %s \n") % (self.__fetchCondition1)
	print (".... getDiCountersInModule: self.__localDataBaseLine1_list = %s \n") % (self.__localDataBaseLine1_list)
    xx = self.__progressBarCount.get()  ## get the current count for the progress bar
    self.__progressBarCount.set(xx+10)  ## increment the count
    self.update() ## update the progress bar
    self.__numberOfLines = len(self.__localDataBaseLine1_list)
    self.__diCounter = 0
    for self.__mmm in sorted(self.__localDataBaseLine1_list):  ## loop through the diCounters in a module
      if(self.__cmjDebug > 3) : print(".... getDiCountersInModule:xxxx self.__mmm = xxx%sxxx") % (self.__mmm)
      if(self.__mmm == '') : continue
      self.__tempElement = []
      self.__tempElement = self.__mmm.rsplit(',')
      self.__tempDiCounter = self.__tempElement[0]
      self.__tempLayer = self.__tempElement[1]
      self.__tempPosition = self.__tempElement[2]
      self.__moduleDiCounterId_dict[self.__tempLayer][self.__tempPosition] = self.__tempElement[0]
      self.__fetchCondition2 = 'di_counter_id:eq:'+self.__tempDiCounter  ## works!!!
      for n in range(0,self.__maxTries):
	try:
	  self.__localDataBaseLine2_list = self.__getCmbSmbValues.query(self.__database,self.__table2,self.__fetchThese2,self.__fetchCondition2,'-'+self.__fetchThese2)
	  sleep(self.__sleepTime)  ## give time for database to answer)
	  break  ## exit loop
	except:
	  print(".... getDiCountersInModule: ****************** Database Query Error ***********************\n")
	  print(".... getDiCountersInModule: self.__localDataBaseLine2_list = self.__getCmbSmbValues.query\n")
	  print (".... getDiCountersInModule: self.__table                = %s \n") % (self.__table2)
	  print (".... getDiCountersInModule: self.__fetchThese2           = %s \n") % (self.__fetchThese2)
	  print (".... getDiCountersInModule: self.__fetchCondition2       = %s \n") % (self.__fetchCondition2)
	  print (".... getDiCountersInModule: self.__tempLayer = %s self.__tempPosition = %s \n") % (self.__tempLayer,self.__tempPosition)
	  print (".... getDiCountersInModule: self.__localDataBaseLine2_list = %s \n") % (self.__localDataBaseLine2_list)
	  print (".... getDiCountersInModule: self__tempDiCounter = %s\n") % (self.__tempDiCounter)
	  if(n == self.__maxTries-1) :print(".... getDiCountersInModule: ***** Database Read Error Error ********** n > self.__maxTries = %s \n") % (self.__maxTries)
      xx = self.__progressBarCount.get()  ## get the current value for the progress bar
      self.__progressBarCount.set(xx+10)  ## increment the counter for the progress bar
      self.update() ## update the progress bar
      if(self.__cmjDebug > 3):
	print (".... getDiCountersInModule: --------------------------------------------------- \n")
	print (".... getDiCountersInModule: self.__table                = %s \n") % (self.__table2)
	print (".... getDiCountersInModule: self.__fetchThese2           = %s \n") % (self.__fetchThese2)
	print (".... getDiCountersInModule: self.__fetchCondition2       = %s \n") % (self.__fetchCondition2)
	print (".... getDiCountersInModule: self.__tempLayer = %s self.__tempPosition = %s \n") % (self.__tempLayer,self.__tempPosition)
	print (".... getDiCountersInModule: self.__localDataBaseLine2_list = %s \n") % (self.__localDataBaseLine2_list)
      for self.__nnn in sorted(self.__localDataBaseLine2_list):
	self.__tempElement2 = []
	if(self.__nnn == '') : continue
	self.__tempElement2 = self.__nnn.rsplit(',')
	self.__tempCmbId = self.__tempElement2[1][7:len(self.__tempElement2[1])]
	self.__tempSmbId = self.__tempElement2[2][7:len(self.__tempElement2[1])]
	self.__tempDiCounterEnd = self.__tempElement2[3]
	if(self.__tempDiCounterEnd == 'top'):
	  self.__moduleCmb_top_dict[self.__tempLayer][self.__tempPosition] = self.__tempCmbId
	  self.__moduleSmb_top_dict[self.__tempLayer][self.__tempPosition] = self.__tempSmbId
	  self.__fetchCondition3 = 'cmb_id:eq:CrvCmb-'+self.__tempCmbId
	  for n in range(0,self.__maxTries):
	    try:
	      self.__localDataBaseLine3_list = self.__getCmbSmbValues.query(self.__database,self.__table3,self.__fetchThese3,self.__fetchCondition3,'-'+self.__fetchThese3)
	      sleep(self.__sleepTime)  ## give time for database to answer
	      break
	    except:
	      print (".... getDiCountersInModule: ****************** Database Query Error *********************** \n")
	      print (".... getDiCountersInModule:self.__localDataBaseLine3_list = self.__getCmbSmbValues.query -- Side A -- \n") 
	      print (".... getDiCountersInModule: self.__table                = %s \n") % (self.__table3)
	      print (".... getDiCountersInModule: self.__fetchThese3           = %s \n") % (self.__fetchThese3)
	      print (".... getDiCountersInModule: self.__fetchCondition3       = %s \n") % (self.__fetchCondition3)
	      print (".... getDiCountersInModule: self.__localDataBaseLine3_list = %s \n") % (self.__localDataBaseLine3_list)
	      print (".... getDiCountersInModule: self.__tempLayer = %s self.__tempPosition = %s \n") % (self.__tempLayer,self.__tempPosition)
	      print (".... getDiCountersInModule: self.__tempCmbId = %s \n") % (self.__tempCmbId)
	      print (".... getDiCountersInModule: self.__tempSmbId = %s \n") % (self.__tempSmbId)
	      print (".... getDiCountersInModule: self__tempDiCounter = %s\n") % (self.__tempDiCounter)
	      if(n == self.__maxTries-1) :print(".... getDiCountersInModule: ***** Database Read Error Error ********** n > self.__maxTries = %s \n") % (self.__maxTries)
	  xx = self.__progressBarCount.get()  ## get the current value of the progress bar counter  
	  self.__progressBarCount.set(xx+10)  ## increment the progress bar counter
	  self.update()  ## update the progress bar
	  self.__tempElement3 = []
	  for self.__ppp in sorted(self.__localDataBaseLine3_list):  ## loop over the Sipms in a diCounter
	    if(self.__ppp == '') : continue
	    self.__tempElement3 = self.__ppp.rsplit(',')
	    self.__tempSipmPosition = self.__tempElement3[1]
	    self.__tempSipmId = self.__tempElement3[2]
	    self.__tempSipmSignoff = self.__tempElement3[3]
	    self.__moduleSipmSignOff_dict[self.__tempSipmId[20:len(self.__tempSipmId)]] = self.__tempSipmSignoff
	    if(self.__cmjDebug > 3): 
	      print (".... getDiCountersInModule: ............................................  \n")
	      print (".... getDiCountersInModule: self.__table                = %s \n") % (self.__table3)
	      print (".... getDiCountersInModule: self.__fetchThese3           = %s \n") % (self.__fetchThese3)
	      print (".... getDiCountersInModule: self.__fetchCondition3       = %s \n") % (self.__fetchCondition3)
	      print (".... getDiCountersInModule: self.__localDataBaseLine3_list = %s \n") % (self.__localDataBaseLine3_list)
	      print (".... getDiCountersInModule: self.__tempLayer = %s self.__tempPosition = %s \n") % (self.__tempLayer,self.__tempPosition)
	      print (".... getDiCountersInModule: self.__tempElement3                = %s \n") % (self.__tempElement3)
	      print (".... getDiCountersInModule: self.__tempCmbId = %s \n") % (self.__tempCmbId)
	      print (".... getDiCountersInModule: self.__tempSmbId = %s \n") % (self.__tempSmbId)
	    self.__moduleSipmId_top_nest_dict[self.__tempLayer][self.__tempPosition][self.__tempSipmPosition] = self.__tempSipmId[20:len(self.__tempSipmId)]
	elif(self.__tempDiCounterEnd == 'bottom'):
	  self.__moduleCmb_bot_dict[self.__tempLayer][self.__tempPosition] = self.__tempCmbId
	  self.__moduleSmb_bot_dict[self.__tempLayer][self.__tempPosition] = self.__tempSmbId
	  self.__fetchCondition3 = 'cmb_id:eq:CrvCmb-'+self.__tempCmbId
	  for n in range(0,self.__maxTries):
	    try:
	      self.__localDataBaseLine3_list = self.__getCmbSmbValues.query(self.__database,self.__table3,self.__fetchThese3,self.__fetchCondition3,'-'+self.__fetchThese3)
	      sleep(self.__sleepTime)  ## give time for database to answer
	      break
	    except:
	      print (".... getDiCountersInModule: ****************** Database Query Error *********************** \n")
	      print (".... getDiCountersInModule: self.__localDataBaseLine3_list = self.__getCmbSmbValues.query -- Side B -- \n")
	      print (".... getDiCountersInModule: self.__table                = %s \n") % (self.__table3)
	      print (".... getDiCountersInModule: self.__fetchThese3           = %s \n") % (self.__fetchThese3)
	      print (".... getDiCountersInModule: self.__fetchCondition3       = %s \n") % (self.__fetchCondition3)
	      print (".... getDiCountersInModule: self.__localDataBaseLine3_list = %s \n") % (self.__localDataBaseLine3_list)
	      print (".... getDiCountersInModule: self.__tempLayer = %s self.__tempPosition = %s \n") % (self.__tempLayer,self.__tempPosition)
	      print (".... getDiCountersInModule: self__tempDiCounter = %s\n") % (self.__tempDiCounter)
	      print (".... getDiCountersInModule: self.__tempCmbId = %s \n") % (self.__tempCmbId)
	      print (".... getDiCountersInModule: self.__tempSmbId = %s \n") % (self.__tempSmbId)
	      if(n == self.__maxTries-1) :print(".... getDiCountersInModule: ***** Database Read Error Error ********** n > self.__maxTries = %s \n") % (self.__maxTries)
	  xx = self.__progressBarCount.get()  ## get the current value of the progress bar counter
	  self.__progressBarCount.set(xx+10)  ## increment the progres bar
	  self.update()  ## update the progresss bar
	  self.__tempElement3 = []
	  for self.__ppp in sorted(self.__localDataBaseLine3_list):  ## loop over the Sipms in a diCounter
	    if(self.__ppp == '') : continue
	    self.__tempElement3 = self.__ppp.rsplit(',')
	    self.__tempSipmPosition = self.__tempElement3[1]
	    self.__tempSipmId = self.__tempElement3[2]
	    self.__tempSipmSignoff = self.__tempElement3[3]
	    self.__moduleSipmSignOff_dict[self.__tempSipmId[20:len(self.__tempSipmId)]] = self.__tempSipmSignoff
	    if(self.__cmjDebug > 3): 
	      print (".... getDiCountersInModule: ............................................  \n")
	      print (".... getDiCountersInModule: self.__table                = %s \n") % (self.__table3)
	      print (".... getDiCountersInModule: self.__fetchThese3           = %s \n") % (self.__fetchThese3)
	      print (".... getDiCountersInModule: self.__fetchCondition3       = %s \n") % (self.__fetchCondition3)
	      print (".... getDiCountersInModule: self.__localDataBaseLine3_list = %s \n") % (self.__localDataBaseLine3_list)
	      print (".... getDiCountersInModule: self.__tempLayer = %s self.__tempPosition = %s \n") % (self.__tempLayer,self.__tempPosition)
	      print (".... getDiCountersInModule: self.__tempElement3                = %s \n") % (self.__tempElement3)
	      print (".... getDiCountersInModule: self.__tempCmbId = %s \n") % (self.__tempCmbId)
	      print (".... getDiCountersInModule: self.__tempSmbId = %s \n") % (self.__tempSmbId)
	    self.__moduleSipmId_bot_nest_dict[self.__tempLayer][self.__tempPosition][self.__tempSipmPosition] = self.__tempSipmId[20:len(self.__tempSipmId)]
	    if (self.__cmjDebug > 3) : print(".... getDiCountersInModule:  self.__moduleSipmId_bot_nest_dict[%s][%s][%s] = %s") % (self.__tempLayer,self.__tempPosition,self.__tempSipmPosition,self.__moduleSipmId_bot_nest_dict[self.__tempLayer][self.__tempPosition][self.__tempSipmPosition])
    if(self.__cmjDebug > 2) : print(".... getDiCountersInModule:  self.__ModuleSideselection = %s \n") % (self.__ModuleSideselection)
    self.setStatusGrid2(self.__ModuleSideselection)  ## Diplay the grid 
    return self.__localDiCounterValues_list
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
  root.geometry('1200x500+100+50')  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.database == "production"):
    myMultiForm.setupProductionDatabase()
  else:
    myMultiForm.setupDevelopmentDatabase()
##
  if(options.debugLevel != 0): myMultiForm.setDebugLevel(options.debugLevel)
  myMultiForm.grid()  ## define GUI
  root.mainloop()     ## run the GUI