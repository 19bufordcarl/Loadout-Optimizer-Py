#################################################
# displayGame.py
#
# Your name: Carl Buford
# Your andrew id: cbuford
#
#################################################

# Graphics framework from: 
# https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
import math, copy, string, random
from cmu_112_graphics import *
from tkinter import *
from PIL import Image
from ShieldTester import ShieldClasses
import ShipClasses
import ProjectileClasses

# Maintains the actual display with the different modes

class TesterMode(Mode):
    def appStarted(mode):
        # Choice of thermal, kinetic, explosive, and absolute dps (ints > 0)
        # Choice of ship (string)
        # Choice of shield boosters (0 <= ints <= 8)
        # total num choices = 6
        mode.margin = 50
        mode.playerChoices = {'Thermal DPS': 10, 'Kinetic DPS': 10, 
                              'Explosive DPS': 10, 'Absolute DPS': 10,
                              'Ship': 'Eagle', 'Shield Boosters': 2}
        mode.enemyChoices =  {'Thermal DPS': 10, 'Kinetic DPS': 10, 
                              'Explosive DPS': 10, 'Absolute DPS': 10,
                              'Ship': 'Eagle', 'Shield Boosters': 2}
        mode.buttonWidth = (mode.width - 2*mode.margin) // 7
        mode.buttonHeight = (mode.height - 2*mode.margin) // \
                            (2*len(mode.playerChoices))
        mode.buttonCoords = dict()
        mode.buttonNames = {0: 'Thermal DPS', 1: 'Kinetic DPS', 
                            2: 'Explosive DPS', 3: 'Absolute DPS',
                            4: 'Ship', 5: 'Shield Boosters'}
        
        mode.choiceOffset = 2 * mode.buttonWidth
        for i in range(2 * len(mode.playerChoices)):
            # coords are stored as tuple for rect (x1, y1, x2, y2)
            # creates even spacing
            if i % 2 == 0:
                margin = mode.margin
                mode.buttonCoords[i//2] = (margin, margin + i*mode.buttonHeight,
                                        margin + mode.buttonWidth,
                                        margin + ((i + 1) * mode.buttonHeight))
                # Now store the enemies buttons
                key = (i // 2) + len(mode.playerChoices)
                mode.buttonCoords[key] = (margin + mode.width // 2, 
                                    margin + i*mode.buttonHeight,
                                    margin + mode.width // 2 + mode.buttonWidth,
                                    margin + ((i + 1) * mode.buttonHeight))

    def redrawAll(mode, canvas):
        # Draws different buttons for the player to enter in their choices
        numChoices = len(mode.playerChoices)
        for key in mode.buttonCoords:
            choiceKey = key % numChoices
            (x1, y1, x2, y2) = mode.buttonCoords[key]
            canvas.create_rectangle(x1, y1, x2, y2, fill='orange')
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                text=mode.buttonNames[choiceKey], 
                                font='Arial 10 bold')
            # Now draw the current values for each possible button
            offset = mode.choiceOffset
            (x3, x4) = (x1 + offset, x2 + offset)
            canvas.create_rectangle(x3, y1, x4, y2, width=5)
            # Check if player or enemy
            buttonName = ''
            areaLabel = ''
            # Player
            if(key == choiceKey):
                buttonName = str(mode.playerChoices[mode.buttonNames[choiceKey]])
                if(key == 0): areaLabel = 'Enemy Weapons'
                elif(key == 4): areaLabel = 'Player Ship Defenses'
            # Enemy
            else:
                buttonName = str(mode.enemyChoices[mode.buttonNames[choiceKey]])
                if(key == 6): areaLabel = 'Player Weapons'
                elif(key == 10): areaLabel = 'Enemy Ship Defenses'
            canvas.create_text((x3 + x4) // 2, (y1 + y2) // 2, text=buttonName, 
                                font='Arial 10')
            if(areaLabel != ''):
                canvas.create_text((x2 + x3) // 2, 
                    (y1 + choiceKey * (mode.buttonHeight + mode.margin)) // 2, 
                    text=areaLabel, font='Arial 10 bold', anchor='s')
        canvas.create_text(mode.width // 2, mode.height - 10, anchor='s', 
            font='Arial 10 bold', text="Press 'b' to go back, or 'Space' to optimize and advance to viewer (press 'v' to return to viewer after optimizing)")

    def shipSelection(mode):
        mode.app.setActiveMode(mode.app.shipSelectionMode)
        return mode.app.shipSelectionMode.shipChoice

    def mousePressed(mode, event):
        numChoices = 6
        for key in mode.buttonCoords:
            (x1, y1, x2, y2) = mode.buttonCoords[key]
            if(x1 <= event.x <= x2 and y1 <= event.y <= y2):
                choice = None
                if(mode.buttonNames[key % numChoices] == 'Ship'):
                    choice = mode.shipSelection()
                else:
                    choice = mode.getUserInput(f'Please Enter {mode.buttonNames[key % numChoices]}')
                if(choice == None): break
                elif(choice.isdigit()):
                    choice = int(choice)
                # Update player choice
                choiceKey = key % numChoices
                playerChoice = mode.playerChoices[mode.buttonNames[choiceKey]]
                enemyChoice = mode.enemyChoices[mode.buttonNames[choiceKey]]
                if(choiceKey == key):
                    if(isinstance(choice, type(playerChoice))):
                        mode.playerChoices[mode.buttonNames[choiceKey]] = choice
                    else:
                        mode.app.showMessage('Please Enter a Valid Input')
                else:
                    if(isinstance(choice, type(enemyChoice))):
                        mode.enemyChoices[mode.buttonNames[choiceKey]] = choice
                    else:
                        mode.app.showMessage('Please Enter a Valid Input')

    def keyPressed(mode, event):
        if(event.key == 'Space'):
            # Optimizes the current constraints and switches to loadout viewer
            playerLoadout = ShieldClasses.testShields(mode.playerChoices)
            playerLoadout['Thermal DPS'] = mode.enemyChoices['Thermal DPS']
            playerLoadout['Kinetic DPS'] = mode.enemyChoices['Kinetic DPS']
            playerLoadout['Explosive DPS'] = mode.enemyChoices['Explosive DPS']
            playerLoadout['Absolute DPS'] = mode.enemyChoices['Absolute DPS']
            enemyLoadout = ShieldClasses.testShields(mode.enemyChoices)
            enemyLoadout['Thermal DPS'] = mode.playerChoices['Thermal DPS']
            enemyLoadout['Kinetic DPS'] = mode.playerChoices['Kinetic DPS']
            enemyLoadout['Explosive DPS'] = mode.playerChoices['Explosive DPS']
            enemyLoadout['Absolute DPS'] = mode.playerChoices['Absolute DPS']
            mode.app.playerLoadout = playerLoadout
            mode.app.enemyLoadout = enemyLoadout
            mode.app.playerShip = ShipClasses.PlayerShip(playerLoadout)
            mode.app.enemyShip = ShipClasses.EnemyShip(enemyLoadout)
            mode.app.setActiveMode(mode.app.viewerMode)
        elif(event.key == 'v'):
            if(mode.app.playerLoadout != dict() and mode.app.enemyLoadout != dict() and
               mode.app.playerShip != None and mode.app.enemyShip != None):
               mode.app.setActiveMode(mode.app.viewerMode)
        elif(event.key == 'b'):
            mode.app.setActiveMode(mode.app.splashScreenMode)

