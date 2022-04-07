##Data verification and plotting tools to ensure that data is correct before being entered into the database
##and to retrieve and plot data already stored in the database. Accepts input and sends data to the correct 
##type-specific verification and/or plotting tool, supporting a broad array of data specification functionalities.
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##11/23/2017 - Untested initial version completed
##12/19/2017 - Fully tested and functional version complete
##01/02/2018 - Added prompt to select which database to use
##02/08/2018 - Added option to re-title histograms
##05/25/2018 - Added functionality to handle transmission tester IDs
##08/20/2018 - Finished debugging added source analysis tools for local file
##08/22/2018 - Finished debugging added source analysis tools for database and added sn retrieval tools

#TODO: Test & debug checkTransmissionQA_db()

#------------------------------------------------------------------------------------------------------------

import sys
import DatabaseQueryTool
import SNTools
import SourceAnalysisTools
import TransmissionQATools
from time import strftime 
from datetime import *

#------------------------------------------------------------------------------------------------------------

##Utility and control variables
inputFile = None
outputFile = None
database = "mu2e_hardware_dev" #Defaults to development
mode = 0 ##O=default, 1 = dicounters, 2 = source-test data, 3 = transmission-test data
checkDB = False ##If true, runs checks on data in the database
checkLocal = False ##If true, runs checks on data from a local file

#------------------------------------------------------------------------------------------------------------

##Function to set which type of data is to be processed. Prompts user if no acceptable value is passed
def getMode(mod = 0):
    global mode

    mode = mod
    while int(mode) not in [1,2,3]:
        print "\nSelect which type of data you wish to check:"
        print 'Enter "1" to check dicounter serial numbers'
        print 'Enter "2" to check source-test data'
        print 'Enter "3" to check transmission-test data'
        mode = int(raw_input("Mode==> "))

#------------------------------------------------------------------------------------------------------------

##Funtion to set whether local or database data is processed (can be both)
def checkDBorLocal(local = False, db = False):
    global checkDB, checkLocal
     
    checkLocal = local
    checkDB = db

    if checkLocal == False and checkDB == False:
        print '\nWould you like to run checks or plot data from a local file? Enter "y" or "n": '
        choice = raw_input()

        if choice.lower() == "y":
            checkLocal = True
        else:
            checkLocal = False
    
        print 'Would you like to run checks or plot data from the database? Enter "y" or "n": '
        choice = raw_input()
        if choice.lower() == "y":
            checkDB = True
        else:
            checkDB = False

#------------------------------------------------------------------------------------------------------------

##Function to select a set of serial numbers to be examined from the database
##Prompts user to enter a list or range of dicounter serial numbers
##Returns a list of dicounter serial numbers for use with database checking functions
def getSNs():
    sns = []
    
    print "\nSelect which dicounters from the database you wish to be checked"
    print "Please enter serial numbers the following formats"
    print "Hyphen separated inclusive range: e.g. 300-350"
    print "Comma separated multiple dicounters or ranges: e.g. 100, 105, 300-350, 260"

    raw = raw_input("Enter dicounters to be checked ==>")

    parsed = raw.split(",")

    for elem in parsed:
        if elem.find("-") > 0:
            minMax = elem.split("-")
            minMax[1] = int(minMax[1]) + 1
            
            for sn in range(int(minMax[0]),int(minMax[1])):
                sns.append(sn)
        else:
            sns.append(elem)

    return sns

#------------------------------------------------------------------------------------------------------------

##Function to extract list of serial numbers from a file so that their data can be checked in the database
##Function is called when user wants to check the same data in the database and from a local file
def getSNsFromFile(fileLines):
    
    sns = []

    for line in fileLines:
        sn = line.split(",")[0][3:].strip()
        if sn not in sns:
            sns.append(sn)

    return sns

#------------------------------------------------------------------------------------------------------------
    
##Function to retrieve a list of serial numbers of dicounters in a given module
def getSNsOfModule():
    global database

    moduleSN = raw_input('\nEnter the serial number of the module. Note single digit numbers must have a preceding zero (e.g. "01", not "1"): ')

    fetchCondition = "module_id:eq:crvmod-" + moduleSN
    
    print "Querying database..."

    sns = DatabaseQueryTool.query(database,"di_counters","di_counter_id",fetchCondition)

    for i in range(len(sns)):
        sns[i] = sns[i][3:]

    return sns

#------------------------------------------------------------------------------------------------------------
##Function to retrieve a lsit of dicounter serial numbers made from a specific fiber spool
def getSNsByFiber():
    global database
    
    print '\nIs the fiber from the production batch (i.e. M1804-0***)? Enter "y" or "n":'
    inp = raw_input()
    if inp.upper() == "Y":
        print "Enter the last 3 digits of the fiber ID (e.g. 30A):"
        fiberID = raw_input()
        fetchCondition = "fiber_id:eq:M1804-0" + fiberID
    else:
        fiberID = raw_input("Enter the entire fiber ID: ")
        fetchCondition = "fiber_id:eq:" + fiberID
    
    print "Querying..."
    sns = DatabaseQueryTool.query(database,"di_counters","di_counter_id",fetchCondition)

    if len(sns) < 1:
        print "No dicounters found made using that fiber"

    for i in range(len(sns)):
        sns[i] = sns[i][3:]

    return sns

#------------------------------------------------------------------------------------------------------------
##Function to retrieve a list of dicounter serial numbers made from a specific extrusion batch
def getSNsByExtrusionBatch():
    global database
    
    batch = raw_input('\nEnter the extrusion batch (e.g. 8_1_2017): ')
    fetchCondition = "batch_id:eq:batch_" + batch 
   
    print "Querying for extrusions in batch..."
    extrusions = DatabaseQueryTool.query(database, "extrusions","extrusion_id",fetchCondition)
        
    sns = []
    print "Querying for dicounters made with those extrusions..."
    for extrus in extrusions:
        fetchCondition = "scint_1:eq:" + str(extrus)
        result = DatabaseQueryTool.query(database, "di_counters","di_counter_id",fetchCondition)
        if len(result) == 0:
            fetchCondition = "scint_2:eq:" + str(extrus)
            result = DatabaseQueryTool.query(database, "di_counters","di_counter_id",fetchCondition)

        if len(result) > 0:
            sns.append(result[0][3:])

    if len(sns) < 1:
        print "No dicounters found using that extrusion batch"

    return sns
                   
