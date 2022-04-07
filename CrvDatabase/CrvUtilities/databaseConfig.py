# -*- coding: utf-8 -*-
## File = "databaseConfig.py"
##
##   Written by:
##   Merrill Jenkins
##   Department of Physics
##   University of South Alabama
##   2016Jan
##
##  This python script contains the class to access
##  the development and production database
##
#!/usr/bin/env python
##
##  To transmit any changes to the dependent
##  python scripts, complete these steps in the
##  Utilities directory:
##     > rm Utilities.zip
##     > zip -r Utilities.zip *.py
##
##	2016Jan21... Add simp and extrusion keys...
##	2016May9... Add Composite, Electronics and Fibers 
##      2016May9... Add getVersion method....
##
##	2018Feb16... Add urls for updated databases.
##	2018Sep19... Change URL's for the development database write dbweb5.fnal.gov -> dbweb6.fnal.gov
##	2020May23... Correct path for electronics development psswrd....
##	2020Jun16... Change Query URL
##      2020Jul13... remove URL's for database from this code an read them in from a file.
##
class databaseConfig(object):
  def __init__(self):
    self.__cmjDebug = 0  ## set to 1 to print debug statements
    self.__sipmKey  = ' '
    self.__extrusionKey = ' '
## -------------------------------------------------------------
  def getVersion(self):
    self.__version="2020Jul13"
    return self.__version
## -------------------------------------------------------------
  def setDebugOn(self):
    self.__cmjDebug = 1
    print "..databaseConfig::setDebugOn \n"
## -------------------------------------------------------------
  def setDebugOff(self):
    self.__cmjDebug = 0
    print "..databaseConfig::setDebugOff \n"
