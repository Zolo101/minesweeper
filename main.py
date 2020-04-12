import tcod
import tcod.event
from tcod.event import Point

from math import floor
import random

import sys

sys.setrecursionlimit(10**6)

# MENU = True

WIDTH = 16 # 10x10,16x16,30x16
HEIGHT = 16
FONT_IMG = "fonts/consolas48x48_gs_tc.png"

MINES = 40 # 10,40,99
FLAGS_REM = MINES

FIRST_CLICK = True

ORIGIN = Point(0,2)

PLAYER_LOCATION = Point(floor(WIDTH/2),floor(HEIGHT/2))

FACE_STATUS = {
    "Normal"    : ":)",
    "Nervous"   : ":O",
    "Won"       : ":D",
    "Failed"    : "X("
}

NUMBER_COLORS = {
    "0": (255,255,255), # basically .
    "1": (41,25,250),
    "2": (6,126,21),
    "3": (251,0,0),
    "4": (16,8,126),
    "5": (127,0,0),
    "6": (19,128,128),
    "7": (255,255,255), # real color: 0,0,0
    "8": (128,128,128)
}

CURRENT_STATUS = FACE_STATUS["Normal"]

field = [[0 for x in range(HEIGHT)] for y in range(WIDTH)]

class Tile:
    def __init__(self, char, hidden = False, flagged = False, mine = False,
                 nearbyMines = 0, x = 0, y = 0):
        self.char = char
        self.hidden = hidden
        self.flagged = flagged
        self.mine = mine
        self.nearbyMines = nearbyMines
        self.x = x
        self.y = y
    
    def NeighbourMines(self):
        inc = 0
        thalist = []
        for a in range(self.x-1,self.x+2):
            for b in range(self.y-1,self.y+2):
                if a < 0 or b < 0: #  no negative indexes
                    continue

                if a >= WIDTH or b >= HEIGHT: # doesnt exist
                    continue

                if field[a][b].mine == True:
                    inc += 1
                    thalist.append(field[a][b])
        return (inc,thalist)



def CreateField():
    fieldarray = []
    for x in range(WIDTH):
        for y in range(HEIGHT):
            field[x][y] = Tile(".",True,x=x,y=y) # NOTHING
            fieldarray.append((field[x][y].x,field[x][y].y))
    
    rm = random.sample(fieldarray, MINES)
    # print(rm)

    for m in range(MINES):
        field[rm[m][0]][rm[m][1]] = Tile("+",True,mine=True,x=rm[m][0],y=rm[m][1]) # MINE

    CheckNearbyMines()

def CheckNearbyMines():
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if field[x][y].mine == False:
                field[x][y].nearbyMines = field[x][y].NeighbourMines()[0]

def PrintMenu(console):
    console.print(0,0,"Mines Rem: " + str(FLAGS_REM))
    console.print(WIDTH-2,1,CURRENT_STATUS,fg=(156,156,0),bg=(255,255,0))
    console.print(0,1,"(R)etry")

def PrintMine(console,o): # Orginx/y
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if field[x][y].flagged == True:
                console.print(o.x+x,o.y+y,"F",fg=(0,0,255),bg=(128,0,0))
            elif field[x][y].hidden == True:
                console.print(o.x+x,o.y+y,"#",fg=(255,255,255),bg=(128,128,128))
            elif field[x][y].char == "+":
                console.print(o.x+x,o.y+y,field[x][y].char,fg=(255,255,255),bg=(255,0,0))
            else:
                if field[x][y].nearbyMines == 0:
                    console.print(o.x+x,o.y+y,".",fg=NUMBER_COLORS[str(field[x][y].nearbyMines)],bg=(0,0,0))
                    field[x][y].char = "."
                else:
                    console.print(o.x+x,o.y+y,str(field[x][y].nearbyMines),fg=NUMBER_COLORS[str(field[x][y].nearbyMines)],bg=(0,0,0))
                    field[x][y].char = str(field[x][y].nearbyMines)
    
    plrloc = field[PLAYER_LOCATION.x][PLAYER_LOCATION.y]

    char = plrloc.char
    if plrloc.hidden == True:
        char = "#"
    if plrloc.flagged == True and plrloc.hidden == True:
        char = "F"
    elif plrloc.mine == True and plrloc.hidden == False:
        char = "+"

    console.print(o.x+PLAYER_LOCATION.x,o.y+PLAYER_LOCATION.y,char,bg=(181,101,94))

