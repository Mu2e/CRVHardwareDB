##Script to parse out keys from guiDiounters.py error messages. Prints all unique keys which were not found in a database table.
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##07/29/17
##12/21/17 - Added prompts for input and output filenames
##12/30/17 - Addded message if no missing keys were found


print "Enter a filename containing the error messages you wish to parse:"
inFilename = raw_input()

inputFile = open(inFilename,"r")

print "Enter a name for the output file"
outFilename = raw_input()
outputFile = open(outFilename,"w")

lines = inputFile.readlines()
outputLines = []

outputFile.write("""The following are all of the keys that were not recognized as being in one of the tables in the database.
Duplicates and errors saying that dicounters were already present have been removed.
Blanks lines indicate blank scintillator ids.\n\n""")

for line in lines:
    if line.startswith("DETAIL:") and line[-8:] != "exists.\n":
        key = str(line.split("(")).split(")")[1][5:]
        if key not in outputLines:
            outputLines.append(key)
            outputFile.write(key + "\n")

if len(outputLines) == 0:
    outputFile.write("No Missing Keys")


inputFile.close()
outputFile.close()