#------------------------------------------------------------------------------------------------------------
##Function to retrieve a list of serial numbers of dicounters of a specific length
def getSNsByLength():
    global database

    print "Enter the length of the dicounters you wish to see plotted in meters: "
    length = float(raw_input())
    fetchCondition = "length_m:ge:" + str(length - 0.01) + "&length_m:le:" + str(length + 0.01)
    
    print "Querying..."
    sns = DatabaseQueryTool.query(database,"di_counters","di_counter_id",fetchCondition)

    if len(sns) == 0:
        print "No dicounters found within +/-1cm of length " + str(length) + " cm"
        
    for i in range(len(sns)):
        sns[i] = sns[i][3:]

    return sns

#------------------------------------------------------------------------------------------------------------

##Function to get input from a local file with dicounter information and run checks.
##Input file should be in the database upload form (Produced by DicounterSerialNumbersFormatConverter.py)
##Prompts user if no input filename is passed
def checkSNs_local(inFilename = "", outFilename = ""):
    global inputFile, outputFile
    
    lines = []
    sns = []
    needInputFile = True
    prodUpFilename = "sns_VerifiedForUpload_" + strftime("%d%b%Y_%H:%M") + ".csv"
    prodUploadFile = open(prodUpFilename,"w")

    ##If a filename was passed, try to open and read from it
    if inFilename != "":
        try:
            inputFile = open(inFilename,"r")
            lines = inputFile.readlines()
            needInputFile = False
            inputFile.close()
        except:
            print '\nFile by the name "' + inputFilename + '" could not be opened'

    ##If no valid filename was passed, prompt for one until a valid file is opened and read from
    while needInputFile:
        print "\nEnter the filename containing the dicounters to check. "
        print "Note: The file should be in the database upload format "
        inputFilename = raw_input()
        try:
            inputFile = open(inputFilename,"r")
            lines = inputFile.readlines()
            needInputFile = False
        except:
            print 'File by the name "' + inputFilename + '" could not be opened'
    inputFile.close()
    
    ##If a output filename is passed, use it. Otherwise, prompt user
    if outFilename != "":
        outputFile = open(outFilename,"a+")
    else:
        print '\nWould you like results to be saved to a file? Enter "y" if yes: '
        inp = raw_input()
        if inp == "y":
            print "Enter the name of the desired output file (existing files will be appended to):"
            inp = raw_input()
            outputFile = open(inp, "a+")
    
    ##Extract the serial number from each line and store
    for line in lines:
        if line[:3] == "di-":
            sns.append(line.split(",")[0][3:])
        
    ##Check for duplicate serial numbers in the file
    SNTools.checkForDuplicateSNs(sns,outputFile)
    ##Check for dicounters which have already been stored in the database
    alreadyInDB = SNTools.checkIfDicountersInDB(sns, database, outputFile)

    ##Produce a file in database upload format with lines containing dicounters already in the DB removed
    for line in lines:
        if line[:3] == "di-":
            if line.split(",")[0][3:] not in alreadyInDB:
                prodUploadFile.write(line)
    
    prodUploadFile.close()
    print "Use " + prodUpFilename + " to upload data to the database. This file contains all the data from the input file which is not already stored in the database. NOTE: Duplicates have not been removed."

#------------------------------------------------------------------------------------------------------------

