# -*- coding: utf-8 -*-
##  File = "sipmLocalMeasurements2016Jun24.py"
##  Derived from File = "sipmLocalMeasurements2016May09.py"
##  Derived from File = "sipmLocalMeasurements2016Jan12.py"
##  Derived from File = "sipmLocalMeasurements2016Jan6.py"
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
##  Modified by cmj2020Jun16... Use cmjGuiLibGrid2019Jan30
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Mar1.... replace dataloader with dataloader3
##  Modified by cmj2021Mar1.... Convert from python2 to python3: 2to3 -w *.py
##  Modified by cmj2021May14... replace tabs with spaces for block statements to convert to python 
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
##      Modified by cmj 2016Jan04... use central class to define URL's
##  Modified by cmj 2016Jan12 to use different directories for support modules...
##            These are located in zip files in the various subdirectories....
##  Modified by cmj2020Jun16... Use cmjGuiLibGrid2019Jan30
##  Modified by cmj2020Jul13.... Change to hdbClient_v2_2
##  Modified by cmj2020Aug03... cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
##  Modified by cmj2021May14.... replace dataloader with dataloader3
##  Modified by cmj2021May14... replace tabs with spaces for block statements to convert to python 3
##
##            To run this script:
##                 python TestSiPM_DataBase2015Jun18.py
##  To change libraries:
##       rm SiPMlib.zip
##       zip -r SiPMlib.zip *.py
##
##  Modified by cmj2020Jul13.... Change to hdbClient_v2_2
import sys
from tkinter import *         # get widget class
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")
from cmjGuiLibGrid import *  ## cmj2020Aug03
from DataLoader import *
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
class packWindow(Frame):
##class packSipmVendorWindow(Frame):
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
        self.__row += 2

##      Vendor supplied parameter
        self.__labelWidth = 40
        self.__vendorLabel = myLabel(self,self.__row,self.__col)
        self.__vendorLabel.setWidth(self.__labelWidth)
        self.__vendorLabel.setFontAll('Arial',10,'bold')
        self.__vendorLabel.setText("Vendor Supplied Parameters from database")
        self.__vendorLabel.makeLabel()
        self.__vendorLabel.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1

##            Write spot on form for vendor supplied bias voltage...
##                  update with values from database later
        self.__vendBiasVolt = myLabel(self,self.__row,self.__col)
        self.__vendBiasVolt.setWidth(self.__labelWidth)
        self.__vendBiasVolt.setFontAll('Arial',10,'bold')
        self.__vendorBiasVoltage = 'Vendor Bias Voltage'
        self.__vendBiasVolt.setText(self.__vendorBiasVoltage)
        self.__vendBiasVolt.makeLabel()
        self.__vendBiasVolt.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##            Enter vendor supplied dark count
##            Write spot on form for vendor supplied dark count...
##                  update with values from database later
        self.__vendDarkCount = myLabel(self,self.__row,self.__col)
        self.__vendDarkCount.setWidth(self.__labelWidth)
        self.__vendDarkCount.setFontAll('Arial',10,'bold')
        self.__vendorDarkCount = 'Vendor Dark Count'
        self.__vendDarkCount.setText(self.__vendorDarkCount)
        self.__vendDarkCount.makeLabel()
        self.__vendDarkCount.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##            Write spot on form for vendor supplied gain...
##                  update with values from database later
        self.__vendGain = myLabel(self,self.__row,self.__col)
        self.__vendGain.setWidth(self.__labelWidth)
        self.__vendGain.setFontAll('Arial',10,'bold')
        self.__vendorGain = 'Vendor Gain'
        self.__vendGain.setText(self.__vendorGain)
        self.__vendGain.makeLabel()
        self.__vendGain.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##            Write spot on form for vendor supplied gain...
##                  update with values from database later
        self.__vendTemp = myLabel(self,self.__row,self.__col)
        self.__vendTemp.setWidth(self.__labelWidth)
        self.__vendTemp.setFontAll('Arial',10,'bold')
        self.__vendorTemp = 'Vendor Temp'
        self.__vendTemp.setText(self.__vendorTemp)
        self.__vendTemp.makeLabel()
        self.__vendTemp.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##
        self.__labelWidth = 20
        self.__entryWidth = 20
        self.__buttonWidth = 5
        self.__fltName = []
        self.__fCount = 0
##      Locally measured parameters
        self.__col += 1
        self.__row = 5
        self.__labelWidth = 40
        self.__measuredLabel = myLabel(self,self.__row,self.__col)
        self.__measuredLabel.setWidth(self.__labelWidth)
        self.__measuredLabel.setFontAll('Arial',10,'bold')
        self.__measuredLabel.setText("Locally Measured Parameters")
        self.__measuredLabel.makeLabel()
        self.__measuredLabel.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
        self.__labelWidth = 20
        self.__entryWidth = 20
        self.__buttonWidth = 5
        self.__fltName = []
        self.__fCount = 0
