'''
      'utilities' module to be shared by both a single test run and Run_All_SFCI_Tests.
      Short functions that return a requested value live here.

'''
# Modules we'll need...
import os

# Write our summary to the *top* of the report or log files
def PrependFile(outFileName, message):
    with open(outFileName, 'r+') as outFile: # has to be readable & writeable for this to work
        contents = outFile.read()
        outFile.seek(0) # Take me to the top...
        outFile.write(message + contents)

# return the total number items in a supplied list (e.g., pieces on a board)
def CountItemsInList(lst):
    numPieces = 0
    for pieceObject in lst:
        numPieces += 1
    return numPieces

# See if the string represents a valid int
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

# build a new piece object
def MakePieceObj(pieceType, pieceLoc):
    pieceObj = {}
    pieceObj["type"] = pieceType
    pieceObj["loc"] = pieceLoc
    #print("DEBUG: Creating a Piece object of %s" % str(pieceObj))
    return pieceObj

# Generic function to take user input, check against legal values & return answer
# if we get a legalValues argument of "*", allow any value.
# Needed for free-form answers like descriptions or where there 
# are a large number of legal responses
def GetUserInput(promptMessageString, legalValuesTuple):
    # Set up a loop to keep asking if given bogus answer
    userResponse = ""
    validResponse = False
    while validResponse == False:
        # Issue a question for what we seek, followed by the list of legal responses.
        print("%s - %s" % (promptMessageString, str(legalValuesTuple)))
        userResponse = input("Response: ") # Get the response, always converts to string
        userResponse = userResponse.rstrip() # ignore any accidental response whitespace
        userResponse = userResponse.lower() # Ignore case - all values in tuples must be LC
        if legalValuesTuple != "*" and not(userResponse in legalValuesTuple):
            print("Invalid response. Choices are %s.  Please try again." % str(legalValuesTuple))
            continue  # Keep trying till they get it right..
        else:
            validResponse = True
            return userResponse
    # Shouldn't get here..."
    print("Process_ERROR in utilities.GetUserInput()! Exiting...")
    syss.exit(1)

# Present a numbered python list of options and have the user choose one, return string
def ChooseValueFromList(promptMessageStr, lst):
    print(promptMessageStr)
    numItems = CountItemsInList(lst)
    print("Please Choose from this list (1-%d):" % numItems)
    itemsIter = 0
    while itemsIter <= (numItems - 1):
        item = lst[itemsIter]
        print(" %d: %s" % ((itemsIter + 1), item)) # make choices 1-numItems, not (0-NumItems-1)
        itemsIter += 1
    isValidResponse = False
    while isValidResponse == False:
        valueNumStr = input("Please enter the number: ")
        if RepresentsInt(valueNumStr): # Make sure the string represents an int
            valueNum = int(valueNumStr)
        else:
            print("Non-integer value entered. Please try again.")
            continue
        if valueNum <= 0 or valueNum > numItems:
            print("Invalid Selection %d. Please try again." % valueNum)
        else: # Valid choice
            value = lst[valueNum - 1]
            isValidResponse = True
    print("'%s' Chosen\n" % value)
    return value
    
# GetFullPath: Function to return a full path name if a relative path is supplied
def GetFullPath(rootTestDir, testFileName):
    fullPath = os.path.join(rootTestDir, testFileName)
    return fullPath

# GetDefaultTests: Get a list of all tests to run by looking in our test case directories
def GetDefaultTests(testList, testDirs):
    from os.path import isfile, join
    for testDir in testDirs:
        #printterm("DEBUG: Looking in directory %s for testcases...\n" % testDir)
        for f in os.listdir(testDir):
            fileFullPath = (join(testDir,f))
            #printterm("DEBUG: Found %s - testing to see if it's a file...\n" % f)
            if isfile(fileFullPath):
                #printterm("DEBUG: %s is a file - append it to the testList[]\n" % f)
                testList.append(fileFullPath)
    #printterm("DEBUG: Default testList is %s\n" % testList)
    return testList
    # END def GetDefaultTests(testList, testDirs):

# GetTestName: The test name is the corresponding test definition file name w/ .<ext> removed
# The supplied testFilename can have either a full path or just a file name
def GetTestName(fullPathTestFileName):
    # Make sure we can find the specified file...
    # Strip off any lead/trail chars & newlines
    fullPathTestFileName = fullPathTestFileName.rstrip()
    if not(os.path.isfile(fullPathTestFileName)):
        return ("ERROR: Test File %s not found! Skipping this test!\n" % fullPathTestFileName) 
    testNameWExt = os.path.basename(fullPathTestFileName)
    splitName = testNameWExt.split(".")
    return splitName[0]

# Generic function to get the value of any file line begginning w/ <key> :
def GetFileValue(fullPathTestFileName, key):
    # Strip off any lead/trail chars & newlines
    fullPathTestFileName = fullPathTestFileName.rstrip()
    with open(fullPathTestFileName, 'r') as testFile:
        for line in testFile:
            if line.startswith("#"): # Skip Comment Lines
                continue 
            if line.startswith(key):
                # Get everything after the first ':'
                value = line.split(":", 1)[1]
                value.rstrip() # Trim any whitespace ff the front or back
                return value
        return ("Process ERROR: No '%s' entry in file %s\n" % (key, fullPathTestFileName))

