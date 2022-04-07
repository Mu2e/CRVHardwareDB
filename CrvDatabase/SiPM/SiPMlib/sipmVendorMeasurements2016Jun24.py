# -*- coding: utf-8 -*-
##  File = "sipmVendorMeasurements2016Jun24.py"
##  Derived from File = "sipmVendorMeasurements2016May09.py"
##  Derived from File = "sipmVendorMeasurements2016Jan12.py"
##  Derived from File = "sipmVendorMeasurements2016Jan6.py"
##  Derived from File = "sipmVendorMeasurements2015Aug5.py"
##  Derived from File = "TestSiPM_DataBase2015Jun18.py"
##
##      Use the grid geometry containter rather than the pack geometry container
##
##  written by cmj 2015Jun18 --- 
##            Set up the GUI interface to recieve SiPMs and
##            record their paramters... add entry to database
##            when the tables are ready.
##  Modified by cmj 2016Jan12 to use different directories for support modules...
##            These are located in zip files in the various subdirectories....
##  Modified by cmj 2016May9... Add the recording temperature.
##                                                            "pre_production" or "production"
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##                        for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2020Jul13.. Use cmjGuiLibGrid2019Jan30
##                        yellow highlight to selected scrolled list items
##  Modified by cmj2020Jul13.... Change to hdbClient_v2_2
##  Modified by cmj2020Aug03... cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2020Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021May14... replace tabs with spaces for block statements to convert to python
##
##
#!/usr/bin/env python
##
##   This is a simple python script to test
##   writting a line to the Fermilab Data 
##   Base.
##        Written by Merrill Jenkins
##             Department of Physics
##             University of South Alabma
##             Mobile, AL 36688
##   Uses the Client class developed by the Fermilab
##   data base group (Steven White, etc.)
##
##            To run this script:
##                 python TestSiPM_DataBase2015Jun18.py
##  To change libraries:
##       rm SiPMlib.zip
##       zip -r SiPMlib.zip *.py
##
import sys
from tkinter import *         # get widget class
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")
from cmjGuiLibGrid import * ## cmj2020Aug03
from DataLoader import DataLoader
from databaseConfig import *
import time

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################     
#######################################################################################
#######################################################################################
##
##      This class is the main class that sets up the GUI
##      window amd checks all supplied widgets.  The User enters the various quantities:
##      string values, integer values, float values, check boxex and radio boxes
##
##     This class contains the functions needed to build the
##        strings to send the data to the database.  This class uses the 
##        client class (DataLoader) developed by the Fermilab data base group 
##        (Steven White, etc.).  All widgets are usd to construct values to be 
##        sent to the database

cmjDiag = 0        # turn off diagnostic print statements
sendDataBase = 1   # set to zero for test purposes (i.e. do not write to data base)
Version = "version2021.05.14"

##
##      This class sets up the GUI window 
##      It sets up the buttons to exit the GUI, 
##      or enter the results into the database
##      or to clear the form...
##class packSipmVendorWindow(Frame):
class packWindow(Frame):
      def __init__(self,parent=NONE,myRow=0,myCol=0):
          Frame.__init__(self,parent)
        self.__database_config = databaseConfig()
        if sendDataBase == 0:
            print("---------- IN TEST MODE.... DATA WILL NOT BE SENT TO DATABASE!!!!!!!!!!!!! ")
        if (cmjDiag >= allDiag or cmjDiag == 100): print('XXXX packSipmWindow::__main__  Enter driving method ')
        self.__labelWidth = 20
        self.__entryWidth = 20
        self.__buttonWidth = 5
        self.__password = self.__database_config.getSipmKey()
####  First Column Entries
        self.__mySaveIt = saveResult()
        self.__mySaveIt.setOutputFileName('sipm_vendorParameters')
        self.__mySaveIt.openFile()
        self.__strName = []
        self.__sCount = 0
        self.__row = myRow
        self.__col = myCol
#                   Enter Worker Name
        self.__strName.append("Worker")
        self.__workerStr = myStringEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__workerStr.setEntryText(self.__strName[self.__sCount])
        self.__sCount += 1
        self.__workerStr.setLabelWidth(self.__labelWidth)
        self.__workerStr.setEntryWidth(self.__entryWidth)
        self.__workerStr.setButtonWidth(self.__buttonWidth)
        self.__workerStr.makeEntry()
        self.__workerStr.grid(row=self.__row,column=self.__col,stick=W)
        self.__mySaveIt.saveOperator(self.__workerStr.getVar())
        self.__row += 1
