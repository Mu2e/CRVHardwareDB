##Script to convert transmission testing data into the format needed for Merrill Jenkin's script to send test data to the CRV Production Database
##Written by: Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##08/01/2017 - Initial version completed - Needs to be altered to correctly account for dicounter length and its effect on B side position of the LED - get length from database
##08/03/2017 - Removed bug which removed a digit from A4 from side A - Still needs above listed alterations
##09/07/2017 - Added function to retrieve dicounter length from the database and use it to calculate the position of the LED in cm from side A for LEDs at B-side
##10/26/2017 - Corrected the order of channels - previously A-side and B-side channels had been switched - order is now correct
##05/21/2018 - Added code to append the tester ID as a comment to each test
##05/24/2018 - Added code to catch and print any duplicate tests to the console
##08/07/2018 - Added "-1"s to end of lines as "null" values to fill in SiPM locations corresponding to crystals in source test - added database option and warning for SNs not in database
##08/08/2018 - Added extra try-except block to query the database a second time if first attempt fails

######################################################################### Instructions ##########################################################################################
##This script can be run from a software editing GUI, the command line, or by double clicking on the program.                                                                  ##
##If run from the command line, the program accepts two arguments. The first argument is interpreted as the input file name/path and the second the output name/path.          ##
##Output file should have the extension .csv for use with the database                                                                                                         ##
##Ensure that the global variable "database" is set to the correct database (development or production)                                                                        ##
##Note: Accessing the database to retrieve dicounter lengths can be slow and the script may take a few minutes to run for large files                                          ##
#################################################################################################################################################################################


import sys
from datetime import datetime, timedelta ##To create random, always unique timestamps for tests where no timestamp was recorded
##sys.path.append("../DatabaseQueryTool.py")
import DatabaseQueryTool ##To retrieve information from the database

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

lines = []
outFileName = ""
database = ""

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