#############################################################################################################
def sourceQA_local(inFilename = ""):
    global inputFile
    
    lines = []
    needInputFile = True
    badDataLines = [] #List of lines which contain negative curents or other data outside threshold
    plotParams = [] #Parameters of what data to plot
    data = {} #Dictionary mapping serial numbers to 3x18 arrays of current data, temps, and timestamps
    goldens = {} #Dictionary mapping dates to golden counter measurements
    sns = [] #List of serial numbers in file
    golds = [] #List of timestamps of golden dicounter tests
    plotThese = [] #List of serial numbers of dicounters that user wants to plotted from the file
    prevLen = 0

    prodUpFilename = "sourceQA_VerifiedForUpload_" + strftime("%d%b%Y_%H:%M") + ".csv"
    prodUploadFile = open(prodUpFilename,"w")

    ##If a filename is passed, try to open and read from it
    if inFilename != "":
        try:
            inputFile = open(inFilename, "r")
            lines = inputFile.readlines()
            needInputFile = False
            inputFile.close()
        except:
            print '\nFile by the name of "' + inFilename + '" could not be read'
        
    ##If no valid filename was passed, prompt user for one
    while needInputFile:
        print "\nEnter the name of the file containing source QA data:"
        print "Note: File should be in the database upload format"

        inFilename = raw_input()
        try:
            inputFile = open(inFilename, "r")
            lines = inputFile.readlines()
            needInputFile = False
        except:
            print '\nFile by the name of "' + inFilename + '" could not be read'
    inputFile.close()
      
    ##Check for negative or unreasonably large data values and list the line numbers where they occur
    print '\nEnter "y" if you would like to specify thresholds to check each data point against'
    print 'Default thresholds are 0 < x < 1.5 mV'
    inp = raw_input()
    if inp.upper() == "Y":
        minThresh = float(raw_input("Enter a minimum threshold: "))
        maxThresh = float(raw_input("Enter a maximum threshold: "))
    else:
        minThresh = 0
        maxThresh = 1.5
    badDataLines = set(SourceAnalysisTools.flagData(lines, minThresh, maxThresh))
    print "\nThe following lines contain unreasonable data values and should be checked and removed."
    print "Note: These lines will be skipped when plotting\n"
    print "Thresholds were " + str(minThresh) + " < x < " + str(maxThresh)
    for lnNum in badDataLines:
        print "Line- " + str(lnNum)
    if len(badDataLines) == 0:
        print "No unreasonable values detected"

   
    #Prompt for a subset of dicounters to plot from the file
    print '\nEnter "y" to specify a subset of dicounters to plot. Default is all'
    inp = raw_input()
    if inp.upper() == "Y":
        print "Enter a comma-separated list of serial numbers of dicounters to plot." 
        print "Indicate ranges with hyphens"
        inp = raw_input()
        parsed = inp.split(",")

        for elem in parsed:
            if elem.find("-") > 0:
                minMax = elem.split("-")
                minMax[1] = int(minMax[1]) + 1
            
                for sn in range(int(minMax[0]),int(minMax[1])):
                    plotThese.append(str(sn))
            else:
                plotThese.append(str(elem))
        if len(plotThese) == 0:
            print "WARNING: No serial numbers specified"
        

    ##Create a list (set) of serial numbers in the file - also create a list of golden counter test dates
    for lnNum in range(len(lines)):
        ##Skip over any lines with data flagged as unreasonable
        if lnNum in badDataLines:
            continue

        lnComponents = lines[lnNum].split(",")
        sn = lnComponents[0].split("-")[1]
        
        #Skip over any lines coresponding to dicounters not in specified list of sns to plot (if applicable)
        if len(plotThese) > 0:
            if sn not in plotThese and sn != "1140":
                continue

        if sn == "1140":
            golds.append(lnComponents[3])
        else:
            sns.append(sn)
    
    sns = set(sns)


    ##Create a hash table which maps serial numbers to 3x18 arrays of data values
    for sn in sns:        
        aSide = [-1] * 18
        bSide = [-1] * 18
        crysts = [-1] * 18
        vals = []
        vals.append(aSide)
        vals.append(bSide)
        vals.append(crysts)

        data[sn] = vals
  
    ##Create a hash table which maps dates to golden dicounter measurements    
    for tstamp in golds:
        aSide = [-1] * 18
        bSide = [-1] * 18
        crysts = [-1] * 18
        vals = []
        vals.append(aSide)
        vals.append(bSide)
        vals.append(crysts)

        #Select which date format to use for strptime()
        if len(tstamp.split(" ")[0].split("/")[2]) > 2: #If date is mm/dd/yyyy
            if len(tstamp.split(" ")[1]) > 5:
                dateFormat = "%m/%d/%Y %H:%M:%S"
            else:
                dateFormat = "%m/%d/%Y %H:%M"
        else:
            if len(tstamp.split(" ")[1]) > 5:
                dateFormat = "%m/%d/%y %H:%M:%S"
            else:
                dateFormat = "%m/%d/%y %H:%M"
        date = datetime.strptime(tstamp, dateFormat).date()

        goldens[date] = vals
     

    ##Fill hashtables with data
    for lnNum in range(len(lines)):
        ##Skip over any lines with data flagged as unreasonable
        if lnNum in badDataLines:
            continue

        lnComponents = lines[lnNum].split(",")

        sn = lnComponents[0].split("-")[1]

        #Skip any dicounter that is not in list of sns to plot (if applicable)
        if len(plotThese) > 0:
            if sn not in plotThese and sn != "1140":
                continue

        #Select which date format to use for strptime()
        if len(lnComponents[3].split(" ")[0].split("/")[2]) > 2: #If date is mm/dd/yyyy
            if len(lnComponents[3].split(" ")[1]) > 5:
                dateFormat = "%m/%d/%Y %H:%M:%S"
            else:
                dateFormat = "%m/%d/%Y %H:%M"
        else:
            if len(lnComponents[3].split(" ")[1]) > 5:
                dateFormat = "%m/%d/%y %H:%M:%S"
            else:
                dateFormat = "%m/%d/%y %H:%M" #mm/dd/yy


        if sn == "1140": #If golden dicounter
            #Extract date of the test
            date = datetime.strptime(lnComponents[3], dateFormat).date()

            if lnComponents[5] == "dark" or lnComponents[5] == "crystal_dark": #If dark current measurement
                #Store timestamp
                dt = datetime.strptime(lnComponents[3], dateFormat)
                #If test is older than the test is currently stored, skip the test
                if goldens[date][0][17] != -1:
                    if dt < goldens[date][0][17]:
                        continue
                goldens[date][0][17] = dt
                goldens[date][1][17] = dt
                goldens[date][2][17] = dt
                #Store temp
                goldens[date][0][16] = float(lnComponents[2]) 
                goldens[date][1][16] = float(lnComponents[2])
                goldens[date][2][16] = float(lnComponents[2])
                #Store currents
                for channel in range(0,4):
                    goldens[date][0][12 + channel] = float(lnComponents[7 + channel]) #A-side readouts
                    goldens[date][1][12 + channel] = float(lnComponents[11 + channel]) #B-side readouts
                    goldens[date][2][12 + channel] = float(lnComponents[15 + channel]) #Crystal readouts

            elif int(lnComponents[4]) > 100: #If source close (1m) to B-side
                #Store timestamp
                dt = datetime.strptime(lnComponents[3], dateFormat)
                #If test is older than the test that is currently stored, skip
                if goldens[date][1][5] != -1:
                    if dt < goldens[date][1][5]:
                        continue
                goldens[date][0][11] = dt #Weak-A
                goldens[date][1][5] = dt #Strong-B
                goldens[date][2][5] = dt #Strong crystals
                #Store temp
                goldens[date][0][10] = float(lnComponents[2]) #Weak-A
                goldens[date][1][4] = float(lnComponents[2]) #Strong-B
                goldens[date][2][4] = float(lnComponents[2]) #Strong crystals
                #Store currents
                for channel in range(0,4):
                    goldens[date][0][6 + channel] = float(lnComponents[7 + channel]) #A-side readouts to weak
                    goldens[date][1][channel] = float(lnComponents[11 + channel]) #B-side readouts to strong
                    goldens[date][2][channel] = float(lnComponents[15 + channel]) #Crystal readouts to strong

            else: #Source close (1m) to A-side
                #Store timestamp
                dt = datetime.strptime(lnComponents[3], dateFormat)
                #If test is older than the test that is currently stored, skip
                if goldens[date][0][5] != -1:
                    if dt < goldens[date][0][5]:
                        continue
                goldens[date][0][5] = dt #Strong-A
                goldens[date][1][11] = dt #Weak-B
                goldens[date][2][11] = dt #Weak crystals
                #Store temp
                goldens[date][0][4] = float(lnComponents[2]) #Strong-A
                goldens[date][1][10] = float(lnComponents[2]) #Weak-B
                goldens[date][2][10] = float(lnComponents[2]) #Weak crystals
                #Store currents
                for channel in range(0,4):
                    goldens[date][0][channel] = float(lnComponents[7 + channel]) #A-side readouts to strong-A
                    goldens[date][1][6 + channel] = float(lnComponents[11 + channel]) #B-side readouts to wea
                    goldens[date][2][6 + channel] = float(lnComponents[15 + channel]) #Crystal readouts weak
  
        else: #If not golden counter
            if lnComponents[5] == "dark" or lnComponents[5] == "crystal_dark": #If dark current measurement
                #Store timestamp
                dt = datetime.strptime(lnComponents[3], dateFormat)
                #If test is older than the test is currently stored, skip the test
                if data[sn][0][17] != -1:
                    if dt < data[sn][0][17]:
                        continue
                data[sn][0][17] = dt
                data[sn][1][17] = dt
                data[sn][2][17] = dt
                #Store temp
                data[sn][0][16] = float(lnComponents[2]) 
                data[sn][1][16] = float(lnComponents[2])
                data[sn][2][16] = float(lnComponents[2])
                #Store currents
                for channel in range(0,4):
                    data[sn][0][12 + channel] = float(lnComponents[7 + channel]) #A-side readouts
                    data[sn][1][12 + channel] = float(lnComponents[11 + channel]) #B-side readouts
                    data[sn][2][12 + channel] = float(lnComponents[15 + channel]) #Crystal readouts

            elif int(lnComponents[4]) > 100: #If source close (1m) to B-side
                #Store timestamp
                dt = datetime.strptime(lnComponents[3], dateFormat)
                #If test is older than the test that is currently stored, skip
                if data[sn][1][5] != -1:
                    if dt < data[sn][1][5]:
                        continue
                data[sn][0][11] = dt #Weak-A
                data[sn][1][5] = dt #Strong-B
                data[sn][2][5] = dt #Strong crystals
                #Store temp
                data[sn][0][10] = float(lnComponents[2]) #Weak-A
                data[sn][1][4] = float(lnComponents[2]) #Strong-B
                data[sn][2][4] = float(lnComponents[2]) #Strong crystals
                #Store currents
                for channel in range(0,4):
                    data[sn][0][6 + channel] = float(lnComponents[7 + channel]) #A-side readouts to weak-A
                    data[sn][1][channel] = float(lnComponents[11 + channel]) #B-side readouts to strong-B
                    data[sn][2][channel] = float(lnComponents[15 + channel]) #Crystal readouts to strong
 
                #Flag different lengths
                if prevLen == 0:
                    prevLen = float(lnComponents[4]) + 100
                else:
                    if abs(float(lnComponents[4]) + 100 - prevLen) > 2:
                        print "WARNING: " + str(sn) + " is of different length than others in the file"

            else: #Source close (1m) to A-side
                #Store timestamp
                dt = datetime.strptime(lnComponents[3], dateFormat)
                #If test is older than the test that is currently stored, skip
                if data[sn][0][5] != -1:
                    if dt < data[sn][0][5]:
                        continue
                data[sn][0][5] = dt #Strong-A
                data[sn][1][11] = dt #Weak-B
                data[sn][2][11] = dt #Weak crystals
                #Store temp
                data[sn][0][4] = float(lnComponents[2]) #Strong-A
                data[sn][1][10] = float(lnComponents[2]) #Weak-B
                data[sn][2][10] = float(lnComponents[2]) #Weak crystals
                #Store currents
                for channel in range(0,4):
                    data[sn][0][channel] = float(lnComponents[7 + channel]) #A-side readouts to strong-A
                    data[sn][1][6 + channel] = float(lnComponents[11 + channel]) #B-side readouts to weak-B
                    data[sn][2][6 + channel] = float(lnComponents[15 + channel]) #Crystal readouts to weak
        
    #Loop to make as many plots as desired
    while True:
        plotParams = SourceAnalysisTools.getPlotParameters()

        SourceAnalysisTools.initializeCanvas("Source QA","Source QA",plotParams)

        SourceAnalysisTools.plotSourceData(plotParams, sns, data, goldens)

        ##Re-title histogram(s) if desired
        ###############################################################################################
        
        ##Close/destroy Root objects to avoid memory leaks
        if raw_input("\nHit any key to close canvas\n") != None:
            SourceAnalysisTools.cleanRootObjects()

        print "Would you like to make another plot?"
        print 'Enter "y" or "n":'
        inp = raw_input()
        if inp.upper() != "Y":
            break
    
    ##Produce a file containing all data in the input file that was not flagged as bad
    for lnNum in range(len(lines)):
        if lnNum not in badDataLines:
            prodUploadFile.write(lines[lnNum])
    
    prodUploadFile.close()
    print "Use " + prodUpFilename + " to upload this data to the database. It contains all data from the input file except lines which were flagged above as containing \"bad\" data."

    return lines
            
