'''
RequestGen.py - A python 3 program for interactively generating both
functional and expected-fail cases (JSON-RPC request strings)
for the SolidFire Chess Service (SFCS) 'MakeMove' API.

Copyright 2016, Dan Doran, Boulder, CO
'''
import sys
import os
import utilities # Local

usageMessage = "Usage: python RequestGen.py"
openingMessage = '''\nWelcome to the SFCS Test Case generator Script.  (Copyright 2016, Dan Doran, Boulder CO)\n
Be aware this script should only allow generation of syntactically-correct test definition files.
It will however allow the generation of chess-rule invalid boardStates, and allow illegal moves.
You will need to edit the test case definition file to create cases for invalid syntax API requests.\n
'''
# Global Constants & vars for file control
rootTestDir = os.getcwd()
testType = "" # TBD - 'e' Expected Error & 'f' Functional
fileDir = "" # TBD
fullFileDir = "" #TBD
testExt = "" # TBD
testName = "" # TBD
fullTestName = "" # TBD
expPassFileExt = ".passtest"
expFailFileExt = ".expfail"
testBoardExt = ".bsfile"
expPassDir = "expPassTestDir"
fullExpPassDir = os.path.join(rootTestDir, expPassDir)
expFailDir = "expFailTestDir"
fullExpFailDir = os.path.join(rootTestDir, expFailDir)
testRelPath = "" # TBD
testAbsPath = "" # TBD
testBoardDir = "Test_Boards"
fullTestBoardDir = os.path.join(rootTestDir, testBoardDir)

# Constants to assemble our SFCS API request.  NOTE: JSON-RPC only recognizes double-quotes in requests
method = '"method" : "MakeMove"'  # Static for our purposes
id = '"id" : 1' # Static
rev = '"jsonrpc" : "2.0"' #  Static

# Vars for play control
playerColor = "" # TBD ("b" or "w")
movedPiece = {} # Piece Object(s) we're gonna move {"type":"?", "loc" : "?"}, and also verify response
capturePiece = {} # Piece to check response for in a capture move to make sure it's gone
destinationSquare = "" # TBD. We'll allow fictional destinations for error checking
move = "" # TBD, Algebraic Chess Notation.  We will allow bogus moves for expected error cases
boardStateList = [] # Our Board, List of pieceObjects, each w/ "type" (UpperCase White, LowerCase Black) & "loc" values
moveType = ""
legalMoveTypes = ["move", "capture", "pawnpromotion", "castling", "enpassant", "check", "checkmate"]

# Tuples & lists for value checking.  All input values lower-cased as they come in, so all legalVals are LC
legalYN = ('y','n') # For Yes/No inputs 
legalTestTypes = ('e','f') # Expected Error & Functional
legalColors = ("b","w")
legalRows = (1,2,3,4,5,6,7,8)
legalColumns = ('a','b','c','d','e','f','g','h')
legalPieceTypes = ('p','r','n','b','q','k')
pieceTypeMappingList = [{"p":"pawn"},{"r":"rook"},{"n":"knight"},{"b":"bishop"},{"q":"queen"},{"k":"king"}]
legalCastlingSides = ("k","q") # kingside & queenside
legalErrorCodes = [{"Invalid Board Error" : -32000},{"Invalid Player Error" : -32010},\
                   {"Invalid Move Error" : -32020},{"Unknown API Error" : -32030}]

# Expected Values we want to check from the SFCS API response
responseColor = "" # Always opposite playerColor
gameState = "" # TBD by test
legalGameStates = ('""',"check","checkmate","stalemate")

#================================
# Function Definitions Start Here
#================================

# Is this an expected error or functional tesst we're building?
def GetTestType():
    promptMessage = ("First Question - Is this a functional test or an expected error test?")
    testType = utilities.GetUserInput(promptMessage, legalTestTypes) # Check input legality
    if testType == 'e':
        print("\nThis is an Expected Error Case expected to return an API Error message\n")
    if testType == 'f':
        print("\nThis is a Functional Test Case expected to return a full API response.\n")
    return testType
# END GetTestType()

# Interactively get a test case description.
def GetTestDescription():
    descriptString = input("Please enter a 1-line description of this test case:\n")
    fullDescLine = "Description : " + descriptString + "\n"
    print("%s" % fullDescLine)
    print("")
    return fullDescLine
# END GetTestDescription()

# Get the name of this test case
def GetTestCaseName():
    testName = input("Please enter your testcase name, preferably per naming conventions: ")
    print("testName is now '%s'\n" % testName)
    return testName
#END GetTestCaseName

#Ask the player for what color they want to play/move
def GetPlayerColor():
    promptMessage = ("What color are you playing?")
    playerColor = utilities.GetUserInput(promptMessage, legalColors) # Check input legality
    # Set both the player and expected response colors
    if playerColor == "w":
        print("Playing as White\n")
    else:
        print("Playing as Black\n")
    return playerColor
# END GetPlayerColor()

