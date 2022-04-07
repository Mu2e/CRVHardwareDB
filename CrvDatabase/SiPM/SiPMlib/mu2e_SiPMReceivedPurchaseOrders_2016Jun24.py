# -*- coding: utf-8 -*-
##  File = "mu2e_SiPMPurchaseOrders_2016Jun24.py"
##  Derived from File = "mu2e_SiPMPurchaseOrders_2016Jan12.py"
##  Derived from File = "mu2e_SiPMPurchaseOrders_2016Jan6.py"
##  Derived from File = "mu2e_SiPMPurchaseOrders_2015Jul30.py"
##
##  This script returns the list of Purchase Orders
##  in the database in a text string that can be written
##  into an independent window.
##  Modified by cmj 2016Jan12 to use different directories for support modules...
##		These are located in zip files in the various subdirectories....
##										"pre_production" or "production"
##  Modified by cmj2016Jun24... Add one more upward level for subdirectory to get to the utilities directory
##				for dataloader... place the CRV utilities directory in the "crvUtilities" directory
##  Modified by cmj2020Jun16... Use cmjGuiLibGrid2019Jan30
##  Modified by cmj2020Jul13.... Change to hdbClient_v2_2
##  Modified by cmj 2020Aug03 cmjGuiLibGrid2019Jan30 -> cmjGuiLibGrid
##  Modified by cmj2020Dec16... replace hdbClient_v2_2 with hdbClient_v3_3 - and (&) on query works
#!/usr/bin/env python
##
cmjDiag = 0
import sys
from Tkinter import *         # get widget class
sys.path.append("../../Utilities/hdbClient_v3_3/Dataloader.zip")
sys.path.append("../CrvUtilities/crvUtilities.zip")
from cmjGuiLibGrid import *  ## cmj2020Aug03
from DataLoader import *
from databaseConfig import *
import time
##
class getPurchaseOrders(Frame):
    def __init__(self,parent=None,myRow=0,myCol=0):
	Frame.__init__(self,parent)
	self.__poList = []
	self.__numberReturned = 10
	self.__database_config = databaseConfig()
##  Get all workers, return as a list
    def getPo(self):
	  self.__queryUrl = self.__database_config.getQueryUrl()
	  self.__vendorValues = DataQuery(self.__queryUrl)
	  self.__vendorValueResults = []
	  self.__database = 'mu2e_hardware_dev'
	  self.__table = "sipm_batches"
	  if (cmjDiag >= allDiag or cmjDiag == 9):
	    print "getWorkerBarCode::getWorker-- self.__queryUrl =%s \n" % self.__queryUrl 
	    print "getWorkerBarCode::getWorker--self.__database = %s \n" % self.__database
	    print "getWorkerBarCode::getWorker--self.__table    = %s \n" % self.__table
	  self.__batch = self.__vendorValues.query(self.__database,self.__table,"po_number,batch_number,quantity_received,date_received",None,'-po_number',self.__numberReturned)
	  return self.__batch  ## return a list of strings
    def setNumberReturned(self,tempNumber):
	  self.__numberReturned = tempNumber
##
##   
class packWindow(Frame):
    def __init__(self,parent=None,myRow = 0, myCol = 0):
	  Frame.__init__(self,parent)
          if (cmjDiag >= allDiag or cmjDiag == 100): print 'XXXX packWindow::__main__  Enter driving method '
	  self.__labelWidth = 20
	  self.__entryWidth = 20
	  self.__buttonWidth = 5
	  self.__database_config = databaseConfig()
	  self.__password = self.__database_config.getSipmKey()
	  self.__dataBaseResults = myScrolledText(self)
	  self.__dataBaseResults.setTextBoxWidth(50)
	  self.__dataBaseResults.setText('Purchase Orders from database',None)
	  self.__dataBaseResults.makeWidgets()
	  self.__banner = ('%10s   %10s   %10s    %10s \n') %('PO Number','Batch Number','Quantity Received','Receive Date')
	  self.__dataBaseResults.setText(self.__banner,None,END)
	  self.__dataBaseText = getPurchaseOrders()
	  self.__dataBaseStringList = self.__dataBaseText.getPo()
	  for self.__mline in self.__dataBaseStringList:
	      parcedRow = self.__mline.split(',')
	      mcount = 0
	      self.__line = '\n'
	      for item in parcedRow:
		# print "item[%d] = %s \n" % (mcount, item)
		mcount += 1     
		self.__line +=  ('%10s   ') % item
	      #self.__line += ' \n'
	      self.__dataBaseResults.setText(self.__line,None,END)
	  self.__dataBaseResults.grid(row=0,column=0)