#-----------------------------------------------------------------------------------------------------------

def sourceQA_database(sns):
    global database

    plotParams = [] #List specify which data to plot
    data = {} #Dictionary mapping serial numbers to 3x18 arrays of current data, temps, and timestamps
    goldens = {} #Dictionary mapping dates to golden counter measurements
    dates = [] #List of dates of tests
    foundSNs = []
    prevLen = 0
    
    ##Ensure serial numbers are ints
    for i in range(len(sns)):
        sns[i] = int(sns[i])

    ##Create a hash table which maps serial numbers to 3x18 arrays of data values
    for sn in sns:    
        if sn == "1140":
            continue

        aSide = [-1] * 18
        bSide = [-1] * 18
        crysts = [-1] * 18
        vals = []
        vals.append(aSide)
        vals.append(bSide)
        vals.append(crysts)

        data[sn] = vals

    #Query the database and store data
    print "\nQuerying the database for..."
    for sn in sns:
        fetchCondit = "di_counter_id:eq:di-" + str(sn)
    
        print "di-" + str(sn)

        results = DatabaseQueryTool.query(database,"di_counter_tests","di_counter_id,light_source,sipm_location,distance,current_amps,test_date,temperature",fetchCondit,"di_counter_id,light_source,sipm_location,distance,current_amps,test_date,temperature")
        
        if len(results) > 0:
            foundSNs.append(sn)

        for result in results:
            components = str(result).split(",")
            
            sn = int(components[0][3:])
            lightSource = components[1]
            sipmLoc = components[2]
            channel = int(sipmLoc[1]) - 1 #Map SiPM locations 1-4 to "channels" 0-3 for array indexing use
            sourcePos = float(components[3])
            dt = datetime.strptime(components[5][:16],"%Y-%m-%d %H:%M")
            dates.append(dt.date())

            if sn == "1140":
                continue

            if lightSource == "led": #If result not a source measurement
                continue
                
            if lightSource == "dark" or lightSource == "crystal_dark":
                if sipmLoc.find("a") != -1:
                    if data[sn][0][17] != -1:
                        if dt >= data[sn][0][17]: #If more recent than or same as currently stored test
                            data[sn][0][12 + channel] = float(components[4]) #Store current
                            data[sn][0][17] = dt #Store timestamp
                            data[sn][0][16] = float(components[6]) #Store temp
                    else: #If no test has been stored previously
                        data[sn][0][12 + channel] = float(components[4]) #Store current
                        data[sn][0][17] = dt #Store timestamp
                        data[sn][0][16] = float(components[6]) #Store temp
                
                elif sipmLoc.find("b") != -1:
                    if data[sn][1][17] != -1:
                        if dt >= data[sn][1][17]: #If more recent than currently stored test
                            data[sn][1][12 + channel] = float(components[4]) #Store current
                            data[sn][1][17] = dt #Store timestamp
                            data[sn][1][16] = float(components[6]) #Store temp
                    else: #If no test has been stored previously
                        data[sn][1][12 + channel] = float(components[4]) #Store current
                        data[sn][1][17] = dt #Store timestamp
                        data[sn][1][16] = float(components[6]) #Store temp

                else: #Crystals
                    if data[sn][2][17] != -1:
                        if dt >= data[sn][2][17]: #If more recent than currently stored test
                            data[sn][2][12 + channel] = float(components[4]) #Store current
                            data[sn][2][17] = dt #Store timestamp
                            data[sn][2][16] = float(components[6]) #Store temp
                    else: #If no test has been stored previously
                        data[sn][2][12 + channel] = float(components[4]) #Store current
                        data[sn][2][17] = dt #Store timestamp
                        data[sn][2][16] = float(components[6]) #Store temp                

            else: #Measurement with the source
                if sipmLoc.find("a") != -1:
                    if sourcePos > 100: #Weak A
                        if data[sn][0][11] != -1:
                            if dt >= data[sn][0][11]: #If more recent than currently stored value
                                data[sn][0][6 + channel] = float(components[4]) #Store current
                                data[sn][0][11] = dt #Store timestamp
                                data[sn][0][10] = float(components[6]) #Store temp
                        else: #If no test has been stored previously
                           data[sn][0][6 + channel] = float(components[4]) #Store current
                           data[sn][0][11] = dt #Store timestamp
                           data[sn][0][10] = float(components[6]) #Store temp 
                           
                        #Flag different lengths
                        if prevLen == 0:
                            prevLen = sourcePos + 100
                        else:
                            if abs(sourcePos + 100 - prevLen) > 2:
                                print "WARNING: " + str(sn) + " is of different length than others"

                    else: #Strong A
                        if data[sn][0][5] != -1:
                            if dt >= data[sn][0][5]: #If more recent than currently stored value
                                data[sn][0][channel] = float(components[4]) #Store current
                                data[sn][0][5] = dt #Store timestamp
                                data[sn][0][4] = float(components[6]) #Store temp
                        else: #If no test has been stored previously
                            data[sn][0][channel] = float(components[4]) #Store current
                            data[sn][0][5] = dt #Store timestamp
                            data[sn][0][4] = float(components[6]) #Store temp 

                elif sipmLoc.find("b") != -1:
                    if sourcePos == 100: #Weak B
                        if data[sn][1][11] != -1:
                            if dt >= data[sn][1][11]: #If more recent than currently stored value
                                data[sn][1][6 + channel] = float(components[4]) #Store current
                                data[sn][1][11] = dt #Store timestamp
                                data[sn][1][10] = float(components[6]) #Store temp
                        else: #If no test has been stored previously
                           data[sn][1][6 + channel] = float(components[4]) #Store current
                           data[sn][1][11] = dt #Store timestamp
                           data[sn][1][10] = float(components[6]) #Store temp 

                    else: #Strong B
                        if data[sn][1][5] != -1:
                            if dt >= data[sn][1][5]: #If more recent than currently stored value
                                data[sn][1][channel] = float(components[4]) #Store current
                                data[sn][1][5] = dt #Store timestamp
                                data[sn][1][4] = float(components[6]) #Store temp
                        else: #If no test has been stored previously
                            data[sn][1][channel] = float(components[4]) #Store current
                            data[sn][1][5] = dt #Store timestamp
                            data[sn][1][4] = float(components[6]) #Store temp  

                else: #Crystals
                    if sourcePos == 100: #Weak crystals
                        if data[sn][2][11] != -1:
                            if dt >= data[sn][2][11]: #If more recent than currently stored value
                                data[sn][2][6 + channel] = float(components[4]) #Store current
                                data[sn][2][11] = dt #Store timestamp
                                data[sn][2][10] = float(components[6]) #Store temp
                        else: #If no test has been stored previously
                           data[sn][2][6 + channel] = float(components[4]) #Store current
                           data[sn][2][11] = dt #Store timestamp
                           data[sn][2][10] = float(components[6]) #Store temp 

                    else: #Strong crystals
                        if data[sn][2][5] != -1:
                            if dt >= data[sn][2][5]: #If more recent than currently stored value
                                data[sn][2][channel] = float(components[4]) #Store current
                                data[sn][2][5] = dt #Store timestamp
                                data[sn][2][4] = float(components[6]) #Store temp
                        else: #If no test has been stored previously
                            data[sn][2][channel] = float(components[4]) #Store current
                            data[sn][2][5] = dt #Store timestamp
                            data[sn][2][4] = float(components[6]) #Store temp  

    
    #Create a hash table which maps dates to golden dicounter measurements from list of test dates 
    dates = set(dates)

    for date in dates:
        aSide = [-1] * 18
        bSide = [-1] * 18
        crysts = [-1] * 18
        vals = []
        vals.append(aSide)
        vals.append(bSide)
        vals.append(crysts)
        goldens[date] = vals

    #Query the database for golden dicounter measurements
    print "Querying the database for golden dicounter measurements.."
    golds = DatabaseQueryTool.query(database,"di_counter_tests","light_source,sipm_location,distance,current_amps,test_date,temperature","di_counter_id:eq:di-1140","light_source,sipm_location,distance,current_amps,test_date,temperature")

    #Store needed golden dicounter measurements
    for result in golds:
        components = str(result).split(",")
            
        lightSource = components[0]
        sipmLoc = components[1]
        channel = int(sipmLoc[1]) - 1 #Map SiPM locations 1-4 to "channels" 0-3 for array indexing use
        sourcePos = float(components[2])
        dt = datetime.strptime(components[4][:16],"%Y-%m-%d %H:%M")
        date = dt.date()

        if date not in goldens.keys():
            continue

        if lightSource == "led": #If not a source measurement
            continue

        if lightSource == "dark" or lightSource == "crystal_dark": 
            if sipmLoc.find("a") != -1:
                if goldens[date][0][17] != -1:
                    if dt > goldens[date][0][17]: #If more recent than previously stored test
                        goldens[date][0][12 + channel] = float(components[3]) #Store current
                        goldens[date][0][17] = dt #Store timestamp
                        goldens[date][0][16] = float(components[5]) #Store temp
                else: #If no previously stored test
                    goldens[date][0][12 + channel] = float(components[3]) #Store current
                    goldens[date][0][17] = dt #Store timestamp
                    goldens[date][0][16] = float(components[5]) #Store temp
            
            elif sipmLoc.find("b") != -1:
                if goldens[date][1][17] != -1:
                    if dt > goldens[date][1][17]: #If more recent than previously stored test
                        goldens[date][1][12 + channel] = float(components[3]) #Store current
                        goldens[date][1][17] = dt #Store timestamp
                        goldens[date][1][16] = float(components[5]) #Store temp
                else: #If no previously stored test
                    goldens[date][1][12 + channel] = float(components[3]) #Store current
                    goldens[date][1][17] = dt #Store timestamp
                    goldens[date][1][16] = float(components[5]) #Store temp

            else: #Crystals
                if goldens[date][2][17] != -1:
                    if dt > goldens[date][2][17]: #If more recent than previously stored test
                        goldens[date][2][12 + channel] = float(components[3]) #Store current
                        goldens[date][2][17] = dt #Store timestamp
                        goldens[date][2][16] = float(components[5]) #Store temp
                else: #If no previously stored test
                    goldens[date][2][12 + channel] = float(components[3]) #Store current
                    goldens[date][2][17] = dt #Store timestamp
                    goldens[date][2][16] = float(components[5]) #Store temp
                
        else: #If measurement with the source
            if sipmLoc.find("a") != -1:
                if sourcePos > 100: #Weak A
                    if goldens[date][0][11] != -1:
                        if dt > goldens[date][0][11]: #If more recent than previously stored test
                            goldens[date][0][6 + channel] = float(components[3]) #Store current
                            goldens[date][0][11] = dt #Store timestamp
                            goldens[date][0][10] = float(components[5]) #Store temp
                    else: #If no previously stored test
                        goldens[date][0][6 + channel] = float(components[3]) #Store current
                        goldens[date][0][11] = dt #Store timestamp
                        goldens[date][0][10] = float(components[5]) #Store temp

                else: #Strong A
                    if goldens[date][0][5] != -1:
                        if dt > goldens[date][0][5]: #If more recent than previously stored test
                            goldens[date][0][channel] = float(components[3]) #Store current
                            goldens[date][0][5] = dt #Store timestamp
                            goldens[date][0][4] = float(components[5]) #Store temp
                    else: #If no previously stored test
                        goldens[date][0][channel] = float(components[3]) #Store current
                        goldens[date][0][5] = dt #Store timestamp
                        goldens[date][0][4] = float(components[5]) #Store temp

            elif sipmLoc.find("b") != -1:
                if sourcePos == 100: #Weak B
                    if goldens[date][1][11] != -1:
                        if dt > goldens[date][1][11]: #If more recent than previously stored test
                            goldens[date][1][6 + channel] = float(components[3]) #Store current
                            goldens[date][1][11] = dt #Store timestamp
                            goldens[date][1][10] = float(components[5]) #Store temp
                    else: #If no previously stored test
                        goldens[date][1][6 + channel] = float(components[3]) #Store current
                        goldens[date][1][11] = dt #Store timestamp
                        goldens[date][1][10] = float(components[5]) #Store temp

                else: #Strong B
                    if goldens[date][1][5] != -1:
                        if dt > goldens[date][1][5]: #If more recent than previously stored test
                            goldens[date][1][channel] = float(components[3]) #Store current
                            goldens[date][1][5] = dt #Store timestamp
                            goldens[date][1][4] = float(components[5]) #Store temp
                    else: #If no previously stored test
                        goldens[date][1][channel] = float(components[3]) #Store current
                        goldens[date][1][5] = dt #Store timestamp
                        goldens[date][1][4] = float(components[5]) #Store temp
            
            else: #Crystals
                if sourcePos == 100: #Weak crystals
                    if goldens[date][2][11] != -1:
                        if dt > goldens[date][2][11]: #If more recent than previously stored test
                            goldens[date][2][6 + channel] = float(components[3]) #Store current
                            goldens[date][2][11] = dt #Store timestamp
                            goldens[date][2][10] = float(components[5]) #Store temp
                    else: #If no previously stored test
                        goldens[date][2][6 + channel] = float(components[3]) #Store current
                        goldens[date][2][11] = dt #Store timestamp
                        goldens[date][2][10] = float(components[5]) #Store temp

                else: #Strong crystals
                    if goldens[date][2][5] != -1:
                        if dt > goldens[date][2][5]: #If more recent than previously stored test
                            goldens[date][2][channel] = float(components[3]) #Store current
                            goldens[date][2][5] = dt #Store timestamp
                            goldens[date][2][4] = float(components[5]) #Store temp
                    else: #If no previously stored test
                        goldens[date][2][channel] = float(components[3]) #Store current
                        goldens[date][2][5] = dt #Store timestamp
                        goldens[date][2][4] = float(components[5]) #Store temp
                        
            
    #Loop to make as many plots as desired
    while True:
        plotParams = SourceAnalysisTools.getPlotParameters()

        SourceAnalysisTools.initializeCanvas("Source QA","Source QA",plotParams)

        SourceAnalysisTools.plotSourceData(plotParams, foundSNs, data, goldens)

        ##Re-title histogram(s) if desired
        ###############################################################################################
        
        ##Close/destroy Root objects to avoid memory leaks
        if raw_input("\nHit any key to close canvas\n") != None:
            SourceAnalysisTools.cleanRootObjects()

        print "Would you like to make another plot?"
        print 'Enter "y" or "n":'
        inp = raw_input()
        if inp.upper() != "Y":
            break