# For expected-error cases - Prompt user to choose which API error they expect for this test case 
def GetExpectedErrorCode():
    promptMessage = ("Expected Error Test Case Chosen. Please choose the API error you expect in the API response.")
    errorType = utilities.ChooseValueFromList(promptMessage, legalErrorCodes) # returns {'error_description' : <code>}
    errorCodeVal = errorType.values()
    #print("DEBUG: errorCodeVal is %s of type %s" % (errorCodeVal, type(errorCodeVal)))
    code = 0 
    for i in errorCodeVal:
        code = int(i)
    #print("DEBUG: our returned code is %d" % code)
    errorCode = {}
    errorCode["code"] = code
    #print("DEBUG: errorCode is %s" % str(errorCode))
    return errorCode
# END GetExpectedErrorCode()

# Little subroutine for DrawCurrentBoard() to return a list of
# piece objects (dicts) in the supplied row.
def GetPiecesInRow(boardStateList, row):
    pieceList = []
    for pieceObj in boardStateList:
        loc = pieceObj.get("loc")
        #See if the row matches...
        if int(loc[1]) == row:
            pieceList.append(pieceObj)
    return pieceList
# END GetPiecesInRow()

# Little function to draw the current board
def DrawCurrentBoard(boardStateList):
    separatorSpace = ("             ") # 14 spaces
    leadSpace = ("         ") # 9 spaces
    separator =  separatorSpace + ("-------------------------------")
    bottomLine = separatorSpace + (" a   b   c   d   e   f   g   h\n")
    emptySquare = "   |" # 3 spaces w/ trailing bar
    # Start our ascii masterpiece...
    print(separator)
    # Start at top row and work down, printing a row, then a separator at a time
    row = 8
    while row > 0:
        rowPieces = GetPiecesInRow(boardStateList, row) # Returns list of Piece objects in the current row, including loc
        rowText = "" # Fill this in left-to-right.
        rowText = (leadSpace + ' ' + str(row) + ' |') # Start the row w/ a row number and edge
        foundPieceInSquare = False
        for column in legalColumns: # a - h
            foundPieceInSquare = False
            for piece in rowPieces: # each piece Dict        
                loc = piece.get("loc") 
                locColumn = loc[0]              
                if locColumn == column: # Found a piece in this square
                    foundPieceInSquare = True
                    pieceType = piece.get("type")
                    rowText += (" %s |" % pieceType) # Add square w/ pieceType
                    break # Skip any further rowPieces since there can only be 1 piece/square, move on to next column                                  
            if (foundPieceInSquare == False):  # If we didn't find any pieces for this square, put an empty one in
                rowText += emptySquare
                continue
        print(rowText) # Print the entire row & the row separator line beneath
        print(separator)
        row -= 1
    print(bottomLine)
# END DrawCurrentBoard()

# We need a board (boardState list of piece objects) for our request.
# Building the same one for multiple test cases is not efficient,
# so we have a Test_Board Repository with all kinds of board setups.
# In the case where we don't already have the board we need
# create ( & optionally archive) a new starting board interactively.

# Subroutine to deliver us a list of starting board categories/dirs in the Test_Board repo
def GetListRepoBoardTypes():
    repoBoardTypes = []   
    repoBoardTypes = os.listdir(fullTestBoardDir)
    #print("DEBUG: Our list of test_Board Directories is:\n%s" % repoBoardTypes)
    return repoBoardTypes
# END GetListRepoBoardTypes()

# Subroutine to get us a listing of board files (.bsfiles) in the chosen Test_Boad repo dir
def GetListBoardNames(boardType):
    boardDir = os.path.join(fullTestBoardDir, boardType)
    boardNames = os.listdir(boardDir)
    return boardNames
# END GetListBoardNames()

# Check if can use one of the boards in our Test_Board repository
def GetRequestBoardFromRepo():
    choseBoard = False
    while choseBoard == False:
        repoBoardTypes = GetListRepoBoardTypes()
        promptMessage = ("Here are the categories of starting boards in our Test_Board repository:")
        boardType = utilities.ChooseValueFromList(promptMessage, repoBoardTypes)
        boardNames = GetListBoardNames(boardType)
        numBoards = 0
        numBoards = len(boardNames)
        if numBoards == 0:
            print("There are no boards in the %s TestBoards repository yet." % boardType)
        else: # Print out the list of boards, 1/line
            print("Here is the current list of %d boards in the %s repository directory:" % (numBoards, boardType))
            iter = 0
            while iter <= (numBoards - 1):
                board = boardNames[iter]
                print(" %d: %s" % ((iter + 1), board)) # make choices 1-numItems, not (0-NumItems-1)
                iter += 1
        promptMessage = ("Do you want to use one of these boards ('u'), inspect another category ('a'), \n\
or build a new board ('b')?")
        legalChoice = ('u','a', 'b')
        useThisBoard = utilities.GetUserInput(promptMessage, legalChoice)
        if useThisBoard == 'u':
            boardName = utilities.ChooseValueFromList(promptMessage, boardNames)
            fullBoardName = os.path.join(fullTestBoardDir, boardType, boardName)
            choseBoard = True
        elif useThisBoard == 'a':
            continue # Try again
        elif useThisBoard == 'b':
            return # return None
    return fullBoardName
# END GetRequestBoardFromRepo()

# Routine to read the contents of the boardFile
def ReadBoardFile(fullBoardName, boardStateList):
    with open(fullBoardName, 'r') as boardFile:
        boardStateList = boardFile.read() # Comes back as str
        boardStateList = eval(boardStateList) # Turn it back to a list
    return boardStateList
