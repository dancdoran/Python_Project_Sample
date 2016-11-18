
""" 
    Run_SFCI_Tests.py - Copyright 2016, Dan Doran, Boulder CO.

    This is the Top-Level Python3 script to run *all* of the testcases in our test case
    repository by default, or from a list of tests, or from a single test case file.
    It reads in the Expected-PASS and Expected-FAIL test case definition files
    in the test repository and writes a Test_Run_Result.report file (ascii) plus an API.log file.

    This test infrastructure is designed to test the SolidFire Chess Service API "MakeMove" Method.
    In addition to python scripts for running tests against the API, it also contains
    interactive scripts to quickly generate new initial testcase chess board 'boardState's
    and testcase definition files (one definition file per test). This way overlooked
    test situations can be quickly generated & added without touching any of the script
    source files.

    REQUIREMENTS:  Python 3.1 or better
                   Python 'json-rpc' V3, 'time' and 'requests' python modules installed
                   Ubuntu Linux 14.04 or better, can also be run on windows
                   Web access for machine running the tests (To access the SFCS server).

    USAGE: python Run_SFCS_Tests.py [-l Path_to_list_of_testcase_files] [-s Path_to_single_test_file]
           Path_to_list_of_testcase_files: optional ascii file with one testcase name on each line
           Path_to_single_test_file: optional single test case definition file
           (Default is to run all tests in the test case directories.)

"""

# Required Python3 modules (Date, Time, File handling, Blather control...)
import sys
import time
import os
import json      # Used for posting to SFCS API
import requests  # Used for posting to SFCS API
import utilities # Local Module


# Global vars and initializations
usagemessage = "Usage: python Run_SFCS_Tests.py [-l path_to_testcase_list_file] [-s path_to single_testFile]\n\
              -l path_to_testcase_list_file: Optional path to ascii file with one testcase definition file on each line\n\
              -s path_to_single_testFile: Optional path to a single test case definition file.\n\
              (Default is to run all tests in the test case directories.)\n"
todaysDate = time.strftime("%m_%d_%Y") # mm/dd/yyyy - 'mericun format
timeStart = time.strftime("%H_%M_%S")  # 24 Hour format
testRunResultFileName = "Test_Results_%s_%s.report" % (todaysDate,timeStart)
testAPILogFileName = "Test_API_%s_%s.log" % (todaysDate,timeStart)
testCaseFileName = ""
rootTestDir = os.getcwd()  # Always run from where we start the script
fullPathTestFileName = ""  # for portability & consistency, all files opened with the full path.
expPassTestDir = os.path.join(rootTestDir, "expPassTestDir") # Location of tests we expect to run w/o errors
expFailTestDir = os.path.join(rootTestDir, "expFailTestDir") # Location of tests we expect to return errors
expPassExt = ".passtest"
expFailExt = ".expfail"
numTests = 0 # Our total count of testcases to be run
# Params supplied for or inferred from API request
expFailTestParams = ("testName : ","Description : ","request : ","errorCode : ") 
expPassTestParams = ("testName : ","Description : ","request : ",'"gameState": ',\
                     '"playerState": ',"movedPieces : ","expectedResponsePieces : ")

# Variables used in posting API requests
apiurl = "http://chesstest.solidfire.net:8080/json-rpc"
apiheaders = {'content-type': 'application/json'}
apiRequest = ""
responseApi = ""
apiMessageid = 1
# Variables used for building API requests and checking API responses
whitePieceList = ['P','R','N','B','Q','K']
blackPieceList = ['p','r','n','b','q','k']
gameStateList = ['""', "check", "checkmate", "stalemate"]
requestBoard = [] # Starting board we send in our request
numRequestBoardPieces = 0  # How many piece objects are on the request boardState
numMovedPieces = 0 # How many pieces did we move (1 except 2 for castling & capture).  Should *not be in response
numNewPieces = 0 # Pieces that have different locs on response from request board, 1, except 2 for castling
numExpectedPieces = 0 # How many piece objects we expect on the response boardState
numResponsePieces = 0 # Number of pieces on the reponse board
expectedErrorCode = 0 # If this has a value, then we're dealing with an expected error case
gameState = "" # Expected response gameState
playerState = ""  # Expected response playerState. Should always be opposite of request playerState
isExpectedErrorCase = False # Bool to tell us if we're dealing with a functional or expected error case
receivedResponseError = False # Did we recieve an error back from the SFCS API
# END Global vars and initializations

#********************************
# Function Definitions Begin Here
#********************************

