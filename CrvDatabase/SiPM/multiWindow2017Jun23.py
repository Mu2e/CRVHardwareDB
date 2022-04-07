# -*- coding: utf-8 -*-
## File = "multiWindow2016Jun27.py"
## Derived from File = "multiWindow2016Jun27.py"
## Derived from File = "multiWindow2016Jun24.py"
## Derived from File = "multiWindow2016jan06.py"
## Derived from File = "multiWindow2016jan06.py"
## Derived from File = "multiWindow2016jan04.py"
## Derived from File = "multiFrame2015Jul22.py"
##
#!/usr/bin/env python
## 
##	A python script to bring up multiple frames
##
##		To run this script:
##	           python TestSiPM_DataBase2015Jun18.py
##  Modified by cmj 2016Jan12 to use different directories for support modules...
##		These are located in zip files in the various subdirectories....
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj 2016Jun27... Add SiPM Type field....
##  Modified by cmj 2017Jun23... Use new crvUtilities Library that has scrollList
##  Modified by cmj2018Oct4... Change to hdbClient_v2_0
##  Modified by cmj2018Oct4.... Change the crvUtilities to contain version of cmjGuiLibGrid2018Oct1 that adds
##				yellow highlight to selected scrolled list items
##  Modified by cmj2018Oct9.... Change to hdbClient_v2_2
##  Modified by cmj2019Jan24... Allow multiple selection of files for either the tests or loading to the 
##				database.
##  Modified by cmj2020Jul13... Use crvUtilitieszip
##  Modified by cmj2020Jun16... Use cmjGuiLibGrid2019Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021May11... replace Dataloader3.zip with Dataloader.zip
##
##
from tkinter import *         # get widget class
import sys
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2021May11
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2018Oct2 add highlight to scrolled list
sys.path.append("SiPMlib/SiPMlib.zip")
from DataLoader import *
from cmjGuiLibGrid import *       ## 2020Aug03
import time

Version = "version2021.05.12"

##
## -------------------------------------------------------------
## 	A class to set up the main window to drive the
##	python GUI
##
class multiWindow(Frame):
    def __init__(self,parent=NONE, myRow = 0, myCol = 0):
      Frame.__init__(self,parent)
      self.__row = 0
      self.__col = 0
      self.__myInstructions = myScrolledText(self)
      self.__myInstructions.setTextBoxWidth(50)
#      self.__myInstructions.setTextColor('red','blue')
#      self.__myInstructions.setTextFont('helvetica',10,'bold')
      self.__myInstructions.makeWidgets()
      self.__myInstructions.setText('','Instructions/InstructionsForMultiWindows2015Jul28.txt')
      self.__myInstructions.grid(row=self.__row,column=self.__col,columnspan=2)
##	Third Column...
      self.__row = 0
      self.__col += 2
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
      self.__buttonWidth = 23

      self.__button1 = myIndependentWindow(self,self.__row,self.__col)
      self.__button1.setButtonName('1) Purchase Orders')
      self.__button1.setButtonWidth(self.__buttonWidth)
      self.__button1.setButtonColor('lightblue')
      self.__button1.setAction('sipmPurchaseOrder2016Jun24')
      self.__button1.makeButton()
      self.__button1.grid(row=self.__row,column=self.__col,sticky=W)
      self.__col = 0
      self.__row += 1

      self.__button2 = myIndependentWindow(self,self.__row,self.__col)
      self.__button2.setButtonName('2) Recieved Batches')
      self.__button2.setButtonWidth(self.__buttonWidth)##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##
      self.__button2.setButtonColor('lightblue')
      self.__button2.setAction('sipmRecievedBatches2016Jun24')
      self.__button2.makeButton()
      self.__button2.grid(row=self.__row,column=self.__col,sticky=W)
      self.__col = 0
      self.__row += 1


      self.__button3 = myIndependentWindow(self,self.__row,self.__col)
      self.__button3.setButtonName('3) SiPM Id Input')
      self.__button3.setButtonWidth(self.__buttonWidth)
      self.__button3.setButtonColor('lightblue')
      self.__button3.setAction('sipm2016Jun24')
      self.__button3.makeButton()
      self.__button3.grid(row=self.__row,column=self.__col,sticky=W)
      self.__col += 1
      self.__row = 2

      self.__button4 = myIndependentWindow(self,self.__row,self.__col)
      self.__button4.setButtonName('4) SiPM Vendor Measurements')
      self.__button4.setButtonWidth(self.__buttonWidth)
      self.__button4.setButtonColor('lightblue')
      self.__button4.setAction('sipmVendorMeasurements2016Jun24')
      self.__button4.makeButton()
      self.__button4.grid(row=self.__row,column=self.__col,sticky=W)
      self.__col = 1
      self.__row += 1

      self.__button5 = myIndependentWindow(self,self.__row,self.__col)
      self.__button5.setButtonName('5) SiPM Local Measurments')
      self.__button5.setButtonWidth(self.__buttonWidth)
      self.__button5.setButtonColor('lightblue')
      self.__button5.setAction('sipmLocalMeasurements2016Jun24')
      self.__button5.makeButton()
      self.__button5.grid(row=self.__row,column=self.__col,sticky=W)
      self.__col += 1

      self.__row += 2
      self.__quitNow = Quitter(self,0,self.__col)
      self.__quitNow.grid(row=self.__row,column=0,sticky=W)
      
##
##
## --------------------------------------------------------------------
if __name__ == '__main__':
     root = Tk()              # or Toplevel()
     bannerText = 'Mu2e:: MultiWindow'
     root.title(bannerText)  
     root.geometry("+100+500")  ## set offset of primary window....
     myMultiForm = multiWindow(root,0,0)
     myMultiForm.grid()
     root.mainloop()
      