# END ReadBoardFile()

# Subroutine for BuildNewRequestBoard to request what the user wants to do next
def GetNextStep(boardStateList):
    print("Current board:")
    DrawCurrentBoard(boardStateList)
    promptMessage = ("Would you like to add a new piece ('a'),\n\
remove an existing piece ('r'),\n\
or declare the board finished ('f'): ")
    legalNextMoves = ('a','r','f')
    nextStep = utilities.GetUserInput(promptMessage, legalNextMoves)
    return nextStep
# END BuildNewRequestBoard

# subroutine to solicit a piece object
def GetBoardPiece(boardStateList):
    DrawCurrentBoard(boardStateList)
    isPieceLegal = False
    pieceStr = ""
    colorChar = ""
    columnChar = ""
    rowChar = ""
    while isPieceLegal == False:
        pieceStr = input("Please enter your 4-character color/piece/loc value <color><piece><loc> (case-insensitive): ")
        if len(pieceStr) != 4:
            print("Invalid entry '%s' - must be 4 characters!" % pieceStr)
            continue # Try Again...
        pieceStr = pieceStr.lower() # make choice case-insensitive
        colorChar = pieceStr[0]
        if colorChar not in legalColors:
            print("Invalid color in first character '%s'.  Must be %s." % (colorChar, str(legalColors)))
            continue
        pieceChar = pieceStr[1]
        if pieceChar not in legalPieceTypes:
            print("Invalid piece type '%s' in second character.  Must be %s." % (pieceChar, str(legalPieceTypes)))
            continue
        if colorChar == "w":
            pieceChar = pieceChar.upper() # Upper-case piece chars for white
        columnChar = pieceStr[2]
        rowChar = pieceStr[3]
        locStr = columnChar + rowChar
        if columnChar not in (legalColumns):
            print("Invalid column in third character '%s'.  Must be %s." % (columnChar, str(legalColumns)))
            continue
        if int(rowChar) not in (legalRows):
            print("Invalid row in fourth character '%s'.  Must be %s." % (rowChar, str(legalRows)))
            continue
        # Looks like it's a legal entry, Break out
        isPieceLegal = True
        break
    pieceObj = {}
    pieceObj["type"] = pieceChar
    pieceObj["loc"] = locStr
    return pieceObj
# END GetBoardPiece()

# Optionally Save a newly-built starting board to the Test_Boards repository
def SaveBoardToRepo(boardStateList):
    promptMessage = ("What Test_Board repository category should this board be saved under?")
    repoBoardTypes = GetListRepoBoardTypes()
    boardType = utilities.ChooseValueFromList(promptMessage, repoBoardTypes)
    boardNames = GetListBoardNames(boardType)
    print("Here are the current boards saved under %s/%s:\n%s\n" % (testBoardDir, boardType, boardNames))
    boardName = input("Please enter a name for this new board, preferably using current naming conventions: ")
    fullBoardName = boardName + testBoardExt # Add .bsfile file extension
    boardFileName = os.path.join(fullTestBoardDir, boardType, fullBoardName)
    print("Saving new starting board to %s" % boardFileName)
    with open(boardFileName, "w") as boardFile:
        contents = str(boardStateList)
        # JSONRPC hates single quotes from lists - Make them double quotes
        contents = contents.replace("'", '"')
        boardFile.write(contents)
    return
# END SaveBoardToRepo()

# Optional function to build a new starting board from scratch
def BuildNewRequestBoard(boardStateList):
    # for fast board populating ask for this 4-character format, case-insensitive:
    # <color><piece><loc>
    print('''Building a new starting board.\n
To make this fast, enter all the info about each new piece in one 4-character String.
The format is case-insensitive: <color><piece><loc> .  For example, adding a black Knight
to square c6 would be:  bnc6 ('n' for knight, since king gets 'k').  White ('w') pieces
will be upper-cased for you. E.G. Adding a white rook to a1 (wra1) will put an "R" on square a1.
At each prompt you will be shown the current board, and asked whether to add another piece('a'),
remove a current piece('r'), or finish('f').  The new boardState will be added to the API request.\n
''')
    keepGoing = True
    while keepGoing == True:
        nextStep = GetNextStep(boardStateList)
        if nextStep == 'a':
            print("Adding a new piece to our board:")
            newPiece = GetBoardPiece(boardStateList)
            boardStateList.append(newPiece)
        elif nextStep == 'r':
            print("Request to remove a piece from our board - please choose:")
            pieceToRemove = GetBoardPiece(boardStateList)
            numPieces = utilities.CountItemsInList(boardStateList)
            if numPieces != 0 and numPieces != 1: # Remove the piece if we have 2 or more pieces on the board
                boardStateList.remove(pieceToRemove)
            else:
                print("Can't remove piece on board with %d pieces." % numPieces)
                continue
        elif nextStep == 'f': #Finish up
            print("Finished Board:")
            DrawCurrentBoard(boardStateList)
            keepGoing = False
            promptMessage =("Would you like to add this new board to the Test_Board repository?")
            saveBoard = utilities.GetUserInput(promptMessage, legalYN)
            if saveBoard == 'y':
                SaveBoardToRepo(boardStateList)
            else:
                print("Not saving this board to the Test_Board repository.  Continuing with building test case.")
            print("Adding this board to the SFCS API request")
            return boardStateList
        else:
            print("Process ERROR: Unexpected invalid input '%s' for GetNextStep.  Exiting..." % nextStep)
            sys.exit(1)