#------------------------------------------------------------------------------------------------------------
                                     
##Function to run checks and make plots on transmission test data from a local file
##Input file must be in the database upload format (Produced by "TransmissionQAFormatConverter.py")
def checkTransmissionQA_local(inFilename = ""):
    global inputFile

    needInputFile = True
    lines = []
    aChannels = [] ##Data without a tester stamp
    aChannels_t1 = [] ##Data from tester 1
    aChannels_t2 = [] ##Data from tester 2
    bChannels = []
    bChannels_t1 = []
    bChannels_t2 = []

    ##If a filename is passed, try to open and read from it
    if inFilename != "":
        try:
            inputFile = open(inFilename, "r")
            lines = inputFile.readlines()
            needInputFile = False
            inputFile.close()
        except:
            print '\nFile by the name of "' + inFilename + '" could not be read"'

    ##If no acceptable filename was passed, prompt user for one until a file is read
    while needInputFile:
        print "\nEnter the name of the file containing transmission QA data"
        print "Note: File should be in the database upload format"
        inFilename = raw_input()

        try:
            inputFile = open(inFilename, "r")
            lines = inputFile.readlines()
            needInputFile = False
            inputFile.close()
        except:
            print '\nFile by the name of "' + inFilename + '" could not be read"'
    inputFile.close()

    ##Parse data from lines read from file
    for line in lines:
        
        lnComponents = line.split(",")
        
        if lnComponents[0][:3] != "di-":
            continue


        if lnComponents[4] == "0":
            if len(lnComponents) < 16:
                 bChannels.extend(lnComponents[11:15])
            else:
                if lnComponents[15].startswith("tester-1"):
                    bChannels_t1.extend(lnComponents[11:15])
                elif lnComponents[15].startswith("tester-2"):
                    bChannels_t2.extend(lnComponents[11:15])
                else:
                    bChannels.extend(lnComponents[11:15])
        else:
            if len(lnComponents) < 16:
                aChannels.extend(lnComponents[7:11])
            else:
                if lnComponents[15].startswith("tester-1"):
                    aChannels_t1.extend(lnComponents[7:11])
                elif lnComponents[15].startswith("tester-2"):
                    aChannels_t2.extend(lnComponents[7:11])
                else:
                    aChannels.extend(lnComponents[7:11])



    ##Convert data values to floats so they can be plotted
    for i in range(len(aChannels)):
        aChannels[i] = float(aChannels[i])
    for i in range(len(aChannels_t1)):
        aChannels_t1[i] = float(aChannels_t1[i])
    for i in range(len(aChannels_t2)):
        aChannels_t2[i] = float(aChannels_t2[i])
    for i in range(len(bChannels)):
        bChannels[i] = float(bChannels[i])
    for i in range(len(bChannels_t1)):
        bChannels_t1[i] = float(bChannels_t1[i])
    for i in range(len(bChannels_t2)):
        bChannels_t2[i] = float(bChannels_t2[i])

    ##Assign data and parameters to Root objects used for plotting
    TransmissionQATools.setASideObjects(aChannels_t1, aChannels_t2, aChannels)
    TransmissionQATools.setBSideObjects(bChannels_t1, bChannels_t2, bChannels)
    TransmissionQATools.setAllChannelsObjects()

    ##Determine which data is to be plotted
    print "\nSelect which data you would like to be plotted:"
    print 'Enter "A" for only A-side data'
    print 'Enter "B" for only B-side data'
    print 'Hit "Enter" for all plots'
    plotMode = raw_input()

    ##Determine which tester's data to plot
    print "\nSelect which tester's data to plot:"
    print 'Enter "1" for tester-1'
    print 'Enter "2" for tester-2'
    print 'Enter "U" for unknown tester'
    print 'Hit "Enter" for all data'
    tester = raw_input()

    ##Initialize Root canvas to plot histograms on
    TransmissionQATools.initializeCanvas("TransmissionQACanvas","Transmission QA Data")

    ##Plot data
    if plotMode.upper() == "A":
        if tester == "1":
            TransmissionQATools.plot(TransmissionQATools.aHist_t1)
        elif tester == "2":
            TransmissionQATools.plot(TransmissionQATools.aHist_t2)
        elif tester.upper() == "U":
            TransmissionQATools.plot(TransmissionQATools.aHist)
        else:
            TransmissionQATools.plotAll(TransmissionQATools.aHist_t1, TransmissionQATools.aHist_t2, TransmissionQATools.aHist)
    elif plotMode.upper() == "B":
        if tester == "1":
            TransmissionQATools.plot(TransmissionQATools.bHist_t1)
        elif tester == "2":
            TransmissionQATools.plot(TransmissionQATools.bHist_t2)
        elif tester.upper() == "U":
            TransmissionQATools.plot(TransmissionQATools.bHist)
        else:
            TransmissionQATools.plotAll(TransmissionQATools.bHist_t1, TransmissionQATools.bHist_t2, TransmissionQATools.bHist)
    else:
        if tester == "1":
            TransmissionQATools.plotAll(TransmissionQATools.aHist_t1, TransmissionQATools.bHist_t1, TransmissionQATools.allHist_t1)
        elif tester == "2":
              TransmissionQATools.plotAll(TransmissionQATools.aHist_t2, TransmissionQATools.bHist_t2, TransmissionQATools.allHist_t2)
        elif tester.upper() == "U":
              TransmissionQATools.plotAll(TransmissionQATools.aHist, TransmissionQATools.bHist, TransmissionQATools.allHist)
        else:
            TransmissionQATools.plotAllOverlaid()

    ##Re-title histograms if desired
    TransmissionQATools.renameHistograms()

    ##Close/delete Root histograms and canvas objects to avoid memory leaks
    if raw_input("\nHit any key to close canvas\n") != None:
        TransmissionQATools.cleanRootObjects()

    return lines
  
