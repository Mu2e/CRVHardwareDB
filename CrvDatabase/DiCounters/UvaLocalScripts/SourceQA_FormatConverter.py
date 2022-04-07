##Script to format ource testing data to the format needed for Merrill Jenkin's script to send data to the CRV Production Database.
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##1-540-355-8918
##07/31/17 - Finished initial form - Needs to be updated to handle different length counters and to run checks on and make plots of data
##08/02/17 - Added block to remove embedded newline characters in final data point - still needs to be updated to adjust for dicounter length and make plots/run checks
##08/31/17 - Corrected bug in original which stored B-side before A-side data from older file types - Added functions to get database dump file and use the fump file to
##           extract the length of dicounters and calculate source position based on said length
##09/07/17 - Added function to get the length of dicounters using the DatabaseQueryTool and calculate the source position based on said length
##05/23/18 - Added code to identify and print to the console duplicate tests - duplicates defined by identical serial numbers and source positions
##07/03/18 - Modified to always switch data order so that A-side is printed before B-side
##07/09/18 - Removed call to calcBiasVoltage(), replaced with default value of 57.0 V. Adapted to handle "golden" reference dicounter and dicounters not in database already
##07/13/18 - Added option to run without creating an upload file (just flag potentially problematic lines)
##07/17/18 - Added 4 channels to each line for current from crystals. Added log file to record sns which could not be found in the database
##08/07/18 - Added comment feature and distinction between "rad" and "dark" for data without crystals and "crystal_rad" and "crystal_dark" for data with crystals
##08/08/18 - Added second try-catch block to repeat queries if failed in order to avoid connection based issues et al
##08/09/18 - Added code to remove newline character from the end of B-side channels when crystals were not present
##08/22/18 - Added default comment of "No Comment"

################################################################### Instructions ##################################################################################
##-This script can be run from and editor or terminal, the command line, or simply by double clicking on the file.                                               ##
##-If run from the command line, the script accepts two arguments. The first argument should be the desired input filename/path. The second should be the desired##
##output filename/path.                                                                                                                                          ##
##-The output file should be given a ".csv" extension.                                                                                                           ##
##-The script will print to the shell any lines it finds that are not correctly formatted. Review these lines and change them if necessary to ensure that no data##
##is inadvertently being skipped.                                                                                                                                ##
##-Duplicate tests will also be printed to the console and dicounters that could not be found in the database printed to "snsNotinDB.txt"                        ##
##-Data should be in following format (<> indicates optional field/component):                                                                                   ##
##dicounterSN<-sourcePosition>  <temp> (old data does not have temp)  <M>M/<d>d/yyyy HH:mm    b1 b2 b3 b4 a1 a2 a3 a4                                            ##
##-Follow all instructions on the source testing SOP in order to ensure proper formatting of data.                                                               ##
##-Note: Accessing the database is relatively slow and the script may take several minutes to run for larger files                                               ##
###################################################################################################################################################################

import sys
##sys.path.append("../DatabaseQueryTool.py")
import DatabaseQueryTool ##To query database
from datetime import *

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