##Function to reformat data and write it to the output file
##Desired ouput string is in the following format:
##Di-counter Number,Voltage,Temperature ( C ),Time Stamp,Source Position (cm from side A),Condition,Flash Rate,A1,A2,A3,A4,B1,B2,B3,B4
def processData():
    global lines, outFileName, database
    outputLine = ""
    lnComponents = []
    testID = [] ##e.g dicounter_100_from_A_tester-1~1 separated by "_" tokens as [dicounter, 100, from, A, tester-1~1]
    prevIDs = {}
    diSN = 0    
    hasTimeStamp = False
    lineNum = 0
    
    outputFile = open(outFileName, "a+") ##Allows appending and will create new file if it doesn't already exist

    #Write a header line to the output file
    outputFile.write("Dicounter_ID,BiasV,Temp,Timestamp,LED_dist_from_SideA,sourceType,sourceRate,A1,A2,A3,A4,B1,B2,B3,B4,S1(N/A),S2(N/A),S3(N/A),S4(N/A),Comments\n")
                     
    for line in lines:
        outputLine = ""
        lnComponents = line.split()

        ##Safegaurd against empty or just-newline-character lines
        if len(lnComponents) == 0:
            continue

        ##Parse out dicounter SN and add to output line with correct prefix
        testID = str(lnComponents[0]).split("_")
        try:
            diSN = int(testID[1])
            if diSN < 100: ##Dicounter SN 100 is the earliest dicounter which is stored in the database
                continue
            outputLine += "di-" + testID[1] +","
        except: ##Print error message and skip line if an invalid (non-integer) dicounter serial number
            print "Invalid dicounter serial number: " + line
            continue

        ##Check for duplicate tests - print any duplicates to the console
        if prevIDs.has_key(lnComponents[0]):
            print "DUPLICATE TEST: " + lnComponents[0] + " at line " + str(lineNum) + " and previously at line " + str(prevIDs[lnComponents[0]])
        else:
            prevIDs[lnComponents[0]] = lineNum
        

        ##Unnecessary after introduction of tester ID
        ##Remove any additional characters joined to the side (e.g. dicounter_322_from_A~1 needs the "~1" removed from the end in order to read LED location)
        ## if len(testID[3]) > 1:
        ##     testID[3] = testID[3][0]

        ##Add default entries for voltage and temperature to the output line
        outputLine += "-1,-1,"


        ##Add timestamp or blank timstamp filler to output line
        hasTimeStamp = False
        try:
            timeStampTest = int(lnComponents[1])
            hasTimeStamp = False
        except:
            hasTimeStamp = True
            
        if hasTimeStamp:
            timeStamp = lnComponents[1]
            outputLine += timeStamp[5:7] + "/" + timeStamp[8:10] + "/" + timeStamp[0:4] + " " + timeStamp[11:16] + ","
        else:
            ##Each test must have a unique timestamp. Therefore, if no real timestamp is present, the test is assigned a value equal to the current time plus 10000 days plus
            ##the line number in the file. This ensures that each timestamp is unique and that fake timestamps are obvious (they occur several decades later...)
            fakeTimeStamp = datetime.now() + timedelta(days = (10000 + lineNum))
            outputLine += fakeTimeStamp.strftime("%m/%d/%Y %H:%M,")

        #Skip dicounter if not in datbase
        ledPos = calcBsideLedPos(database,diSN)
        if ledPos < 0:
            print "WARNING: " + str(diSN) + " could not be found in the database - skipping"
            continue
        
        ##Add LED position,"led" identifier,, default flash rate, data 
        if testID[3] == "A" or testID[3] == "a":
            if hasTimeStamp:
                outputLine += "0,led,-1,-1,-1,-1,-1," + lnComponents[2] + "," + lnComponents[3] + "," + lnComponents[4] + "," + lnComponents[5] + ",-1,-1,-1,-1"
            else:
                outputLine += "0,led,-1,-1,-1,-1,-1," + lnComponents[1] + "," + lnComponents[2] + "," + lnComponents[3] + "," + lnComponents[4] + ",-1,-1,-1,-1"
        elif testID[3] == "B" or testID[3] == "b":
            if hasTimeStamp:
                outputLine += str(ledPos) + ",led,-1," + lnComponents[2] + "," + lnComponents[3] + "," + lnComponents[4] + "," + lnComponents[5] + ",-1,-1,-1,-1,-1,-1,-1,-1"
            else:
                outputLine += str(ledPos) + ",led,-1," + lnComponents[1] + "," + lnComponents[2] + "," + lnComponents[3] + "," + lnComponents[4] + ",-1,-1,-1,-1,-1,-1,-1,-1"
        else: ##Print error message and skip line if LED side identifier is incorrect (i.e. not "A","a","B", or "b")
            print "Invalid LED side identifier: " + line
            continue

        ##Add tester ID to the comment field
        outputLine += "," + testID[4] + "\n"      
        
        outputFile.write(outputLine)
        lineNum += 1
        
    outputFile.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to create an obviously fake time stamp for early data which did not have timestamps
def fakeTimeStamp():
    now = datetime.now()
    tDelta = timedelta(days = 10000)
    fakeTimestamp = now + tDelta

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to get length of dicounter from database and use it to calculate the proper position of the LED on B-side
def calcBsideLedPos(database,diSN):
    fetchCondition = "di_counter_id:eq:di-" + str(diSN)

    try:
        diLength = float(DatabaseQueryTool.query(database,"di_counters","length_m",fetchCondition)[0])
        ledPosition = int(diLength * 100)
    except:
        try:
            diLength = float(DatabaseQueryTool.query(database,"di_counters","length_m",fetchCondition)[0])
            ledPosition = int(diLength * 100)
        except:
            ledPosition = -1

    return ledPosition
    
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
##Program driver function
def main(argv):
    global database
    print "Which database would you like to be used?"
    print 'Enter "d" for development or "p" for production'
    dbChoice = raw_input()
    if dbChoice.upper() == "D":
        database = "mu2e_hardware_dev"
    else:
        database = "mu2e_hardware_prd"
    
    getInput()
    processData()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Primary program execution
if __name__ == "__main__":
    main(sys.argv)

    