# END BuildNewRequestBoard

def GetRequestBoard():
    boardStateList = [] # send back as list, not string
    getBoard = False
    while getBoard == False:
        promptMessage = ("Would you like to use or inspect starting boards in our Test_Board repository?")
        getRepoBoards = utilities.GetUserInput(promptMessage, legalYN)
        if getRepoBoards == 'y':
            boardFile = GetRequestBoardFromRepo()
            if boardFile != None:
                boardStateList = ReadBoardFile(boardFile, boardStateList)
                print("Here is the starting board you've chosen:")
                DrawCurrentBoard(boardStateList)
                promptMessage = ("Is this the board you want to use?")
                likeThisBoard = utilities.GetUserInput(promptMessage, legalYN)
                if likeThisBoard == 'y':
                    getBoard = True
                    break
                else:
                    continue # Try again
            else: # User wants to build a new board
                boardStateList = BuildNewRequestBoard(boardStateList)
                getBoard = True
                break
        elif getRepoBoards == 'n':
            promptMessage = ("Would you like to create a new starting board?")
            getNewBoard = utilities.GetUserInput(promptMessage, legalYN)
            if getNewBoard == 'y':
                boardStateList = BuildNewRequestBoard(boardStateList)
                getBoard = True
                break
            else:
                print("Not sure what you want to do - Please try again.")
                continue # Try Again
        else:
            print("Not sure what you want to do... Exiting")
        sys.exit(1)
    return boardStateList
# END GetRequestBoard

# Return a list of the piece(s) we're moving or removing via capture.  Should *not* be in response board
def GetMovedPieces(moveType, moveList):
    movedPieces = []
    # Castling is the one move where we return two pieces, item 1 & 2 in list
    if moveType != "castling":
        movedPieces = [moveList[1]] # single moved piece
    else: # Castling move
        movedPieces = [moveList[1], moveList[2]]
    # Append the captured Piece on this list if a capture move
    if moveType.endswith("capture"): # All capture moves
        movedPieces.append(moveList[2])
    # Assemble & return a line
    movedPiecesLine = "movedPieces : " + str(movedPieces) + "\n"
    return movedPiecesLine
# END GetMovedPieces()

# Pieces we expect to be in the response - movedPiece in new loc, or king+rook in new locs for castling
def GetResponsePieces(moveType, moveList):
    responsePieces = []
    # Castling is the one move where we return two moved pieces, item 3 & 4 in list
    if moveType == "castling":
        responsePieces = [moveList[3], moveList[4]]
    # for captures, the moved piece is after the captured piece in the moveList
    elif moveType.endswith("capture"):
        responsePieces = [moveList[3]]
    else: # All other moves
        responsePieces = [moveList[2]] # The movedPiece new location
    # Assemle & return a line
    responsePiecesLine = "expectedResponsePieces : " + str(responsePieces) + "\n"
    return responsePiecesLine
# END GetResponsePieces()

def GetMoveType():
    promptMessage = ("What sort of move do you want to make?\n\
Choose 'check','checkmate' or 'pawnpromotion' even if it includes a capture.")
    moveType = utilities.ChooseValueFromList(promptMessage, legalMoveTypes) 
    # Append 'capture' to Moveype if it includes one
    if moveType == "check":
        promptMessage = ("Will this check move include a capture?")
        isCapture = utilities.GetUserInput(promptMessage, legalYN)
        if isCapture == 'y':
            moveType = "checkcapture"
    if moveType == "checkmate":
        promptMessage = ("Will this checkmate move include a capture?")
        isCapture = utilities.GetUserInput(promptMessage, legalYN)
        if isCapture == 'y':
            moveType = "checkmatecapture"
    if moveType == "pawnpromotion":
        promptMessage = ("Will this pawn promotion move include a capture?")
        isCapture = utilities.GetUserInput(promptMessage, legalYN)
        if isCapture == 'y':
            moveType = "pawnpromotioncapture"
    return moveType
# END GetMoveType()

