import random, sys, pygame, time, copy
from pygame.locals import *

FPS = 10 # frames per second to update the screen
WINDOWWIDTH = 1200 # width of the program's window, in pixels
WINDOWHEIGHT = 675 # height in pixels
SPACESIZE = 32 # width & height of each space on the board, in pixels
BOARDWIDTH = 19 # how many columns of lines on the game board
BOARDHEIGHT = 19 # how many rows of lines on the game board
WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value

# Amount of space on the left & right side (XMARGIN) or above and below
# (YMARGIN) the game board, in pixels.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#              R    G    B
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
TAN        = (227, 195, 122)
GREEN      = (  0, 155,   0)

GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
bgColor = TAN
TEXTBGCOLOR = GREEN

def main():

    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Go')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    while True:
        runGame()

def runGame():
    mainBoard = getNewBoard()
    oldBoard = getNewBoard()
    groups = []
    turn = 'black'
    blackCaptures = 0
    whiteCaptures = 0
    passNumber = 0

    # Make the Surface and Rect objects for the "New Game" button
    newGameSurf = FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)

    # Make the Surface and Rect objects for the "Pass" button
    passSurf = FONT.render('Pass', True, TEXTCOLOR, TEXTBGCOLOR)
    passRect = passSurf.get_rect()
    passRect.topright = (WINDOWWIDTH - 8, 40)

    # Make the Surface and Rect objects for the "Resign" button
    resignSurf = FONT.render('Resign', True, TEXTCOLOR, TEXTBGCOLOR)
    resignRect = resignSurf.get_rect()
    resignRect.topright = (WINDOWWIDTH - 8, 70)


    drawBoard(mainBoard)
    drawTurn(turn)
    drawCaptures(blackCaptures, whiteCaptures)
    DISPLAYSURF.blit(newGameSurf, newGameRect)
    DISPLAYSURF.blit(passSurf, passRect)
    DISPLAYSURF.blit(resignSurf, resignRect)
    pygame.display.update()

    while True:
        captures = 0
        movexy = None
        while movexy == None:
            # Keep looping until the player clicks on a valid space.

            checkForQuit()
            passer = False
            for event in pygame.event.get(): # event handling loop
                if event.type == MOUSEBUTTONUP:
                    # Handle mouse click events
                    mousex, mousey = event.pos
                    if newGameRect.collidepoint( (mousex, mousey) ):
                        # Start a new game
                        return
                    if passRect.collidepoint( (mousex, mousey) ):
                        #make no move and switch turns
                        passer = True #to break out of outer loops
                        passNumber += 1
                        break
                    if resignRect.collidepoint( (mousex, mousey) ):
                        drawBoard(mainBoard)
                        drawCaptures(blackCaptures, whiteCaptures)
                        DISPLAYSURF.blit(passSurf, passRect)
                        DISPLAYSURF.blit(resignSurf, resignRect)
                        showGameOver(turn)
                        return
                    # movexy is set to a two-item tuple XY coordinate, or None value
                    movexy = getSpaceClicked(mousex, mousey)
                    if movexy != None and not isValidMove(mainBoard, movexy[0], movexy[1]):
                        movexy = None
            if passer == True:
                break
        if passer == True:
            drawBoard(mainBoard)
            drawPass(turn)
            turn = opposite(turn)
            if passNumber == 1:
                drawTurn(turn)
            drawCaptures(blackCaptures, whiteCaptures)
            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(passSurf, passRect)
            DISPLAYSURF.blit(resignSurf, resignRect)
            pygame.display.update()
            if passNumber == 2:
                showGameOver()
                return
            continue
        if turn == 'black':
            tile = 'BLACK_TILE'
        elif turn == 'white':
            tile = 'WHITE_TILE'

        #call function to get opposing pieces adjacent to (movexy[0], movexy[1])
        adjacentPieces = getAdjacentPieces(mainBoard, opposite(tile), movexy[0], movexy[1])

        #check each of those pieces' groups to see if they have 1 liberty; if so, remove them
        originalGroups = copy.deepcopy(groups)
        originalBoard = copy.deepcopy(mainBoard)
        for piece in adjacentPieces:
            for i in groups:
                if piece in i:
                    if numLiberties(mainBoard, i) == 1:
                        for (a, b) in i:
                            mainBoard[a][b] = EMPTY_SPACE
                            captures += 1
                        groups.remove(i)

        #call function to get friendly pieces adjacent to (movexy[0], movexy[1])
        adjacentPieces = getAdjacentPieces(mainBoard, tile, movexy[0], movexy[1])

        #tentatively join these pieces' groups (including the new move) into one new group
        newGroup = set()
        newGroup.add((movexy[0], movexy[1]))

        for piece in adjacentPieces:
            for i in groups:
                if piece in i:
                    newGroup = newGroup.union(i)

        #if that new group has zero liberties, continue (invalid move)
        newBoard = copy.deepcopy(mainBoard)
        newBoard[movexy[0]][movexy[1]] = tile
        if numLiberties(newBoard, newGroup) == 0:
            continue

        #if board is in a state that it was just in due to a ko fight, reset board and groups and continue
        different = False
        for i in range(len(newBoard)):
            for j in range(len(newBoard[i])):
                if newBoard[i][j] != oldBoard[i][j]:
                    different = True
        if not different and len(groups) > 0:
            #same state and not first move
            groups = originalGroups
            mainBoard = originalBoard
            continue
        else:
            oldBoard = originalBoard

        #otherwise, join the groups into one and remove the old groups
        groupsToRemove = []
        for i in range(len(groups)):
            for j in groups[i]:
                if j in newGroup:
                    groupsToRemove.append(i)
                    break
        groupsReplacement = []
        for i in range(len(groups)):
            if i not in groupsToRemove:
                groupsReplacement.append(groups[i])
        groups = groupsReplacement

        groups.append(newGroup)
        mainBoard = newBoard

        if turn == 'black':
            blackCaptures += captures
            turn = 'white'
        elif turn == 'white':
            whiteCaptures += captures
            turn = 'black'

        drawBoard(mainBoard, (movexy[0], movexy[1]))
        drawTurn(turn)
        drawCaptures(blackCaptures, whiteCaptures)
        DISPLAYSURF.blit(newGameSurf, newGameRect)
        DISPLAYSURF.blit(passSurf, passRect)
        DISPLAYSURF.blit(resignSurf, resignRect)
        pygame.display.update()
        passNumber = 0

        # Check for a winner.

