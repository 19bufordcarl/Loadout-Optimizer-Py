#################################################
# ShipClasses.py
#
# Your name: Carl Buford
# Your andrew id: cbuford
#
#################################################

import math, copy

# Contains all data storing classes for ships to be used in the game world
# Sprites from https://i.pinimg.com/originals/33/8b/32/338b325178c15394ce18b5a75649f14c.png

class SpaceShip(object):
    def __init__(self, loadout, x=0, y=0, theta=0):
        # loadout is a dictionary mapping different attributes of a ship
        self.kinDPS = loadout['Kinetic DPS']
        self.thmDPS = loadout['Thermal DPS']
        self.expDPS = loadout['Explosive DPS']
        self.absDPS = loadout['Absolute DPS']
        self.shieldHP = loadout['HP']
        self.upgrade = loadout['Upgrade']
        self.boosters = loadout['Boosters']
        self.regen = loadout['Regen']
        self.kinRes = loadout['Kinetic Resistance']
        self.thmRes = loadout['Thermal Resistance']
        self.expRes = loadout['Explosive Resistance']
        self.estLife = loadout['Lifespan']
        self.shieldHPLeft = self.shieldHP
        self.theta = theta
        self.vector = (math.cos(self.theta), math.sin(self.theta))
        self.speed = 100
        self.x = x
        self.y = y
        self.r = 50
        # temporary, for collisions only
        self.mass = 50
        self.strafeLeft = False
        self.strafeRight = False
        self.speedMult = 3
        self.strafeMult = 2
        self.regenDelay = 500
        self.fireDelay = 100

    def align(self):
        # recomputes the current thrust vector
        self.vector = (math.cos(self.theta), math.sin(self.theta))

    def thrust(self, dspeed):
        # applies a boost to the current speed
        self.speed += dspeed

    def turn(self, dtheta):
        # turns and aligns the ship to the new thrust vector
        self.theta += dtheta
        self.align()

# Separates out the player and enemy instances to ease collision checking
class PlayerShip(SpaceShip):
    def __init__(self, loadout, x=0, y=0, theta=0):
        super().__init__(loadout, x, y, theta)
        self.fireCooldownTimer = 0

    def __eq__(self, other):
        return isinstance(other, PlayerShip) and self.estLife == other.estLife

class EnemyShip(SpaceShip):
    def __init__(self, loadout, x=0, y=0, theta=math.pi):
        super().__init__(loadout, x, y, theta)

    def __eq__(self, other):
        return isinstance(other, EnemyShip) and self.estLife == other.estLife