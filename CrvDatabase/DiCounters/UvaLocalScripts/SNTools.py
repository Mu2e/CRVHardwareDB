##Serial number verification tools for pre-upload data verification
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##10/25/17 - Initial version completed
##11/29/17 - Fully tested
##12/06/17 - Added statement printing the query in progress

import DatabaseQueryTool
from collections import Counter

##Function to check for duplicate serial numbers
##Accepts a list of serial numbers
##Prints each duplicate serial number and its frequency
def checkForDuplicateSNs(sns, outputFile = None):
  snCounter = Counter(sns) ##Counts the frequency of each serial number in sns
  noDuplicates = True

  if outputFile == None:
    print "\nDuplicate Dicounters: \"(Serial Number, Frequency)\""
    for sn in snCounter:
      if snCounter[sn] > 1:
        print "(" + str(sn) + ", " + str(snCounter[sn]) + ")"
        noDuplicates = False

    if noDuplicates:
      print "No duplicates"
    print 
  else:
    outputFile.write("Duplicate Dicounters: \"(Serial Number, Frequency)\"\n")
    for sn in snCounter:
      if snCounter[sn] > 1:
        outputFile.write("(" + str(sn) + ", " + str(snCounter[sn]) + ")\n")
        noDuplicates = False

    if noDuplicates:
      outputFile.write("No duplicates")
    outputFile.write("\n")


##Function to check if dicounters have already been stored in the "Dicounters"
##table of the database.
##-Accepts a list of serial numbers
##-Prints the serial numbers (dicounters) which have already been stored in the 
##database and will therefore return an "already exists" error when uploading
def checkIfDicountersInDB(sns, database = "mu2e_hardware_dev", outputFile = None):
    
  alreadyInDB = []
  fetchCondition = ""
  
  sns = set(sns) ##Removes duplicates from the list to reduce number of necessary queries
  
  print "\nQuerying database for..."
  for sn in sns:
    fetchCondition = "di_counter_id:eq:di-" + str(sn)
    
    print "di-" + str(sn)

    if len(DatabaseQueryTool.query(database,"di_counters","di_counter_id",fetchCondition)) > 0:
      alreadyInDB.append(sn)

  print"Finished querying"

  alreadyInDB.sort()

  if outputFile == None:
    print "\nDicounters which are already in the database: \"Serial Number\""
    for sn in alreadyInDB:
      print sn
    print 
  else:
    outputFile.write("\nDicounters which are already in the database: \"Serial Number\"\n")
    for sn in alreadyInDB:
      outputFile.write(sn)
      outputFile.write("\n")
    outputFile.write("\n")

  return alreadyInDB