def translateBoardToPixelCoord(x, y):
    return XMARGIN + x * SPACESIZE, YMARGIN + y * SPACESIZE

def drawBoard(board, last=None):
    # Draw background of board.
    DISPLAYSURF.fill(bgColor)

    # Draw grid lines of the board.
    for x in range(BOARDWIDTH):
        # Draw the horizontal lines.
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx = (x * SPACESIZE) + XMARGIN
        endy = YMARGIN + ((BOARDHEIGHT - 1) * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT):
        # Draw the vertical lines.
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx = XMARGIN + ((BOARDWIDTH - 1) * SPACESIZE)
        endy = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    # Draw the small circles on the go board.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if x % 6 == 3 and y % 6 == 3:
                centerx, centery = translateBoardToPixelCoord(x, y)
                pygame.draw.circle(DISPLAYSURF, GRIDLINECOLOR, (centerx, centery), 5, 0)

    # Draw the black & white tiles.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tileColor = WHITE
                else:
                    tileColor = BLACK
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
                if last == (x, y):
                    pygame.draw.circle(DISPLAYSURF, GREEN, (centerx, centery), int(SPACESIZE / 4) - 4)

def getSpaceClicked(mousex, mousey):
    # Return a tuple of two integers of the board space coordinates where
    # the mouse was clicked. (Or returns None not in any space.)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex > (x - 0.5) * SPACESIZE + XMARGIN and \
               mousex < (x + 0.5) * SPACESIZE + XMARGIN and \
               mousey > (y - 0.5) * SPACESIZE + YMARGIN and \
               mousey < (y + 0.5) * SPACESIZE + YMARGIN:
                return (x, y)
    return None

def drawPass(turn):
    passedSurf = FONT.render("%s Passed" % (turn.title()), True, TEXTCOLOR)
    passedRect = passedSurf.get_rect()
    passedRect.bottomleft = (10, 50)
    DISPLAYSURF.blit(passedSurf, passedRect)