def CheckDestinationLegality(testType, destinationSquare):
    moveMessage = ""
    legalDest = False
    while legalDest == False:
        if len(destinationSquare) != 2:
            if testType == 'f': 
                moveMessage += ("ERROR: Invalid destination square value '%s'!  columnrow format only." % destinationSquare)
                destinationSquare = input("Please enter a move destination loc (<column><row>): ")
                continue # Try again
            else: # Expected Error - see if the user meant this as the error          
                moveMessage += ("WARNING: %s is an invalid location and will return a move error from the API" % destinationSquare)
                promptMessage = ("Did you intend that to be the expected error?")
                intentional = utilities.GetUserInput(promptMessage, legalYN)
                if intentional == 'y':
                    return moveMessage
                else:
                    moveMessage += ("ERROR: Invalid destination square value '%s'!  columnrow format only." % destinationSquare)
                    destinationSquare = input("Please enter a move destination loc (<column><row>): ")
                    continue # Try again
        columnChar = destinationSquare[0]
        rowChar = destinationSquare[1]
        if columnChar not in (legalColumns):
            if testType == 'f':
                moveMessage += ("ERROR: Invalid column '%s'.  Must be %s." % (columnChar, str(legalColumns)))
                destinationSquare = input("Please enter a move destination loc (<column><row>): ")
                continue # Try again
            else: # Expected Error - see if the user meant this as the error
                moveMessage += ("WARNING: %s is an invalid column and will return a board error from the API" % destinationSquare)
                promptMessage = ("Did you intend that to be the expected error?")
                intentional = utilities.GetUserInput(promptMessage, legalYN)
                if intentional == 'y':
                    return moveMessage
                else:
                    moveMessage += ("ERROR: Invalid destination square value '%s'!  columnrow format only." % destinationSquare)
                    destinationSquare = input("Please enter a move destination loc (<column><row>): ")
                    continue # Try again 
        if int(rowChar) not in (legalRows):
            if testType == 'f':
                moveMessage += ("ERROR: Invalid row '%s'.  Must be %s." % (rowChar, str(legalRows)))
                destinationSquare = input("Please enter a move destination loc (<column><row>): ")
                continue # Try again
            else: # Expected Error - see if the user meant this as the error
                moveMessage += ("WARNING: %s is an invalid row and will return a board error from the API" % destinationSquare) 
                promptMessage = ("Did you intend that to be the expected error?")
                intentional = utilities.GetUserInput(promptMessage, legalYN)
                if intentional == 'y':
                    return moveMessage
                else:
                    moveMessage += ("ERROR: Invalid destination square value '%s'!  columnrow format only." % destinationSquare)
                    destinationSquare = input("Please enter a move destination loc (<column><row>): ")
                    continue # Try again
        legalDest = True  
    return moveMessage
# END CheckDestinationLegality()

def GetDestinationSquare(testType, moveType, boardStateList):
    DrawCurrentBoard(boardStateList)
    promptMessage = ("What square (loc) do you want to move your piece to for this %s?: " % moveType)
    destinationSquare = input(promptMessage)
    moveMessage = CheckDestinationLegality(testType, destinationSquare)
    return destinationSquare
# END GetDestinationSquare()

# Special function for building a castling move request List. Return the moveList w/ the move,
# the two moved pieces in their original locs, and the expected result two pieces
def GetCastlingMove(playerColor, moveList):
    # Determine castling notation here - Add castling move from algebraic chess notation as first list element
    # We have 2 possible castling moves for each playerColor side - 'kingSide' & 'queenSide'
    print("Castling move chosen.")
    move = ""
    promptMessage = ("Which rook do you want to swap w/ your King - (Kingside ('k') or Queenside ('q')?")
    castlingSide = utilities.GetUserInput(promptMessage, legalCastlingSides)
    if castlingSide == "k":
        move = ("0-0")
    elif castlingSide == "q":
        move = ("0-0-0")
    else:
        print("Process ERROR - unknown castling move.  Exiting.")
        sys.exit(1)
    # Since we know the playerColor and castlingside, add the original position King & rook Pieces
    #print("DEBUG: Our Castling move string list item came back as %s" % moveList)
    origRookPiece = {}
    origKingPiece = {}
    newRookPiece = {}
    newKingPices = ()
    if playerColor == "w":
        if castlingSide == 'k': # Kingside (right)
            origRookPiece = utilities.MakePieceObj("R","h1")
            origKingPiece = utilities.MakePieceObj("K","e1")
            newRookPiece = utilities.MakePieceObj("R","f1")
            newKingPiece = utilities.MakePieceObj("K","g1")
        elif castlingSide == 'q': # Queenside (left)
            origRookPiece = utilities.MakePieceObj("R","a1")
            origKingPiece = utilities.MakePieceObj("K","e1")
            newRookPiece = utilities.MakePieceObj("R","d1")
            newKingPiece = utilities.MakePieceObj("K","c1")
        else:
            print("Process ERROR - illegal castling notation found in move string : '%s'. Exiting...\n" % requestMoveString)
            sys.exit(1)
    if playerColor == "b":
        if castlingSide == 'k': # Kingside (right)
            origRookPiece = utilities.MakePieceObj("r","h8")
            origKingPiece = utilities.MakePieceObj("k","e8")
            newRookPiece = utilities.MakePieceObj("r","f8")
            newKingPiece = utilities.MakePieceObj("k","g8")
        elif castlingSide == 'q': # Queenside (left)
            origRookPiece = utilities.MakePieceObj("r","a8")
            origKingPiece = utilities.MakePieceObj("k","e8")
            newRookPiece = utilities.MakePieceObj("r","d8")
            newKingPiece = utilities.MakePieceObj("k","c8")
        else:
            print("Process ERROR - illegal castling notation found in move string : '%s'. Exiting...\n" % requestMoveString)
            sys.exit(1) 
    moveList = [move, origRookPiece, origKingPiece, newRookPiece, newKingPiece]
    #print("DEBUG: End of requestMoveCastling, our full moveList should be:\n%s\n" % moveList) 
    return moveList
# END requestMoveCastling()

