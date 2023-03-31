# -*- coding: utf-8 -*-
##
##      A python script to read the Sipm tables in the hardware database
##      and display the overall Sipm status for a selected pack number
##
##   Written by
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##
##   2023Mar6.... change the cmb number for a di-counter in a module.
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
from datetime import *
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")  ## 2020Dec16
sys.path.append("../CrvUtilities/crvUtilities.zip")      ## 2018Oct2 add highlight to scrolled list
from DataLoader import *   ## module to read/write to database....
from databaseConfig import *
from cmjGuiLibGrid import *  ## cmj2020Aug03
from ModulesNonStaggered import *
#import SipmMeasurements
##
ProgramName = "guiChangeCmb.py"
Version = "version2023.03.08"
##
##
##
##
## -------------------------------------------------------------
##       A class to set up the main window to drive the
##      python GUI
##
class multiWindow(Frame):
  def __init__(self,parent=NONE, myRow = 0, myCol = 0):
    self.__masterFrame = Frame.__init__(self,parent)
    self.__cmjDebug = 0 ## default... no debug messages printed out
    self.__addNewCmb_insert = 0 ## this should be non-zero to insert new cmb; zero to undo existing cmb_id
    self.__database_config  = databaseConfig()
    self.setupProductionDatabase()  ## set up communications with database ## cmj2022Aug31## Default
    self.__myModules  = crvModules()
    ## setup parameters for updating database
    self.__maxTries = 1
    self.__sleepTime = 0.5
    ## set up geometry for GUI
    self.__gridWidth = int(10)
    self.__labelWidth = self.__gridWidth
    self.__entryWidth = self.__gridWidth
    self.__buttonWidth = self.__gridWidth
    self.__labelWidth = 25
    self.__entryWidth = 30
    self.__buttonWidth = 5
    self.__maxRow = 2
##     cmbInformation
    self.__cmbIdOld = "none"
##     First Column...
    self.__col = 0
    self.__row = 0
    self.__firstRow = 0
##
##     Instruction Box...
    self.__myInstructions = myScrolledText(self.__masterFrame)
    self.__myInstructions.setTextBoxWidth(50)
    self.__myInstructions.makeWidgets()
    self.__myInstructions.setText('','Instructions/InstructionsForGuiChangeCmb2023Mar7.txt')
    self.__myInstructions.grid(row=self.__row,column=self.__col,columnspan=2)
    ## Enter Existing CMB
    # self.__firstRow += 1
    self.__row += 3
    self.__col = 0
    self.__buttonName_CurrentCmb = 'Current CMB '
    self.currentCmbString(self.__masterFrame,self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName_CurrentCmb)
    self.__row += 3
    ## Display Existing CMB Information
    self.__currentCmbText = myScrolledText(self.__masterFrame)
    self.__currentCmbText.setTextBoxWidth(50)
    self.__currentCmbText.makeWidgets()
    self.__currentCmbText.setTextBoxHeight(5)
    #self.__currentCmbDatabaseText = "cmb_id     di_counter     side     smb_id \n"
    self.__currentCmbDatabaseText = "{st1:<20} {st2:<20} {st3:<20} {st4:<20} \n".format(st1='cmb_id',st2='di_counter',st3='side',st4='smb_id')
    self.__currentCmbText.setText(self.__currentCmbDatabaseText)
    self.__currentCmbText.grid(row=self.__row,column=self.__col,columnspan=2)
    ## Enter New CMB information
    self.__row += 3
    self.__col = 0
    self.__buttonName_NewCmb = 'New CMB '
    self.newCmbString(self.__masterFrame,self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName_NewCmb)
    self.__row += 3
    ## Display New CMB Information
    self.__newCmbText = myScrolledText(self.__masterFrame)
    self.__newCmbText.setTextBoxWidth(50)
    self.__newCmbText.makeWidgets()
    self.__newCmbText.setTextBoxHeight(5)
    #self.__newCmbDatabaseText = "cmb_id     di_counter     side     smb_id \n"
    #self.__newCmbDatabaseText = "{st1:<20} {st2:<20} {st3:<20} {st4:<20} \n".format(st1='cmb_id',st2='di_counter',st3='side',st4='smb_id')
    self.__newCmbDatabaseText="New CMB \n"
    self.__newCmbText.setText(self.__newCmbDatabaseText)
    self.__newCmbText.grid(row=self.__row,column=self.__col,columnspan=2)
    ##  Add the debug level button...
    self.__row += 3
    self.__col = 0
    self.__buttonName_DebugLevel = 'Set Debug Level (0 default) '
    self.debugString(self.__masterFrame,self.__row,self.__col,self.__labelWidth,self.__entryWidth,self.__buttonWidth,buttonName=self.__buttonName_DebugLevel)
    ##  Save last row....
    self.__lastRow = self.__row + 1
###     Third Column...
    self.__row = 0
    self.__col = 2
    self.__logo = mu2eLogo(self.__masterFrame,self.__row,self.__col)     # display Mu2e logo!
    self.__logo.grid(row=self.__row,column=self.__col,rowspan=2,sticky=NE)
##         Display the script's version number
    self.__version = myLabel(self.__masterFrame,self.__row,self.__col)
    self.__version.setForgroundColor('blue')
    self.__version.setFontAll('Arial',10,'bold')
    self.__version.setWidth(20)
    self.__version.setText(Version)
    self.__version.makeLabel()
    self.__version.grid(row=self.__row,column=self.__col,stick=E)
    self.__row += 1