def drawTurn(turn):
    # Draws whose turn it is at the bottom of the screen.
    turnSurf = FONT.render("%s's Turn" % (turn.title()), True, TEXTCOLOR)
    turnRect = turnSurf.get_rect()
    turnRect.bottomleft = (10, WINDOWHEIGHT - 5)
    DISPLAYSURF.blit(turnSurf, turnRect)

def drawCaptures(blackCaptures, whiteCaptures):
    if blackCaptures == 1:
        blackSurf = FONT.render("black has captured %d tile" % (blackCaptures), True, TEXTCOLOR)
    else:
        blackSurf = FONT.render("black has captured %d tiles" % (blackCaptures), True, TEXTCOLOR)

    blackRect = blackSurf.get_rect()
    blackRect.bottomleft = (10, WINDOWHEIGHT - 80)
    DISPLAYSURF.blit(blackSurf, blackRect)

    if whiteCaptures == 1:
        whiteSurf = FONT.render("white has captured %d tile" % (whiteCaptures), True, TEXTCOLOR)
    else:
        whiteSurf = FONT.render("white has captured %d tiles" % (whiteCaptures), True, TEXTCOLOR)

    whiteRect = whiteSurf.get_rect()
    whiteRect.bottomleft = (10, WINDOWHEIGHT - 60)
    DISPLAYSURF.blit(whiteSurf, whiteRect)

def getNewBoard():
    # Creates a brand new, empty board data structure.
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)

    return board

def isValidMove(board, xstart, ystart):
    # Returns False iff the player's move is invalid.
    if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):
        return False
    return True

def numLiberties(board, group):
    emptySpaces = set()
    for (a, b) in group:
        for j in getAdjacentPieces(board, EMPTY_SPACE, a, b):
            emptySpaces.add(j)
    return len(emptySpaces)

def getAdjacentPieces(board, tile, x, y):
    pieces = []
    if isOnBoard(x - 1, y) and board[x - 1][y] == tile:
        pieces.append((x - 1, y))
    if isOnBoard(x, y + 1) and board[x][y + 1] == tile:
        pieces.append((x, y + 1))
    if isOnBoard(x + 1, y) and board[x + 1][y] == tile:
        pieces.append((x + 1, y))
    if isOnBoard(x, y - 1) and board[x][y - 1] == tile:
        pieces.append((x, y - 1))
    return pieces

def isOnBoard(x, y):
    # Returns True if the coordinates are located on the board.
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT

def showGameOver(resigner=None):
    if resigner:
        resignSurf = FONT.render('%s Resigned'%resigner.title(), True, TEXTCOLOR)
        resignRect = resignSurf.get_rect()
        resignRect.bottomleft = (10, 70)
        DISPLAYSURF.blit(resignSurf, resignRect)

        winnerSurf = BIGFONT.render('%s Wins'%opposite(resigner).title(), True, TEXTCOLOR)
        winnerRect = winnerSurf.get_rect()
        winnerRect.topright = (WINDOWWIDTH - 8, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(winnerSurf, winnerRect)
    else:
        gameOverSurf = FONT.render('Game Over', True, TEXTCOLOR)
        gameOverRect = gameOverSurf.get_rect()
        gameOverRect.bottomleft = (10, 70)
        DISPLAYSURF.blit(gameOverSurf, gameOverRect)

    # Make the Surface and Rect objects for the "New Game" button
    newGameSurf = FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)
    DISPLAYSURF.blit(newGameSurf, newGameRect)
    pygame.display.update()

    while True:
        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                # Handle mouse click events
                mousex, mousey = event.pos
                if newGameRect.collidepoint( (mousex, mousey) ):
                    # Start a new game
                    return

def opposite(color):
    if color == 'black':
        return 'white'
    if color == 'white':
        return 'black'
    if color == 'WHITE_TILE':
        return 'BLACK_TILE'
    if color == 'BLACK_TILE':
        return 'WHITE_TILE'
    if color == 'BLACK':
        return 'WHITE'
    if color == 'WHITE':
        return 'BLACK'

def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

if __name__ == '__main__':
    main()

#to do:
#make list with every board state to be able to handle superko and multiple undo moves
#add ability to play computer
    #make a computer AI
#add code to score completed games
    #add komi (6.5?) text
#work on comments
#add option to undo move