#                   Enter Institution... replace with Listbox...
        self.__strName.append("Institution")
        self.__InstitutionStr = myStringEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__InstitutionStr.setEntryText(self.__strName[self.__sCount])
        self.__sCount += 1
        self.__InstitutionStr.setLabelWidth(self.__labelWidth)
        self.__InstitutionStr.setEntryWidth(self.__entryWidth)
        self.__InstitutionStr.setButtonWidth(self.__buttonWidth)
        self.__InstitutionStr.makeEntry()
        self.__InstitutionStr.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
#                   Enter Workstation... replace with Listbox...
        self.__strName.append("Workstation")
        self.__InstitutionStr = myStringEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__InstitutionStr.setEntryText(self.__strName[self.__sCount])
        self.__sCount += 1
        self.__InstitutionStr.setLabelWidth(self.__labelWidth)
        self.__InstitutionStr.setEntryWidth(self.__entryWidth)
        self.__InstitutionStr.setButtonWidth(self.__buttonWidth)
        self.__InstitutionStr.makeEntry()
        self.__InstitutionStr.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
#                   Enter Batch Number... 
        self.__sipmIdNumberStr = myStringEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__strName.append("SiPM ID Number")
        self.__sipmIdNumberStr.setEntryText(self.__strName[self.__sCount])
        self.__sCount += 1
        self.__sipmIdNumberStr.setLabelWidth(self.__labelWidth)
        self.__sipmIdNumberStr.setEntryWidth(self.__entryWidth)
        self.__sipmIdNumberStr.setButtonWidth(self.__buttonWidth)
        self.__sipmIdNumberStr.makeEntry()
        self.__sipmIdNumberStr.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1

##      Vendor supplied parameter
        self.__labelWidth = 40
        self.__vendorLabel = myLabel(self,self.__row,self.__col)
        self.__vendorLabel.setWidth(self.__labelWidth)
        self.__vendorLabel.setFontAll('Arial',10,'bold')
        self.__vendorLabel.setText("Vendor Supplied Parameters")
        self.__vendorLabel.makeLabel()
        self.__vendorLabel.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
        self.__labelWidth = 20
        self.__entryWidth = 20
        self.__buttonWidth = 5
        self.__fltName = []
        self.__fCount = 0
##            Enter vendor supplied bias voltage
        self.__vendBiasVolt = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Vendor Bias Voltage")
        self.__vendBiasVolt.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__vendBiasVolt.setLabelWidth(self.__labelWidth)
        self.__vendBiasVolt.setEntryWidth(self.__entryWidth)
        self.__vendBiasVolt.setButtonWidth(self.__buttonWidth)
        self.__vendBiasVolt.makeEntry()
        self.__vendBiasVolt.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##            Enter vendor supplied dark count
        self.__vendDarkCount = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Vendor Dark Count")
        self.__vendDarkCount.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__vendDarkCount.setLabelWidth(self.__labelWidth)
        self.__vendDarkCount.setEntryWidth(self.__entryWidth)
        self.__vendDarkCount.setButtonWidth(self.__buttonWidth)
        self.__vendDarkCount.makeEntry()
        self.__vendDarkCount.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##            Enter vendor supplied gain
        self.__vendGain = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Vendor Gain")
        self.__vendGain.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__vendGain.setLabelWidth(self.__labelWidth)
        self.__vendGain.setEntryWidth(self.__entryWidth)
        self.__vendGain.setButtonWidth(self.__buttonWidth)
        self.__vendGain.makeEntry()
        self.__vendGain.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1

#### 2016May9... add temperature
##            Enter vendor supplied gain
        self.__vendTemp = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Vendor Temperature")
        self.__vendTemp.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__vendTemp.setLabelWidth(self.__labelWidth)
        self.__vendTemp.setEntryWidth(self.__entryWidth)
        self.__vendTemp.setButtonWidth(self.__buttonWidth)
        self.__vendTemp.makeEntry()
        self.__vendTemp.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1