#----------------------------------------------------------------------------------------------------------  

##Function to make plots of transmission QA data in the database
##Accepts a list of serial numbers of dicounters to plot data from
def checkTransmissionQA_db(snList):
    global database

    lines = []
    aChannels = []
    aChannels_t1 = []
    aChannels_t2 = []
    bChannels = []
    bChannels_t1 = []
    bChannels_t2 = []
    

    ##Get data from the database for dicounters with serial numbers included in snList
    print "Querying the database for..."
    for sn in snList:
        print "di-" + str(sn) 

        fetchCondition = "di_counter_id:eq:di-" + str(sn)
        
        lines = DatabaseQueryTool.query(database,"di_counter_tests","di_counter_id,light_source,sipm_location,distance,current_amps",fetchCondition,"di_counter_id,light_source,sipm_location,distance,current_amps,comments")

        ##Parse data from the query results and store in corresponding lists
        for lnNum in range(len(lines)):
            lnComponents = str(lines[lnNum]).split(",")

            if lnComponents[1] != "led":
                continue
            
            ##Determine which tester was used for each measurement
            if lnComponents[5].startswith("tester-1"):
                tester = "1"
            elif lnComponents[5].startswith("tester-2"):
                tester = "2"
            else:
                tester = "U"

            ##Data stored in the development database is backwards (i.e. A channels and B channels switched)
            ##Additionally, data in dev database does not have a tester ID
            if database == "mu2e_hardware_dev":
                if lnComponents[2][0] == "b":
                    if float(lnComponents[3]) > 0:
                        aChannels.append(lnComponents[4])
                elif lnComponents[2][0] == "a":
                    if float(lnComponents[3]) == 0:
                        bChannels.append(lnComponents[4])
            else:
                if lnComponents[2][0] == "a":
                    if float(lnComponents[3]) > 0:
                        if tester == "1":
                            aChannels_t1.append(lnComponents[4])
                        elif tester == "2":
                            aChannels_t2.append(lnComponents[4])
                        else:
                            aChannels.append(lnComponents[4])
                elif lnComponents[2][0] == "b":
                    if float(lnComponents[3]) == 0:
                        if tester == "1":
                            bChannels_t1.append(lnComponents[4])
                        elif tester == "2":
                            bChannels_t2.append(lnComponents[4])
                        else:
                            bChannels.append(lnComponents[4])
   
    print "Finished querying"

    ##Convert data values to floats so they can be plotted
    for i in range(len(aChannels)):
        aChannels[i] = float(aChannels[i])
    for i in range(len(aChannels_t1)):
        aChannels_t1[i] = float(aChannels_t1[i])
    for i in range(len(aChannels_t2)):
        aChannels_t2[i] = float(aChannels_t2[i])
    for i in range(len(bChannels)):
        bChannels[i] = float(bChannels[i])
    for i in range(len(bChannels_t1)):
        bChannels_t1[i] = float(bChannels_t1[i])
    for i in range(len(bChannels_t2)):
        bChannels_t2[i] = float(bChannels_t2[i])

    ##Assign data and parameters to Root objects used for plotting
    TransmissionQATools.setASideObjects(aChannels_t1, aChannels_t2, aChannels)
    TransmissionQATools.setBSideObjects(bChannels_t1, bChannels_t2, bChannels)
    TransmissionQATools.setAllChannelsObjects()

    ##Determine which data is to be plotted
    print "\nSelect which data you would like to be plotted:"
    print 'Enter "A" for only A-side data'
    print 'Enter "B" for only B-side data'
    print 'Hit "Enter" for all plots'
    plotMode = raw_input()

    ##Determine which tester's data to plot
    print "\nSelect which tester's data to plot:"
    print 'Enter "1" for tester-1'
    print 'Enter "2" for tester-2'
    print 'Enter "U" for unknown tester'
    print 'Hit "Enter" for all data'
    tester = raw_input()

    ##Initialize a Root canvas to plot histograms on
    TransmissionQATools.initializeCanvas("TransmissionQACanvas","Transmission QA Data")

    ##Plot data
    if plotMode.upper() == "A":
        if tester == "1":
            TransmissionQATools.plot(TransmissionQATools.aHist_t1)
        elif tester == "2":
            TransmissionQATools.plot(TransmissionQATools.aHist_t2)
        elif tester.upper() == "U":
            TransmissionQATools.plot(TransmissionQATools.aHist)
        else:
            TransmissionQATools.plotAll(TransmissionQATools.aHist_t1, TransmissionQATools.aHist_t2, TransmissionQATools.aHist)
    elif plotMode.upper() == "B":
        if tester == "1":
            TransmissionQATools.plot(TransmissionQATools.bHist_t1)
        elif tester == "2":
            TransmissionQATools.plot(TransmissionQATools.bHist_t2)
        elif tester.upper() == "U":
            TransmissionQATools.plot(TransmissionQATools.bHist)
        else:
            TransmissionQATools.plotAll(TransmissionQATools.bHist_t1, TransmissionQATools.bHist_t2, TransmissionQATools.bHist)
    else:
        if tester == "1":
            TransmissionQATools.plotAll(TransmissionQATools.aHist_t1, TransmissionQATools.bHist_t1, TransmissionQATools.allHist_t1)
        elif tester == "2":
              TransmissionQATools.plotAll(TransmissionQATools.aHist_t2, TransmissionQATools.bHist_t2, TransmissionQATools.allHist_t2)
        elif tester.upper() == "U":
              TransmissionQATools.plotAll(TransmissionQATools.aHist, TransmissionQATools.bHist, TransmissionQATools.allHist)
        else:
            TransmissionQATools.plotAllOverlaid()

    ##Re-title histograms if desired
    TransmissionQATools.renameHistograms()

    ##Close/delete Root histograms and canvas objects to avoid memory leaks
    if raw_input("\nHit any key to close canvas") != None:
         TransmissionQATools.cleanRootObjects()

