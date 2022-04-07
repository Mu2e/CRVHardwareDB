##Script to convert Google Drive format dicounter_serial_numbers spreadsheet to the form needed for Merrill Jenkins' script DiCounters.py (or GUI) to send data to the CRV Production Database
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##06/09/17 - Initial version completed
##07/13/17 - Modified instructions to include restrictions on output file names
##07/24/17 - Removed lines which deleted trailing commas (not necessary if input file is properly formatted)
##07/25/17 - Replaced hardcoded file paths with prompts for filenames. Functionalized program. Made it possible to run script from the command line.
##06/06/18 - Completely re-wrote processData() to be much cleaner and easier to edit - added capacity to handle production scintillator
##06/19/18 - Modified processData() to be able to determine what lines to ignore when processing
##06/22/18 - Modified to not add prefixes to production fibers


#################################       INSTRUCTIONS AND REQUIREMENTS BEFORE RUNNING:      ##################################################
##-Input file and output file should have .csv extensions                                                                                   #
##-Input file cannot have any commas or special characters used in it any point. Change commas to semi-colons or other punctuation.         #
##-Input file columns must be at least as wide as the widest attribute in said column. Otherwise, extraneous commas will be appended to line#
##-Fields in the input file should not have prefixes (e.g. 117, not di-117; 123456789, not fiber_lot-123456789) - remove any such prefixes  #
##-Modify the filename and path for the output file as desired and to be suitable for the system. Do not use spaces or special characters.  #
##-The script can be run from IDLE, the command line ,or simply by double clicking the file.                                                #
##-If two arguments are passed to the script from the command line, the first will be interpreted as the input filename and the second, the #
##output filename. In all other cases, the script will prompt the user for both filenames.                                                  #
#############################################################################################################################################

import sys


lines = []
inFileName = ""
outFileName = ""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to get and assign input and output filenames and read from inputFile
def getInput():
    global outFileName
    inputFile = None
    
    if len(sys.argv) != 3: ##Control path if run as an executable or with incorrect number of arguments passed to it - Prompts user for names
        inputFile = None
        while inputFile == None:
            print "\nEnter an input file name/path:  "
            inFileName = raw_input()  
            inputFile = readFile(inFileName, inputFile)

        print "Enter a name for the output file: "
        outFileName = raw_input()
    else: ##If correct number of arguments passed (2) from command line, first is used as inputFileName, second as outFileName
        readFile(sys.argv[1], inputFile)
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

##Function to process and re-format data to the desired output 
def processData():
    global lines
    
    ##Open a new file to write the data to
    otptFile = open(outFileName,"w")

    otptFile.write(lines[0])
    
    for line in lines:

        lnComponents = line.split(",")

        ##Bypass dicounters which have not been built yet (no manufacture date)
        if len(lnComponents[2]) < 1:
            continue

        ##Add "di-" prefix to each dicounter serial number
        if lnComponents[0][0].isdigit():
            lnComponents[0] = "di-" + lnComponents[0]
        else:
            continue

        ##Add prefix to scintillator ID number
        ##Scintillator #1
        if len(lnComponents[3]) > 4: ##If pre-production extrusion
            lnComponents[3] = "RD" + lnComponents[3]
        elif int(lnComponents[0][3:]) > 1000 and len(lnComponents[3]) > 0: ##If production extrusion and ID number present
            lnComponents[3] = "Mu2e-CRV" + lnComponents[3]
        elif int(lnComponents[0][3:]) in range(381,385):
            lnComponents[3] = "Mu2e-CRV" + lnComponents[3]
                
        ##Scintillator #2
        if len(lnComponents[4]) > 4: ##If pre-production extrusion
            lnComponents[4] = "RD" + lnComponents[4]
        elif int(lnComponents[0][3:]) > 1000 and len(lnComponents[3]) > 0: ##If production extrusion and ID number present
            lnComponents[4] = "Mu2e-CRV" + lnComponents[4]
        elif int(lnComponents[0][3:]) in range(381,385):
            lnComponents[4] = "Mu2e-CRV" + lnComponents[4]
################            


        ##Add "fiber-lot-" prefix to fiber lot numbers
        if len(lnComponents[6]) > 0 and lnComponents[6][0].isdigit():
            lnComponents[6] = "fiber_lot-" + lnComponents[6]
        elif len(lnComponents[6]) < 5:
            lnComponents[6] = "fiber_lot-none"

        ##Add "0" to each line without comments
        if len(lnComponents[17]) < 2:
            lnComponents[17] = "0\n"

        ##Write line to file
        for comp in range(len(lnComponents) - 1):
            otptFile.write(lnComponents[comp] + ",")
        otptFile.write(lnComponents[len(lnComponents) -1])

    otptFile.close()

            
     
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Program driver function
def main(argv):
    getInput()
    processData()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Primary program execution
if __name__ == "__main__":
    main(sys.argv)