## -------------------------------------------------------------
##  Modified by cmj2020Jul13 to read URL from File
  def getQueryUrl(self):
    if (self.__cmjDebug == 1): print '..databaseConfig.getQueryUrl().... enter'
    self.__queryUrl = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig.getQueryUrl()... before open'
      self.__tempFile=open('../CrvUtilities/86DevelopmentQueryUrl.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig.getQueryUrl()... after open'
    except Exception as e:
      self.__tempFile.close()
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program cannot access the database... \n'
      print 'databaseConfig.getQueryUrl():No_Url_Found \n'
      return 'from: databaseConfig.getQueryUrl:No_Url_Found'
    self.__queryUrl=self.__tempFile.read()
    if (self.__cmjDebug == 1):  print '..databaseConfig.getQueryUrl():self.__queryUrl = %s \n' % self.__queryUrl
    self.__tempFile.close()
    return self.__queryUrl.rstrip()
## -------------------------------------------------------------
##  Modified by cmj2020Jul13 to read URL from File
  def getWriteUrl(self):
    if (self.__cmjDebug == 1): print '..databaseConfig.getWriteUrl().... enter'
    self.__writeUrl = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getWriteUrl()... before open'
      self.__tempFile=open('../CrvUtilities/86DevelopmentWriteUrl.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getWriteUrl()... after open'
    except Exception as e:
      self.__tempFile.close()
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program cannot access the database... \n'
      print 'from: databaseConfig.getWriteUrl:No_Url_Found \n'
      return 'from: databaseConfig.getWriteUrl:No_Url_Found'
    self.__writeUrl=self.__tempFile.read()
    if (self.__cmjDebug == 1):  print '..databaseConfig:self.__writeUrl = %s \n' % self.__writeUrl
    self.__tempFile.close()
    return self.__writeUrl.rstrip()
## -------------------------------------------------------------
##  This is the sipm development key
  def getSipmKey(self):
    if (self.__cmjDebug == 1): print 'getSipmKey.... enter'
    self.__sipmKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getSipmKey... before open'
      self.__tempFile=open('../CrvUtilities/86Sipm.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getSipmKey... after open'
    except Exception as e:
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program will run, but in the test mode... \n'
      print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
      return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getSipmKey.... enter'
    self.__sipmKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__sipmKey.rstrip()
## -------------------------------------------------------------
##  This is the extrusion development key
  def getExtrusionKey(self):
    if (self.__cmjDebug == 1): print '..databaseConfig::getExtrusionKey.... enter'
    self.__extrusionKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getExtrusionmKey... before open'
      self.__tempFile=open('../CrvUtilities/86Extrusions.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getExtrusionKey... after open'
    except Exception as e:
	print 'exception: %s' % e
	print 'file not found: contact database administrators \n'
	print 'the program will run, but in the test mode... \n'
	print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
	return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getExtrusionKey.... enter'
    self.__extrusionKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__extrusionKey.rstrip()
## -------------------------------------------------------------
## -------------  2016 May9 ---- Add Electronics ---------------
## -------------------------------------------------------------
##  This is the electronics development key
  def getElectronicsKey(self):
    if (self.__cmjDebug == 1): print '..databaseConfig::getElectronicsKey.... enter'
    self.__electronicsKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getElectronicsKey... before open'
      self.__tempFile=open('../CrvUtilities/86Electronics.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getElectronicsKey... after open'
    except Exception as e:
	print 'exception: %s' % e
	print 'file not found: contact database administrators \n'
	print 'the program will run, but in the test mode... \n'
	print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
	return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getElectronicsKey.... enter'
    self.__electronicsKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__electronicsKey.rstrip() 
## -------------------------------------------------------------
## -------------  2016 May9 ---- Add Electronics ---------------
##--------------------------------------------------------------
##
## -------------------------------------------------------------
## -------------  2016 May9 ---- Add Fibers --------------------
## -------------------------------------------------------------
##  This is the fibers development key
  def getFibersKey(self):
    if (self.__cmjDebug == 1): print '..databaseConfig::getFibersKey.... enter'
    self.__fibersKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getFibersKey... before open'
      self.__tempFile=open('../CrvUtilities/86Fibers.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getFibersKey... after open'
    except Exception as e:
	print 'exception: %s' % e
	print 'file not found: contact database administrators \n'
	print 'the program will run, but in the test mode... \n'
	print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
	return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getFibersKey.... enter'
    self.__fibersKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__fibersKey.rstrip()
## -------------------------------------------------------------
## -------------  2016 May9 ---- Add Fibers --------------------
##--------------------------------------------------------------
##
## -------------------------------------------------------------
## -------------  2016 May9 ---- Add Composite -----------------
## -------------------------------------------------------------
##  This is the composite development key
  def getCompositeKey(self):
    if (self.__cmjDebug == 1): print '..databaseConfig::getCompositeKey.... enter'
    self.__compositeKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getCompositeKey... before open'
      self.__tempFile=open('../CrvUtilities/86Composite.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getCompositeKey... after open'
    except Exception as e:
	print 'exception: %s' % e
	print 'file not found: contact database administrators \n'
	print 'the program will run, but in the test mode... \n'
	print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
	return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getCompositeKey.... enter'
    self.__compositeKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__compositeKey.rstrip()
## -------------------------------------------------------------
## -------------  2016 May9 ---- Add Composite -----------------
##--------------------------------------------------------------
##
## -------------------------------------------------------------
##--------------------------------------------------------------
## -------------------------------------------------------------
##		Production database accessor functions....
##  Modified by cmj2020Jul13 to read Url from file
  def getProductionQueryUrl(self):
    if (self.__cmjDebug == 1): print '..databaseConfig.getProductionQueryUrl.()... enter'
    self.__productionQueryUrl = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig.getProductionQueryUrl()... before open'
      self.__tempFile=open('../CrvUtilities/86ProductionQueryUrl.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig.getProductionQueryUrl()... after open'
    except Exception as e:
      print 'exception: %s' % e
      self.__tempFile.close()
      print 'file not found: contact database administrators \n'
      print 'the program will cannot access the database... \n'
      return 'from: databaseConfig.getProductionQueryUrl():::No_Url_Found'
    self.__productionQueryUrl=self.__tempFile.read()
    if (self.__cmjDebug == 1):  print '..databaseConfig.getProductionQueryUrl():self.__productionQueryUrl = %s \n' % self.__productionQueryUrl
    self.__tempFile.close()
    return self.__productionQueryUrl.rstrip()
## -------------------------------------------------------------
## cmj2020Jul13... read the URL from a file
  def getProductionWriteUrl(self):
    if (self.__cmjDebug == 1): print '..databaseConfig.getProductionWriteUrl() enter'
    self.__productionWriteUrl = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getProductionWriteUrl()... before open'
      self.__tempFile=open('../CrvUtilities/86ProductionWriteUrl.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getProductionWriteUrl()... after open'
    except Exception as e:
      self.__tempFile.close()
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program cannot access the database... \n'
      return 'from: databaseConfig.self.__productionWriteUrl():No_Url_Found'
    self.__productionWriteUrl=self.__tempFile.read()
    if (self.__cmjDebug == 1):  print '..databaseConfig.self.__productionWriteUrl():self.__productionWriteUrl = %s \n' % self.__productionWriteUrl
    self.__tempFile.close()
    return self.__productionWriteUrl.rstrip()
## -------------------------------------------------------------
##  This is the sipm production key
  def getSipmProductionKey(self):
    if (self.__cmjDebug == 1): print 'getSipmProductionKey.... enter'
    self.__sipmKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getSipmProductionKey... before open'
      self.__tempFile=open('../CrvUtilities/86SipmPro.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getSipmProductionKey... after open'
    except Exception as e:
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program will run, but in the test mode... \n'
      print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
      return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getSipmProductionKey.... enter'
    self.__sipmKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__sipmKey.rstrip()
## -------------------------------------------------------------
##  This is the extrusion production key
  def getExtrusionProductionKey(self):
    if (self.__cmjDebug == 1): print '..databaseConfig::getExtrusionProductionKey.... enter'
    self.__extrusionKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getExtrusionmProductionKey... before open'
      self.__tempFile=open('../CrvUtilities/86ExtrusionsPro.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getExtrusionProductionKey... after open'
    except Exception as e:
	print 'exception: %s' % e
	print 'file not found: contact database administrators \n'
	print 'the program will run, but in the test mode... \n'
	print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
	return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getExtrusionKey.... enter'
    self.__extrusionKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__extrusionKey.rstrip()

## -------------------------------------------------------------
## --- 2016 May9 ---- Add Electronics Production Database ------
## -------------------------------------------------------------
##  This is the electronics production key
  def getElectronicsProductionKey(self):
    if (self.__cmjDebug == 1): print 'getElectronicsProductionKey.... enter'
    self.__electronicsKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getElectronicsProductionKey... before open'
      self.__tempFile=open('../CrvUtilities/86ElectronicsPro.txt','r')  ## cmj2020May28... fixed bug... file name.
      if (self.__cmjDebug == 1): print '..databaseConfig::getElectronicsProductionKey... after open'
    except Exception as e:
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program will run, but in the test mode... \n'
      print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
      return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getElectronicsProductionKey.... enter'
    self.__electronicsKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__electronicsKey.rstrip()
## -------------------------------------------------------------
## --- 2016 May9 ---- Add Electronics Production Database ------
## -------------------------------------------------------------
##
## -------------------------------------------------------------
## --- 2016 May9 ---- Add Fibers Production Database -----------
## -------------------------------------------------------------
##  This is the fibers production key
  def getFibersProductionKey(self):
    if (self.__cmjDebug == 1): print 'getFibersProductionKey.... enter'
    self.__fibersKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getFibersProductionKey... before open'
      self.__tempFile=open('../CrvUtilities/86FibersPro.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getFibersProductionKey... after open'
    except Exception as e:
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program will run, but in the test mode... \n'
      print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
      return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getFibersProductionKey.... enter'
    self.__fibersKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__fibersKey.rstrip()
## -------------------------------------------------------------
## --- 2016 May9 ---- Add Fibers Production Database -----------
## -------------------------------------------------------------
##
## -------------------------------------------------------------
## --- 2016 May9 ---- Add Composite Production Database -----------
## -------------------------------------------------------------
##  This is the fibers production key
  def getCompositeProductionKey(self):
    if (self.__cmjDebug == 1): print 'getCompositeProductionKey.... enter'
    self.__compositeKey = ''
    try:
      if (self.__cmjDebug == 1 ): print '..databaseConfig::getCompositeProductionKey... before open'
      self.__tempFile=open('../CrvUtilities/86CompositePro.txt','r')
      if (self.__cmjDebug == 1): print '..databaseConfig::getCompositeProductionKey... after open'
    except Exception as e:
      print 'exception: %s' % e
      print 'file not found: contact database administrators \n'
      print 'the program will run, but in the test mode... \n'
      print 'DATA WILL NOT BE SENT TO THE DATABASE \n'
      return ' '
    if (self.__cmjDebug == 1): print '..databaseConfig::getCompositeProductionKey.... enter'
    self.__compositeKey=self.__tempFile.read()
    self.__tempFile.close()
    return self.__compositeKey.rstrip()
## -------------------------------------------------------------
## --- 2016 May9 ---- Add Composite Production Database -----------
## ------------------------------------------------------------