class ShipSelectionMode(Mode):
    def appStarted(mode):
        mode.shipDict = ShieldClasses.getShipDict(mode.app.testerMode.playerChoices)
        mode.shipChoice = 'Eagle'
        mode.margin = mode.height // len(mode.shipDict)
        mode.promptNotActive = True
        if(mode.promptNotActive):
            mode.selectShip()
    
    def redrawAll(mode, canvas):
        i = 0
        for key in mode.shipDict:
            i += 1
            shipInstance = mode.shipDict[key]
            canvas.create_rectangle(mode.width//3, i * mode.margin, 
                (2 * mode.width) // 3, (i + 1) * mode.margin)
            canvas.create_text(mode.width // 2, 
                (i * mode.margin + (i + 1) * mode.margin) // 2, text=shipInstance,
                font='Arial 10')

    def initializeSelection(mode):
        mode.appStarted()

    def selectShip(mode):
        mode.promptNotActive = not mode.promptNotActive
        choice = mode.getUserInput('Please Enter Your Desired Ship ID (1-38)')
        if(choice == None):
            mode.app.showMessage('Please Enter a Valid Input')
            mode.initializeSelection()
        elif(choice.isdigit()):
            choice = int(choice)
            if(choice > 0 and choice < 39):
                for ship in mode.shipDict:
                    if(mode.shipDict[ship].id == choice):
                        mode.shipChoice = ship
                        mode.app.setActiveMode(mode.app.testerMode)
                        break
            else:
                mode.app.showMessage('Please Enter a Valid Input')
                mode.initializeSelection()
        else:
            mode.app.showMessage('Please Enter a Valid Input')
            mode.initializeSelection()
        

class ViewerMode(Mode):
    # Once the loadouts have been sent to the tester for optimization,
    # The user can select to go to this viewer screen
    # From the Viewer screen, the user can then select to begin the fight
    def appStarted(mode):
        mode.margin = 50 
        playerLoadoutDisplay = copy.deepcopy(mode.app.playerLoadout)
        enemyLoadoutDisplay = copy.deepcopy(mode.app.enemyLoadout)
        mode.frameWidth = (mode.width - 2*mode.margin) // 6
        mode.frameHeight = (mode.height - 2*mode.margin) // (2*len(playerLoadoutDisplay))
        mode.frameCoords = dict()
        mode.frameNames = dict()
        i = 0
        for key in playerLoadoutDisplay:
            mode.frameNames[i] = key
            i += 1
        mode.frameOffset = int(1.5 * mode.frameWidth)
        for j in range(2 * len(playerLoadoutDisplay)):
            # coords are stored as tuple for rect (x1, y1, x2, y2)
            # creates even spacing
            if j % 2 == 0:
                margin = mode.margin
                mode.frameCoords[j//2] = (margin, margin + j*mode.frameHeight,
                    margin + mode.frameWidth, margin + ((j + 1) * mode.frameHeight))
                # store enemy frames
                key = j // 2 + len(playerLoadoutDisplay)
                mode.frameCoords[key] = (margin + mode.width // 2, 
                                    margin + j*mode.frameHeight,
                                    margin + mode.width // 2 + mode.frameWidth,
                                    margin + ((j + 1) * mode.frameHeight))

    def redrawAll(mode, canvas):
        # Similar to previous, but with modifications to suit viewing (no input)
        numFrames = len(mode.app.playerLoadout)
        for key in mode.frameCoords:
            frameKey = key % numFrames
            (x1, y1, x2, y2) = mode.frameCoords[key]                
            canvas.create_rectangle(x1, y1, x2, y2, fill='light blue')
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                text=mode.frameNames[frameKey], 
                                font='Arial 10 bold')
            # Now draw the current values for each possible frame
            offset = mode.frameOffset
            (x3, x4) = (x1 + offset, x2 + offset)
            if(key == 0):
                canvas.create_text((x2 + x3) // 2, 0, text='Player Loadout', anchor='n')
            canvas.create_rectangle(x3, y1, x4, y2, width=5)
            # Check if player or enemy
            frameValue = ''
            if(key == frameKey):
                frameValueTemp = mode.app.playerLoadout[mode.frameNames[frameKey]]
                if(isinstance(frameValueTemp, float)): 
                    frameValue = '%0.3f' % frameValueTemp      
                else:          
                    frameValue = str(mode.app.playerLoadout[mode.frameNames[frameKey]])
            else:
                frameValueTemp = mode.app.enemyLoadout[mode.frameNames[frameKey]]
                if(isinstance(frameValueTemp, float)): 
                    frameValue = '%0.3f' % frameValueTemp      
                else:          
                    frameValue = str(mode.app.enemyLoadout[mode.frameNames[frameKey]])
            canvas.create_text((x3 + x4) // 2, (y1 + y2) // 2, text=frameValue, 
                                font='Arial 8')
        canvas.create_text(mode.width // 2, mode.height - 10, anchor='s', 
            font='Arial 10 bold', text="Press 'b' to go back, or 'Space' to advance to battle")
        canvas.create_text((x2 + x3) // 2, 0, text='Enemy Loadout', anchor='n')

    def keyPressed(mode, event):
        if(event.key == 'Space'):
            mode.app.setActiveMode(mode.app.gameMode)
            mode.app.gameMode.resetBattle()
        elif(event.key == 'b'):
            mode.app.setActiveMode(mode.app.testerMode)

class GameMode(Mode):
    # This holds the dogfighting 2d space side scrolling game
    def appStarted(mode):
        # Initializes the world and ships for the battle
        mode.scrollX = 0
        mode.scrollY = 0
        mode.scrollXMargin = mode.width // 3
        mode.scrollYMargin = mode.height // 3
        mode.worldDims = (mode.width // 2 - 2000, mode.height // 2 - 2000, 
                          mode.width // 2 + 2000, mode.height // 2 + 2000)
        mode.player = mode.app.playerShip
        mode.player.x = mode.width // 2
        mode.player.y = mode.height // 2
        mode.player.theta = math.pi
        mode.player.align()
        mode.player.shieldHPLeft = mode.player.shieldHP
        mode.enemy = mode.app.enemyShip
        mode.enemy.x = mode.width
        mode.enemy.y = mode.height // 3
        mode.enemy.theta = 0
        mode.enemy.align()
        mode.enemy.shieldHPLeft = mode.enemy.shieldHP
        mode.gameOver = False
        # All speeds are inversed
        # 1 is fastest, how often it moves by one unit vector
        # background from 
        # https://wallpapersite.com/download-most-popular-wallpapers/dark-space-stars-4k-8k-7935.html
        backgroundPath = 'images/' + 'SpaceBackground.jpg'
        mode.background = mode.loadImage(backgroundPath)
        mode.background = ImageTk.PhotoImage(mode.background)
        # ship from https://i.pinimg.com/originals/33/8b/32/338b325178c15394ce18b5a75649f14c.png
        shipImagePath = 'images/' + 'ShipSpritesDemo.png' 
        mode.shipSprite = mode.loadImage(shipImagePath)
        mode.shipSprite = mode.scaleImage(mode.shipSprite, 2/3)
        # explosion from http://pixelartmaker.com/art/99d3853cad9ebbc.png
        explosionImagePath = 'images/' + 'Explosion.png'
        mode.explosionSprite = mode.loadImage(explosionImagePath)
        mode.timerDelay = 1
        mode.timerCounter = 0
        mode.minSpeed = 20
        mode.player.speed, mode.enemy.speed = mode.minSpeed, mode.minSpeed
        mode.projectiles = [ ]

    def getEnemyGoalTheta(mode):
        # Calculate the angle that the enemy should face to align with the player
        if(mode.enemy.x == mode.player.x and mode.enemy.y >= mode.player.y):
            # player is directly above
            goalTheta = math.pi / 2
        elif(mode.enemy.x == mode.player.x and mode.enemy.y < mode.player.y):
            # player is directly below
            goalTheta = 3*math.pi / 2
        else:
            # slope is from the 
            slope = (mode.player.y - mode.enemy.y) / (mode.player.x - mode.enemy.x)
            tempTheta = math.atan(slope)
            if(mode.player.x > mode.enemy.x and tempTheta > 0):
                # player is to the right and up
                goalTheta = tempTheta
            elif(mode.player.x > mode.enemy.x and tempTheta < 0):
                # player is to the right and down
                goalTheta = 2*math.pi + tempTheta
            elif(mode.player.x < mode.enemy.x):
                # player is to the left
                goalTheta = math.pi + tempTheta
        return goalTheta

    def enemyAI(mode):
        # Controls all the decision making for the enemy ship
        (px0, py0, px1, py1) = mode.getPlayerBounds()
        (ex0, ey0, ex1, ey1) = mode.getEnemyBounds()
        (wx0, wy0, wx1, wy1) = mode.worldDims
        playerCoords = (mode.player.x, mode.player.y)
        enemyCoords = (mode.enemy.x, mode.enemy.y)
        distance = mode.dist(playerCoords, enemyCoords)
        # Ensure enemy theta >= 0 and < 2pi
        while(mode.enemy.theta >= 2*math.pi): mode.enemy.theta -= 2*math.pi
        while(mode.enemy.theta < 0): mode.enemy.theta += 2*math.pi
        goalTheta = mode.getEnemyGoalTheta()
        dotProd = math.cos(goalTheta)*math.cos(mode.enemy.theta) + \
                math.sin(goalTheta)*math.sin(mode.enemy.theta)
        # Avoid the boundaries
        if((mode.enemy.x <= wx0 + 100 and math.cos(mode.enemy.theta) < 0) or \
            (mode.enemy.x >= wx1 - 100 and math.cos(mode.enemy.theta) > 0) or \
            (mode.enemy.y <= wy0 + 100 and math.sin(mode.enemy.theta) < 0) or \
            (mode.enemy.y >= wy1 - 100 and math.sin(mode.enemy.theta) > 0)):
            mode.enemy.theta += math.pi / 72
            mode.enemy.align()
        if(random.randint(0, 10) < 3):
            # only check to move sometimes to be fair to player input speed
            if(goalTheta > mode.enemy.theta or random.randint(0, 10) < 2):
                # need to turn left
                mode.enemy.theta += math.pi / 72
                mode.enemy.align()
            elif(goalTheta < mode.enemy.theta or random.randint(0, 10) < 2):
                # need to turn right
                mode.enemy.theta -= math.pi / 72
                mode.enemy.align()
            # moderate speed based on distance and dot product
            if(mode.enemy.speed != 1 and (distance >= 300 or dotProd < 0)):
                mode.enemy.speed -= 1
            elif(distance < 300 and mode.enemy.speed < mode.minSpeed and dotProd > 0):
                mode.enemy.speed += 1
        if(mode.enemy.theta == goalTheta or (mode.timerCounter % mode.enemy.fireDelay == 0 and 
                abs(goalTheta - mode.enemy.theta) < math.pi / 12)):
            mode.fireAllWeapons(mode.enemy)

    def timerFired(mode):
        # Time related events like ship and projectile movement / collision
        if(not mode.gameOver):
            if(mode.player.shieldHPLeft < 0):
                mode.gameOver = True
            elif(mode.enemy.shieldHPLeft < 0):
                mode.gameOver = True
            mode.timerCounter += 1
            if(mode.player.speed < mode.minSpeed and mode.timerCounter % mode.player.speed == 0):
                mode.moveShip(mode.player)
            mode.player.fireCooldownTimer += 1
            mode.enemyAI()
            if(mode.enemy.speed < mode.minSpeed and mode.timerCounter % mode.enemy.speed == 0):
                mode.moveShip(mode.enemy)
            if(mode.timerCounter % mode.player.regenDelay == 0):
                # apply player and enemy regen
                mode.player.shieldHPLeft += mode.player.regen
                if(mode.player.shieldHPLeft > mode.player.shieldHP):
                    mode.player.shieldHPLeft = mode.player.shieldHP
                mode.enemy.shieldHPLeft += mode.enemy.regen
                if(mode.enemy.shieldHPLeft > mode.enemy.shieldHP):
                    mode.enemy.shieldHPLeft = mode.enemy.shieldHP
            for projectile in mode.projectiles:
                if(projectile.timer > 5000): 
                    mode.projectiles.remove(projectile)
                    continue
                projectile.timer += 1
                if(mode.timerCounter % projectile.speed == 0):
                    mode.moveProjectile(projectile)
                mode.checkForProjectileHit(projectile)

    def resetBattle(mode):
        mode.appStarted()

    def keyPressed(mode, event):
        # All possible key press controls such as turning, thrusting, and strafing
        if(event.key == 'b'):
            mode.app.setActiveMode(mode.app.viewerMode)
        elif(event.key == 'r'):
            mode.resetBattle()
        elif(event.key == 'h'):
            mode.app.setActiveMode(mode.app.helpMode)
        if(not mode.gameOver):
            if(event.key == 'w'):
                mode.player.speed -= 1
                if(mode.player.speed < 1): mode.player.speed = 1
            elif(event.key == 's'):
                mode.player.speed += 1
                if(mode.player.speed > mode.minSpeed): mode.player.speed = mode.minSpeed
            elif(event.key == 'q'):
                mode.player.turn(-math.pi / 36)
            elif(event.key == 'e'):
                mode.player.turn(math.pi / 36)
            elif(event.key == 'a'):
                mode.player.strafeRight = False
                mode.player.strafeLeft = True
            elif(event.key == 'd'):
                mode.player.strafeLeft = False
                mode.player.strafeRight = True
            elif(event.key == 'Enter'):
                if(mode.player.fireCooldownTimer >= mode.player.fireDelay):
                    mode.player.fireCooldownTimer = 0
                    mode.fireAllWeapons(mode.player)
            # cheats to kill player / enemy
            elif(event.key == '1'):
                mode.player.shieldHPLeft = 0
            elif(event.key == '2'):
                mode.enemy.shieldHPLeft = 0

    def keyReleased(mode, event):
        # Ends the appropriate strafe maneuver
        if(event.key == 'a'):
            mode.player.strafeLeft = False
        elif(event.key == 'd'):
            mode.player.strafeRight = False

    def fireAllWeapons(mode, ship):
        fromPlayer = isinstance(ship, ShipClasses.PlayerShip)
        if(ship.kinDPS > 0):
            mode.projectiles.append(ProjectileClasses.KineticProjectile(
                ship.x, ship.y, ship.kinDPS, ship.theta, fromPlayer))
        if(ship.thmDPS > 0):
            mode.projectiles.append(ProjectileClasses.ThermalProjectile(
                ship.x, ship.y, ship.thmDPS, ship.theta, fromPlayer))
        if(ship.expDPS > 0):
            mode.projectiles.append(ProjectileClasses.ExplosiveProjectile(
                ship.x, ship.y, ship.expDPS, ship.theta, fromPlayer))
        if(ship.absDPS > 0):
            mode.projectiles.append(ProjectileClasses.AbsoluteProjectile(
                ship.x, ship.y, ship.absDPS, ship.theta, fromPlayer))

    def checkForProjectileHit(mode, projectile):
        # Checks if a projectile has hit its mark and computes the damage
        projBounds = mode.getProjectileBounds(projectile)
        playerBounds = mode.getPlayerBounds()
        enemyBounds = mode.getEnemyBounds()
        if(mode.boundsIntersect(projBounds, playerBounds) and not projectile.fromPlayer):
            if(isinstance(projectile, ProjectileClasses.ThermalProjectile)):
                damageTaken = projectile.damage * (1 - mode.player.thmRes)
            elif(isinstance(projectile, ProjectileClasses.KineticProjectile)):
                damageTaken = projectile.damage * (1 - mode.player.kinRes)
            elif(isinstance(projectile, ProjectileClasses.ExplosiveProjectile)):
                damageTaken = projectile.damage * (1 - mode.player.expRes)
            elif(isinstance(projectile, ProjectileClasses.AbsoluteProjectile)):
                damageTaken = projectile.damage
            mode.player.shieldHPLeft -= damageTaken
            mode.projectiles.remove(projectile)
        elif(mode.boundsIntersect(projBounds, enemyBounds) and projectile.fromPlayer):
            if(isinstance(projectile, ProjectileClasses.ThermalProjectile)):
                damageTaken = projectile.damage * (1 - mode.enemy.thmRes)
            elif(isinstance(projectile, ProjectileClasses.KineticProjectile)):
                damageTaken = projectile.damage * (1 - mode.enemy.kinRes)
            elif(isinstance(projectile, ProjectileClasses.ExplosiveProjectile)):
                damageTaken = projectile.damage * (1 - mode.enemy.expRes)
            elif(isinstance(projectile, ProjectileClasses.AbsoluteProjectile)):
                damageTaken = projectile.damage
            mode.enemy.shieldHPLeft -= damageTaken
            mode.projectiles.remove(projectile)

    # All the following compute their bounds with minor nuances for each
    def getProjectileBounds(mode, projectile):
        (x0, y0) = (projectile.x - projectile.r, projectile.y - projectile.r)
        (x1, y1) = (projectile.x + projectile.r, projectile.y + projectile.r)
        return(x0, y0, x1, y1)

    def getPlayerBounds(mode):
        (x0, y0) = (mode.player.x - mode.player.r, mode.player.y - mode.player.r)
        (x1, y1) = (mode.player.x + mode.player.r, mode.player.y + mode.player.r)
        return(x0, y0, x1, y1)

    def getEnemyBounds(mode):
        (x0, y0) = (mode.enemy.x - mode.enemy.r, mode.enemy.y - mode.enemy.r)
        (x1, y1) = (mode.enemy.x + mode.enemy.r, mode.enemy.y + mode.enemy.r)
        return(x0, y0, x1, y1)

    def dist(mode, coordsA, coordsB):
        (x0, y0) = coordsA
        (x1, y1) = coordsB
        return ((x1 - x0)**2 + (y1 - y0)**2)**.5

    def boundsIntersect(mode, boundsA, boundsB):
        # changed to work better for circles
        (ax0, ay0, ax1, ay1) = boundsA
        (bx0, by0, bx1, by1) = boundsB
        aRad = abs(ax1 - ax0) / 2
        bRad = abs(bx1 - bx0) / 2
        acx = (ax1 + ax0) / 2
        acy = (ay1 + ay0) / 2
        bcx = (bx1 + bx0) / 2
        bcy = (by1 + by0) / 2
        maxDist = mode.dist((acx, acy), (bcx, bcy))
        return ((ax1 >= bx0) and (bx1 >= ax0) and
                (ay1 >= by0) and (by1 >= ay0)) and maxDist < (aRad + bRad)

    # makePlayerVisible and sizeChanged from
    # https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
    def makePlayerVisible(mode):
        # scroll to make player visible as needed
        if (mode.player.x < mode.scrollX + mode.scrollXMargin):
            mode.scrollX = mode.player.x - mode.scrollXMargin
        if (mode.player.x > mode.scrollX + mode.width - mode.scrollXMargin):
            mode.scrollX = mode.player.x - mode.width + mode.scrollXMargin
        # I made a simple add to make y work too
        if (mode.player.y < mode.scrollY + mode.scrollYMargin):
            mode.scrollY = mode.player.y - mode.scrollYMargin
        if (mode.player.y > mode.scrollY + mode.height - mode.scrollYMargin):
            mode.scrollY = mode.player.y - mode.height + mode.scrollYMargin
    
    def sizeChanged(mode):
        mode.makePlayerVisible()

    def moveShip(mode, ship):
        # Applies the thrust vector to a ship
        (dx, dy) = ship.vector
        movedEntirely = True
        ship.x += ship.speedMult*dx
        if(ship.x < mode.worldDims[0] or ship.x > mode.worldDims[2]):
            # Ensure that the ship stays in bounds 
            ship.x -= ship.speedMult*dx
            movedEntirely = False
        ship.y += ship.speedMult*dy
        if(ship.y < mode.worldDims[1] or ship.y > mode.worldDims[3]):
            # Ensure that the ship stays in bounds 
            ship.y -= ship.speedMult*dy
            movedEntirely = False
        if(ship.strafeLeft):
            leftTheta = ship.theta - (math.pi / 2)
            (dx2, dy2) = (math.cos(leftTheta), math.sin(leftTheta))
            ship.x += ship.strafeMult*dx2
            ship.y += ship.strafeMult*dy2
        elif(ship.strafeRight):
            rightTheta = ship.theta + (math.pi / 2)
            (dx1, dy1) = (math.cos(rightTheta), math.sin(rightTheta))
            ship.x += ship.strafeMult*dx1
            ship.y += ship.strafeMult*dy1
        if(mode.player == ship):
            mode.makePlayerVisible()
        mode.checkForCollision()
        return movedEntirely

    def moveProjectile(mode, projectile):
        # moves an indicated projectile
        (dx, dy) = projectile.vector
        projectile.x += 10*dx
        projectile.y += 10*dy

    def calculateVelocities(mode):
        # calculates the current 'velocities' of the ships for collision's sake
        playerXVelocity = mode.player.vector[0]*mode.player.speedMult
        playerYVelocity = mode.player.vector[1]*mode.player.speedMult
        if(mode.player.strafeLeft):
            leftTheta = mode.player.theta + (math.pi / 2)
            (dx2, dy2) = (math.cos(leftTheta), math.sin(leftTheta))
            playerXVelocity += mode.player.strafeMult*dx2
            playerYVelocity += mode.player.strafeMult*dy2
        elif(mode.player.strafeRight):
            rightTheta = mode.player.theta - (math.pi / 2)
            (dx1, dy1) = (math.cos(rightTheta), math.sin(rightTheta))
            playerXVelocity += mode.player.strafeMult*dx1
            playerYVelocity += mode.player.strafeMult*dy1
        enemyXVelocity = mode.enemy.vector[0]*mode.enemy.speedMult
        enemyYVelocity = mode.enemy.vector[1]*mode.enemy.speedMult
        if(mode.enemy.strafeLeft):
            leftTheta = mode.enemy.theta + (math.pi / 2)
            (dx2, dy2) = (math.cos(leftTheta), math.sin(leftTheta))
            enemyXVelocity += mode.enemy.strafeMult*dx2
            enemyYVelocity += mode.enemy.strafeMult*dy2
        elif(mode.enemy.strafeRight):
            rightTheta = mode.enemy.theta - (math.pi / 2)
            (dx1, dy1) = (math.cos(rightTheta), math.sin(rightTheta))
            enemyXVelocity += mode.enemy.strafeMult*dx1
            enemyYVelocity += mode.enemy.strafeMult*dy1
        return(playerXVelocity, playerYVelocity, enemyXVelocity, enemyYVelocity)

    def checkForCollision(mode):
        # Checks and bounces the ships if they are colliding
        playerBounds = mode.getPlayerBounds()
        enemyBounds = mode.getEnemyBounds()
        dotProd = math.cos(mode.player.theta)*math.cos(mode.enemy.theta) + \
                math.sin(mode.player.theta)*math.sin(mode.enemy.theta)
        if(mode.boundsIntersect(playerBounds, enemyBounds)):
            # Models a semi perfectly elastic collision
            (playerXVelocity, playerYVelocity, enemyXVelocity, enemyYVelocity) =\
                mode.calculateVelocities()
            playerNewXVelocity = (playerXVelocity * (mode.player.mass - mode.enemy.mass) +\
                (2 * mode.enemy.mass * enemyXVelocity)) / (mode.player.mass + mode.enemy.mass)
            playerNewYVelocity = (playerYVelocity * (mode.player.mass - mode.enemy.mass) +\
                (2 * mode.enemy.mass * enemyYVelocity)) / (mode.player.mass + mode.enemy.mass)
            enemyNewXVelocity = (enemyXVelocity * (mode.enemy.mass - mode.player.mass) +\
                (2 * mode.player.mass * playerXVelocity)) / (mode.player.mass + mode.enemy.mass)
            enemyNewYVelocity = (enemyYVelocity * (mode.enemy.mass - mode.player.mass) +\
                (2 * mode.player.mass * playerYVelocity)) / (mode.player.mass + mode.enemy.mass)
            playerTheta = math.atan(playerNewYVelocity / playerNewXVelocity)
            enemyTheta = math.atan(enemyNewYVelocity / enemyNewXVelocity)
            if((playerNewXVelocity < 0 and playerNewYVelocity < 0) or 
                    (playerNewXVelocity < 0 and playerNewYVelocity > 0)):
                playerTheta += math.pi
            if((enemyNewXVelocity < 0 and enemyNewYVelocity < 0) or
                    (enemyNewXVelocity < 0 and enemyNewYVelocity > 0)):
                enemyTheta += math.pi
            mode.player.theta = playerTheta
            if(dotProd > 0):
                mode.player.theta = -mode.player.theta
                playerTheta = -playerTheta
                playerNewXVelocity = -playerNewXVelocity
                playerNewYVelocity = -playerNewYVelocity
            mode.player.vector = (math.cos(playerTheta), math.sin(playerTheta))
            mode.player.x += playerNewXVelocity
            mode.player.y += playerNewYVelocity
            mode.enemy.theta = enemyTheta
            mode.enemy.vector = (math.cos(enemyTheta), math.sin(enemyTheta))
            mode.enemy.x += enemyNewXVelocity
            mode.enemy.y += enemyNewYVelocity
            mode.enemy.speed, mode.player.speed = mode.enemy.speed * 2, mode.player.speed * 2

    def drawBackground(mode, canvas, image, cx, cy):
        # creates the world's background static image
        sx = mode.scrollX
        sy = mode.scrollY
        canvas.create_image(cx - sx, cy - sy, image=image)

    def drawBorders(mode, canvas):
        sx = mode.scrollX
        sy = mode.scrollY
        (x1, y1, x2, y2) = mode.worldDims
        x1 -= mode.player.r
        y1 -= mode.player.r
        x2 += mode.player.r
        y2 += mode.player.r
        canvas.create_rectangle(x1 - sx, y1 - sy, x2 - sx, y2 -sy, width=5,
            outline='white')

    def drawPlayer(mode, canvas):
        # draws the player with it's blue shield circle behind it
        sx = mode.scrollX
        sy = mode.scrollY
        (x0, y0, x1, y1) = mode.getPlayerBounds()
        canvas.create_oval(x0 - sx, y0 - sy, x1 - sx, y1 - sy, fill='light blue')
        degrees = ((-mode.player.theta*180) / math.pi) - 90
        image = mode.shipSprite
        rotatedImage = image.rotate(degrees)
        canvas.create_image(((x0 + x1) / 2) - sx, ((y0 + y1) / 2) -sy, 
                            image=ImageTk.PhotoImage(rotatedImage))
        if(mode.player.shieldHPLeft <= 0):
            canvas.create_image(((x0 + x1) / 2) - sx, ((y0 + y1) / 2) -sy, 
                            image=ImageTk.PhotoImage(mode.explosionSprite))

    def drawEnemy(mode, canvas):
        # draws the enemy with it's pink shield circle behind it
        sx = mode.scrollX
        sy = mode.scrollY
        (x0, y0, x1, y1) = mode.getEnemyBounds()
        canvas.create_oval(x0 - sx, y0 - sy, x1 - sx, y1 - sy, fill='pink')
        degrees = ((-mode.enemy.theta*180) / math.pi) - 90
        image = mode.shipSprite
        rotatedImage = image.rotate(degrees)
        canvas.create_image(((x0 + x1) / 2) - sx, ((y0 + y1) / 2) -sy, 
                            image=ImageTk.PhotoImage(rotatedImage))
        if(mode.enemy.shieldHPLeft <= 0):
            canvas.create_image(((x0 + x1) / 2) - sx, ((y0 + y1) / 2) -sy, 
                            image=ImageTk.PhotoImage(mode.explosionSprite))

    def drawProjectiles(mode, canvas):
        # draws all the current projectiles in the world
        sx = mode.scrollX
        sy = mode.scrollY
        for projectile in mode.projectiles:
            (x0, y0, x1, y1) = mode.getProjectileBounds(projectile)
            canvas.create_oval(x0 - sx, y0 - sy, x1 - sx, y1 - sy, 
                                fill=projectile.color)

    def drawGameOver(mode, canvas):
        # Informs the player of a game over scenario with a message
        message = ''
        if(mode.player.shieldHPLeft <= 0):
            message = '''
                            Enemy Won!!!

                        Press r to rematch

            Press b to return to loadout screen
            '''
        elif(mode.enemy.shieldHPLeft <= 0):
            message = '''
                            Player Won!!!

                        Press r to rematch

            Press b to return to loadout screen
            '''
        canvas.create_text(mode.width // 2, mode.height // 2, text=message,
            font='Arial 32 bold', fill='white')

    def redrawAll(mode, canvas):
        # draws all the relavent objects in order
        mode.drawBackground(canvas, mode.background, 0, 0)
        mode.drawPlayer(canvas)
        mode.drawEnemy(canvas)
        mode.drawBorders(canvas)
        if(mode.gameOver):
            mode.drawGameOver(canvas)
        mode.drawProjectiles(canvas)
        mode.drawBorders(canvas)

class SpalshScreenMode(Mode):
    def appStarted(mode):
        mode.message = '''

    Welcome to a shield tester application for the MMO game Elite: Dangerous
            
        -Press space to be taken to the tester mode where you can choose
        your and your enemy's loadout before pressing 'Space' to optimize!
            
        -Pressing h takes you to a help screen for the battle simulator
        '''
        # background from 
        # https://wallpapersite.com/download-most-popular-wallpapers/dark-space-stars-4k-8k-7935.html
        backgroundPath = 'images/' + 'SpaceBackground.jpg'
        mode.background = mode.loadImage(backgroundPath)
        mode.background = ImageTk.PhotoImage(mode.background)

    def redrawAll(mode, canvas):
        canvas.create_image(-1600, 0, image=mode.background)
        canvas.create_text(mode.width // 2, mode.height // 2, text=mode.message,
            font='Arial 18 bold', fill='white')

    def keyPressed(mode, event):
        if(event.key == 'Space'):
            mode.app.setActiveMode(mode.app.testerMode)

class HelpMode(Mode):
    def appStarted(mode):
        mode.message = '''
            -Press 'w/s' to increase/decrease your throttle speed
            -Press 'a/d' to strafe left/right
            -Press 'q/e' to turn left/right
            -Press 'Enter' to fire your weapons
            -Press 'b' to return to battle
        '''
        # background from 
        # https://wallpapersite.com/download-most-popular-wallpapers/dark-space-stars-4k-8k-7935.html
        backgroundPath = 'images/' + 'SpaceBackground.jpg'
        mode.background = mode.loadImage(backgroundPath)
        mode.background = ImageTk.PhotoImage(mode.background)

    def redrawAll(mode, canvas):
        canvas.create_image(-1600, 0, image=mode.background)
        canvas.create_text(mode.width // 2, mode.height // 2, text=mode.message,
            font='Arial 18 bold', fill='white')

    def keyPressed(mode, event):
        if(event.key == 'b'):
            mode.app.setActiveMode(mode.app.gameMode)

class EliteShieldGame(ModalApp):
    # Sets up the entire modal app with the appropriate loadouts and ships
    def appStarted(app):
        app.splashScreenMode = SpalshScreenMode()
        app.testerMode = TesterMode()
        app.shipSelectionMode = ShipSelectionMode()
        app.viewerMode = ViewerMode()
        app.gameMode = GameMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)
        app.playerLoadout = dict()
        app.enemyLoadout = dict()
        app.playerShip = None
        app.enemyShip = None
        app.timerDelay = 1

#################################################
# Run the game
#################################################

def runApp():
    # Initializes and runs the entire application
    EliteShieldGame(width=1200, height=600)