def GameOver():
    global CURRENT_STATUS
    CURRENT_STATUS = FACE_STATUS["Failed"]
    for x in range(WIDTH):
        for y in range(HEIGHT):
            field[x][y].hidden = False

def CheckWon():
    global CURRENT_STATUS
    flaggedMines = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if field[x][y].mine == True and field[x][y].flagged == True:
                flaggedMines += 1
    
    if flaggedMines >= MINES:
        CURRENT_STATUS = FACE_STATUS["Won"]
        for x in range(WIDTH):
            for y in range(HEIGHT):
                field[x][y].hidden = False

def Restart():
    global CURRENT_STATUS
    global FLAGS_REM
    CreateField()
    CURRENT_STATUS = FACE_STATUS["Normal"]
    FLAGS_REM = MINES

def OpenZeroTiles(coords):

    if coords.x < 0 or coords.y < 0: #  no negative indexes
        return 
    
    if coords.x >= WIDTH or coords.y >= HEIGHT: # doesnt exist
        return

    otile = field[coords.x][coords.y]
    
    if otile.mine == True:
        return
    elif otile.hidden == False:
        return
    elif otile.nearbyMines > 0:
        otile.hidden = False
        return

    otile.hidden = False

    OpenZeroTiles(Point(coords.x-1,coords.y-1))
    OpenZeroTiles(Point(coords.x,coords.y-1))
    OpenZeroTiles(Point(coords.x+1,coords.y-1))
    OpenZeroTiles(Point(coords.x-1,coords.y))
    # OpenZeroTiles(Point(coords.x,coords.y))
    OpenZeroTiles(Point(coords.x+1,coords.y))
    OpenZeroTiles(Point(coords.x-1,coords.y+1))
    OpenZeroTiles(Point(coords.x,coords.y+1))
    OpenZeroTiles(Point(coords.x+1,coords.y+1))

def HintOpen(coords):
    hint = field[coords.x][coords.y].nearbyMines
    flagged = []
    hidden = []
    opened = []
    for a in range(coords.x-1,coords.x+2):
        for b in range(coords.y-1,coords.y+2):
            if a < 0 or b < 0: #  no negative indexes
                continue

            if a >= WIDTH or b >= HEIGHT: # doesnt exist
                continue
            
            if field[a][b].flagged == True:
                flagged.append(field[a][b])
            
            if field[a][b].nearbyMines == 0 and field[a][b].hidden == True:
                opened.append(field[a][b])
                continue
            
            if field[a][b].hidden == True:
                hidden.append(field[a][b])
            
    
    # print([len(flagged),hint])
    if len(flagged) >= hint:
        for h in range(len(hidden)):
            hidden[h].hidden = False
        
        for o in range(len(opened)):
            #opo = Point(opened[o])
            #print(Point(opened[o].x,opened[o].y))
            # print(field[opo.x][opo.y].hidden)
            #print("hello")
             
            #field[opo.x][opo.y].hidden = False
            # print(Point(opened[o].x,opened[o].y))
            OpenZeroTiles(Point(opened[o].x,opened[o].y))

def HintFlag(coords):
    global FLAGS_REM
    hint = field[coords.x][coords.y].nearbyMines
    hidden = []
    for a in range(coords.x-1,coords.x+2):
        for b in range(coords.y-1,coords.y+2):
            if a < 0 or b < 0: #  no negative indexes
                continue

            if a >= WIDTH or b >= HEIGHT: # doesnt exist
                continue

            if field[a][b].hidden == True or field[a][b].flagged == True:
                hidden.append(field[a][b])

    # print(hint)
    # print(len(hidden))
    
    if hint == len(hidden):
        for h in range(len(hidden)):
            if hidden[h].flagged == True:
                continue
            hidden[h].flagged = True
            FLAGS_REM -= 1