##            Enter measured supplied bias voltage
        self.__measuredBiasVolt = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Measured Bias Voltage")
        self.__measuredBiasVolt.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__measuredBiasVolt.setLabelWidth(self.__labelWidth)
        self.__measuredBiasVolt.setEntryWidth(self.__entryWidth)
        self.__measuredBiasVolt.setButtonWidth(self.__buttonWidth)
        self.__measuredBiasVolt.makeEntry()
        self.__measuredBiasVolt.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##            Enter measured supplied dark count
        self.__measuredDarkCount = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Measured Dark Count")
        self.__measuredDarkCount.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__measuredDarkCount.setLabelWidth(self.__labelWidth)
        self.__measuredDarkCount.setEntryWidth(self.__entryWidth)
        self.__measuredDarkCount.setButtonWidth(self.__buttonWidth)
        self.__measuredDarkCount.makeEntry()
        self.__measuredDarkCount.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
##            Enter measured supplied gain
        self.__measuredGain = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Measured Gain")
        self.__measuredGain.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__measuredGain.setLabelWidth(self.__labelWidth)
        self.__measuredGain.setEntryWidth(self.__entryWidth)
        self.__measuredGain.setButtonWidth(self.__buttonWidth)
        self.__measuredGain.makeEntry()
        self.__measuredGain.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1

##            Enter measured supplied temperature
        self.__measuredTemp = myFloatEntry(self,self.__row,self.__col,self.__mySaveIt)
        self.__fltName.append("Measured Temp")
        self.__measuredTemp.setEntryText(self.__fltName[self.__fCount])
        self.__fCount += 1
        self.__measuredTemp.setLabelWidth(self.__labelWidth)
        self.__measuredTemp.setEntryWidth(self.__entryWidth)
        self.__measuredTemp.setButtonWidth(self.__buttonWidth)
        self.__measuredTemp.makeEntry()
        self.__measuredTemp.grid(row=self.__row,column=self.__col,stick=W)
        self.__row += 1
#### Second Column entries
#        self.__col += 1
        self.__oldRow = self.__row
        self.__row = 0
        self.__myInstructions = myScrolledText(self)
        self.__myInstructions.setTextBoxWidth(55)
        self.__myInstructions.makeWidgets()
        self.__myInstructions.setText('','Instructions/InstructionsForSipmMeasuredValues2015Jul30.txt')
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
#       Display the date the script is being run
        self.__date = myDate(self,self.__row,self.__col,10)      # make entry to row... pack right
        self.__date.grid(row=self.__row,column=self.__col,columnspan=2,sticky=E)
##      Add button to retrieve the last few SiPM entered into the database
##      This appears in a separate window with a scroll bar
        self.__row +=1
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
        self.__maxRow = 10
        self.__col = 0
        self.__buttonWidth = 15
        self.__quitNow = Quitter(self,self.__maxRow,0)
        self.__quitNow.grid(row=self.__maxRow,column=self.__col,sticky=W)
##    Add the "Enter Vendor Values to the Data Base" button
        self.__col +=1
        self.__nextMeasured = Button(self,text='Enter Measurements',command=self.nextEntryLocal,width=self.__buttonWidth,bg='green',fg='black')
        self.__nextMeasured.grid(row=self.__maxRow,column=self.__col,sticky=W)
##              Add status bar below the control bar
        self.__statusBar = myLabel(self,self.__maxRow+1,0)
        self.__statusWidth = 2*(2*self.__labelWidth+self.__entryWidth+1*self.__buttonWidth)
          self.__statusBar.setWidth(self.__statusWidth)
          self.__statusBar.setText('Status: ')
        self.__statusBar.setFontAll('Arial',10,'bold')
          self.__statusBar.makeLabel()
          self.__statusBar.grid(row=self.__maxRow+1,column=0,columnspan=4,sticky=W)

## --------------------------------------------------------------
    ## This method calls the method to write the GUI entries to the database
##      def nextEntryVendor(self):  
      def nextEntryLocal(self): 
        self.__statusBar.setText('')
        self.__statusBar.makeLabel()
        self.__mySaveIt.saveBarCode('Not Used')
        self.__mySaveIt.saveCounterNumber('Not Used')
        self.__mySaveIt.saveResults()            # write results to file for now... json file later
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
        self.__measuredBiasVolt.resetEntry()
        self.__measuredDarkCount.resetEntry()
        self.__measuredGain.resetEntry()
        self.__measuredTemp.resetEntry()
        self.getVendorValues()

    ##-----------------------------------------------------------------
    ## This method retrieves the entries from the GUI fields and builds
    ## a dictionary for to pass on to the database... the SiPM_Id table...
      def buildRowString_for_SiPM_VendorValues_table(self):
        self.__sendRow = {}            ## define empty dictionary