#------------------------------------------------------------------------------------------------------------

##Program driver function
def main(args):
    global database, mode, checkLocal, checkDB

    fileLines = []
    sns = []
    
    ##Select which type of data is to be checked
    getMode()
    if mode != 1:
        checkDBorLocal()

    ##Choose which functions to run based on selected mode and checkLocal & checkDB parameters
    if mode == 1:
        ##Prompt for selection of which database to use
        print "\nSelect which database you would like to utilize."
        print 'Enter "0" for development and "1" for production:'
        choice = raw_input()
        if choice == "0":
            database = "mu2e_hardware_dev"
        else:
            database = "mu2e_hardware_prd"

        checkSNs_local()
    else:
        if checkLocal:
            if mode == 2:
               fileLines =  sourceQA_local()
            elif mode == 2:
                checkTransmissionQA_local()
        
        if checkDB:
            ##Prompt for selection of which database to use
            print "\nSelect which database you would like to utilize."
            print 'Enter "0" for development and "1" for production:'
            choice = raw_input()
            if choice == "0":
                database = "mu2e_hardware_dev"
            else:
                database = "mu2e_hardware_prd"

            print "\nEnter how you would like to choose which dicounters to plot:"
            if checkLocal:
                print 'Enter "S" for the same dicounters as were in the local file'
            print 'Enter "M" for dicounters from a specific module'
            print 'Enter "F" for dicounters made from a specific fiber'
            print 'Enter "L" for dicounters of a specific length'
            print 'Enter "E" for dicounters made from a specific extrusion batch'
            print 'Hit "Enter" to enter a list of serial numbers'
            choice = raw_input("Choice ======> ")
            choice = choice.upper()
            
            if choice == "S":
                sns = getSNsFromFile(fileLines)
            elif choice == "M":
                sns = getSNsOfModule()
            elif choice == "F":
                sns = getSNsByFiber()
            elif choice == "L":
                sns = getSNsByLength() 
            elif choice == "E":
                sns = getSNsByExtrusionBatch()
            else:
                sns = getSNs()
                
            if mode == 2:
                sourceQA_database(sns)
            elif mode == 3:
                checkTransmissionQA_database(sns)

#------------------------------------------------------------------------------------------------------------

##Trigger Program Execution if called as main
if __name__ == "__main__":
    main(sys.argv)