##         Display the date the script is being run
    self.__date = myDate(self.__masterFrame,self.__row,self.__col,10)      # make entry to row... pack right
    self.__date.grid(row=self.__row,column=self.__col,sticky=W)
##  Back to the first column
##  Add Control Bar at the bottom...
    self.__col = 0
    self.__firstRow = self.__lastRow+1
    self.__buttonWidth = 10
    self.__quitNow = Quitter(self.__masterFrame,0,self.__col)
    self.__quitNow.grid(row=self.__lastRow,column=0,sticky=W)
    return
##
## -------------------------------------------------------------------
##
##  This function gets the current CMB information from the 
##  "counter_mother_boards" tables
##  Then fetch the four SiPM id's for this cmb_id
##
  def cmbQuery(self,tempCmbId):
    if(self.__cmjDebug > 0):
      print("...multiWindow::cmbQuery... Enter \n")
      print(("...multiWindow::cmbQuery... Get Information for cmb %s") % (tempCmbId))
    ##  Get the current cmb record
    self.__localCmbResult = []
    self.__item = []
    self.__getCmbValues = DataQuery(self.__queryUrl)
    self.__cmb_table = "counter_mother_boards"
    self.__cmb_fetchThese = "cmb_id,di_counter_id,di_counter_end,smb_id"
    self.__cmb_fetchCondition = "cmb_id:eq:CrvCmb-"+str(tempCmbId).upper()
    if(self.__cmjDebug > 1): 
      print(("...multiWindow::cmbQuery... self.__cmb_fetchThese = xx%sxx ")%(self.__cmb_fetchThese))
      print(("...multiWindow::cmbQuery... self.__cmb_fetchCondition = xx%sxx ") % (self.__cmb_fetchCondition))
    ## fetch current cmb record from data base.
    self.__localCmbResult = self.__getCmbValues.query(self.__database,self.__cmb_table,self.__cmb_fetchThese,self.__cmb_fetchCondition)  ## cmj2022Sep01
    sleep(self.__sleepTime)
    if(self.__cmjDebug > 1):
      print(("...multiWindow::cmbQuery... self.__localCmbResult \n %s \n") % self.__localCmbResult)
      print(("...multiWindow::cmbQuery... self.__localCmbResult[0] = %s \n") % self.__localCmbResult[0])
    self.__tempString = self.__localCmbResult[0]
    self.__item = self.__tempString.rsplit(',')
    self.__cmb_id_old = self.__item[0]
    self.__di_counter_store = self.__item[1]      ## store this value to update the new cmb_id and to change the cmb_id in the exising dicounter
    self.__di_counter_end_store = self.__item[2]  ## store this value to update the new cmb_id
    self.__smb_id_store = self.__item[3]          ## store this value to update the new cmb_id
    cmb_old_string=self.__cmb_id_old.replace('CrvCmb-','')
    smb_old_string=self.__smb_id_store.replace('CrvSmb-','')
    self.__currentCmbDatabaseText = "{0:<20}".format(cmb_old_string)+" "+"{0:<20}".format(self.__di_counter_store)+" "+"{0:<20}".format(self.__di_counter_end_store)+" "+"{0:<20}".format(smb_old_string)+"\n"
    if(self.__cmjDebug > 1):
      print(("...multiWindow::cmbQuery... self.__item =  %s ") % (self.__item))
      print(("...multiWindow::cmbQuery... cmb_id = %s di_counter = %s di_counter_end = %s smb_id = %s \n")%(self.__cmb_id_old,self.__di_counter_store,self.__di_counter_end_store,self.__smb_id_store))
    ## Update results on the main page in the text box
    self.__currentCmbText.appendText(self.__currentCmbDatabaseText)
    ##
    ##  Get the FOUR (4) Sipm_id that goes with this cmb
    self.__getSipmValues = DataQuery(self.__queryUrl)
    self.__localSipmResult_store = []  ## store these four sipm_id so they may be updated with the new cmb_id
    self.__item = []
    self.__sipm_table = "sipms"
    self.__sipm_fetchThese = "sipm_id"
    self.__sipm_fetchCondition = "cmb_id:eq:CrvCmb-"+str(tempCmbId).upper()
    self.__sipmResult_store_list = self.__getSipmValues.query(self.__database,self.__sipm_table,self.__sipm_fetchThese,self.__sipm_fetchCondition)  ## get the simp_id for the current cmb_id
    if(self.__cmjDebug > 1) : print(("...multiWindow::cmbQuery... self.__sipmResult_store_list \n %s \n")%(self.__sipmResult_store_list))
    ## 
    if(self.__cmjDebug > 0) : print("...multiWindow::cmbQuery... Exit \n")
    return
##
##
## -------------------------------------------------------------------
##
  def exchangeCmb(self,tempCmbId):
    self.changeOldCmbInDatabase(tempCmbId)  ## remove di_counter_id from old cmb record
    self.addNewCmbInDatabase(tempCmbId)     ## write new cmb record with old di_counter_id
    self.changeSipmInDatabase(tempCmbId)    ## update Sipms with new cmb_id
    return