# Special pawnpromotion moveList - Always promote to queen
def GetPawnPromotionMove(playerColor, startColumn, startRow, destinationColumn,\
                         destinationRow, moveList, boardStateList):
    #print("DEBUG: Our pawn to be promoted is in column %s, row %d" % (startColumn, startRow))
    move = ""
    origPawn = {}
    newQueen = {}
    capturedPiece = {}
    # Make sure we're on the correct row - 2 for black, 7 for white
    if playerColor == "w" and startRow != 7:
        print("Process ERROR: Can't have white move type of 'pawnpromotion' without the pawn on row 7")
        print("Try again... Exiting")
        sys.exit(1)
    if playerColor == "b" and startRow != 2:
        print("Process ERROR: Can't have black move type of 'pawnpromotion' without the pawn on row 2")
        print("Try again... Exiting")
        sys.exit(1)
    # OK, we should be good to go for that promotion. Always go for Queen
    # We have everything to assemble our pawn peice
    startSquare = startColumn + str(startRow)
    destinationSquare = destinationColumn + str(destinationRow)
    if playerColor == "w":
        origPawn = utilities.MakePieceObj("P", startSquare)
        if startColumn == destinationColumn: # No capture
            move = destinationSquare + "=Q"
        else: # capture or illegal move for error case
            move = destinationSquare + "x" + "=Q"
            capturedPiece = GetCapturedPiece(destinationSquare, boardStateList)
        newQueen = utilities.MakePieceObj("Q", destinationSquare)
    if playerColor == "b":
        origPawn = utilities.MakePieceObj("p", startSquare)
        if startColumn == destinationColumn: # No capture
            move = destinationSquare + "=q"
        else:
            move = destinationSquare + "x" + "=q"
            capturedPiece = GetCapturedPiece(destinationSquare, boardStateList)
        newQueen = utilities.MakePieceObj("q", destinationSquare)
    # Add two pieces (origPawn & newQueen) if no capture, append the capturedPiece otherwise
    if capturedPiece == {}:
        moveList = [move, origPawn, newQueen]
    else: # Also add the captured piece
        moveList = [move, origPawn, capturedPiece, newQueen]
    return moveList
# END GetPawnPromotionMove()

# Notation for En Passant is a bit like capture notation with '(ep)' appended:
# <StartColumn>'x'<destLoc>'(ep)  e.g. exd3(ep)
def GetPawnEnPassantMove(playerColor, startColumn, startRow, destinationColumn,\
                         destinationRow, moveList, boardStateList):
    move = ""
    origPawn = {}
    capturedPawn = {}
    startSquare = startColumn + str(startRow)
    destinationSquare = destinationColumn + str(destinationRow)
    # Legality Check - Both move & capture pawns on same row and adjacent to each other
    captureLoc = destinationColumn + str(startRow)
    capturedPawn = GetCapturedPiece(captureLoc, boardStateList)
    if capturedPawn == None or capturedPawn == {}:
        print("Process ERROR: Didn't find any piece on En Passant capture square %s" % captureLoc)
        print("Try again... Exiting")
        sys.exit(1)
    capturedType = capturedPawn.get("type")
    if capturedType == None or capturedType == "" or capturedType.lower() != 'p':
        print("Process ERROR: Didn't find a pawn on En Passant capture square %s" % captureLoc)
        print("Try again... Exiting")
        sys.exit(1)
    if playerColor == "w":
        origPawn = utilities.MakePieceObj("P", startSquare)
        movedPawn = utilities.MakePieceObj("P", destinationSquare)  
    if playerColor == "b":
        origPawn = utilities.MakePieceObj("p", startSquare)
        movedPawn = utilities.MakePieceObj("p", destinationSquare) 
    move = startColumn + "x" + destinationSquare + "(ep)"
    moveList = [move, origPawn, capturedPawn, movedPawn]
    return moveList
# END GetPawnEnPassantMove()