lines = [] ##All of the lines of the input data file
outFileName = ""
flagged = {} ##A dictionary which stores all input data lines which do not match the required format
db_dicounters = [] ##A list of all dicounters currently stored in the database - Extracted from the .csv dumpfile
db_dicounterTests = [] ##A list of all dicounter tests currently stored in the database
database = "" ##The name of the database to be accessed to obtain dicounter lengths and run checks over 

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to get and assign input and output filenames and read from inputFile
def getInput():
    global outFileName
    inputFile = None
    
    if len(sys.argv) != 3: ##Control path if run as an executable or with incorrect number of arguments passed to it - Prompts user for names
        while inputFile == None:
            print "\nEnter an input file name/path:  "
            inFileName = raw_input()  
            inputFile = readFile(inFileName, inputFile)

        print "Enter a name for the output file: "
        outFileName = raw_input()       
    else: ##If correct number of arguments passed (2) from command line, first is used as inputFileName, second as outFileName
        readFile(sys.argv[1])
        if inputFile == None: ##If the file with the name of the first argument to the script cannot be found or read - prompt user for new filename
            while inputFile == None:
                print "\nEnter a different input file name/path:  "
                inFileName = raw_input()  
                inputFile = readFile(inFileName, inputFile)
                
        outFileName += sys.argv[2]

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to read an entire input file
def readFile(inFileN, inFile):
    global lines
    
    try:    
        inFile = open(inFileN, "r")
        lines = inFile.readlines() ##Read the entire file
    except IOError:
        print "File IO Error\n"
    finally:
        if inFile != None:
            inFile.close()

    return inFile

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#@deprecated
##This function reads in the dump files from the database "Dicounters" and "Dicounter Tests" tables
##This function is no longer needed now that dicounter length is being extracted from the database itself, not dump files
def getDatabaseDumpInfo():

    global db_dicounters, db_dicounterTests
    
    dicountersDumpFile = None
    dicounterTestsDumpFile = None

    while dicountersDumpFile == None:
        print 'Enter the name/path for the database "Dicounters" table dump file: '
        dicountersDumpFilename = raw_input()
        try:
            dicountersDumpFile = open(dicountersDumpFilename,"r")
            db_dicounters = dicountersDumpFile.readlines()
        except IOError:
            print 'File IOError: File "{0}" cannot be found or read\n"'.format(dicountersDumpFilename)
        finally:
            if dicountersDumpFile != None:
                dicountersDumpFile.close()

    while dicounterTestsDumpFile == None:
        print 'Enter the name/path for the database "Dicounter Tests" table dump file: '
        dicounterTestsDumpFilename = raw_input()
        try:
            dicounterTestsDumpFile = open(dicounterTestsDumpFilename,"r")
            db_dicounterTests = dicounterTestsDumpFile.readlines()
        except IOError:
            print 'File IOError: File "{0}" cannot be found or read\n"'.format(dicounterTestsDumpFilename)
        finally:
            if dicounterTestsDumpFile != None:
                dicounterTestsDumpFile.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to find mis-formatted/incorrect "<serial number>-<source position>"s.
##The order of precedence for flags is invalid length/format, invalid dicounter SN, invalid source position
##Duplcates can be found and flagged if corresponding block is un-commented
def flagLines():
    global lines, flagged
    prevIDs = {}
    idComponents = [] 
    di_id = ""
    diSN = -1
    
    for lineNum in range(len(lines)):
        di_id = str(lines[lineNum]).split("\t")[0]
        ##Ensure that the first set of characters is in the form "<dicounterSerialNum>" (dark current) or "<dicounterSerialNum>-<sourcePosition>" (source meaurements)
        idComponents = di_id.split("-")
        if len(idComponents) > 2 or len(idComponents) < 1: ##Flag if the if the dicounter ID has too many or too few components
            flagged[lineNum] = "Invalid dicounter-sourcePosition ID"
        else:
            try:
                diSN = int(idComponents[0])
            except:
                if idComponents[0].upper() != "GOLD": ##Check if dicounter was reference "golden" dicounter
                    flagged[lineNum] = "Invalid dicounter serial number" ##Flag if dicounter ID  is not in the form "<dicounterSN>" or "<dicounterSN>-"<something>"

            if len(idComponents)== 2:##Flag if source position is not labeled as being a distance X from either side "A" or "B"
                if idComponents[1][-1] != "A" and idComponents[1][-1] != "B": 
                    flagged[lineNum] = "Invalid source position"
                sourcePos = idComponents[1][:-1]
                try:
                    float(sourcePos)
                except:
                    flagged[lineNum] = "Invalid source position"

        ##Check for duplicate keys - print warning to console
        if prevIDs.has_key(di_id):
            print "DUPLICATE TEST: " + di_id + " at line " + str(lineNum) + " and previously at line " + str(prevIDs[di_id])