def OpenNearbyTiles(coords):
    for a in range(coords.x-2,coords.x+2):
        for b in range(coords.y-2,coords.y+2):
            if a < 0 or b < 0: #  no negative indexes
                continue

            if a >= WIDTH or b >= HEIGHT: # doesnt exist
                continue

            if field[a][b].mine == False:
                field[a][b].hidden = False

def OpenTile(coords):
    if coords.x < 0 or coords.y < 0: #  no negative indexes
        return
    try:
        field[coords.x][coords.y]
    except IndexError:
        return
    
    openedTile = field[coords.x][coords.y]
    if openedTile.mine == True:
        openedTile.hidden = False
        openedTile.flagged = False
        GameOver()
    elif openedTile.nearbyMines == 0:
        OpenZeroTiles(coords)
    elif openedTile.nearbyMines > 0 and openedTile.hidden == False:
        HintOpen(coords)
    else:
        openedTile.hidden = False

def FlagTile(coords):
    global FLAGS_REM
    flaggedTile = field[coords.x][coords.y]

    if flaggedTile.nearbyMines > 0:
        HintFlag(coords)

    if flaggedTile.hidden == False and flaggedTile.flagged == False:
        return

    if flaggedTile.flagged == False:
        if FLAGS_REM < 1:
            return
        else:
            flaggedTile.flagged = True
            FLAGS_REM -= 1
    else:
        flaggedTile.flagged = False
        FLAGS_REM += 1

def ClickHandler(coords):
    return Point(coords.x-ORIGIN[0],coords.y-ORIGIN[1])

def MovePL(coords):
    global PLAYER_LOCATION
    if coords.x < 0 or coords.y < 0: #  no negative indexes
        return
    
    if coords.x >= WIDTH or coords.y >= HEIGHT:
        return 

    PLAYER_LOCATION = coords

class State(tcod.event.EventDispatch):
    def ev_mousemotion(self, event):
        MovePL(ClickHandler(event.tile))
    def ev_mousebuttonup(self, event):
        if event.button == 1:
            OpenTile(ClickHandler(event.tile))
        if event.button == 3:
            FlagTile(ClickHandler(event.tile))
    def ev_keydown(self, event):
        # print(event.sym)
        if event.sym == 1073741906 or event.sym == 119: # up
            MovePL(Point(PLAYER_LOCATION.x,PLAYER_LOCATION.y-1))
        if event.sym == 1073741904 or event.sym == 97: # left
            MovePL(Point(PLAYER_LOCATION.x-1,PLAYER_LOCATION.y))
        if event.sym == 1073741905 or event.sym == 115: # down
            MovePL(Point(PLAYER_LOCATION.x,PLAYER_LOCATION.y+1))
        if event.sym == 1073741903 or event.sym == 100: # right
            MovePL(Point(PLAYER_LOCATION.x+1,PLAYER_LOCATION.y))
        if event.sym == 13: # open the tile the PLAYER_LOCATION is on
            OpenTile(PLAYER_LOCATION)
        if event.sym == 114:
            Restart() 


state = State()

CreateField()

tcod.console_set_custom_font(
    FONT_IMG,
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GRAYSCALE,
)

with tcod.console_init_root(WIDTH+ORIGIN.x,HEIGHT+ORIGIN.y,"Zelo's Minesweeper",order="F",vsync=True) as root_console:
    while True: # run every frame
        root_console.clear()
        PrintMenu(root_console)
        PrintMine(root_console,ORIGIN)
        tcod.console_flush()
        for event in tcod.event.wait():
            CheckWon()
            mouse_state = state.dispatch(event)

            if event.type == "QUIT":
                raise SystemExit()