#### Second Column entries
        self.__col += 1
        self.__oldRow = self.__row
        self.__row = 0
        self.__myInstructions = myScrolledText(self)
        self.__myInstructions.setTextBoxWidth(40)
        self.__myInstructions.makeWidgets()
        self.__myInstructions.setText('','Instructions/InstructionsForSipmVendorValues2015Jul30.txt')
        self.__myInstructions.grid(row=self.__row,column=self.__col,columnspan=2,rowspan=5)
        self.__col += 1
#### Thrid Column entries
        self.__row = 0
        self.__col += 1
        self.__logo = mu2eLogo(self,self.__row,self.__col)     # display Mu2e logo!
        self.__logo.grid(row=self.__row,column=self.__col,rowspan=3,columnspan=2,sticky=NE)
        self.__row += 3
#       Display the script's version number
        self.__version = myLabel(self,self.__row,self.__col)
        self.__version.setForgroundColor('blue')
        self.__version.setFontAll('Arial',10,'bold')
        self.__version.setWidth(20)
        self.__version.setText(Version)
        self.__version.makeLabel()
        self.__version.grid(row=self.__row,column=self.__col,columnspan=2,stick=E)
        self.__row += 1
#         Display the date the script is being run
        self.__date = myDate(self,self.__row,self.__col,10)      # make entry to row... pack right
        self.__date.grid(row=self.__row,column=self.__col,columnspan=2,sticky=E)
        self.__row += 1
##      Add button to retrieve the last few SiPM entered into the database
##      This appears in a separate window with a scroll bar
        self.__button1 = myIndependentWindow(self,self.__row,self.__col)
        self.__button1.setButtonName('Get Database Results')
        self.__button1.setButtonWidth(20)
        self.__button1.setButtonColor('lightblue')
        self.__button1.setAction('mu2e_SiPM_2016Jun24')
        self.__button1.makeButton()
        self.__button1.grid(row=self.__row,column=self.__col,sticky=W)
        self.__row += 1

##
##    Add Control bar with quit, enter data base and clear form buttons...
        self.__maxRow = 9
        self.__col = 0
        self.__buttonWidth = 15
        self.__quitNow = Quitter(self,self.__maxRow,0)
        self.__quitNow.grid(row=self.__maxRow,column=self.__col,sticky=W)
##    Add the "Enter Vendor Values to the Data Base" button
        self.__col +=1
        self.__nextMeasured = Button(self,text='Enter Vendor Info',command=self.nextEntryVendor,width=self.__buttonWidth,bg='green',fg='black')
        self.__nextMeasured.grid(row=self.__maxRow,column=self.__col,sticky=W)
##              Add status bar below the control bar
        self.__statusBar = myLabel(self,self.__maxRow+1,0)
        self.__statusWidth = 2*self.__labelWidth+self.__entryWidth+1*self.__buttonWidth
        self.__statusBar.setWidth(self.__statusWidth)
        self.__statusBar.setText('Status: ')
        self.__statusBar.setFontAll('Arial',10,'bold')
        self.__statusBar.makeLabel()
        self.__statusBar.grid(row=self.__maxRow+1,column=0,columnspan=2,sticky=W)


## --------------------------------------------------------------
    ## This method calls the method to write the GUI entries to the database
      def nextEntryVendor(self):  
        self.__statusBar.setText('')
        self.__statusBar.makeLabel()
        self.__mySaveIt.saveBarCode('Not Used')
        self.__mySaveIt.saveCounterNumber('Not Used')
        self.__mySaveIt.saveResults()            # write results to file for now... json file later
