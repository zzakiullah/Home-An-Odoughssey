'''
Home - An O-dough-ssey
(title inspired by Farah)
Zulaikha Zakiullah

From here on out, I will refer to Poppin' Fresh (Pillsbury Doughboy) as PF.

There is a (potential) misconception that I have to clear up.
Or maybe I'm being paranoid.

Last but not least, to whoever's playing, if you think you know a lot about
Poppin' Fresh, playing this will prove you clearly don't. I still don't think
I do, since I'm only the narrator.
'''

from pygame import *
from random import *
from math import *
from glob import *  
import os

font.init()
init()

# all fonts
agencyFBGiant, agencyFBGiant2, agencyFBLarge, agencyFBLarge2, agencyFBLarge2Bold = font.SysFont('Agency FB', 300), font.SysFont('Agency FB', 100), font.SysFont('Agency FB', 60), font.SysFont('Agency FB', 50), font.SysFont('Agency FB', 56, True, False) 
agencyFBHuge, agencyFBBig2, agencyFBBig, agencyFBSmall = font.SysFont('Agency FB', 40, True, False), font.SysFont('Agency FB', 40), font.SysFont('Agency FB', 34), font.SysFont('Agency FB', 28) 

# centering the gaming screen
inf = display.Info()
windowPos = inf.current_w, inf.current_h
os.environ['SDL_VIDEO_WINDOW_POS'] = str((windowPos[0]-1250)//2)+", "+str((windowPos[1]-700)//2)
screen = display.set_mode((1250, 700)) #, FULLSCREEN)

# top bar display
display.set_caption("Home - An Odoughssey")
display.set_icon(transform.scale(image.load('Pictures/Menu/Pillsbury-logo.png'), (32, 32)))

vel = 0      # velocity/speed of player
healthNum = 10  # how much health player has left
healthPic = image.load('Pictures/health.png')

pfX, pfY = 0,0    # PF's position (on the screen)
# Portions of the background will be blitted onto the screen at a time.
# From there, PF's position in relation to the screen can be calculated.

# animation sequences for each of PF's movements
moveSeqs = [[image.load(r) for r in glob('Pictures/Sprites/run00*.png')], [image.load(b) for b in glob('Pictures/Sprites/brake00*.png')], [image.load(c) for c in glob('Pictures/Sprites/cruise00*.png')], [image.load(s) for s in glob('Pictures/Sprites/stop00*.png')]]
            # stopSeq only contains one image)
# sequences when he is hurt (has hit something, lost healthNum)
hurtSeqs = [[image.load(r) for r in glob('Pictures/Sprites/run-hurt*.png')], [image.load(b) for b in glob('Pictures/Sprites/brake-hurt*.png')], [image.load(c) for c in glob('Pictures/Sprites/cruise-hurt*.png')], [image.load(s) for s in glob('Pictures/Sprites/stop-hurt*.png')]]
# sequences when his health is low (only thing different is he has a frown)
sadSeqs = [[image.load(r) for r in glob('Pictures/Sprites/run-sad*.png')], [image.load(b) for b in glob('Pictures/Sprites/brake-sad*.png')], [image.load(c) for c in glob('Pictures/Sprites/cruise-sad*.png')], [image.load(s) for s in glob('Pictures/Sprites/stop-sad*.png')]]

moveTypes = ['run', 'brake', 'cruise', 'stop']
moveType = ''

seqNum = 0 # sequence number, showing what picture from the sprite is shown
groundY = 400  # y-pos of the ground

# levels
lvlNum = part = 1
lvlNames = ['Escape', 'Haste', 'Curiosity', 'Conflict', 'Loss', 'Addiction',
            'Fear', 'Ignorance', 'Belonging', 'Reminiscence']

startTime = time.get_ticks()//500
# elapsedTime -> time player has spent playing level
elapsedTime = startPauseTime = stopPauseTime = pausedTime = 0

sceneSpeeds = [10, 12, 14, 14, 14, 14, 16, 18, 14, 12]
sceneSpeed = sceneSpeeds[lvlNum-1] # number of pixels scene shifts every time
                                   # through the while page != 'exit' loop
# number of parts to each level (corresponds to number of songs that play in each level)
numLvlParts = [2, 2, 3, 3, 3, 3, 3, 3, 3, 2]
changingScene = False # True when switching scenes (song changes mid-level)
scenePts = [0, 1250]
scenes, shiftScenes = [], []
for i in range(1, 11):
    scenes.append([image.load(j) for j in glob('Pictures/Scenes/scene'+str(i)+'-*')])
    shiftScenes.append([])
    for j in range(numLvlParts[i-1]-1):
        shiftScenes[i-1].append([image.load(k) for k in glob('Pictures/Scene Changes/Level '+str(i)+'/*-'+str(j+1)+'-*')])
shiftNum = 0
# totalTimes -> amount of time each level takes to play (in seconds)
totalTimes = [186, 238, 282, 348, 364, 337, 363, 394, 289, 282] 
timeLeft = totalTimes[lvlNum-1]
click, pressed = True, True # click -> flag for mouse button being pressed, pressed -> flag for arrow keys being pressed
laneNum = 3 # lane player is in during game

songs = [glob('Music/Level '+str(i)+' - '+lvlNames[i-1]+'/*.ogg') for i in range(1, 11)]

# surfaces
infoSurf = Surface((1250, 700), SRCALPHA) # surface that info bars are on (health, ammo left, time left, etc.)
laneSurfs = [Surface((1250, 700), SRCALPHA) for i in range(5)] # surfaces for each lane (5 lanes)
popupSurf = Surface((1250, 700), SRCALPHA) # surface that buttons come up when game is paused
gameoverSurf = Surface((1250, 700), SRCALPHA) # surface that comes up in game over sequence
hurtSurf = Surface((1250, 700), SRCALPHA) # surface that is used when a player's health is <= 3, in which the screen turns a translucent red

numPoints = 0 # player's score

# ALL FUNCTIONS

# moving the scene along
def shiftScene(scenePic):
    global scenePts, sceneSpeed
    # screen blits 2 copies of the background side by side each time and shifts
    # to the left by a certasin number of pixels (value of sceneSpeed)
    screen.blit(scenePic,(scenePts[0], 0))
    screen.blit(scenePic,(scenePts[1], 0))
    scenePts = [scenePts[i] - sceneSpeed for i in range(len(scenePts))]
    for i in range(len(scenePts)):
        # when one picture is blitted to the left to the point where it doesn't
        # show up on the screen anymore, it is then blitted to the right side of
        # the screen
        if scenePts[i] <= -1250:
            scenePts[i] = 2500+scenePts[i]

hit = False
def chooseMove():
    global moveType, vel, laneNum, clickArrow
    # moving horizontally
    if keys[K_RIGHT]:
        moveType = 'run'
        vel += 1
    elif keys[K_LEFT]:
        moveType = 'brake'
        vel += -2
    elif keys[K_RIGHT] == False and keys[K_LEFT] == False and vel > 0:
        moveType = 'cruise'
        vel += -1
    elif vel == 0:
        moveType = 'stop'
        vel = 0
    # moving vertically (switching lanes)
    if keys[K_UP] and laneNum > 1:
        if clickArrow:
            laneNum -= 1
            clickArrow = False
    elif keys[K_DOWN] and laneNum < 5:
        if clickArrow:
            laneNum += 1
        clickArrow = False
    else:
        clickArrow = True

# moving character on the screen
def move(moveSeq, laneNumber):
    global pfX, pfY, vel, seqNum, pfPic, pfRect, groundY, laneSurfs
    if seqNum == len(moveSeq): # restarting move sequence
        seqNum = 0
    pfPic = moveSeq[seqNum%len(moveSeq)]
    if vel > 0:
        pfX += vel
    elif vel <= 0:
        vel = 0
    pfX -= sceneSpeed  # so PF will move back as the screen moves back
    groundY = 350+50*laneNumber-10
    pfY = groundY - pfPic.get_height()
    laneSurfs[laneNumber-1].blit(pfPic, (pfX, pfY))
    seqNum += 1
    # pfRect is used for checking whether PF has collided with an object or not
    pfRect = Rect(pfX, pfY, pfPic.get_width(), pfPic.get_height())

# shooting food
clickSpace = False # flag for when the spacebar is being pressed
ammoTypes = [image.load('Pictures/Ammo/cookie.png'), image.load('Pictures/Ammo/croissant.png'),
             image.load('Pictures/Ammo/cinnamon-roll.png'), image.load('Pictures/Ammo/pizza.png')]
ammoScores = [10, 10, 10, 10] # amount of each ammo player has; relates to ammoTypes, ammSymbols, and ammoNames
ammoUsing = ammoTypes[0] # ammo player is armed with at the moment
numAmmoTypes = [1, 1, 2, 2, 3, 3, 4, 4, 4, 4] # number of types of ammo in each level
ammoSymbols = [image.load('Pictures/Ammo/cookie-symbol.png'), image.load('Pictures/Ammo/croissant-symbol.png'),
               image.load('Pictures/Ammo/cinnamon-roll-symbol.png'), image.load('Pictures/Ammo/pizza-symbol.png')]
shootSpeed = 30 # speed that ammo is being launched
ammoNames = ['cookie', 'croissant', 'cinnamon roll', 'pizza']
def chooseAmmo(ammoList, level):
    global ammoUsing
    if keys[K_1]:
        ammoUsing = ammoList[0]    
    elif keys[K_2] and level >= 3:
        ammoUsing = ammoList[1]
    elif keys[K_3] and level >= 5:
        ammoUsing = ammoList[2]
    elif keys[K_4] and level >= 7:
        ammoUsing = ammoList[3]
shotInfo = []
# when a player has just hit the space bar
def initShoot(laneNumber):
    global shotInfo, ammoScores, ammoTypes
    # shotInfo appends a list that contains:
    # [shot xPos, shot yPos, ammo type (that was shot), lane the ammo shot is in]
    shotInfo.append([pfX+pfPic.get_width()-50, groundY-68, ammoUsing, laneNumber])
    # deducting 1 ammo from the number of ammo the player has
    ammoScores[ammoTypes.index(ammoUsing)] = ammoScores[ammoTypes.index(ammoUsing)] - 1

# used when a shot is flying in the air
def shoot():
    global shotInfo, shootSpeed, lvlNum
    for s in range(len(shotInfo)):
        # adds shootSpeed to xPos of shot, making the shot move across the screen
        shotInfo[s] = [shotInfo[s][0]+shootSpeed]+shotInfo[s][1:]
        laneSurfs[shotInfo[s][3]-1].blit(shotInfo[s][2], (shotInfo[s][0], shotInfo[s][1]))
    # deletes any shots in the list if their xPos is > 1250 in which case they'd be offscreen
    shotInfo = [shotInfo[s] for s in range(len(shotInfo)) if shotInfo[s][0] < 1250]

explodePos = []
# checking player collision with objects on screen (excluding reload cans)
def checkObjHit(objRectList):
    global numPoints, objPos, shotInfo, shootSpeed, laneNum, explodePos
    delPosRect, delPosShot = [], []
    for objRect in objRectList:
        for i in range(len(shotInfo)):
            # checks if pfRect collides with an objectRect
            if objRect.collidepoint((shotInfo[i][0], shotInfo[i][1])) and (objRect[1]-300)//50 == shotInfo[i][3]-1:
                explodePos.append([objRect[0], shotInfo[i][3]-1, 0, objRect[2]//50])
                numPoints += 5
                delPosRect.append(objRectList.index(objRect))
                delPosShot.append(i)
    objPos = [objPos[i] for i in range(len(objPos)) if i not in delPosRect]
    shotInfo = [shotInfo[i] for i in range(len(shotInfo)) if i not in delPosShot]
    
explodeSeq = [image.load(e) for e in glob('Pictures/Ammo/explosion*')]
# exploding objects once they've been hit
def explodeAmmo():
    global explodePos, laneSurfs, sceneSpeed, objPos
    for i in range(len(explodePos)):
        explodePic = explodeSeq[explodePos[i][2]]
        for j in range(explodePos[i][3]):
            laneSurfs[explodePos[i][1]].blit(explodePic, (explodePos[i][0]+j*50, 400+50*explodePos[i][1]-explodePic.get_height()))
        explodePos[i][0] = explodePos[i][0] - sceneSpeed
        explodePos[i][2] = explodePos[i][2] + 1
    for i in range(len(explodePos)):
        if explodePos[0][2] > len(glob('Pictures/Ammo/explosion*'))-1:
            del explodePos[0]

hurt, healing, offScreen, hurtTime, offScreenStartTime = False, False, True, -1, 0
# checking if character has hit an obstacle
def checkPlayerHit(characterRect, objRectList, laneNumber):
    global hurtTime, hurt, healing, healthNum, hit, offScreen, offScreenStartTime
    if hurt == False and healing == False:
        for objRect in objRectList:
            if characterRect.colliderect(objRect) and (objRect[1]-300)//50 == laneNumber-1 and healthNum > 0:
                hurtTime, hurt, hit = time.get_ticks()//1000, True, True
        if pfX <= 0-pfPic.get_width() or pfX >= 1250:
            if offScreen:
                offScreenStartTime, offScreen = time.get_ticks()//1000, False
            if time.get_ticks()//1000 - offScreenStartTime == 2:
                hurtTime, hurt, hit = time.get_ticks()//1000, True, True
    if hurtTime > 0:
        if hurt:
            healthNum -= 1
            hurt, healing = False, True
        else:
            if time.get_ticks()//1000 - hurtTime == 2:
                healing, hit, offScreen, hurtTime = False, False, True, -1

objSpeeds = [[10, 10, 10, 10], [20, 16, 22, 12, 14, 18], [18, 20, 10, 10, 20, 22, 26, 18],
             [16, 20, 20, 14, 18, 20, 16, 16], [16, 16, 16, 16], [14, 14, 14, 16, 16, 12, 16, 16],
             [18, 14, 14, 18, 16, 16], [18, 20, 20, 20, 22, 18, 22, 22],
             [18, 18, 18, 12, 10, 10, 10], [10, 10, 10, 10]]
# objects/obstacles
obj = [[image.load(i) for i in glob('Pictures/Obstacles/Level '+str(j)+'/*')] for j in range(1, 11)]
# whether each level has objects coming from the left, right, or both
lvlDirects = [['left'], ['left', 'right'], ['left', 'right'], ['left', 'right'], ['left', 'right'], ['left', 'right'], ['left', 'right'], ['left', 'right'], ['left', 'right'], ['left', 'right']]

signs = [-1, 1] # -1 corresponds to objects moving left on screen, their x-values decreasing
                # +1 corresponds to objects moving right on screen, their x-values increasing
# colours corresponding to objects
objClrs = [(255,0,0),(0,0,255),(0,255,0),(255,255,0),(255,0,255),(0,255,255),(100,0,0),(0,0,100)]
# colours corresponding to targets
targetClrs = [(0,0,0),(50,50,50),(100,100,100),(150,150,150),(200,200,200)]
# colours corresponding to reload cans
reloadClrs = [(128,0,255),(64,0,64),(150,40,220),(140,70,180)]
def loadItems(levelNum, objList, speeds):
    global objPts, targetPts, reloadPts, objPos, targetPos, reloadPos, x, y, pics, p
    pics = [image.load('Levels/level'+str(levelNum)+'-'+d+'.png') for d in lvlDirects[lvlNum-1]]    
    for x in range(pics[0].get_width()):
        for y in range(pics[0].get_height()):
            for p in pics:
                if p.get_at((x, y))[:3] != (255, 255, 255) and p.get_at((x, y))[:3] in objClrs:
                    objPts.append([x, y, objList[levelNum-1][objClrs.index(p.get_at((x, y))[:3])], speeds[objClrs.index(p.get_at((x, y))[:3])]*signs[pics.index(p)], signs[pics.index(p)]]) 
                elif p.get_at((x, y))[:3] != (255, 255, 255) and p.get_at((x, y))[:3] in targetClrs:
                    loadTargets(p.get_at((x, y))[:3])
                elif p.get_at((x, y))[:3] != (255, 255, 255) and p.get_at((x, y))[:3] in reloadClrs:
                    loadReloadAmmo(p.get_at((x, y))[:3])
    objPos = []
    targetPos = []
    reloadPos = []

targetPts = []
targets = [image.load('Pictures/Targets/cookie-target.png'), image.load('Pictures/Targets/croissant-target.png'),
           image.load('Pictures/Targets/cinnamon-roll-target.png'), image.load('Pictures/Targets/pizza-target.png'),
           image.load('Pictures/Targets/rainbow-target.png')]
targetPos = []
# recording target positions
def loadTargets(col):
    global targetPts, x, y
    targetPts.append([x, y, targets[targetClrs.index(col)], sceneSpeed*signs[pics.index(p)], signs[pics.index(p)]])
reloadAmmo = [image.load('Pictures/Reload/cookie.png'), image.load('Pictures/Reload/croissant.png'),
              image.load('Pictures/Reload/cinnamon-roll.png'), image.load('Pictures/Reload/pizza.png')]              
reloadPts = []
# recording reload can positions
def loadReloadAmmo(col):
    global reloadPts, x, y
    reloadPts.append([x, y, reloadAmmo[reloadClrs.index(col)], sceneSpeed*signs[pics.index(p)], signs[pics.index(p)]])
reloadPos = []
objRects = []
targetRects = []
reloadRects = []

startObjX, startTargX, startReloadX = 0, 0, 0
# setting the obstacles on the screen
def setObj():
    global elapsedTime, objPts, objPos, sceneSpeed, laneSurfs, objRects
    objRects = []
    for i in range(len(objPts)):
        if elapsedTime == objPts[0][0]:
            if signs.index(objPts[0][4]) == 0:
                startObjX = 1250 # if objects are moving left
            else:
                startObjX = 0-objPts[0][2].get_width() # if objects are moving right
            objPos.append([startObjX, objPts[0][1], objPts[0][2], objPts[0][3]])
            del objPts[0]
    for i in range(len(objPos)):
        laneSurfs[objPos[i][1]].blit(objPos[i][2], (objPos[i][0], 385+50*objPos[i][1]-objPos[i][2].get_height()))
        objRects.append(Rect(objPos[i][0], 300+objPos[i][1]*50, objPos[i][2].get_width(), 50))
        objPos[i][0] = objPos[i][0] + objPos[i][3]
    for i in range(len(objPos)):
        if objPos[0][0] < -1*objPos[0][2].get_width():
            del objPos[0]
            del objRects[0]

# setting targets
def setTargets():
    global targetPts, targetPos, targetRects, elapsedTime, laneSurfs
    targetRects = []
    for i in range(len(targetPts)):
        if elapsedTime == targetPts[0][0]:
            if signs.index(targetPts[0][4]) == 0:
                startTargX = 1250
            else:
                startTargX = 0-objPts[0][2].get_width()
            targetPos.append([startTargX, targetPts[0][1], targetPts[0][2], targetPts[0][3]])
            del targetPts[0]
    for i in range(len(targetPos)):
        laneSurfs[targetPos[i][1]].blit(targetPos[i][2], (targetPos[i][0], 385+50*targetPos[i][1]-targetPos[i][2].get_height()))
        targetRects.append(Rect(targetPos[i][0], 300+targetPos[i][1]*50, targetPos[i][2].get_width(), targetPos[i][2].get_height()))
        targetPos[i][0] = targetPos[i][0] + targetPos[i][3]
    for i in range(len(targetPos)):
        if targetPos[0][0] < -1*targetPos[0][2].get_width():
            del targetPos[0]
            del targetRects[0]

reloadRects = []
# setting reload cans (for ammo)
def setReload():
    global reloadPts, reloadPos, reloadRects, elapsedTime, laneSurfs
    reloadRects = []
    for i in range(len(reloadPts)):
        if elapsedTime == reloadPts[0][0]:
            if signs.index(reloadPts[0][4]) == 0:
                startReloadX = 1250
            else:
                startReloadX = 0-objPts[0][2].get_width()
            reloadPos.append([startReloadX, reloadPts[0][1], reloadPts[0][2], reloadPts[0][3]])
            del reloadPts[0]
    for i in range(len(reloadPos)):
        laneSurfs[reloadPos[i][1]].blit(reloadPos[i][2], (reloadPos[i][0], 385+50*reloadPos[i][1]-reloadPos[i][2].get_height()))
        reloadRects.append(Rect(reloadPos[i][0], 300+reloadPos[i][1]*50, reloadPos[i][2].get_width(), reloadPos[i][2].get_height()))
        reloadPos[i][0] = reloadPos[i][0] + reloadPos[i][3]
    for i in range(len(reloadPos)):
        if reloadPos[0][0] < -1*reloadPos[0][2].get_width():
            del reloadPos[0]
            del reloadRects[0]

numTargetPts = [10, 20, 40, 80, 200] # amount of points each target is worth
targExpPos = []
# if player has hit target with correct ammo, target will explode blue
rightTargExp = [image.load(b) for b in glob('Pictures/Targets/blue0*')]
# if player has hit target with incorrect ammo, target will explode red
wrongTargExp = [image.load(f) for f in glob('Pictures/Targets/fire0*')]
targExpSeqs = [rightTargExp, wrongTargExp]

# check if player hit target with ammo
def checkTargetHit(ammoInUse, targetRectList):
    global numPoints, targetPos, shotInfo, shootSpeed, laneNum, targExpPos
    delPosRect, delPosShot = [], []
    for targetRect in targetRectList:
        for i in range(len(shotInfo)):
            if targetRect.collidepoint((shotInfo[i][0], shotInfo[i][1])) and (targetRect[1]-300)//50 == shotInfo[i][3]-1:
                # check if player hit target with correct ammo
                if ammoTypes.index(ammoInUse) == targets.index(targetPos[targetRectList.index(targetRect)][2]) or targets.index(targetPos[targetRectList.index(targetRect)][2]) == 4:
                    targExpPos.append([targetRect[0], shotInfo[i][3]-1, 0, 0])
                    muteSound('Sounds/Woo_hoo.ogg')
                    numPoints += numTargetPts[targets.index(targetPos[targetRectList.index(targetRect)][2])]
                else:
                    targExpPos.append([targetRect[0], shotInfo[i][3]-1, 0, 1])
                    numPoints -= numTargetPts[ammoTypes.index(ammoInUse)]
                delPosRect.append(targetRectList.index(targetRect))
                delPosShot.append(i)
    targetPos = [targetPos[i] for i in range(len(targetPos)) if i not in delPosRect]
    shotInfo = [shotInfo[i] for i in range(len(shotInfo)) if i not in delPosShot]

# exploding target
def explodeTarget():
    global targExpPos, laneSurfs, sceneSpeed, explodeSurf
    for i in range(len(targExpPos)):
        explodePic = targExpSeqs[targExpPos[i][3]][targExpPos[i][2]]
        laneSurfs[targExpPos[i][1]].blit(explodePic, (targExpPos[i][0], 400+50*targExpPos[i][1]-explodePic.get_height()))
        targExpPos[i][0] = targExpPos[i][0] - sceneSpeed
        targExpPos[i][2] = targExpPos[i][2] + 1
    for i in range(len(targExpPos)):
        if targExpPos[0][2] > len(targExpSeqs[targExpPos[0][3]])-1:
            del targExpPos[0]

# check if player collides with a reload ammo object
def checkReload(characterRect, numAmmoList):
    global reloadPos, reloadRects, numPoints
    for reloadRect in reloadRects:
        if reloadRect.colliderect(characterRect) and laneNum-1 == (reloadRect[1]-300)//50:
            if numAmmoList[reloadAmmo.index(reloadPos[reloadRects.index(reloadRect)][2])] == 10:
                numPoints += 10
            numAmmoList[reloadAmmo.index(reloadPos[reloadRects.index(reloadRect)][2])] = 10
            del reloadPos[reloadRects.index(reloadRect)]
            del reloadRects[reloadRects.index(reloadRect)]
    return numAmmoList

# music, sound, and pause buttons
buttonPics = [image.load(i) for i in glob('Pictures/Buttons/*-button.png')]
buttonClrs = [(0, 0, 0, 180), (0, 0, 0, 180), (0, 0, 0, 180)]
buttonFlags = [True, True, False] # music on true, sound on true, game paused false
# music, sound, and pause rects
buttonRects = [Rect(1060, 635, 50, 50), Rect(1120, 635, 50, 50), Rect(1180, 635, 50, 50)]

# loading tip pictures (show at bottom of gaming screen, says how to play, etc.
# though I do admit some of them are kind of filler
tipPics = []
for i in range(1, 11):
    tipPics.append([image.load(j) for j in glob('Pictures/Tips/tip'+str(i)+'-*')])

redX = image.load('Pictures/Buttons/x.png')
# displaying stat bars, time left in game, etc.
def showInfo(health, healthSymbol, score, elapTime, totalTime):
    global agencyFBBig, agencyFBSmall, numAmmoTypes, lvlNum, ammoTypes, ammoSymbols, ammoScores, ammoUsing, buttonPics, buttonFlags, infoSurf, timeLeft
    draw.rect(infoSurf, (0, 0, 0, 0), (0, 0, 1250, 700))
    # health bar
    draw.rect(infoSurf, (0, 0, 0, 180), (940, 10, 290, 40))
    statTxt = agencyFBBig.render(str(healthNum), True, (255, 255, 255))
    infoSurf.blit(statTxt, (965-statTxt.get_width(), 10))
    draw.rect(infoSurf, (210, 210, 210), (994, 20, 230, 20))
    draw.rect(infoSurf, (210, 10, 10), (993, 21, health*23, 18))
    infoSurf.blit(healthSymbol, (968, 11))
    # amount of each ammo
    for i in range(numAmmoTypes[lvlNum-1]):
        if ammoUsing == ammoTypes[i]:
            draw.circle(infoSurf, (0, 200, 255, 180), (60+i*100, 45), 35)
        else:
            draw.circle(infoSurf, (0, 0, 0, 180), (60+i*100, 45), 35)
        draw.circle(infoSurf, (0, 0, 0, 180), (25+i*100, 20), 15)
        draw.circle(infoSurf, (0, 0, 0, 180), (95+i*100, 70), 20)
        infoSurf.blit(ammoSymbols[i], (60+i*100-ammoSymbols[i].get_width()//2, 45-ammoSymbols[i].get_height()//2))
        keyNum = agencyFBSmall.render(str(i+1), True, (0, 200, 255))
        ammoScoreTxt = agencyFBSmall.render(str(ammoScores[i]), True, (255, 255, 255))
        infoSurf.blit(keyNum, (25+i*100-keyNum.get_width()//2, 20-keyNum.get_height()//2))
        infoSurf.blit(ammoScoreTxt, (95+i*100-ammoScoreTxt.get_width()//2, 70-ammoScoreTxt.get_height()//2))        
    # pause, sound, and music buttons
    for i in range(3):
        draw.circle(infoSurf, buttonClrs[i], (1085+60*i, 660), 25)    
        infoSurf.blit(buttonPics[i], (1085+60*i-buttonPics[i].get_width()//2, 660-buttonPics[i].get_height()//2))
        if buttonFlags[i] == False and i != 2: # @ position 2 is the pause button & there's no need to put an x on top of the pause button                                       
            infoSurf.blit(redX, (1085+60*i-redX.get_width()//2, 660-redX.get_height()//2))
    # score
    scoreTxt = agencyFBBig.render('- '+str(score)+' -', True, (255, 255, 255))
    draw.rect(infoSurf, (0, 0, 0, 180), (620-scoreTxt.get_width()//2, 10, scoreTxt.get_width()+10, scoreTxt.get_height()+10))
    infoSurf.blit(scoreTxt, (625-scoreTxt.get_width()//2, 15))
    screen.blit(infoSurf, (0, 0))
    # clock (how much time is left in the level) 
    draw.circle(infoSurf, (0, 0, 0, 180), (60, 650), 35)
    timeLeft = totalTime - elapTime
    if timeLeft < 0:
        timeLeft = 0
    timeLeftMin = str(timeLeft//60)
    if 0 <= timeLeft%60 < 10:
        timeLeftSec = '0'+str(timeLeft%60)
    else:
        timeLeftSec = str(timeLeft%60)
    timeTxt = agencyFBSmall.render(timeLeftMin+':'+timeLeftSec, True, (0, 200, 255))
    infoSurf.blit(timeTxt, (60-timeTxt.get_width()//2, 650-timeTxt.get_height()//2))
    endAng = 2*pi*(timeLeft/totalTime)
    draw.arc(infoSurf, (0, 200, 255), (29, 619, 62, 62), pi/2, pi/2+endAng, 5)
    # tip section
    draw.rect(infoSurf, (0, 0, 0, 180), (625-tipPics[lvlNum-1][part-1].get_width()//2, 690-tipPics[lvlNum-1][part-1].get_height(), tipPics[lvlNum-1][part-1].get_width(), tipPics[lvlNum-1][part-1].get_height()))
    infoSurf.blit(tipPics[lvlNum-1][part-1], (625-tipPics[lvlNum-1][part-1].get_width()//2, 690-tipPics[lvlNum-1][part-1].get_height()))
    screen.blit(infoSurf, (0, 0))

def checkSounds():
    global click, buttonRects, buttonClrs, buttonFlags
    # checking whether music and/or sound is on
    for i in range(len(buttonRects)-1):
        if buttonRects[i].collidepoint((mx, my)):
            buttonClrs[i] = (0, 200, 255)
            if mb[0] == 1:
                if buttonFlags[i] and click:
                    buttonFlags[i] = False
                    click = False
                if buttonFlags[i] == False and click:
                    buttonFlags[i] = True
        else:
            buttonClrs[i] = (0, 0, 0, 180)

def muteMusic(flagList):
    # muting music or playing it
    if flagList[0] == False:
        mixer.music.set_volume(0)
    else:
        mixer.music.set_volume(0.5)

# options that show when game is paused
popupRects = [Rect(545, 260, 160, 50), Rect(545, 320, 160, 50),
              Rect(545, 380, 160, 50), Rect(545, 440, 160, 50)]
popupButtons = ['Back (B)', 'Restart (R)', 'Journey Select (J)', 'Main Menu (M)']
# pause (useless comment)
def pause(pic, rectList):
    global click, pausedTime, justPaused, startPauseTime
    if justPaused:
        startPauseTime = time.get_ticks()//500
        justPaused = False
    mixer.music.pause()
    pages = ['play', 'play', 'select level', 'menu']
    draw.rect(popupSurf, (0, 0, 0, 0), (0, 0, 1250, 700))
    screen.blit(pic, (0, 0))
    pauseTxt = agencyFBBig.render('< GAME PAUSED >', True, (255, 255, 255))
    draw.rect(popupSurf, (0, 0, 0, 180), (0, 0, 1250, 700))
    popupSurf.blit(pauseTxt, (625-pauseTxt.get_width()//2, 185+pauseTxt.get_height()//2))
    for popRect in popupRects:
        draw.rect(popupSurf, (0, 0, 0), (popRect))
        popTxt = agencyFBSmall.render(popupButtons[popupRects.index(popRect)], True, (255, 255, 255))
        popupSurf.blit(popTxt, (625-popTxt.get_width()//2, popRect[1]+popRect[3]//2-popTxt.get_height()//2))
        if popRect.collidepoint((mx, my)):
            draw.rect(popupSurf, (255, 255, 255), (popRect), 2)
            if mb[0] == 1 and click:
                if popupRects.index(popRect) == 1:
                    startLevel()
                if popupRects.index(popRect) != 0:
                    mixer.music.stop()
                    # if person chooses not to go back to game, elapsedTime
                    # must be added to pausedTime to put elapsedTime back to zero
                    pausedTime = elapsedTime + initPauseTime + time.get_ticks()//500 - startPauseTime
                else:
                    mixer.music.unpause()
                    # if person chooses to go back to current game, elapsedTime
                    # cannot be added so elapsedTime is not set to zero
                    pausedTime = initPauseTime + time.get_ticks()//500 - startPauseTime
                click = False
                return pages[popupRects.index(popRect)]
    # keyboard shortcuts
    if keys[K_b]:
        mixer.music.unpause()
        pausedTime = initPauseTime + time.get_ticks()//500 - startPauseTime
        return 'play'
    if keys[K_r]:
        startLevel()
        mixer.music.stop()
        pausedTime = elapsedTime + initPauseTime + time.get_ticks()//500 - startPauseTime
        return 'play'
    if keys[K_j]:
        mixer.music.stop()
        pausedTime = elapsedTime + initPauseTime + time.get_ticks()//500 - startPauseTime
        return 'select level'
    if keys[K_m]:
        mixer.music.stop()
        pausedTime = elapsedTime + initPauseTime + time.get_ticks()//500 - startPauseTime
        return 'menu'
    screen.blit(popupSurf, (0, 0))
    return 'pause'

# play sequence
def play():
    global playOnce, reloadPts, reloadPos, reloadRects, targetPts, targetPos, targetRects, objPos, objPts, objRects, laneSurfs, click, shiftNum, justPaused, buttonRects, buttonClrs, initPauseTime, pausedTime, clickSpace, changingScene, lvlNum, part, numPoints, health, elapsedTime, totalTime, pausePic, mb, mx, my
    playOnce = True
    if numPoints < 0: # so a player can't get a negative score
        numPoints = 0
    for i in range(5): # drawing each surface for each lane
        draw.rect(laneSurfs[i], (0, 0, 0, 0), (0, 0, 1250, 700))
    justPaused = True
    if elapsedTime == 0:
        mixer.music.stop()
    chooseMove()
    chooseAmmo(ammoTypes, lvlNum)
    keys = key.get_pressed()
    # more keyboard shortcuts if you get lazy and don't feel like using your mouse
    if keys[K_p]:
        return 'pause'
    if keys[K_r]:
        startLevel()
        return 'play'
    # shooting
    if keys[K_SPACE]:
        if clickSpace and ammoScores[ammoTypes.index(ammoUsing)] > 0:
            initShoot(laneNum)
            clickSpace = False
        else:
            clickSpace = True
    if mixer.music.get_busy() == False and part == 1 and elapsedTime == 0:
        mixer.music.load(songs[lvlNum-1][part-1])
        mixer.music.play()
    elif mixer.music.get_busy() == False and part < numLvlParts[lvlNum-1]:
        changingScene = True
    # when level is done
    if timeLeft == 0:
        sceneSpeed = 0
        return 'end level'
    if changingScene:
        shiftScene(shiftScenes[lvlNum-1][part-1][shiftNum])
        shiftNum += 1
        if shiftNum > 5:
            shiftNum = 0
            changingScene = False
            part += 1
            mixer.music.load(songs[lvlNum-1][part-1])
            mixer.music.play()
    else:        
        shiftScene(scenes[lvlNum-1][part-1])
    setObj()
    setTargets()
    setReload()
    checkObjHit(objRects)
    checkTargetHit(ammoUsing, targetRects)
    explodeTarget()
    explodeAmmo()
    shoot()
    if hit:
        move(hurtSeqs[moveTypes.index(moveType)], laneNum)
    elif hit == False and healthNum > 3:
        move(moveSeqs[moveTypes.index(moveType)], laneNum)
    else:
        move(sadSeqs[moveTypes.index(moveType)], laneNum)
    for i in range(len(laneSurfs)):
        screen.blit(laneSurfs[i], (0, 0))
    checkPlayerHit(pfRect, objRects+targetRects, laneNum)
    if hit and healthNum < 4:
        draw.rect(hurtSurf, (255, 0, 0, 120), (0, 0, 1250, 700))
        screen.blit(hurtSurf, (0, 0))
    if healthNum == 0:
        sceneSpeed = 0
        return 'game over'
    checkReload(pfRect, ammoScores)
    showInfo(healthNum, healthPic, numPoints, elapsedTime//2, totalTimes[lvlNum-1])
    checkSounds()
    muteMusic(buttonFlags)
    pausePic = screen.copy()
    initPauseTime = pausedTime
    if buttonRects[2].collidepoint((mx, my)):
        buttonClrs[2] = (0, 200, 255)
        if mb[0] == 1 and click:
            click = False
            return 'pause'
    else:
        buttonClrs[2] = (0, 0, 0, 180)
    elapsedTime = time.get_ticks()//500-pausedTime
    return 'play'

clickArrow = False

pages = ['play', 'pause', 'select level', 'epilogue', 'menu']
pauseButtons = ['play', 'restart', 'select level', 'menu']

# setting all variables to what they should be at beginning of any level
def startLevel():
    global sceneSpeed, numPoints, ammoUsing, numAmmoLeft, offScreen, comparingScore, ammoScores, healthNum, startTime, elapsedTime, startPauseTime, laneNum, part, pfX, vel, objPts, page, targetPts, targetPos, hit, reloadPts, reloadPos, objPts, objPos
    objPts, objPos, targetPts, targetPos, reloadPts, reloadPos = [], [], [], [], [], []
    loadItems(lvlNum, obj, objSpeeds[lvlNum-1])
    startTime, healthNum, ammoScores, numAmmoLeft, laneNum, part, pfX = time.get_ticks()//500, 10, [10, 10, 10, 10], 0, 3, 1, 200
    numPoints = elapsedTime = startPauseTime = vel = 0
    comparingScore, hit, timeLeft, sceneSpeed, offScreen = True, False, totalTimes[lvlNum-1], sceneSpeeds[lvlNum-1], True
    ammoUsing = ammoTypes[0]

lvlShown = 1 # level shown on level select screen

loadedScenes, circLoadScenes = [image.load(i) for i in glob('Pictures/Level Select/loading*')], [image.load(i) for i in glob('Pictures/Level Select/level*')]
selectLvlTxt = agencyFBBig.render('Use left & right arrow keys or click arrows to select level. Press enter or click bubble to start level.', True, (255, 255, 255))
leftArrow, blueLeftArrow = agencyFBGiant.render('<', True, (255, 255, 255)), agencyFBGiant.render('<', True, (0, 200, 255)) 
leftArrowRect = Rect(150, 325-leftArrow.get_height()//2, leftArrow.get_width(), leftArrow.get_height())
rightArrow, blueRightArrow = agencyFBGiant.render('>', True, (255, 255, 255)), agencyFBGiant.render('>', True, (0, 200, 255)) 
rightArrowRect = Rect(1100-rightArrow.get_width(), 325-rightArrow.get_height()//2, rightArrow.get_width(), rightArrow.get_height())
bubbleRect = Rect(400, 100, 450, 450)
# level select screen
def selectLevel():
    global page, click, lvlShown, pressed
    startSong('Music/The Legend of Zelda Ocarina of Time - Title Theme.ogg')
    mx, my = mouse.get_pos()
    keys = key.get_pressed()
    if keys[K_RETURN] or mb[0] == 1 and bubbleRect.collidepoint((mx, my)) and click:
        click = False
        page = 'play'
        return lvlShown, page
    if (keys[K_LEFT] and pressed or leftArrowRect.collidepoint((mx, my)) and mb[0] == 1 and click) and lvlShown != 1:
        click = False
        pressed = False
        lvlShown -= 1
    if (keys[K_RIGHT] and pressed or rightArrowRect.collidepoint((mx, my)) and mb[0] == 1 and click) and lvlShown != 10:
        click = False
        pressed = False
        lvlShown += 1
    if keys[K_LEFT] == False and keys[K_RIGHT] == False:
        pressed = True
    screen.blit(loadedScenes[lvlShown-1], (0, 0))
    screen.blit(circLoadScenes[lvlShown-1], (400, 100))
    screen.blit(selectLvlTxt, (625-selectLvlTxt.get_width()//2, 30))
    if lvlShown != 1 and leftArrowRect.collidepoint((mx, my)):
        screen.blit(blueLeftArrow, (150, 325-leftArrow.get_height()//2))
    elif lvlShown != 1:
        screen.blit(leftArrow, (150, 325-leftArrow.get_height()//2))
    if lvlShown != 10 and rightArrowRect.collidepoint((mx, my)):
        screen.blit(blueRightArrow, (1100-rightArrow.get_width(), 325-rightArrow.get_height()//2))
    elif lvlShown != 10:
        screen.blit(rightArrow, (1100-rightArrow.get_width(), 325-rightArrow.get_height()//2))
    menuButton()
    return 0, page

# opts --> menu button pictures
opts = [image.load(glob('Pictures/Menu/'+str(j)+'*')[i]) for j in range(1, 9) for i in range(len(glob('Pictures/Menu/'+str(j)+'*')))]
modeRects = [Rect(525, y, 200, 50) for y in range(400, 640, 60)] # Rects for buttons shown on menu 
pagesOnMenu = ['select level', 'epilogue', 'high scores', 'credits']

titleTxt = transform.scale(image.load('Pictures/Menu/title.png'), (880, 200))
spaceBack = image.load('Pictures/Menu/space2.jpg')
doughboy = image.load('Pictures/Menu/doughboy.png')
# menu screen
def menu(txtList, pageList, pageRects):
    global click, titleTxt, spaceBack, doughboy
    startSong('Music/The Legend of Zelda Ocarina of Time - Title Theme.ogg')
    screen.blit(spaceBack, (-30, -10))
    screen.blit(titleTxt, (625-titleTxt.get_width()//2, 20))
    screen.blit(doughboy, (100, 250))
    for i in range(len(pageRects)):
        mx, my = mouse.get_pos()
        if pageRects[i].collidepoint((mx, my)):
            screen.blit(txtList[i+4], (625-txtList[i+4].get_width()//2, pageRects[i][1]+pageRects[i][3]//2-txtList[i+4].get_height()//2))
            mb = mouse.get_pressed()
            if mb[0] == 1 and click:
                click = False
                return pageList[i]
        else:
            screen.blit(txtList[i], (625-txtList[i].get_width()//2, pageRects[i][1]+pageRects[i][3]//2-txtList[i].get_height()//2))
    return 'menu'

# checking whether song must be loaded and played or not
def startSong(songName):
    if mixer.music.get_busy() == False:
        mixer.music.load(songName)
        mixer.music.play()

# checking whether to play sound or not
def muteSound(soundName):
    if buttonFlags[1] == False:
        mixer.Sound(soundName).set_volume(0)
    else:
        mixer.Sound(soundName).set_volume(1)
        mixer.Sound(soundName).play()

creditTxt, creditBack = transform.scale(image.load('Pictures/Menu/credits.png'), (800, 700)), image.load('Pictures/Menu/space3.jpg') 
# credit screen
def creditScene():
    startSong('Music/The Legend of Zelda Ocarina of Time - Title Theme.ogg')
    screen.blit(creditBack, (0, 0))
    screen.blit(creditTxt, (625-creditTxt.get_width()//2, -10))
    menuButton()

menuButtonSmall, menuButtonBig = image.load('Pictures/Menu/menuButton.png'), image.load('Pictures/Menu/menuButtonBig.png')
buttonRect = Rect(10, 625, 160, 80)
# used for checking whether "main menu" button is pressed
def menuButton():
    global page, click, menuButtonSmall, menuButtonBig
    if buttonRect.collidepoint((mx, my)):
        screen.blit(menuButtonBig, (buttonRect[0]+buttonRect[2]//2-menuButtonBig.get_width()//2, buttonRect[1]+buttonRect[3]//2-menuButtonBig.get_height()//2))
        if mb[0] == 1 and click:
            click = False
            page = 'menu'
    else:
        screen.blit(menuButtonSmall, (buttonRect[0]+buttonRect[2]//2-menuButtonSmall.get_width()//2, buttonRect[1]+buttonRect[3]//2-menuButtonSmall.get_height()//2))

# background for each level to display at the end when showing score
scoreBacks = [transform.scale(image.load(s), (1250, 700)) for s in glob('Pictures/Scores/score0*')]
scoreFormat = image.load('Pictures/Scores/score.png')
nextButton, restartButton, nextButtonBig, restartButtonBig = image.load('Pictures/Scores/nextButton.png'), image.load('Pictures/Scores/restartButton.png'), image.load('Pictures/Scores/nextButtonBig.png'), image.load('Pictures/Scores/restartButtonBig.png')
endButtons = [nextButton, restartButton, nextButtonBig, restartButtonBig]
endRects = [Rect(1100+nextButton.get_width()//2-nextButtonBig.get_width()//2, 610+nextButton.get_height()//2-nextButtonBig.get_height()//2, nextButtonBig.get_width(), nextButtonBig.get_height()),
            Rect(1+restartButton.get_width()//2-restartButtonBig.get_width()//2, 610+restartButton.get_height()//2-restartButtonBig.get_height()//2, restartButtonBig.get_width(), restartButtonBig.get_height())] 
endPages = ['select level', 'play']
txtPos = [[760, 270], [600, 362], [760, 362], [600, 453], [760, 453], [760, 601]] 
multiplierTxt = agencyFBLarge.render('100', True, (255, 255, 255))
comparingScore = True
numAmmoLeft = 0
# screen shown at the end of a level
def endLevel(background, txtFormat, points, constant, healthLeft):
    global comparingScore, page, numAmmoLeft
    startSong('Music/Super Mario Galaxy 2 - Star Chance.ogg')
    screen.blit(background, (0, 0))
    screen.blit(txtFormat, (625-txtFormat.get_width()//2-10, -5))
    ammoScore = 0
    numAmmoLeft = 0
    for a in range(len(ammoScores)):
        if (lvlNum-1)//2 >= a: # checks to see if ammo is available in that level at the time or not
                               # to determine whether to add the number or that ammo left in the score
            ammoScore += 100*ammoScores[a]
            numAmmoLeft += ammoScores[a]
    total = numPoints + 100*healthNum + ammoScore
    txtList = [points, constant, agencyFBLarge.render(str(numAmmoLeft), True, (255, 255, 255)), constant, healthLeft, agencyFBLarge.render(str(total), True, (255, 255, 255))]
    for t in range(len(txtList)):
        screen.blit(txtList[t], (txtPos[t][0]-txtList[t].get_width(), txtPos[t][1]-txtList[t].get_height()))
    if comparingScore: # if there's no flag, the file will keep overwriting itself with the same score 
        checkHighScore('High Scores/lvl'+str(lvlNum)+'.txt', total)
        comparingScore = False
    endGameButtons()

# buttons shown when either player gets to the end of a level or achieves a game over
def endGameButtons():
    global page, click
    for i in range(len(endRects)):
        if endRects[i].collidepoint((mx, my)):
            screen.blit(endButtons[i+2], (endRects[i][0], endRects[i][1]))
            if mb[0] == 1 and click:
                click = False
                if i == 1:
                    startLevel()
                mixer.music.stop()
                page = endPages[i]
        else:
            screen.blit(endButtons[i], (endRects[i][0]+endButtons[i+2].get_width()//2-endButtons[i].get_width()//2, endRects[i][1]+endButtons[i+2].get_height()//2-endButtons[i].get_height()//2))

waitCount, gameoverSeq, countSeq, playOnce = 0, 1, -1, True
# so apparently PF is in Family Guy, which is where I got the 'game over' sequence
gameoverPics = [image.load(g) for g in glob('Pictures/Game Over/*')]
gameoverTxt = agencyFBGiant2.render('< GAME OVER >', True, (255, 255, 255))
# game over sequence
def gameover(pic):
    global waitCount, gameoverSeq, page, playOnce, countSeq
    draw.rect(gameoverSurf, (0, 0, 0, 255), (0, 0, 1250, 700))
    mixer.music.stop()
    if playOnce: # flag used so the 'Too Bad' music doesn't play on indefinitely
        muteSound('Sounds/Super Mario Galaxy - Too Bad.ogg')
        playOnce = False
    screen.blit(pic, (0, 0))
    if waitCount == 2: # same pic must be blitted more than once or the animation
                       # will go too fast
        if gameoverSeq == 6 or gameoverSeq == 1:
            countSeq *= -1
        waitCount = 0
        gameoverSeq += countSeq
    waitCount += 1
    draw.rect(gameoverSurf, (0, 0, 0, 180), (0, 0, 1250, 700))
    gameoverSurf.blit(gameoverTxt, (625-gameoverTxt.get_width()//2, 50))
    screen.blit(gameoverSurf, (0, 0))
    endGameButtons()

# checking whether a score a player gets in a level makes it to the high score board
def checkHighScore(fileName, score):
    scoreFile = [int(i) for i in open(fileName).read().strip().split('\n')]
    pos = 0
    while True:
        if score >= scoreFile[pos]:
            if pos == 0:
                scoreFile = [score] + scoreFile[:9]
            elif pos == 9:
                scoreFile = scoreFile[:9] + [score]
            else:
                scoreFile = scoreFile[:pos] + [score] + scoreFile[pos+1:]
            break
        if pos == 9:
            break
        pos += 1
    out = open(fileName, 'w')
    for s in scoreFile:
        scoreStr = str(s)
        if len(scoreStr) < 6:
            scoreStr = '0'*(6-len(scoreStr))+scoreStr
        out.write(scoreStr+'\n')
    out.close()

highScorePic = transform.scale(image.load('Pictures/Menu/space4.jpg'), (1250, 700))
lvlScoreShown = 1
loaded = False
highScoreButtons = [agencyFBLarge2.render('>>', True, (255, 255, 255)), agencyFBLarge2.render('<<', True, (255, 255, 255)),
                    agencyFBLarge2Bold.render('>>', True, (255, 255, 255)), agencyFBLarge2Bold.render('<<', True, (255, 255, 255))]
highScoreRects = [Rect(850, 30, highScoreButtons[2].get_width(), highScoreButtons[2].get_height()),
                  Rect(400-highScoreButtons[3].get_width(), 30, highScoreButtons[3].get_width(), highScoreButtons[3].get_height())]
add = [1, -1]
limits = [10, 1]
namesTxt = [agencyFBLarge2.render('Journey '+str(lvlNames.index(name)+1)+' - '+name, True, (255, 255, 255)) for name in lvlNames]
scoreLines = []
highScores = [open(filename).read().strip().split('\n') for filename in glob('High Scores/*')]
# high score screen
def displayHighScores(background, scoreList, levelName):
    global lvlScoreShown, loaded, scoreLines, click, pressed
    startSong('Music/The Legend of Zelda Ocarina of Time - Title Theme.ogg')
    screen.blit(background, (0, 0))
    if loaded == False:
        loaded = True
        for i in range(len(scoreList)):
            scoreLines.append(agencyFBBig2.render(str(i+1)+'.'+' '*8+scoreList[i], True, (255, 255, 255)))
    screen.blit(levelName, (625-levelName.get_width()//2, 30))
    for i in range(len(scoreLines)):
        screen.blit(scoreLines[i], (715-scoreLines[i].get_width(), 120+i*50))
    for i in range(len(highScoreRects)):
        if highScoreRects[i].collidepoint((mx, my)) and lvlScoreShown != limits[i]:
            screen.blit(highScoreButtons[i+2], (highScoreRects[i][0], highScoreRects[i][1]))
            if mb[0] == 1 and click:
                click = False
                loaded = False
                scoreLines = []
                lvlScoreShown += add[i]
        elif lvlScoreShown != limits[i]:
            screen.blit(highScoreButtons[i], (highScoreRects[i][0], highScoreRects[i][1]))            
    # changing what level's high scores are shown
    if keys[K_RIGHT] and pressed and lvlScoreShown != 10:
        pressed = False
        loaded = False
        scoreLines = []
        lvlScoreShown += 1
    if keys[K_LEFT] and pressed and lvlScoreShown != 1:
        pressed = False
        loaded = False
        scoreLines = []
        lvlScoreShown -= 1
    if keys[K_RIGHT] == False and keys[K_LEFT] == False:
        pressed = True
    menuButton()

infoPic = image.load('Pictures/Buttons/info.png')
infoPicBig = image.load('Pictures/Buttons/info-big.png')
infoRect = Rect(1190, 640, 50, 50)
# checking if story button (the info icon when selecting a level) is clicked
def checkStory(pic, bigPic, origPage):
    mx, my = mouse.get_pos()
    global click
    if infoRect.collidepoint((mx, my)):
        screen.blit(bigPic, (1190, 640))
        if mb[0] and click:
            click = False
            return 'story'
    else:
        screen.blit(pic, (1195, 645))
    return origPage       

storyPics = [image.load(s) for s in glob('Story/story*')]
backButton = agencyFBBig.render('< Back', True, (0, 0, 0))
backButtonBig = agencyFBHuge.render('< Back', True, (0, 0, 0))
backRect = Rect(10, 645, backButtonBig.get_width(), 40)
epiloguePic = image.load('Story/epilogue.png')
# showing story
def story(pic, pageName, oldPageName):
    global click
    screen.blit(pic, (-1, 0))
    if backRect.collidepoint((mx, my)):
        screen.blit(backButtonBig, (10, 645))
        if mb[0] == 1 and click:
            click = False
            return oldPageName
    else:
        screen.blit(backButton, (10+backButtonBig.get_width()//2-backButton.get_width()//2, 645+backButtonBig.get_height()//2-backButton.get_height()//2))
    return pageName

justPaused = True
page = 'menu'
initPauseTime = 0
mixer.music.set_volume(0.5)

while page != 'exit':
    mx, my = mouse.get_pos()
    mb = mouse.get_pressed()
    keys = key.get_pressed()
    for e in event.get():
        if e.type == QUIT:
            page = 'exit'
    if keys[K_ESCAPE]: # if you're lazy?
        page = 'exit'
    if mb[0] == 0:
        click = True
    if page != 'play' and page != 'pause':
        if justPaused and time.get_ticks()//500 < 40:
            # time.get_ticks()//500 < 40 --> compensates for time it takes for
            # program to start
            startPauseTime = 0
            justPaused = False
        elif justPaused:
            startPauseTime = time.get_ticks()//500
            justPaused = False
        pausedTime = elapsedTime + initPauseTime + time.get_ticks()//500 - startPauseTime
    if page == 'play':
        page = play()
    elif page == 'pause':
        page = pause(pausePic, popupRects)
    elif page == 'select level':
        lvlNum, page = selectLevel()
        page = checkStory(infoPic, infoPicBig, page)
        if page == 'play':
            startLevel()
    elif page == 'menu':
        page = menu(opts, pagesOnMenu, modeRects)
    elif page == 'credits':
        creditScene()
    elif page == 'end level':
        endLevel(scoreBacks[lvlNum-1], scoreFormat, agencyFBLarge.render(str(numPoints), True, (255, 255, 255)), multiplierTxt, agencyFBLarge.render(str(healthNum), True, (255, 255, 255)))
    elif page == 'game over':
        gameover(gameoverPics[gameoverSeq])
    elif page == 'story':
        page = story(storyPics[lvlShown-1], 'story', 'select level')
    elif page == 'epilogue':
        page = story(epiloguePic, 'epilogue', 'menu')
    elif page == 'high scores':
        displayHighScores(highScorePic, highScores[lvlScoreShown-1], namesTxt[lvlScoreShown-1])
    time.Clock().tick(100)
    display.flip()
quit()