#########################################################################################################################################################################################
##This block will flag duplicate <dicounterSN>-<sourceposition>s. It is only necessary if only one test for each dicounter and source position can be stored/ it is desired that only one
##test be stored in the database.                
##
##        if prevIDs.has_key(di_id): ##Flag if dicounter ID (serial number + source position combination) has already been read. This will flag all instances of that ID
##            if flagged.has_key(lineNum):
##                flagged[lineNum] += " & Duplicate dicounter-sourcePosition ID"
##            else:
##                flagged[lineNum] = "Duplicate dicounter-sourceposition ID"
##            if flagged.has_key(prevIDs.get(di_id)):
##                flagged[prevIDs.get(di_id)] += " & Duplicate dicounter-sourcePosition ID"
##            else:
##                flagged[prevIDs.get(di_id)] = "Duplicate dicounter-sourcePosition ID"
##                         
#########################################################################################################################################################################################

        if not prevIDs.has_key(di_id): ##If the line is not a duplicate add it to the list of previous IDs
            prevIDs[di_id] = lineNum

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
##Function to reformat data and write it to the output file. Also prints flagged lines to the console
def processData(comment = ""):
    global lines, flagged, outFileName, database
    
    lnComponents = []
    di_id = ""
    diSN = 0
    sourePos = ""
    temp = -1.0
    dateTime = ""
    data = []
    formattedLine = ""
    skippedSNs = [] ##Serial numbers of dicounters which could not be found in the database and are therefore skipped during processing

    outputFile = open(outFileName,"w")
    skippedLogFile = open("snsNotinDB.txt","a+")
    skippedLogFile.write(datetime.now().strftime("\n" + "%d%b%Y_%H:%M") + ":\n")
    
    for lineNum in range(len(lines)):
        formattedLine = ""
        
        if lineNum not in flagged.keys():
            lnComponents = lines[lineNum].split("\t")
            
            ##Add prefix to dicounter serial number and remove source position. Add to output line
            di_id = lnComponents[0]
            diSN= di_id.split("-")[0]
            if diSN.upper() == "GOLD":
                diSN = "1140"
            formattedLine += "di-" + diSN +","

            ##Store temp if it is included. Otherwise give temp default value of -1.0. Use default bias of 57.0 V
            try:
                temp = float(lnComponents[1])
            except:
                temp = -1.0

            formattedLine += "57.0," + str(temp) + ","

            ##Add date-timestamp to output line. On pre-production file versions date is second column. On newer files, date is third column and temp is second column.
            if temp == -1:          ##Old file version which did not store temp
                formattedLine += lnComponents[1] + ","
            else:                   ##File version which does have temp
                formattedLine += lnComponents[2] + ","

                
            if len(lnComponents) >= 16: #If has crystal data
                sourceType = "crystal_rad"
                darkType = "crystal_dark"
            else:
                sourceType = "rad"
                darkType = "dark"
                    
            ##Add source position in cm from side A to output line and label "rad,1 mCi^137". For dark current, leave source position blank, label "dark", and leave source info blank
            if len(di_id.split("-")) == 2:
                sourcePos = di_id.split("-")[1]
                
                try:
                    formattedLine += str(getSourcePositionFromDB(diSN,sourcePos,database)) + "," + sourceType + ",1 mCi Cs^137,"
                    ##formattedLine += str(getSourcePositionFromDump(diSN,sourcePos)) + ",rad,1 mCi Cs^137," ##If using dump file
                except:
                    try: #Try query a second time if first query failed in case of connection issues et al
                        formattedLine += str(getSourcePositionFromDB(diSN,sourcePos,database)) + "," + sourceType + ",1 mCi Cs^137,"
                    except:
                        skippedSNs.append(diSN)
                        print "WARNING: " + diSN + " could not be located in the database and was skipped"
                        continue
            else:
                try:
                    fetchCondition = "di_counter_id:eq:di-" + diSN
                    dbTest = DatabaseQueryTool.query(database,"di_counters","length_m",fetchCondition)[0]
                    formattedLine += "," + darkType + ",,"
                except:
                    try: #Try query a second time if first query failed in case of connection issues et al
                        fetchCondition = "di_counter_id:eq:di-" + diSN
                        dbTest = DatabaseQueryTool.query(database,"di_counters","length_m",fetchCondition)[0]
                        formattedLine += "," + darkType + ",,"
                    except:
                        skippedSNs.append(diSN)
                        print "WARNING: " + diSN + " could not be located in the database and was skipped"
                        continue
                
  
            
            ##Add data values to output line
            
            if lnComponents[11].find("\n"):
                lnComponents[11] = lnComponents[11][:-1]
            data = lnComponents[8:12] + lnComponents[4:8] ##Switches B-side and A-side values to be in correct order of A then B

            for channel in data:
                formattedLine += channel + ","

            ##Add NaI crystal current data to output line - crystals are located 1m from B-side end
            if len(lnComponents) >= 16:
                for val in lnComponents[12:17]:
                    formattedLine += val + ","
                formattedLine = formattedLine[:-3]
            else:
                formattedLine += "-1,-1,-1,-1"

            #Add comment field (or empty string if no comment was provided) and newline
            formattedLine += "," + comment + "\n"

            ##Write output line to file
            outputFile.write(formattedLine)
        else:
            ##Print out the line number, error, and line for each flagged line
            print "Line " + str(lineNum) + " -- " + flagged[lineNum]+ ":\t" + lines[lineNum]

    ##Print the serial number of any dicounters which could not be found in the database to a log file "snsNotinDB.txt" under a heading with the timestamp
    skippedSNs = set(skippedSNs)
    for sn in skippedSNs:
        skippedLogFile.write(sn + "\n")

    outputFile.close()
    skippedLogFile.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to calculate the temperature adjusted bias voltage given the temperature