# Assemble our Algebraic Chess Notation "move" value, moved Piece(s) and result piece(s) in a list
# List order is important, and depends upon moveType.  ACN wants all move piece chars upperCase
def GetMove(testType, moveType, playerColor, boardStateList):
    moveList = [] # ["<move>", <movedPiece(s)>, <resultPiece(s)>]
    move = ""
    # Get castling moves out of the way immediately so we don't have
    # to dance around moving more than one piece
    if moveType == 'castling':
        moveList = GetCastlingMove(playerColor, moveList) # We're done with the moveString
        print("For our %s move, our starting and moved Pieces will be %s\n" % (moveType, moveList))
        return moveList # We're Done
    # All other moveTypes require a single piece to move
    movedPiece = GetBoardPiece(boardStateList)
    startSquare = movedPiece["loc"]
    startColumn = startSquare[0]
    startRow = int(startSquare[1])
    pieceType = movedPiece["type"]
    pieceTypeUC = pieceType.upper() # All move pieces UpperCase
    destinationSquare = GetDestinationSquare(testType, moveType, boardStateList)
    destinationColumn = destinationSquare[0]
    destinationRow = int(destinationSquare[1])
    # After a move, the moved piece should be in a new location
    newMovedPiece = utilities.MakePieceObj(pieceType, destinationSquare)
    # Pawn moves - just a destination square for a non-capture move
    if moveType == "move" and pieceType.lower() == "p":
        move = destinationSquare
        print("Our %s will be %s\n" % (moveType, move))
        moveList = [move, movedPiece, newMovedPiece]
        return moveList
    # Handle pawnpromotion move in its own routine like castling - Always promote to Queen
    elif (moveType == "pawnpromotion" or moveType == "pawnpromotioncapture") and pieceType.lower() == "p":
        moveList = GetPawnPromotionMove(playerColor, startColumn, startRow, destinationColumn,\
                                        destinationRow, moveList, boardStateList)
        move = moveList[0]
        print("Our %s move will be %s\n" % (moveType, move))
        # We're done with this move.
        return moveList
    # Add an 'x' for pawn capture moves
    elif moveType.endswith("capture") and pieceType.lower() == "p":
        move = startColumn + "x" + destinationSquare
        print("Our %s move will be %s\n" % (moveType, move))
        capturedPiece = GetCapturedPiece(destinationSquare, boardStateList)
        moveList = [move, movedPiece, capturedPiece, newMovedPiece,]
        return moveList
    # Handle En Passant Moves with its own routine also
    elif moveType == "enpassant":
        moveList = GetPawnEnPassantMove(playerColor, startColumn, startRow, destinationColumn,\
                                        destinationRow, moveList, boardStateList)
        move = moveList[0]
        print("Our %s move will be %s\n" % (moveType, move))
        return moveList
    # Regular moves - Use extra start column char in notation to eliminate ambiguous moves
    elif moveType == "move":
        move = pieceTypeUC + startColumn + destinationSquare
        print("Our %s will be %s\n" % (moveType, move))
        moveList = [move, movedPiece, newMovedPiece]
        return moveList
    # Insert an 'x' into the move string to indicate an intended capture
    elif moveType.endswith("capture"):
        move = pieceTypeUC + startColumn + 'x' + destinationSquare
        print("Our %s move will be %s\n" % (moveType, move))
        capturedPiece = GetCapturedPiece(destinationSquare, boardStateList)
        moveList = [move, movedPiece,  capturedPiece, newMovedPiece]
        return moveList
    # Append a '+' to indicate a check move
    elif moveType == "check":
        move = pieceTypeUC + startColumn + destinationSquare + '+'
        print("Our %s move will be %s\n" % (moveType, move))
        moveList = [move, movedPiece, newMovedPiece]
        return moveList
    # also insert an 'x' for a checkcapture mcove
    elif moveType == "checkcapture":
        move = pieceTypeUC + startColumn + 'x' + destinationSquare + '+'
        print("Our %s move will be %s\n" % (moveType, move))
        capturedPiece = GetCapturedPiece(destinationSquare, boardStateList)
        moveList = [move, movedPiece, capturedPiece, newMovedPiece]
        return moveList
        # Append a '#' to indicate a checkmate move
    elif moveType == "checkmate":
        move = pieceTypeUC + startColumn + destinationSquare + '#'
        print("Our %s move will be %s\n" % (moveType, move))
        moveList = [move, movedPiece, newMovedPiece]
        return moveList
    # also insert an 'x' for a checkmate + capture move
    elif moveType == "checkmatecapture":
        move = pieceTypeUC + startColumn + 'x' + destinationSquare + '#'
        print("Our %s move will be %s\n" % (moveType, move))
        capturedPiece = GetCapturedPiece(destinationSquare, boardStateList)
        moveList = [move, movedPiece,  capturedPiece, newMovedPiece]
        return moveList
    # Should have covered all bases and not got here...
    print("Process ERROR: not able to obtain a moveType or moveList in GetMove.  Exiting.")
    sys.exit(1)
# END GetMove()

# We'll assemble the request as a concatination of strings
def AssembleRequest(playerColor, moveValue, boardStateList):
    boardState = ('"boardState": %s' % str(boardStateList))
    # Lists give us single quotes when converted to strings. JSON-RPC hates them. Make them double quotes
    boardState = boardState.replace("'", '"')
    # We'll assemble the request as a concatination of strings
    move = "" # "move": "<moveValue>"
    move = ('"move": "%s"' % moveValue)
    playerState = ""  # {"playerState': "<playerColor>"
    playerState = ('"playerState": "%s"' % playerColor)
    params = ""
    params = ('"params": {%s, %s, %s}' % (boardState, move, playerState))
    #print("DEBUG: AssembleRequest params is %s" % params)
    request = ""
    request = "{" + method + "," + params + "," + id + "," + rev + "}"
    fullRequest = ("request : %s" % request)
    #print("DEBUG: AssembleRequest fullRequest is:\n%s\n" % fullRequest)
    return fullRequest
# END AssembleRequest()

# gameState is a tricky since "" (continue play) is a valid response
def GetExpectedGameState():
    promptMessage = ("What gameState value do you expect in the response?  \"\" for continue play")
    gameStateVal = utilities.GetUserInput(promptMessage, legalGameStates) 
    gameState = ('"gameState": "' + gameStateVal + '"\n') # return a string
    return gameState
# END GetExpectedGameState()

# just return the opposite of GetPlayerState
def GetExpectedPlayerState(playerColor):
    responseColor = ""
    if playerColor == "w":
        responseColor = "b"
    if playerColor == "b":
        responseColor = "w"
    playerState = ('"playerState": "' + responseColor + '"\n' )
    return playerState
# END GetExpectedPlayerState()