# Alias some print commands to direct blather to report & log files
def printterm(data):
    print(data)

def printreport(data):
    print(data)
    with open(testRunResultFileName, "a") as reportFile:
        print(data, file=reportFile)

def printlog(data):
    print(data)
    with open(testAPILogFileName, "a") as logFile:
        print(data, file=logFile)

def printall(data):
    print(data)
    with open(testRunResultFileName, "a") as reportFile:
        print(data, file=reportFile)
    with open(testAPILogFileName, "a") as logFile:
        print(data, file=logFile)
# END printing aliases

# Get the requestBoard from the apiRequest
def GetRequestBoardState(apiRequest):
    # turn our apiRequest string to a dict
    apiRequest = eval(apiRequest)
    params = apiRequest.get("params")
    requestBoard = params.get("boardState")
    # Make sure we got something  - We'll let the API determine the goodness of our boardState
    if requestBoard == None: 
        return ("Process ERROR: GetRequestBoardState gave us nothing from %s\n" % fullPathTestFileName)
    else:
        return requestBoard
# END GetRequestBoardState()

# Count the number of Piece objects on a board - works for request & response boardStates
def GetNumBoardPieces(boardState):
    numPieces = 0
    numPieces = utilities.CountItemsInList(boardState)
    # Some chess math
    if numPieces == 0 or numPieces >= 33:
        return ("Process ERROR: boardState has %d Pieces on it.  Must be between 1 & 32." % numPieces)
    return numPieces
# END GetNumBoardPieces()

# Expected Error cases will have an expected error code from the API response
def GetExpectedErrorCode(fullPathTestFileName):
    errorDict = {}
    errorCode = 0
    errorValStr = utilities.GetFileValue(fullPathTestFileName, "errorCode")
    errorValStr = errorValStr.rstrip() # Trim off \n
    #printterm("DEBUG: Expected Response Error Dict line is %s" % errorValStr)
    errorDict = eval(errorValStr)
    if errorDict == {}:
        return ("Process ERROR: Our testFile returned an empty value on the 'errorCode' line")
    # Now get the integer errorCode
    errorCode = errorDict.get("code")
    if errorCode == 0:
        return ("Process ERROR: Our testFile returned a '0' value on the 'errorCode' line")
    else: # We got something...
        return errorCode
    return ("Process ERROR: we failed to retrieve any expected errorCode from our expFail test file.")
# END GetExpectedErrorCode

# What gameState value were we expecting in the API response?
def GetExpectedGameState(fullPathTestFileName):
    expectedGameState = ""
    expectedGameState = utilities.GetFileValue(fullPathTestFileName, '"gameState"')
    if expectedGameState.startswith("Process ERROR"):
        return expectedGameState
    elif expectedGameState == "":
        return ("Process ERROR: we failed to retrieve any expectedGameState value from our test file.")
    else:
        expectedGameState = expectedGameState[2:-2] # strip off leading & trailing quotes, spaces & ]\n
        return expectedGameState
# END GetExpectedGameState

# Functional Tests - What playerState value ('w' or 'b') were we expecting in the API response?
def GetExpectedPlayerState(fullPathTestFileName):
    expectedPlayerState = "" 
    expectedPlayerState = utilities.GetFileValue(fullPathTestFileName, '"playerState"') # w/ quotes
    if expectedPlayerState.startswith("Process ERROR"):
        return expectedPlayerState
    elif expectedPlayerState == "":
        return ("Process ERROR: we failed to retrieve any expectedPlayerState value from our test file.")
    else:
        expectedPlayerState = expectedPlayerState[2:-2] # strip off leading & trailing quotes, spaces & ]\n 
        return expectedPlayerState
# END GetExpectedGameState

# Get a list of moved and captured pieces which we should *not* see in the response boardState
def GetMovedPieces(fullPathTestFileName):
    movedPieces = []
    movedPiecesStr = utilities.GetFileValue(fullPathTestFileName, "movedPieces")
    #printterm("DEBUG: Expected movedPieces list string is %s" % movedPiecesStr)
    if movedPiecesStr.startswith("Process ERROR"):
        return movedPiecesStr
    # Turn it back into a list
    movedPieces = eval(movedPiecesStr)
    if movedPieces == []:
        return ("Process ERROR: Our testFile returned an empty list for the movedPieces entry")
    else:
        return movedPieces
    return ("Process ERROR: we failed to retrieve any movedPieces from our test file.")
# END GetMovedPieces()

