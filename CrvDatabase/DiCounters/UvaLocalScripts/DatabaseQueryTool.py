##Database query and information retrieval tool
##Utilizes database access tools written by Merril Jenkins at USAL
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##Based off databaseConfig.py and DataLoader.py written by Prof. Jenkins of USAL
##09/07/17 - Initial version completed - query method can be called by other functions
##09/13/17 - Completed independent run-mode functionality
##01/09/18 - Added paths to DataLoader.py and databasConfig.py so script works in proper file structure.

##################################################################   Instructions   #################################################################################
##-This script can accept parameters from the command line, through prompting the user, or its query functionality can be called from another module.              ##
##-If called from the command line, the arguments expected are:  <database> <table> <columns> OPTIONAL<fetchCondition> OP<order> OP<numRowsLimit> OP<echoURL>(T/F) ##
##-If not enough command line arguments are passed, the script will prompt user for query parameters                                                               ##
##-Names are case sensitive and there are no protections against mis-entered paramters. Any parameter that is incorrectly entered or does not math a value in the  ##
##  database will cause the script to fail.                                                                                                                        ##
#####################################################################################################################################################################

import sys
sys.path.append("../../Utilities/DataLoader.zip")
sys.path.append("../CrvUtilities/crvUtilities.zip")
from databaseConfig import * 
from DataLoader import *

database = ""
table = ""
columns = ""
fetchCondition = None
order = None
limit = None
echoURL = False

toFile = False
outputFilename = ""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Function to query the database using DataQuery.query()
##Args:
##      database - The name of the database to be queried.  (This database must be in QueryEngine's configuration file.)
##      table - The name of the table to query on.
##      columns - A comma seperated string of the table columns to be returned.
##      fetchCondition - (optional) <column>:<op>:<value> - can be repeated; seperated by ampersand (&)
##          op can be: lt, le, eq, ne, ge, gt
##      order - (optional) A comma seperated string of columns designating row order in the returned list.
##          Start the string with a minus (-) for descending order.
##      limit - (optional) - A integer designating the maximum number of rows to be returned.
##
##Returns results as a list
##For more information: https://cdcvs.fnal.gov/redmine/projects/qengine/wiki
def query(database,table,columns,fetchCondition =None,order=None,limit=None,echoURL=False):
    db_config = databaseConfig()
    if database == "mu2e_hardware_dev":
        queryURL = databaseConfig.getQueryUrl(db_config)
    else:
        queryURL = databaseConfig.getProductionQueryUrl(db_config)
    db_dataLoader = DataQuery(queryURL)
    
    queryResults = []
    queryResults = DataQuery.query(db_dataLoader,database,table,columns,fetchCondition,order,limit,echoURL)
    
    return queryResults[:-1]    

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##A function to obtain and assign values to the paramters needed to query the database.
##Accepts values from command line arguments passed to the function call or by prompting the user
def getQueryParameters():
    global database,table,columns,fetchCondition,order,limit,echoURL,toFile,outputFilename

    numArgs = len(sys.argv)
    if numArgs >= 4:
        database = sys.argv[1]
        table = sys.argv[2]
        columns = sys.argv[3]
        if numArgs >= 5:
            fetchCondition = sys.argv[4]
        if numArgs >= 6:
            order = sys.argv[5]
        if numArgs >= 7:
            limit = sys.argv[6]
        if numArgs >= 8:
            erchoURL = sys.argv[7]
    else:
        ##Database selection
        print '\nSelect which database you wish to query: Enter "0" for Development or "1" for Production: '
        selector = int(raw_input())
        if selector == 0:
            database = "mu2e_hardware_dev"
        elif selector == 1:
            database = "mu2e_hardware_prd" ###############################Needs the correct name for the production database

        ##Table selection
        print '\nSelect which table you wish to query: Enter "0" for Dicounters, "1" for Dicounter Tests, "2" for Modules, or "3" for Module Tests: '
        selector = int(raw_input())
        if selector == 0:
            table = "di_counters"
        elif selector == 1:
            table = "di_counter_tests"
        elif selector == 2:
            table = "modules"
        elif selector == 3:
            table = "module_tests"

        ##Column selection
        print "\nEnter the columns you wish to query as a comma separated list. \n"
        if selector == 0:
            print 'Column options in Dicounters are:\n "di_counter_id","fiber_id","length_m","manf_date","manf_loc","fgb_man","location",'
            print '"scint_1","scint_2","module_id","module_layer","layer_position","comments","create_time","create_user","update_time","update_user"\n'
        elif selector == 1:
            print 'Colunm options in Dicounter Tests are: \n'
            print '"di_counter_id","test_date","sipm_location","current_amps","current_amps_date","light_source","flash_rate_hz","temperature",'
            print '"distance","distance_vector","sipm_test_voltage","comments","create_time","create_user","update_time","update_user"\n'
        elif selector == 2:
            print "Column options in Modules are: \n"
            print '"module_id","module_type","location","width_mm","height_mm","thick_mm","expoxy_lot","aluminum","deviation_from_flat_mm","comments",'
            print '"construction_date","create_time","create_user","update_time","update_user"\n'
        elif selector == 3:
            print "Column options in Module Tests are: \n"
            print '"module_id","test_date","light_yield_source","light_yield_avg","light_yield_stdev","comments","create_time","create_user","update_time","update_user"\n'
        raw = raw_input()
        if raw != "":
            columns = raw

        ##Fetch condition
        print "\nOPTIONAL: Enter a condition to be used to select data in the form. Default is all data: \n"
        print "<column>:<op>:<condition>     (e.g.   di_counter_id:eq:di-300)\n"
        print "Allowed operations are: lt, le, eq, ne, ge, gt\n"
        raw = raw_input()
        if raw != "":
            fetchCondition = raw
        
        ##Order
        print "\nOPTIONAL: Enter a comma separated list of columns in the order which you wish them to be displayed. Default is table order:\n"
        raw = raw_input()
        if raw != "":
            order = raw

        ##Row number limit
        print "\nOPTIONAL: Enter the maximum number or rows you wish to be retreived/displayed. Default is all: "
        raw = raw_input()
        if raw != "":
            limit = raw

        ##Echo URL
        print '\nOPTIONAL: Enter "True" if you would like the queried URL to be echoed or "False" otherwise:'
        raw = raw_input()
        if raw != "":
            echoURL = raw

    ##Print to file selection   
    print '\nWould you like the results to be printed to a file?    Enter "y" or "n":   '
    inp = raw_input()
    if inp == "y":
        toFile = True
        print "Enter a name for the output file. Note: file will be appended to if it already exists: "
        outputFilename = raw_input()
    else:
        toFile = False

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

##Driver function
def main(argv):
    global database,table,columns,fetchCondition,order,limit,echoURL,toFile,outputFilename
    queryResults = []

    getQueryParameters()
    
    queryResults = query(database,table,columns,fetchCondition,order,limit,echoURL)
    
    if toFile:
        outputFile = file(outputFilename,"a+")
        outputFile.write(str(queryResults)) 
        outputFile.close()
    else:
        print "\n##########################   Results   ##########################"
        print queryResults

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Primary Program Execution
if __name__ == "__main__":
    main(sys.argv)

        