#        self.__sendRow['po_number'] = self.__mySaveIt.getStrEntry('Purchase Order')
        self.__sendRow['sipm_id'] = self.__mySaveIt.getStrEntry('SiPM ID Number')
        self.__sendRow['test_type'] = 'measured'
        self.__sendRow['worker_barcode'] = self.__mySaveIt.getStrEntry('Worker')
        self.__sendRow['workstation_barcode'] = self.__mySaveIt.getStrEntry('Workstation')
        self.__sendRow['bias_voltage'] = self.__mySaveIt.getFltEntry('Measured Bias Voltage')
        self.__sendRow['dark_count'] = self.__mySaveIt.getFltEntry('Measured Dark Count')
        self.__sendRow['gain'] = self.__mySaveIt.getFltEntry('Measured Gain')
        self.__sendRow['temp_degc'] = self._mySaveIt.getFltEnty('Measured Temp')

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
    ## -----------------------------------------------------------------
    ## This method retrieves the Vendor Bias voltage, dark currents and gains, previously entered
      def getVendorValues(self):
        ##self.__queryUrl = "http://dbweb3.fnal.gov:8088/QE/mu2e_hw_dev/app/SQ/query"
        self.__queryUrl = self.__database_config.getQueryUrl()
        self.__vendorValues = DataQuery(self.__queryUrl)
        self.__vendorValueResults = []
        self.__database = 'mu2e_hardware_dev'
        if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0):
          print("self.__queryUrl =%s \n" % self.__queryUrl) 
          print("self.__database = %s \n" % self.__database)
          print("self.__table    = %s \n" % self.__table)
        self.__queryString = "sipm_id:eq:"+self.__mySaveIt.getStrEntry('SiPM ID Number')+"&test_type:eq:vendor"
        if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0):
          print('self.__queryString = %s \n' % self.__queryString)
        rows = self.__vendorValues.query(self.__database,self.__table,"sipm_id,test_type,bias_voltage,dark_count,gain",self.__queryString,'-create_time',5)
        ##rows = self.__vendorValues.query(self.__database,self.__table,"sipm_id,test_type,bias_voltage,dark_count,gain",'sipm_id:eq:sp-0100&test_type:eq:vendor','-create_time',5)
        if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0): 
          print('XXXX packWindow::buildRowString... sendRow... key = %s value = %s \n' % (key,self.__sendRow[key]))
          for mlist in rows:
            print(mlist)
        parcedRow = rows[0].split(',')          ## split the first into strings delimited by commas
        self.__vendorBiasVoltageValue = parcedRow[2]
        self.__vendorDarkCountValue = parcedRow[3]
        self.__vendorGainValue = parcedRow[4]
        if (cmjDiag >= allDiag or cmjDiag == 9 or cmjDiagNext != 0): 
            for mlist in parcedRow:
              print('parcedRow = %s \n' % mlist)
            print('parcedRow[2] = %s parcedRow[3] = %s parcedRow[4] = %s \n' %(parcedRow[2],parcedRow[3],parcedRow[4]))
        ## update form with vendor values from database....
        self.__vendorBiasVoltage = 'Vendor Bias Voltage: '+parcedRow[2]
        self.__vendBiasVolt.setText(self.__vendorBiasVoltage)
        self.__vendBiasVolt.makeLabel()
        self.__vendorDarkCount = 'Vendor Dark Count: '+parcedRow[3]
        self.__vendDarkCount.setText(self.__vendorDarkCount)
        self.__vendDarkCount.makeLabel()
        self.__vendorGain = 'Vendor Gain: '+parcedRow[4]
        self.__vendGain.setText(self.__vendorGain)
        self.__vendGain.makeLabel()

        self.__vendorTemp = 'Vendor Temp: '+parcedRow[5]
        self.__vendTemp.setText(self.__vendorTemp)
        self.__vendTemp.makeLabel()
##
## --------------------------------------------------------------------
if __name__ == '__main__':
     root = Tk()              # or Toplevel()
     bannerText = 'Mu2e:: SiPM Vendor Parameters'
     root.title(bannerText)  
#     n = tkk.Notebook(root)
#     myWindow=packSipmVendorWindow(root,0,0).grid()
     myWindow=packWindow(root,0,0).grid()
     root.mainloop()