# Get a list of new moved piece location(s) that we expect to see in the response boardState
def GetExpectedResponsePieces(fullPathTestFileName):
    expectedResponsePieces = []
    expectedResponsePiecesStr = utilities.GetFileValue(fullPathTestFileName, "expectedResponsePieces")
    #printterm("DEBUG: Expected expectedResponsePieces list string is %s" % expectedResponsePiecesStr)
    if expectedResponsePiecesStr.startswith("Process ERROR"):
        return expectedResponsePiecesStr
    # Turn it back into a list
    expectedResponsePieces = eval(expectedResponsePiecesStr)
    if expectedResponsePieces == []:
        return ("Process ERROR: Our testFile returned an empty list for the expectedResponsePieces entry")
    else:
        return expectedResponsePieces
    return ("Process ERROR: we failed to retrieve any expectedResponsePieces from our test file.")
# END GetExpectedResponsePieces()
            
# GetResponseAPI: Function to submit our apiRequest to the SFCS API and return what we get back
def GetResponseAPI(apiRequest):
    responseApi = ""
    json_str = json.dumps(apiRequest) 
    #printterm("DEBUG: json_str after json.dumps(apiRequest) is:")
    #printterm(json_str)
    data = json.loads(json_str)
    #printterm("\nDEBUG: 'data' after json.loads(json_str) that we're posting to API is:\n")
    #printterm(data)
    responseApi = requests.post(apiurl, data, headers=apiheaders).json()
    #printterm("\nDEBUG: The returned responseApi is:\n")
    #printterm(responseApi)
    return responseApi
#END def GetResponseAPI(apiRequestAPI)