##
## -------------------------------------------------------------------
##
##  This function adds a new cmb_id (cmb_id_new) in the "counter_mother_boards"
##  table 
##  and writes the CMB information from cmb_id_old into this record.
##  Then it changes the cmb_id to cmb_id_new for FOUR Sipms in the "simps" table
##  Finally, it (removes, actually renames) the di_counter_id in the original 
##  (cmb_id_old) record.
  def addNewCmbInDatabase(self,tempCmbId):
    self.__cmb_id_new = "CrvCmb-"+tempCmbId.rstrip()  ## store the new cmb_id
    if(self.__cmjDebug > 0):
      print(" \n")
      print("...multiWindow::addNewCmbInDatabase... ----------------------------------- ")
      print("...multiWindow::addNewCmbInDatabase... Enter")
    ##
    ##  Insert the new Counter Mother Board
    ##  Change add new cmb_id record, use the
    ##  exising information from "cmb_id_old"
    ##  to build the new record.
    #self.__electronicsGroup = "electronic_tables"
    #self.__cmbTable = 'counter_mother_boards'
    self.__electronicsGroup = "Electronic Tables"
    self.__cmbTable = "counter_mother_boards"
    if(self.__cmjDebug > 9): 
      print(" \n ----------------- Add new CMB record ")
      print((".......... electronics password ......... xx%sxx")%(self.__electronicsPassword))
      print((".......... self.__update_url ............ xx%sxx")%(self.__update_url))
      print((".......... self.__electroncsGroup ....... xx%sxx")%(self.__electronicsGroup))
      print((".......... self.__cmbTable .............. xx%sxx")%(self.__cmbTable))
    self.__addNewCmbInDatabaseTable = DataLoader(self.__electronicsPassword,self.__update_url,self.__electronicsGroup,self.__cmbTable)
    self.__send_new_cmb_row = {}
    self.__send_new_cmb_row['cmb_id']= self.__cmb_id_new.rstrip()
    self.__send_new_cmb_row['di_counter_id'] = self.__di_counter_store.rstrip()
    self.__send_new_cmb_row['di_counter_end']= self.__di_counter_end_store.rstrip()
    self.__send_new_cmb_row['smb_id'] = self.__smb_id_store.rstrip()
    self.__newCmbDatabaseText = "{st1:<20} {st2:<20} {st3:<20} {st4:<20} \n".format(st1='cmb_id',st2='di_counter',st3='side',st4='smb_id')  ## header
    self.__newCmbText.appendText(self.__newCmbDatabaseText)
    cmb_new = self.__cmb_id_new.replace('CrvCmb-','')
    smb_old = self.__smb_id_store.replace('CrvSmb-','')
    self.__newCmbDatabaseText = "{0:<20}".format(cmb_new)+" "+"{0:<20}".format(self.__di_counter_store)+" "+"{0:<20}".format(self.__di_counter_end_store)+" "+"{0:<20}".format(smb_old)+"\n"
    if(self.__cmjDebug > 7): print(("...multiWindow::addNewCmbInDatabase self.__send_new_cmb_row: %s") % (self.__send_new_cmb_row))
    if(self.__addNewCmb_insert != 0):
      print("XXXX ...multiWindow::addNewCmbInDatabase: addRow: Insert")
      self.__addNewCmbInDatabaseTable.addRow(self.__send_new_cmb_row,'insert')  ## Make a new row or entry.
    else:
      print("XXXX ...multiWindow::addNewCmbInDatabase: addRow: Update")
      self.__addNewCmbInDatabaseTable.addRow(self.__send_new_cmb_row,'update')  ## Make a new row or entry.
    for n in range(0,self.__maxTries):
      (retValCmb,codeCmb,textCmb) = self.__addNewCmbInDatabaseTable.send()  ## send it to the data base!
      tempString = str(textCmb)
      sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
      #if retValCmb:                        ## success!  data sent to database
      if((retValCmb) and (tempString.find('No')<=0) and (tempString.find('Password')<=0)):  ## success!  data sent to database
        self.__newCmbText.appendText(self.__newCmbDatabaseText)
        tempString = "XXXX ...multiWindow::addNewCmbInDatabase: New CMB Record: "+self.__cmb_id_new+"Database Transmission Success!!!"
        print(tempString)
        if(self.__cmjDebug > 8):
          print(("XXXX ...multiWindow::addNewCmbInDatabase: retValCmb  = %s") % (retValCmb))
          print(("XXXX ...multiWindow::addNewCmbInDatabase: codeCmb    = %s") % (codeCmb))
          print(("XXXX ...multiWindow::addNewCmbInDatabase: textCmb    = %s") % (textCmb))
        break
      elif(self.__electronicsPassword == '') :
        print(('XXXX ...multiWindow::addNewCmbInDatabase:: (Cmb) Update Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
      else:
        print('XXXX ...multiWindow::addNewCmbInDatabase:  (Cmb) Database Transmission: Failed!!!')
        print(("XXXX ...multiWindow::addNewCmbInDatabase: retValCmb = %s") % (retValCmb))
        print(("XXXX ...multiWindow::addNewCmbInDatabase: codeCmb   = %s") % (codeCmb))
        print(("XXXX ...multiWindow::addNewCmbInDatabase: textCmb   = %s") % (textCmb))
        print(("XXXX ...multiWindow::addNewCmbInDatabase: self.__send_new_cmb_row \n %s ")% (self.__send_new_cmb_row))
        print(codeCmb)
        print(textCmb)
    if(self.__cmjDebug > 0):
      print("...multiWindow::addNewCmbInDatabase... Enter")
      print("...multiWindow::addNewCmbInDatabase... ----------------------------------- ")
      print(" \n")
    return
##
## -------------------------------------------------------------------
##
##  Then it changes the cmb_id to cmb_id_new for FOUR Sipms in the "simps" table
  def changeSipmInDatabase(self, tempCmbId):
    self.__cmb_id_new = "CrvCmb-"+tempCmbId.rstrip()  ## store the new cmb_id
    if(self.__cmjDebug > 0):
      print(" \n")
      print("...multiWindow::changeSipmInDatabase... ----------------------------------- ")
      print("...multiWindow::changeSipmInDatabase... Enter")
    ##  Update the SiPMs table with the new "cmb_id"
    ##  There are FOUR (4) entries: Four (4) SiPMs per CMB 
    ##  Only replace (change) the "cmb_id" to the new one
    #self.__sipmsGroup = 'sipm tables'
    #self.__sipms_table = 'sipms'
    self.__sipmsGroup = "SiPM Tables"
    self.__sipms_table = "sipms"
    if(self.__cmjDebug > 9):
      print(" \n ----------------- Update/change four SiPM records ")
      print((".......... sipms password ......... xx%sxx")%(self.__sipmsPassword))
      print((".......... self.__update_url ............ xx%sxx")%(self.__update_url))
      print((".......... self.__sipmsGroup ....... xx%sxx")%(self.__sipmsGroup))
      print((".......... self.__sipmsTable .............. xx%sxx")%(self.__sipms_table))
    self.__changeSipmTable = DataLoader(self.__sipmsPassword,self.__update_url,self.__sipmsGroup,self.__sipms_table)
    print(self.__sipmResult_store_list)
    for sipmId in self.__sipmResult_store_list:
      if(sipmId == '') : continue  ## skip extra null list member
      self.__update_sipm_row = {}
      self.__update_sipm_row['sipm_id'] = sipmId.rstrip()
      self.__update_sipm_row['cmb_id'] = self.__cmb_id_new.rstrip()
      print((".......... sipmId ........... xx%sxx")%(sipmId))
      print((".......... cmbId ............ xx%sxx")%(self.__cmb_id_new))
      self.__changeSipmTable.addRow(self.__update_sipm_row,'update')  ## Update existing simp record
      for n in range(0,self.__maxTries):
        (retValSipm,codeSipm,textSipm) = self.__changeSipmTable.send()  ## send it to the data base!
        tempString = str(textSipm)
        if(self.__cmjDebug > 2): print("textSipm = %s" % textSipm)
        sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!
        if((retValSipm) and (tempString.find('No')<=0) and (tempString.find('Password')<=0)): ## success!  data sent to database
          reducedSipm = sipmId.replace('CrvSipm-S14283(ES2)_','')
          sipmTempString = "{0:<10}".format("SiPM")+": "+"{0:<10}".format(reducedSipm)+'\n'
          self.__newCmbText.appendText(sipmTempString)
          tempString = "XXXX ...multiWindow::changeSipmInDatabase: Updated Sipm Record: sipm_id = "+sipmId.replace('CrvSipm-S14283(ES2)_','')+" cmb_id = "+self.__cmb_id_new.replace('CrvCmb-','')+" Update Database Transmission Success!!!"
          print(("%s") % (tempString))
          if(self.__cmjDebug > 8):
            print(("XXXX ...multiWindow::changeSipmInDatabase: retValSipm = %s") % (retValSipm))
            print(("XXXX ...multiWindow::changeSipmInDatabase: codeSipm     = %s") % (codeSipm))
            print(("XXXX ...multiWindow::changeSipmInDatabase: textSipm     = %s") % (textSipm))
          break
        elif(self.__sipmsPassword == '') :
          print(('XXXX ...multiWindow::changeSipmInDatabase:: (Sipm) Update Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
        else:
          print('XXXX ...multiWindow::changeSipmInDatabase:  (Sipm) Database Transmission: Failed!!!')
          print(("XXXX ...multiWindow::changeSipmInDatabase: self.__update_sipm_row \n %s") % (self.__update_sipm_row))
          print(codeSipm)
          print(textSipm)
    if(self.__cmjDebug > 0):    
      print("...multiWindow::changeSipmInDatabase... Exit")
      print("...multiWindow::changeSipmInDatabase... ----------------------------------- ")
      print(" \n")
    return
##
## -------------------------------------------------------------------
##
##  Finally, Update the old cmb_id record to dissaociate the dicounter_id 
##  Set the dicounter to "NULL" (in python that is None)
  def changeOldCmbInDatabase(self,tempCmbId):
    if(self.__cmjDebug > 0):
      print(" \n")
      print("...multiWindow::changeOldCmbInDatabase... ----------------------------------- ")
      print("...multiWindow::changeOldCmbInDatabase... Enter")
    self.__electronicsGroup = "Electronic Tables"
    self.__cmbTable = "counter_mother_boards"
    if(self.__cmjDebug > 9): 
      print(" \n ----------------- Update old CMB record.  Change dicounter")
      print((".......... electronics password ......... xx%sxx")%(self.__electronicsPassword))
      print((".......... self.__update_url ............ xx%sxx")%(self.__update_url))
      print((".......... self.__electroncsGroup ....... xx%sxx")%(self.__electronicsGroup))
      print((".......... self.__cmbTable .............. xx%sxx")%(self.__cmbTable))
    self.__update_old_cmb = DataLoader(self.__electronicsPassword,self.__update_url,self.__electronicsGroup,self.__cmbTable)
    send_updated_old_cmb_row = {}
    send_updated_old_cmb_row['cmb_id'] = self.__cmb_id_old
    send_updated_old_cmb_row['di_counter_id'] = None
    self.__update_old_cmb.addRow(send_updated_old_cmb_row,'update')  ## Update existing "old_cmb_id" record.
    for n in range(0,self.__maxTries):
      (retValOldCmb,codeOldCmb,textOldCmb) = self.__update_old_cmb.send()  ## send it to the data base!
      tempString = str(textOldCmb)
      print("textOldCmb = %s" % textOldCmb)
      sleep(self.__sleepTime) ## sleep so we don't send two records with the same timestamp!                       ## success!  data sent to database
      if((retValOldCmb) and (tempString.find('No')<=0) and (tempString.find('Password')<=0)): ## success!  data sent to database
        removeString="Replace "+self.__di_counter_store+" with None \n"
        self.__newCmbText.appendText(removeString)
        tempString = "XXXX ...multiWindow::changeOldCmbInDatabase: Updated CMB Record: cmb_id_old = "+self.__cmb_id_old+" Replace "+self.__di_counter_store+" with None "+" Update Database Transmission Success!!!"
        print(("%s") % (tempString))
        if(self.__cmjDebug > 8) :
          print(("XXXX ...multiWindow::changeOldCmbInDatabase: retValOldCmb  = %s") % (retValOldCmb))
          print(("XXXX ...multiWindow::changeOldCmbInDatabase: codeOldCmb    = %s") % (codeOldCmb))
          print(("XXXX ...multiWindow::changeOldCmbInDatabase: textOldCmb    = %s") % (textOldCmb))
        break
      elif(self.__electronicsPassword == '') :
        print(('XXXX ...multiWindow::changeOldCmbInDatabase:: (CMB: remove dicounter) Update Test mode... DATA WILL NOT BE SENT TO THE DATABASE'))
      else:
        print('XXXX ...multiWindow::changeOldCmbInDatabase:  (CMB: remove dicounter) Database Transmission: Failed!!!')
        print(("XXXX ...multiWindow::changeOldCmbInDatabase: send_updated_old_cmb_row  \n %s") % (send_updated_old_cmb_row))
        print(codeOldCmb)
        print(textOldCmb)
    ##
    if(self.__cmjDebug > 0):
      print("...multiWindow::changeOldCmbInDatabase... Exit")  
      print("...multiWindow::changeOldCmbInDatabase... ----------------------------------- \n")
    return
##
## -----------------------------------------------------------------
## -----------------------------------------------------------------
##
##  A function to make a dummy dicounter in the database.
##  This dicounter will be associated with the old cmb_id 
##  (in the "electronics_tabble"
##
  def sendDummyDiCounterToDatabase(self):
    self.__dummy_di_counter_id = 'none'
    if(self.__cmjDebug > 0):
      print(" \n")
      print("...multiWindow::endDummyDiCounterToDatabase... ----------------------------------- ")
      print("...multiWindow::endDummyDiCounterToDatabase... Enter")
    self.__compositeGroup = "Composite Tables"
    self.__diCounterTable = "Di_Counters"
    if(self.__cmjDebug > 8):  print("XXXX ...multiWindow::sendDummyDiCounterToDatabase... self.__url = %s " % self.__update_url)
    if(self.__cmjDebug == 9): print("XXXX ...multiWindow::sendDummyDiCounterToDatabase... self.__password = %s \n" % self.__Compositeassword)
    localCmbId = self.__cmb_id_old.replace('-','')
    localDiCounterId="di-DUMMY-"+localCmbId
    ## Must load the diCounter table first!
    ## Build a dummy di_counter record
    self.__sendDiCounterRow = {}
    self.__sendDiCounterRow['di_counter_id'] = localDiCounterId
    self.__sendDiCounterRow['fiber_id'] = 'fiber_lot-none'
    self.__sendDiCounterRow['module_id'] = 'None'
    self.__sendDiCounterRow['module_layer'] = 'None'
    self.__sendDiCounterRow['layer_position'] = 'None'
    self.__sendDiCounterRow['length_m'] = float(-9999.99)
    dt = datetime.today()
    dt.strftime('%Y-%m-%d %I:%M:%S')
    print(("---------- sendDummyDiCounterToDatabase -------- date --- %s") % (dt))
    self.__sendDiCounterRow['manf_date'] = 'xxxxx'
    self.__sendDiCounterRow['manf_loc'] = 'Mars'
    self.__sendDiCounterRow['location'] = 'Earth'
    self.__sendDiCounterRow['scint_1'] = 'None1'
    self.__sendDiCounterRow['scint_2'] = 'None2'
    self.__sendDiCounterRow['comments'] = 'NoneTop'
    self.__sendDiCounterRow['fgb_man'] = 'Marvin'
    ##  Add new line to new cmb scrolled text window
    dummyDicounterString = "Add dummy di-counter: "+localDiCounterId+'\n'
    self.__newCmbText.appendText(dummyDicounterString)
    if(self.__cmjDebug > 2): 
      print(("XXXX ...multiWindow::sendDummyDiCounterToDatabase: self.__sendDiCounterRow = %s") % (self.__sendDiCounterRow))  ## cmj2022May10.
    if self.__sendToDatabase != 0:
      print("send to diCounter database!")
      self.__addDummyDicounter = DataLoader(self.__compositePassword,self.__update_url,self.__compositeGroup,self.__diCounterTable)
      self.__addDummyDicounter.addRow(self.__sendDiCounterRow,'insert')  ## Insert a non-existant dummy di-counter 
      for n in range(0,self.__maxTries):            ## cmj2019May23... try to send maxTries time to database
        (retValDicounter,codeDicounter,textDicounter) = self.__addDummyDicounter.send()  ## send it to the data base!
        if(self.__cmjDebug > 2): print("textDicounter = %s" % textDicounter)
        sleep(self.__sleepTime)     ## sleep so we don't send two records with the same timestamp....
        tempString = str(textDicounter)
        if((retValDicounter) and (tempString.find('No')<=0) and (tempString.find('Password')<=0) and (tempString.find('forged')<=0)): ## success!  data sent to database
          print("XXXX ...multiWindow::sendDummyDiCounterToDatabase: send DUMMY di-counter = %s"+localDiCounterId+"to database Transmission Success!!!")
          print(textDicounter)
          if(self.__cmjDebug > 8) :
            print(("XXXX ...multiWindow::changeOldCmbInDatabase: retValDicounter  = %s") % (retValDicounter))
            print(("XXXX ...multiWindow::changeOldCmbInDatabase: codeDicounter    = %s") % (codeDicounter))
            print(("XXXX ...multiWindow::changeOldCmbInDatabase: textDicounter    = %s") % (textDicounter))
            print(("XXXX ...multiWindow::changeOldCmbInDatabase: textOldCmb       = %s") % (textOldCmb))
          break
        elif (tempString.find('forged') != -1):
          print("XXXX...multiWindow::sendDummyDiCounterToDatabase: WRONG PASSWORD FOR DATABASE... see adminiatrator")
          break
        elif self.__compsitePassword == '':
          print(('XXXX...multiWindow::sendDummyDiCounterToDatabase: Test mode... DATA WILL NOT BE SENT TO THE DATABASE')) ## cmj2022Jul08
          break
        else:
          print("XXXX...multiWindow::sendDummyDiCounterToDatabase:  di-Counter Database Transmission: Failed!!!")
          print(("XXXX ...multiWindow::changeOldCmbInDatabase: self.__sendDiCounterRow  \n %s") % (self.__sendDiCounterRow))
          print(retValDicounter)
          print(codeDicounter)
          print(textDicounter)
    if(self.__cmjDebug > 0):
      print("...multiWindow::sendDummyDiCounterToDatabase... Exit")  
      print("...multiWindow::sendDummyDiCounterToDatabase... ----------------------------------- \n")
    self.__dummy_di_counter_id = localDiCounterId
    return
##
## ===================================================================  
##   Configure Database... get database passwords...
## ===================================================================
## ------------------------------------------------------------------
##  There are two connections: query and send for development database
  def setupDevelopmentDatabase(self):
    print("...multiWindow::setupDevelopmentDatabase... xxxx DEVELOPMENT DATABASE xxxx Enter \n")
    self.setupQueryDevelopmentDatabase()
    self.sendToDevelopmentDatabase()
    print("...multiWindow::setupDevelopmentDatabase... xxxx DEVELOPMENT DATABASE xxxx Exit \n")
    return
## -------------------------------------------------------------------
##  There are two connections: query and send for production database
  def setupProductionDatabase(self):
    print("...multiWindow::setupProductionDatabase... xxxx PRODUCTION DATABASE xxxx Enter \n")
    self.setupQueryProductionDatabase()
    self.sendToProductionDatabase()
    print("...multiWindow::setupProductionDatabase... xxxx PRODUCTION DATABASE xxxx Exit \n")
    return    
## -------------------------------------------------------------------
## -------------------------------------------------------------------
##      Make querries to development data base
  def setupQueryDevelopmentDatabase(self):
    self.__database = 'mu2e_hardware_dev'
    self.__whichDatabase = 'development'
    print("...multiWindow::setupQueryDevelopmentDatabase... query from development database \n")
    self.__queryUrl = self.__database_config.getQueryUrl()
    if(self.__cmjDebug > 8) : print(("...multiWindow::setupQueryDevelopmentDatabase... self.__queryUrl = %s ") % (self.__queryUrl))
##
## -------------------------------------------------------------------
##      Make querries to production data base
  def setupQueryProductionDatabase(self):
    self.__database = 'mu2e_hardware_prd'
    self.__whichDatabase = 'production'
    print("...multiWindow::setupQueryProductionDatabase... query from production database \n")
    self.__queryUrl = self.__database_config.getProductionQueryUrl() ## cmj2022Sep1
    if(self.__cmjDebug > 8) : print(("...multiWindow::setupQueryProductionDatabase... self.__queryUrl = %s ") % (self.__queryUrl))
## -----------------------------------------------------------------
##  send to the development database
  def sendToDevelopmentDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    self.__whichDatabase = 'development'
    ## setup the development database url
    if(self.__cmjDebug > 9): self.__database_config.setDebugOn()
    print("...multiWindow::sendToDevelopmentDatabase... send to development database \n")
    self.__update_url = self.__database_config.getWriteUrl()
    self.__sipmsPassword = self.__database_config.getSipmKey()
    self.__electronicsPassword = self.__database_config.getElectronicsKey()
    self.__compositePassword = self.__database_config.getCompositeKey()
    if(self.__cmjDebug > 7): print(("...multiWindow::sendToDevelopmentDatabase...  self.__update_url = xx%sxx") % self.__update_url)
    if(self.__cmjDebug > 9):
      print(("...multiWindow::sendToDevelopmentDatabase... sipm (development) password       = xx%sxx") % self.__sipmsPassword)
      print(("...multiWindow::sendToDevelopmentDatabase... electronic (development) password = xx%sxx") % self.__electronicsPassword)
      print(("...multiWindow::sendToDevelopmentDatabase... composite (development) password  = xx%sxx") % self.__compositePassword)
## -----------------------------------------------------------------
  def sendToProductionDatabase(self):
    self.__sendToDatabase = 1      ## send to database
    self.__whichDatabase = 'production'
    if(self.__cmjDebug > 9): self.__database_config.setDebugOn()
    print("...multiWindow::sendToProductionDatabase... send to production database \n")
    self.__update_url = self.__database_config.getProductionWriteUrl()
    self.__sipmsPassword = self.__database_config.getSipmProductionKey()
    self.__electronicsPassword = self.__database_config.getElectronicsProductionKey()
    self.__compositePassword = self.__database_config.getCompositeProductionKey()
    if(self.__cmjDebug > 7): print(("...multiWindow::sendToProductionDatabase...  self.__update_url = xx%sxx") % self.__update_url)
    if(self.__cmjDebug > 9):
      #print(("...multiWindow::sendToProductionDatabase... composite password  = xx%sxx") % self.__password)
      print(("...multiWindow::sendToProductionDatabase... sipm (production) password       = xx%sxx") % self.__sipmsPassword)
      print(("...multiWindow::sendToProductionDatabase... electronic (production) password = xx%sxx") % self.__electronicsPassword)
      print(("...multiWindow::sendToProductionDatabase... composite (production) password   = xx%sxx") % self.__compositePassword)
    self.__database = 'mu2e_hardware_prd'
##
## ===================================================================
## -------------------------------------------------------------------
##  Provide this function so the debug level may be set when
##  the multiWindow class is called.
  def setDebugLevel(self,tempDebug):
    self.__cmjDebug = tempDebug
    return
##
## 
## ===================================================================
## ===================================================================
##      Local String Entry button
##      Need to setup here to retain local program flow
##  This button is for setting the old_cmb_id
  def currentCmbString(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    self.__LocalFrame = tempFrame
    self.__currentCmbString_row = tempRow
    self.__currentCmbString_col = tempCol
    self.__currentCmbString_labelWidth = self.__gridWidth
    self.__currentCmbString_entryWidth = self.__gridWidth
    self.__currentCmbString_buttonWidth= self.__gridWidth
    self.__currentCmbString_entyLabel = ''
    self.__currentCmbString_buttonText = 'Enter'
    self.__currentCmbString_buttonName = buttonName
    self.__currentCmbString_result = 'xxxxaaaa'
    self.__entryLabel_CurrentCmb = '' 
    self.__label_currentCmb = Label(self.__LocalFrame,width=self.__currentCmbString_labelWidth,text=self.__currentCmbString_buttonName,anchor=W,justify=LEFT)
    self.__label_currentCmb.grid(row=self.__currentCmbString_row,column=self.__currentCmbString_col,sticky=W)
    self.__ent_currentCmb = Entry(self.__LocalFrame,width=self.__currentCmbString_entryWidth)
    self.__var_currentCmb = StringVar()        # associate string variable with entry field
    self.__ent_currentCmb.config(textvariable=self.__var_currentCmb)
    self.__var_currentCmb.set('')
    self.__ent_currentCmb.grid(row=self.__currentCmbString_row,column=self.__currentCmbString_col+1,sticky=W)
    self.__ent_currentCmb.focus()
    self.__ent_currentCmb.bind('<Return>',lambda event:self.fetch())
    self.__button_currentCmb = Button(self.__LocalFrame,text=self.__currentCmbString_buttonText,width=self.__currentCmbString_buttonWidth,anchor=W,justify=LEFT,command=self.currentCmbStringFetch)
    self.__button_currentCmb.config(bg='#E3E3E3')
    self.__button_currentCmb.grid(row=self.__currentCmbString_row,column=self.__currentCmbString_col+2,sticky=W)
  def currentCmbStringFetch(self):
    self.__cmbIdOld = self.__ent_currentCmb.get()  ## This is the "cmb_id" with out the "CrvCmb-" prefix
    self.__button_currentCmb.config(bg='yellow')
    self.cmbQuery(self.__cmbIdOld)
    if(self.__cmjDebug > 3): print(("--- currentCmbStringFetch... after Button in multiWindow = %s") %(self.__cmbIdOld))
    return self.__cmbIdOld
## ===================================================================
##      Local String Entry button
##      Need to setup here to retain local program flow
##  This button is for setting the new_cmb_id
  def newCmbString(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    self.__LocalFrame = tempFrame
    self.__newCmbString_row = tempRow
    self.__newCmbString_col = tempCol
    self.__newCmbString_labelWidth = self.__gridWidth
    self.__newCmbString_entryWidth = self.__gridWidth
    self.__newCmbString_buttonWidth= self.__gridWidth
    self.__newCmbString_entyLabel = ''
    self.__newCmbString_buttonText = 'Enter'
    self.__newCmbString_buttonName = buttonName
    self.__newCmbString_result = 'xxxxaaaa'
    self.__entryLabel_newCmb = '' 
    self.__label_newCmb = Label(self.__LocalFrame,width=self.__newCmbString_labelWidth,text=self.__newCmbString_buttonName,anchor=W,justify=LEFT)
    self.__label_newCmb.grid(row=self.__newCmbString_row,column=self.__newCmbString_col,sticky=W)
    self.__ent_newCmb = Entry(self.__LocalFrame,width=self.__newCmbString_entryWidth)
    self.__var_newCmb = StringVar()        # associate string variable with entry field
    self.__ent_newCmb.config(textvariable=self.__var_newCmb)
    self.__var_newCmb.set('')
    self.__ent_newCmb.grid(row=self.__newCmbString_row,column=self.__newCmbString_col+1,sticky=W)
    self.__ent_newCmb.focus()
    self.__ent_newCmb.bind('<Return>',lambda event:self.fetch())
    self.__button_newCmb = Button(self.__LocalFrame,text=self.__newCmbString_buttonText,width=self.__newCmbString_buttonWidth,anchor=W,justify=LEFT,command=self.newCmbStringFetch)
    self.__button_newCmb.config(bg='#E3E3E3')
    self.__button_newCmb.grid(row=self.__newCmbString_row,column=self.__newCmbString_col+2,sticky=W)
  def newCmbStringFetch(self):
    self.__newCmbId = self.__ent_newCmb.get()  ## This is the "cmb_id" with out the "CrvCmb-" prefix
    self.__button_newCmb.config(bg='yellow')
    #self.changeCmbInDatabase(self.__newCmbId.upper())
    self.exchangeCmb(self.__newCmbId.upper())
    ##print("---- newCmbStringFetch.... THE CALL TO self.changeCmbInDatabase(self.__newCmbId) IS DISABLED FOR TESTING \n")
    if(self.__cmjDebug > 3) : print(("--- newCmbStringFetch... after Button in multiWindow = %s") %(self.__newCmbId.upper()))
    return self.__newCmbId
## ===================================================================
##      Local String Entry button
##      Need to setup here to retain local program flow
##  This button is for setting the debug level
  def debugString(self,tempFrame,tempRow,tempCol,totWidth=20,labelWidth=10,entryWidth=10,entryText='',buttonName='default',buttonText='Enter'):
    self.__LocalFrame = tempFrame
    self.__debugString_row = tempRow
    self.__debugString_col = tempCol
    self.__debugString_labelWidth = self.__gridWidth
    self.__debugString_entryWidth = self.__gridWidth
    self.__debugString_buttonWidth= self.__gridWidth
    self.__debugString_entyLabel = ''
    self.__debugString_buttonText = 'Enter'
    self.__debugString_buttonName = buttonName
    self.__debugString_result = 'xxxxaaaa'
    self.__entryLabel_debug = '' 
    self.__label_debug = Label(self.__LocalFrame,width=self.__debugString_labelWidth,text=self.__debugString_buttonName,anchor=W,justify=LEFT)
    self.__label_debug.grid(row=self.__debugString_row,column=self.__debugString_col,sticky=W)
    self.__ent_debug = Entry(self.__LocalFrame,width=self.__debugString_entryWidth)
    self.__var_debug = StringVar()        # associate string variable with entry field
    self.__ent_debug.config(textvariable=self.__var_debug)
    self.__var_debug.set('')
    self.__ent_debug.grid(row=self.__debugString_row,column=self.__debugString_col+1,sticky=W)
    self.__ent_debug.focus()
    self.__ent_debug.bind('<Return>',lambda event:self.fetch())
    self.__button_debug = Button(self.__LocalFrame,text=self.__debugString_buttonText,width=self.__debugString_buttonWidth,anchor=W,justify=LEFT,command=self.debugStringFetch)
    self.__button_debug.config(bg='#E3E3E3')
    self.__button_debug.grid(row=self.__debugString_row,column=self.__debugString_col+2,sticky=W)
  def debugStringFetch(self):
    self.__cmjDebug = int(self.__ent_debug.get())
    self.__button_debug.config(bg='yellow')
    #self.setDebugLevel(self.__cmjDebug)
    if(self.__cmjDebug > 3) : print(("--- debugStringFetch... after Button in multiWindow:  self.__cmjDebug = %s") %(self.__cmjDebug))
    return self.__cmjDebug
##
## ===================================================================
## ===================================================================
## -------------------------------------------------------------------
##   Launch the script here!
## --------------------------------------------------------------------
## ===================================================================
if __name__ == '__main__':
  parser = optparse.OptionParser("usage: %prog [options] file1.txt \n")
  parser.add_option('--debug',dest='debugLevel',type='int',default=0,help='set debug: 0 (off - default), 1, 2, 3, ... ,10')
  parser.add_option('--database',dest='database',type='string',default="production",help='development or production')
  ##
  options, args = parser.parse_args()
  print(("'__main__': options.database  = %s \n") % (options.database))
  root = Tk()              # or Toplevel()
  bannerText = 'Mu2e::'+ProgramName
  root.title(bannerText)  
  root.geometry('500x500+100+50')  ## set offset of primary window....
  myMultiForm = multiWindow(root,0,0)
  if(options.debugLevel != 0): myMultiForm.setDebugLevel(options.debugLevel)
  if(options.database == "production"):
    myMultiForm.setupProductionDatabase()
  else:
    myMultiForm.setupDevelopmentDatabase()
##
  myMultiForm.grid()  ## define GUI
  root.mainloop()     ## run the GUI