# Returns the piece (dict form) in the destinationSquare, None if empty
def GetCapturedPiece(destinationSquare, boardStateList):
    capturedPiece = None
    for capturedPiece in boardStateList:
        if capturedPiece.get("loc") == destinationSquare:
            return capturedPiece
    return capturedPiece 
# END GetCapturedPiece()

# Put all the elements of an expected error test definition file together
# Add newlines where needed for readability
def AssembleExpErrTestContents(testName, testDescription, request, expectedErrorCode):
    contents = ""
    expErrCode = ("errorCode : %s" % expectedErrorCode)
    contents = testName + "\n" + testDescription + request + "\n" + expErrCode + "\n"
    #print("DEBUG: Test file contents are:\n%s\n" % contents)
    return contents
# END AssembleExpErrTestContents()

# Put all the elements of a functional test defintion file together
# Add newlines where needed for readability
def AssembleFuncTestContents(testName, testDescription, request,\
                             expectedGameState, expectedPlayerState,\
                             movedPieces, expectedResponsePieces):
    contents = ""
    contents = testName + "\n" + testDescription + str(request) + "\n" + expectedGameState +\
               expectedPlayerState + movedPieces + expectedResponsePieces
    #print("DEBUG: Test file contents are:\n%s\n" % contents)
    return contents
# END AssembleFuncTestContents()

# Finishing function writes our new test definition file to the correct test repository
def WriteTestFile(testType, testName, testFileContents):
    if testType == 'e':
        fileDir = expFailDir
        fullFileDir = fullExpFailDir
        testExt = expFailFileExt
    if testType == 'f':
        fileDir = expPassDir
        fullFileDir = fullExpPassDir
        testExt = expPassFileExt
    # We can get all our paths once we get a test name
    fullTestName = testName + testExt
    testRelPath = os.path.join(fileDir, fullTestName)
    testAbsPath = os.path.join(fullFileDir, fullTestName)
    with open(testAbsPath, "w") as testFile:
        testFile.write(testFileContents)
    print("Congratulations, test definition file %s/%s has been written \n\
and is ready for testing with 'Run_SFCS_Tests'." % (fileDir, fullTestName))
    return

# END FUNCTION DEFINITIONS

#=============================================================================
# main() main() main() main() main() main() main() main() main() main() main() 
#=============================================================================
def main():
    # Some command line sanity checking  
    arglen = len(sys.argv)
    if arglen != 1:
        print("No arguments needed for this script!")
        print(usageMessage)
        return 0
    # Now that that's out of the way, start in earnest.  Functions do most of the blather
    print(openingMessage)
    testType = GetTestType() # Expected Error ('e') of functional ('f')
    testDescription = GetTestDescription() # Single string
    testName = GetTestCaseName() # Name w/ no path or extension
    testNameLine = ("testName : " + testName)
    # We'll always need a full request for both expected error and functional tests
    playerColor = GetPlayerColor() # 'w' or 'b', also sets the expected response player color.
    boardStateList = GetRequestBoard() # Our Starting Board (list) - either from the Test_Board repository
                                       # or created interactively (optionally saved to the repository)
    moveType = GetMoveType() # move,capture,pawnpromotion,castling,check,checkmate,enpassant
    moveList = GetMove(testType, moveType, playerColor, boardStateList) # Returns a list:
    #print("DEBUG: our returned moveList from GetMove is %s\n" % moveList)
    # ['move_string'(Algebraic Chess Notation), movedPieces (2 for castling, one for all otherr moveTypes)
    move = moveList[0]
    request = AssembleRequest(playerColor, move, boardStateList) # Valid request Dict ready for API submission
    # Assemble of our test case file with after getting our expected response values
    if testType == 'e': # Expected Error case
        expectedErrorCode = GetExpectedErrorCode() # None for functional tests
        testFileContents = AssembleExpErrTestContents(testNameLine, testDescription, request, expectedErrorCode)
    elif testType == 'f': # Functional test, gather expected response values
        expectedGameState = GetExpectedGameState() # "", "check", "checkmate", "stalemate"
        #print("DEBUG: our expected response gameState is %s" % expectedGameState)
        expectedPlayerState = GetExpectedPlayerState(playerColor) # Set when we chose playerColor
        #print("DEBUG: our expected response playerState is %s" % expectedPlayerState)
        movedPieces = GetMovedPieces(moveType, moveList) # string list of one or two pieces we expect *not* to see in response. 
                                                         # [<movedPiece>, <capturedPiece>] or [<rook>,<king>] for castling
        #print("DEBUG: Our Moved Pieces are %s" % movedPieces)
        expectedResponsePieces = GetResponsePieces(moveType, moveList) # string list of pieces new in response
                                                     # Moved piece(s) in new locs (w/ new type for pawnpromotion), two for castling
        #print("DEBUG: Our expected Response Pieces are %s" % expectedResponsePieces)
        testFileContents = AssembleFuncTestContents(testName, testDescription, request,\
                                                    expectedGameState, expectedPlayerState,\
                                                    movedPieces, expectedResponsePieces)
    else:
        print("Process ERROR: invalid testType %s. Exiting..." % testType)
        sys.exit(1)
    # Finish up...
    testFile = WriteTestFile(testType, testName, testFileContents)

    return 0

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