# GetFinalTestResult(): Function to check our response from the SFCS API against what we were told to
# expect from the test definition file.  
# PROGRAMMING NOTE: We can't do a simple Diff against an expected response file since the order
# the response params and the boardState vary with each call.  We need to check the
# individual elements to see if they return as expected.
#
# We have Five possible results from our API Response test:
# 1) The API request checker returns empty or with a Process ERROR
# 2) "functionalTestPASS": - Test that did not expect an error has a correct game reponse
# 3) "functionalTestFAIL": - We recieved an unexpected ERROR code or API response incorrect
# 4) "expectedErrorCasePASS":  Test API response is the expected API error code
# 5) "expectedErrorCaseFAIL":- Test API did not throw expected error code or unexpectedly sent a full API response
def GetFinalTestResult(responseApi, expectResponseList, isExpectedErrorCase, receivedResponseError, requestBoard):
    testStatus = ""
    # Let's Deal with expected error cases first
    if isExpectedErrorCase and receivedResponseError:
        # Did we get the correct ErrorState returned to us?
        responseError = responseApi.get("error")
        #printterm("DEBUG: The error dict we got from the API response is: %s" % str(responseError))
        printterm("\n")
        if responseError == None:
            testStatus = ("functionalTestFAIL: API response 'error' dict is empty.")
            return testStatus
        # Get the response error code
        responseErrorCode = 0
        responseErrorCode = responseError.get("code")
        #printterm("DEBUG: The error code value we got from the API response is: %d" % responseErrorCode)
        #printterm("DEBUG: The expectResponseList for this expected error case is %s" % expectResponseList)
        expectedErrorCode = expectResponseList[0] # Code should be only entry
        #printterm("DEBUG: Comparing expected code value of %d to returned response code value of %d ..." % (int(expectedErrorCode), responseErrorCode))
        if responseErrorCode == 0:
            testStatus = ("Process ERROR - We have an expected Error Test Case, but no expected error code value")
            return testStatus
        elif responseErrorCode == int(expectedErrorCode):
            testStatus = "expectedErrorCasePASS" # Don't need to send anything more
            return testStatus    
        else: # Not the error we were expecting
            testStatus = "expectedErrorCaseFAIL\nExpecting: %s\nReceived: %s" % (expectedErrorCode, responseErrorCode)
            return testStatus

    elif isExpectedErrorCase and not(receivedResponseError): # Accidentally passed the API...
        expectedErrorCode = expectResponseList[0] # Code should be only entry
        testStatus = "expectedErrorCaseFAIL\nExpecting: %s\nReceived: %s" % (expectedErrorCode, str(responseApi))
        return testStatus

    elif not(isExpectedErrorCase) and receivedResponseError: # Got an error back for a test we thought should pass
        testStatus = ("functionalTestFAIL: Received unexpected API response error %s" % str(responseApi))
        return testStatus

    elif not(isExpectedErrorCase) and not(receivedResponseError): # Got a full API response for a functional test
        printterm("Functional Test - compare response values with expected values")
        # OK, we're dealing with a functional test.  We need to parse
        # out the values of interest from the responseApi string, and check
        # them against the expected values we should already have.

        # We can't use 'if value in requestApi' since it comes back with single quotes and different
        # spacing around the key:value separator.  So we need to bust up the nested dicts & lists.   
        #  Break the responseApi Dict apart
        #printterm(str(responseApi))
        #printterm("\n")
        # Check the response message "id" value - should be 1
        respIDVal = 0 
        respIDVal = (responseApi["id"])
        #printterm(str(respIDVal))
        #printterm("\n")   
        if respIDVal != apiMessageid:
            testStatus = ("functionalTestFAIL: response message ID value of %d is not %s" % (respIDVal, apiMessageid))
            return testStatus 

        # make sure we have something in the 'result' dict...
        resultValue = ""
        resultValue = responseApi.get("result")
        #printterm("DEBUG: 'result :' value in response API is %s" % (str(resultValue)))
        if resultValue == "":
            testStatus = ("functionalTestFAIL: API response 'result' entry is empty.")
            return testStatus
        
        # Break down the resultDict further and check each value
        # Do we have a 'gameState' dict entry and is it what we expect?
        # Since "" is a valid gameState value, set it to BOGUS to detect an error
        responseGameState = "BOGUS"
        responseGameState = resultValue.get("gameState")
        #printterm("DEBUG: gameState value in response came back as %s" % responseGameState)
        # Since an empty val is a legal gamestate, swap in ""
        if responseGameState == None:
            responseGameState = ""
        # See if it's the gameState we expected
        expectedGameState = expectResponseList[0] # Order is [expectedGameState, expectedPlayerState, movedPieces, expectedResponsePieces]
        if responseGameState != expectedGameState or responseGameState == "BOGUS":
            testStatus = ("functionalTestFAIL: API response of gameState: %s does not equal the expected gameState: %s\n" % (responseGameState,expectedGameState))
            return testStatus

        # See if it's the playerState value we expectd
        responsePlayerState = ""
        responsePlayerState = resultValue.get("playerState")
        if responsePlayerState == None:
            testStatus = ("functionalTestFAIL: No playerState in API response.")
            return testStatus
        #printterm("DEBUG: response playerState value is: %s" % responsePlayerState)
        # See if it's the playerState we expected
        expectedPlayerState = expectResponseList[1]
        if responsePlayerState != expectedPlayerState:
            testStatus = ("functionalTestFAIL: API response of playerState: %s does not equal the expected playerState: %s\n" % (responsePlayerState,expectedPlayerState))
            return testStatus  

        # Get the movedPieces and expectedResponsePieces out of the expetResponseList so we can do comparisons of the response board
        movedPieces = expectResponseList[2]
        expectedResponsePieces = expectResponseList[3]

        # Try to get the response boardState value so we can inspect it
        respBSList = resultValue.get("boardState") # Should be a list
        if respBSList == None:
            testStatus = ("functionalTestFAIL: API response boardState is unexpectedly empty!")
            return testStatus
        #printterm("DEBUG: Response board is:\n%s\n" % str(respBSList))
        # See if the response boardState has the expected number of Pieces
        # The expected number of pieces is the number in the requestBoard - movedPieces + expectedResponsePieces
        numRequestBoardPieces = GetNumBoardPieces(requestBoard)
        numMovedPieces = utilities.CountItemsInList(movedPieces)
        numNewPieces = utilities.CountItemsInList(expectedResponsePieces)
        numExpectedPieces = (int(numRequestBoardPieces) - numMovedPieces + numNewPieces)
        # Now get the number of pieces in our API response board
        numResponsePieces = GetNumBoardPieces(respBSList)
        if numResponsePieces != numExpectedPieces:
            testStatus = ("functionalTestFAIL: API response boardState %s contains %d Pieces.  Expected %s\n" % (str(respBSList),numResponsePieces,numExpectedPieces))
            return testStatus  

        # boardState ListChecks.
        # 1) Make sure the movedPieces moved.  The response boardState should *not* have them
        if movedPieces == []:
            testStatus = ("Process ERROR: The expectResponseList did not contain the required movedPieces value.")
            return testStatus
        # Comes back as a list w/ one 2-element piece object, in the form of a dict
        for rpiece in movedPieces:
            # Check that it moved
            if rpiece in respBSList:
                testStatus = ("functionalTestFAIL: API response boardState %s still contains the moved Piece %s." % (str(respBSList),rpiece))
   
        # 2) Make sure the expectedResponsePieces are in the response boardState
        if expectedResponsePieces == []:
            testStatus = ("Process ERROR: the expectResponseList did not contain the required expectedResponsePieces value.")
            return testStatus
        for erPiece in expectedResponsePieces:
            if not(erPiece in respBSList):
                testStatus = ("functionalTestFAIL: API response boardState %s does not contain the expected Pieces %s.\n" % (respBSList,erPieces))
                return testStatus

        # 3) Finally, iterate through the request boardState pieces.  If it's not the moved piece (piecesMoved),
        #    Make sure the piece is still in the reponse boardState.
        if requestBoard == None or requestBoard == []:
            testStatus = ("Process ERROR: GetFinalTestResult() did not get the required requestBoard value.")
            return testStatus
        # We should have our requestBoard now
        # iterate through the request boardState and make sure each piece in in the response boardState 
        # Add the new expected pieces to the request board for comparison
        for rPiece in expectedResponsePieces:
            requestBoard.append(rPiece)
        for piece in requestBoard:
            if piece == {}:
                testStatus = ("Process ERROR: Unable to get a piece object out of the requestBoard")
                return testStatus
            # A piece that moved should not be in the response boardState w/ its original loc
            for mPiece in movedPieces:
                if mPiece in respBSList:
                    testStatus = ("functionalTestFAIL: API response board %s still has the original location of moved piece %s" % (str(respBSList),str(piece)))
                    return testStatus
            # Every piece in the expectedResponsePieces list should be in the response board
            for rPiece in respBSList:
                if rPiece not in respBSList:
                    testStatus = ("functionalTestFAIL: API response board %s does not contain the expected Piece %s" % (str(respBSList),piece))
                    return testStatus
    # If we get here, we should have passed all checks
    return "functionalTestPASS"