##        self.__password = "xdvi%4ew"
          ## self.__url = "https://dbweb3.fnal.gov:8443/hardwaredb/mu2edev/HdbHandler.py/loader"
        self.__url = self.__database_config.getWriteUrl()
        if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0):
            print("XXXX __packWindow__::Next Counter: self.__url = %s " % (self.__url))
        ## build string for the SiPM Tables... 
        ## There are several tables in the SiPM group...
        self.__group = "SiPM Tables"
        ##  Build string for the first table in the sipms table...
        self.__table = "sipm_measure_tests"
        self.__user = self.__mySaveIt.getOperator()+" (SLF6.6:GUI)"
        self.__sipmIdString = self.buildRowString_for_SiPM_VendorValues_table()
        if sendDataBase != 0:
          print("send to database!")
          myDataLoader1 = DataLoader(self.__password,self.__url,self.__group,self.__table)
          myDataLoader1.addRow( self.__sipmIdString)
          retVal,code,text = myDataLoader1.send()  ## send it to the data base!
          print("text = %s" % text)
          if retVal:
            self.__statusBar.setForgroundColor('black')
            self.__statusBar.setFontAll('arial',10,'normal')
            self.__statusBar.setText("Data Sent: "+text)
            self.__statusBar.makeLabel()
            if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0):
              print("XXXX __packSipmWindow__::Next Counter: SiPM ID Data Trasmission Success!!!")
              print(text)
          elif self.__password == '':
            self.__statusBar.setForgroundColor('red')
            self.__statusBar.setFontAll('arial',10,'normal')
            self.__statusBar.setText('Test mode: DATA WILL NOT BE SENT TO THE DATABASE')
            self.__statusBar.makeLabel()
          else:
            self.__statusBar.setForgroundColor('red')
            self.__statusBar.setFontAll('arial',10,'normal')
            self.__statusBar.setText('Error (SiPM): '+code+' '+text)
            self.__statusBar.makeLabel()
            if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0):
                print("XXXX __packSipmWindow__::Next Counter: Failed!!!")
                print(code)
                print(text) 

        ## Reset all fields...
        self.__sipmIdNumberStr.resetEntry()
        self.__vendBiasVolt.resetEntry()
        self.__vendDarkCount.resetEntry()
        self.__vendGain.resetEntry()
        self.__vendTemp.resetEntry()

  
    ##-----------------------------------------------------------------
    ## This method retrieves the entries from the GUI fields and builds
    ## a dictionary for to pass on to the database... the SiPM_Id table...
      def buildRowString_for_SiPM_VendorValues_table(self):
        self.__sendRow = {}            ## define empty dictionary
#        self.__sendRow['po_number'] = self.__mySaveIt.getStrEntry('Purchase Order')
        self.__sendRow['sipm_id'] = self.__mySaveIt.getStrEntry('SiPM ID Number')
        self.__sendRow['test_type'] = 'vendor'
        self.__sendRow['worker_barcode'] = self.__mySaveIt.getStrEntry('Worker')
        self.__sendRow['workstation_barcode'] = self.__mySaveIt.getStrEntry('Workstation')
        self.__sendRow['bias_voltage'] = self.__mySaveIt.getFltEntry('Vendor Bias Voltage')
        self.__sendRow['dark_count'] = self.__mySaveIt.getFltEntry('Vendor Dark Count')
        self.__sendRow['gain'] = self.__mySaveIt.getFltEntry('Vendor Gain')
        self.__sendRow['temp_degc'] = self.__mySaveIt.getFltEntry('Vendor Temperature')

          for key in list(self.__sendRow.keys()):
                if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0): print('XXXX packWindow::buildRowString... sendRow... key = %s value = %s \n' % (key,self.__sendRow[key]))
        return(self.__sendRow)
    ##-----------------------------------------------------------------
    ## This method retrieves the entries from the GUI fields and builds
    ## a dictionary to pass on to the database
      def buildRowString(self):
        self.__sendRow = {}            ## define empty dictionary
        ## Load Integer dictionary list 
        for mlist in self.__strName:
              self.__sendRow[mlist] = self.__mySaveIt.getStrEntry(mlist)
        ## Load Float dictionary list 
        for mlist in self.__fltName:
              self.__sendRow[mlist] = self.__mySaveIt.getFltEntry(mlist)
        self.__sendRow['create_time']= strftime('%Y-%m-%d %H:%M:%Z')
        for key in list(self.__sendRow.keys()):
                if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0): print('XXXX packWindow::buildRowString... sendRow... key = %s value = %s \n' % (key,self.__sendRow[key]))
        return(self.__sendRow)

## --------------------------------------------------------------------
if __name__ == '__main__':
     root = Tk()              # or Toplevel()
     bannerText = 'Mu2e:: SiPM Vendor Parameters'
     root.title(bannerText)  
#     n = tkk.Notebook(root)
##     myWindow=packSipmVendorWindow(root,0,0).grid()
     myWindow=packWindow(root,0,0).grid()
     root.mainloop()