def calcBiasV(temp):
    if temp < 0:
        return 57.0
    else:
        return round(57.0 + (24.0 - float(temp)) * 0.054,2)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Funtion to extract dicounter length from the database and use it to return a source position in cm
##This function replaces getSourcePositionFromDump()
def getSourcePositionFromDB(diSN,sourcePos,database):
    sourcePos_in_cm = -1

    fetchCondition = "di_counter_id:eq:di-" + diSN
    
    diLength = float(DatabaseQueryTool.query(database,"di_counters","length_m",fetchCondition)[0])

    if diLength > 0:
        if sourcePos[-1] == "A":
            try:
                sourcePos_in_cm = int(float(sourcePos[:-1]) * 100)
            except:
                sourcePos_in_cm = -1
                
        elif sourcePos[-1] == "B":
            try:
                sourcePos_in_cm = int((diLength * 100) - (float(sourcePos[:-1]) * 100))
            except:
                sourcePos_in_cm = -1

    return sourcePos_in_cm

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
##Function to extract dicounter length from the dicounter information in database .csv dumpfile and use it to return a source position in cm
##This function has been replaced by getSourcePositionFromDB but is left here as a backup
def getSourcePositionFromDump(diSN,sourcePos):
    global db_dicounters

    diLength = 0.0
    sourcePos_in_cm = -1

    lineN = 0
    for dicounter in db_dicounters:
        if lineN == 0 or dicounter[:4] != '"di-':
            lineN += 1
            continue
        lineN += 1

        
        db_diSN = str(dicounter.split(",")[0]).split("-")[1][:-1]
        if db_diSN == diSN:
                diLength = float(dicounter.split(",")[2])
                break

    if diLength > 0:
        if sourcePos[-1] == "A":
            try:
                sourcePos_in_cm = int(float(sourcePos[:-1]) * 100)
            except:
                sourcePos_in_cm = -1
                
        elif sourcePos[-1] == "B":
            try:
                sourcePos_in_cm = int((diLength * 100) - (float(sourcePos[:-1]) * 100))
            except:
                sourcePos_in_cm = -1

    return sourcePos_in_cm

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Program driver function
def main(argv):
    global flagged, lines, database

    print "Which database would you like to be used?"
    print 'Enter "d" for development or "p" for production'
    dbChoice = raw_input()
    if dbChoice.upper() == "D":
        database = "mu2e_hardware_dev"
    else:
        database = "mu2e_hardware_prd"
    
    getInput()
    ##getDatabaseDumpInfo() ##Obsolete function. Replaced by individual database acess using DatabaseQueryTool    
    flagLines()
    
    print "Would you like to produce a database upload format file?"
    print 'Enter "y" or "n":'
    response = raw_input()
    if response.upper() == "Y":
        
        ##Add comments if desired
        print "Would you like to add a comment? Note, comment will be applied to all tests in the current file"
        print 'Enter "y" or "n":'
        inp = raw_input()
        if inp.upper() == "Y":
            print "Enter comment:"
            comment = raw_input()
        else:
            comment = "No Comment"

        print "Running - This may take a few minutes"
        processData(comment)
    else:
        ##Print out the line number, error, and line for each flagged line
        for lineNum in range(len(lines)):
            if lineNum in flagged.keys():
                print "Line " + str(lineNum) + " -- " + flagged[lineNum]+ ":\t" + lines[lineNum] 


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Primary program execution
if __name__ == "__main__":
    main(sys.argv)