# END def GetTestResult(responseApi)

# You'd think python would have a built-in for this...
def GetPercent(part, whole):
  percent = 100 * float(part)/float(whole)
  formatPercent = format(percent, '.1f')
  percentStr = str(formatPercent) + " %"
  return percentStr

# End of function definitions

#*****************************************************************************
# main() main() main() main() main() main() main() main() main() main() main() 
#*****************************************************************************
def main():
    # Print something to the top of all files in case something bombs
    printall("\nExample SolidFire Chess Service API testing scripts & reports.")
    printall("Copyright 2016 - Dan Doran, Boulder, CO\n")
    # Send this opening blather to just the screen.  We will prepend it to the
    # top of the report & log files at the very end of the test.
    openingMessage = '''\n 
      **** Welcome to the SolidFire Chess Service API Testing System. ****\n
           Test Results will be written to 'Test_Results_<date>_<time>.report'.
           All API requests and results will be logged to 'Test_API_<date>_<time>.log.'\n'''
    printterm(openingMessage)
    
    # Get the optional test list file name or test file name from the command line.
    arglen = 0
    arglen = len(sys.argv)
    testListFileName = ""
    singleTestFileName = ""
    fullPathTestFileName = ""
    testFileName = ""
    option = ""
    if arglen >= 4:
        printterm("wrong number of args found!")
        printterm(usagemessage)
        return 0
    if arglen == 2: # Help request?
        option = sys.argv[1]
        # Look for a command help request & post the usage message if found
        if "-h" in option or "-H" in option:
            printterm("Help requested: %s" % option)
            printterm(usagemessage)
            return 0
        else:
            printterm("Unknown option or no testcase info supplied: %s" % option)
            printterm(usagemessage)
            return 0

    if arglen == 3: # Possible list of tests (-l listpath) or single test request (-s testfilepath)
        option = sys.argv[1]
        testarg = sys.argv[2]
        if option == '-l':
            testListFileName = testarg
            printterm("Test list file %s chosen.\nWill read and try to tun testcases in that file.\n" % testListFileName)     
        elif option == '-s':
            singleTestFileName = testarg
            printterm("Single test definition file %s chosen.\nWill try to run just that test\n" % singleTestFileName)
        else:
            printterm("Unkown option %s supplied." % option)
            printterm(usagemessage)
            return 0

    # Write in some opening blather to both the test results file and the screen...
    printreport("This is a test facility that exercises the SFCS API 'MakeMove' method with a variety")
    printreport("of tests definition files expected to either PASS (correct params in result) or produce a")
    printreport("specified Error.\n")
    printall("Search for the string 'FAILED' (all upper case) to go directly to any failing test.\n")

    printall("Date of Test: %s" % todaysDate)
    printall("Time of Test: %s" % timeStart)
    
    # testList building begins...
    testList = [] # A python list of testcase file names
    # See if we have a supplied file containing testcase names
    if option == '-l':
        if testListFileName != "": # Test List File name supplied...
            if os.path.isfile(testListFileName):
                with open(testListFileName, 'r') as testListFile:
                    printall("\nReading in test file names to run from %s..." % testListFileName)
                    for line in testListFile:
                        line = line.rstrip() # clean up
                        # expand to full path
                        fullPathTestFileName = utilities.GetFullPath(rootTestDir, line)
                        testList.append(fullPathTestFileName)
            else:
                printreport("Unable to find test list file '%s'. Please try again.  Exiting" % testListFileName)
                return 1
        else:
            printreport("Empty test list file argument given. Please try again.  Exiting")
            return 1
    # See if we have a single test chosen instead...
    elif option == '-s':
        if singleTestFileName != "":
            # Expand to full path
            fullPathTestFileName = utilities.GetFullPath(rootTestDir, singleTestFileName)
            testList.append(fullPathTestFileName)
        else:
            printreport("No file argument given for '-s' option. Exiting.")
            return 1
    # If no file name is supplied, call 'GetDefaultTests' to gather all test files in the test dirs
    else:
        # Supply the name of the Test Directories here:
        testDirs = [expPassTestDir, expFailTestDir]
        testList = utilities.GetDefaultTests(testList, testDirs)
    # Make sure we found some tests...
    numTests = len(testList)
    if numTests == 0:
        # Print to screen and test report file...
        printreport("ERROR : No test definition files found in the test dirs or supplied.  Exiting.")
        sys.exit(1)
    else: # Found some tests
        printall("\nFound %d test files to run:" % numTests)
        for testFile in testList:
            printall("%s" % testFile)
        printall("\n")

    # We've got our populated fileList. 
    # Metrics for Report Summary
    numPassingTests = 0
    numFailingTests = 0
    numTestsExited = 0

    #============================================
    # START TEST(S) HERE.  RUN ONE TEST AT A TIME
    #============================================
    printall("                **** Beginning SFCS API Tests ****\n")

    for fullPathTestFileName in testList:
        # Get the file base name (including extension)
        testFileName = os.path.basename(fullPathTestFileName)
        #print("DEBUG: fullPathTestFileName is %s" % fullPathTestFileName)
        #print("DEBUG: testFileName in %s is %s" % (testListFileName, testFileName))
        # Get the testName w/o any path or file extensions on fail if we can't find it
        testName = ""
        testName = utilities.GetTestName(fullPathTestFileName)
        if testName == "" or "ERROR" in testName:
            printterm("DEBUG: Returned testname is %s" % testName)
            printall("Process ERROR: Unable to find test case name in file %s" % fullPathTestFileName)
            printall("Moving on to next testcase.\n")
            numTestsExited += 1
            continue      
        
        printall("======================================================================")
        printall("****** Starting test case %s ******\n" % testName)
        # Check the completeness of our test definition file
        # Switch on the file extension - if '.expfail', only check for the request params needed for an expFail test
        isExpectedErrorCase = False # Flag to tell us if this is a funtional or expected error case
        receivedResponseError = False # Flag to tell us if we got one
        fileext = os.path.splitext(testFileName)[1] # returns 2-element tuple, (basename, .ext)
        if fileext == expFailExt:
            testParams = expFailTestParams # Defined Constant Tuples
            isExpectedErrorCase = True
        elif fileext == expPassExt:
            testParams = expPassTestParams   # Defined Constant Tuples
            isExpectedErrorCase = False
        else:
            printall("Process ERROR: Unknown file extension '%s' on TestFileName. Only '%s' and '%s' allowed" % (fileext, expPassExt, expFailExt))
        # Call "CheckTestFile" to see if or test definition file is complete.
        #checkMessage =  CheckTestFile(fullPathTestFileName, testParams)
        #if checkMessage == "" or "GOOD FILE" not in checkMessage:
        #    printall("Process ERROR - incomplete test case definition file '%s' - Exiting." % fullPathTestFileName)
        #    printall(checkMessage)
        #    numTestsExited += 1
        #    sys.exit(1)
        #else:
        #    printall("Test case definition file passed completeness check.\n") 

        # Give us the test name line
        printall("Test: %s specified in test definition file %s\n" % (testName, testFileName))
        # Add the Test Description as well
        testDescription = ""
        testDescription = utilities.GetFileValue(fullPathTestFileName, "Description")
        printall("Test Description: %s" % testDescription)
        printall("***Beginning test run of %s***\n" % testName)
        # Choose whether to expect an error code based on our isExpectedErrorCase flag
        if isExpectedErrorCase: # bool
            printreport("This is an expected Error Case.")
            # Since this is an expected Error Case, we should have an expected errorCode
            expectedErrorCode = GetExpectedErrorCode(fullPathTestFileName)
            # Make sure we got a value back...
            if expectedErrorCode == 0:
                printall("Process ERROR - Problems retrieving our expected error code - Exiting")   
                printall("\n")
                numTestsExited += 1
                continue
            printreport("The Expected API Response Error Code value is: %d" % expectedErrorCode)
        else: # Functional test, not an expected Error case...
            printreport("This is a functional test expected to return a full API response.\n")
        # Run that puppy! Fine the "request : " value in our test files and then
        # submit it to the SolidFire Chess Service API.  The APU should returns a full JSON-RPC result
        # if all that goes well, an ERROR otherwise
        printterm("Get the API Request from the '%s' test definition file...\n" % testName)
        apiRequest = ""
        apiRequest = utilities.GetFileValue(fullPathTestFileName, "request")
        # We should always get an API request back, either good ones or error case ones
        # We have three possible responses for creating our API request:
        # 1) apiRequst empty - Fail as a Process ERROR 
        # 2) apiRequest returns a process ERROR - Fail as a process ERROR
        # 3) full apiRequest returned - continue with the test
        if apiRequest == "":
            printall("Process ERROR: Unexpected empty API request returned for testcase %s" % testName)
            printall("Marking as a Test Exit Error and move on to next testcase.\n")
            numTestsExited += 1
            # Continue on to the next test case...
            continue
        if "Process ERROR" in apiRequest:
            printall("Unexpected 'Process ERROR' returned for test case %s API request:" % testName)
            printall(apiRequest)
            # Continue on to the next test case...
            printall("Continuing on to next test case\n")
            numTestsExited += 1
            continue
        printall("We have an API Request for %s. Submit it to the SFCS API and save to log file.\n" % testName)
        # Write the API Request to just the log file
        printlog("API Request for testcase %s:" % testName)
        printlog(apiRequest)

        # Submit the API Request to the SFCS API call "GetResponseAPI:"
        responseApi = ""
        responseApi = GetResponseAPI(apiRequest)
        # Check for no response or a process ERROR (as opposed to an API Error Code) from our request
        if responseApi == "":
            printall("Process ERROR: Test % Failed to return a valid API response or ErrorCode." % testName)
            printall("SFCS API Response:")
            printall(responseApi)
            printall("Marking as a Test Exit Error and move on to next testcase.\n")
            numTestsExited += 1
            continue

        # We have a non-empty response from the SFCS API
        # Write it to the log file, then see if it's what we expect
        printreport("We have an API Response from the SFCS Server for test %s - Saving to log file.\n" % testName)
        # See if we got an error in our API response - can happen both for ExFail & functional
        if responseApi.get('error'):
            receivedResponseError = True
            printall("Received an 'error' message in the SFCS API response:\n")
            printreport(str(responseApi))
        else:
            printlog("SFCS API Response:")
        printlog(str(responseApi))
        printall("Checking our SFCS API response against the expected response params...")
        testResult = ""
        requestBoard = GetRequestBoardState(apiRequest)
        expectResponseList = [] # List to hold all of our expected response elements
        # If this is an expected error case, we should already have our expected error code.
        # We need to pass that into the expectResponseList before we call GetFinalTestResult
        if isExpectedErrorCase:
            expectResponseList = [expectedErrorCode] # int: -32000, -32010, -32-2-, -32030

        # If this is *not* an expected error case (aka a functonal test) and we didn't get an API error,
        # Call "GetExpectedResponseValues:" to populate the expresDict with expected values.
        if not(isExpectedErrorCase): # Bool
            if not(receivedResponseError): # We got a full API response, gather our expected values
                # Gather up what we want to look for in the response from the testCase definition file
                expectedGameState = GetExpectedGameState(fullPathTestFileName)
                expectedPlayerState = GetExpectedPlayerState(fullPathTestFileName)
                expectedPiecesMoved = GetMovedPieces(fullPathTestFileName)
                expectedResponsePieces = GetExpectedResponsePieces(fullPathTestFileName)
                # That should cover it.  Put it all into the expectReslonseList
                expectResponseList = [expectedGameState, expectedPlayerState, expectedPiecesMoved, expectedResponsePieces]
                #printterm("DEBUG: GetExpectedResponseValues returned expectResponseList %s" % str(expectResponseList))
                expectResponseListNumItems = utilities.CountItemsInList(expectResponseList)
                if expectResponseListNumItems != 4:
                    printall("ERROR - Problems retrieving our expected response params,  Expected 4, got %s - Exiting" % expectResponseListNumItems)   
                    printall(str(expectResponseList))
                    numTestsExited += 1
                    sys.exit(1)
                printterm("Finished collecting our expected API response values.\n")
                printterm(str(expectResponseList))
            else: # Functional test expected to pass received an 'error' back - go to GetFinalTestResult()
                pass

        # Call 'GetFinalTestResult:' to determine if we passed or failed.
        # We have Five possible results from our API Response test:
        # 1) The API request checker returns empty or with a Process ERROR
        # 2) functional test PASS - Test that did not expect an error has a correct reponse
        # 3) functional test FAIL - We recieved an unexpected ERROR code or response incorrect
        # 4) expected error case PASS - testResult is the expected API error code
        # 5) expected error case  FAIL - Test did not throw expected error code
        testResult = GetFinalTestResult(responseApi, expectResponseList, isExpectedErrorCase, receivedResponseError, requestBoard)

        #printterm("Evaluating our testResult for a final test return value.\n")
        if testResult == "Process ERROR" in testResult:
            printall("Process ERROR: 'GetTestResult' failed to return a valid check value for test %s" % testName)
            printall("GetTestResult Response:")
            printall(testResult)
            printall("Marking as a Test Exit Error and move on to next testcase.\n")
            numTestsExited += 1
            continue
        # A passing test only gives us a single word
        if testResult == "functionalTestPASS":
            printall("All API response params as expected.\n")
            printall("FUNCTIONAL TEST %s PASSED." % testName)
            printall("=============================================================================\n\n")
            numPassingTests += 1
            continue
        # A FAILed test give us the result and a string about what failed
        if "functionalTestFAIL" in testResult:
            printall("Found unexpected results in the API response!\n")
            printall("FUNCTIONAL TEST %s FAILED." % testName)
            printall("Returned Failure Information:")
            printall(testResult)
            printall("=============================================================================\n\n")
            printall("Moving on to next test...\n")
            numFailingTests += 1
            continue
        # A passing test only gives us a single word
        if testResult == "expectedErrorCasePASS":
            printall("Expected Error code returned.\n")
            printall("EXPECTED Error TEST %s PASSED.\n" % testName)
            printall("=============================================================================\n\n")
            numPassingTests += 1
            continue
        # A FAILed test give us the result and a string about what failed
        if "expectedErrorCaseFAIL" in testResult:
            printall("Found unexpected results in the API response!")
            printall("EXPECTED Error TEST %s FAILED.\n" % testName)
            printall("Returned Failure Information:")
            printall(testResult)
            printall("=============================================================================\n\n")
            printall("Moving on to next test...\n")
            numFailingTests += 1
            continue
        
    # Create a test summary for the screen, report & log files
    # Get our pass & fail percentages
    percentPass = GetPercent(numPassingTests, numTests)
    percentFail = GetPercent(numFailingTests, numTests)
    percentExited = GetPercent(numTestsExited, numTests)

    summaryMessage = ("\n\n      **** ALL %d TESTS COMPLETED! TEST SUMMARY ****\n\
           %d of %d Tests PASSED - %s\n\
           %d of %d Tests FAILED - %s\n\
           %d of %d Tests UNEXPECTEDLY EXITED - %s\n" \
    % (numTests, numPassingTests, numTests, percentPass,\
       numFailingTests, numTests, percentFail,\
       numTestsExited, numTests, percentExited))
    printterm(summaryMessage) # For the benefit of interactive users

    # *Finally, Now that everything else has been written to the output files, 
    # insert the opening message & summary at the top of the report & APAI log files
    fullMessage = openingMessage + summaryMessage
    utilities.PrependFile(testRunResultFileName, fullMessage)
    utilities.PrependFile(testAPILogFileName, fullMessage)

    # Looks like our work is done here....
    printall("Thank You for using our amazing API testing facility!!!\n")
    printterm("Full Results can be found in test report file %s" % testRunResultFileName)
    printterm("and API log file %s\n" % testAPILogFileName)
    printall("Exiting Run_SFCS_Tests!")
    return 0

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
