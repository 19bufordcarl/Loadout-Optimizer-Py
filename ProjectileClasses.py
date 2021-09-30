#################################################
# ProjectileClasses.py
#
# Your name: Carl Buford
# Your andrew id: cbuford
#
#################################################

import math, copy

# These are all the classes for the projectiles in the battle scenario

class Projectile(object):
    # holds the relevant data for a generic projectile
    def __init__(self, x, y, damage, theta, fromPlayer):
        self.x = x
        self.y = y
        self.damage = damage
        self.vector = (math.cos(theta), math.sin(theta))
        self.fromPlayer = fromPlayer
        self.timer = 0

class ThermalProjectile(Projectile):
    # thermal projectiles move the fastest
    def __init__(self, x, y, damage, theta, fromPlayer):
        super().__init__(x, y, damage, theta, fromPlayer)
        self.color = 'red'
        self.speed = 1
        self.r = 2

class KineticProjectile(Projectile):
    # thermal projectiles move the second fastest
    def __init__(self, x, y, damage, theta, fromPlayer):
        super().__init__(x, y, damage, theta, fromPlayer)
        self.color = 'yellow'
        self.speed = 2
        self.r = 5

class ExplosiveProjectile(Projectile):
    # explosive projectiles move the slowest, but will explode***
    def __init__(self, x, y, damage, theta, fromPlayer):
        super().__init__(x, y, damage, theta, fromPlayer)
        self.color = 'orange'
        self.speed = 5
        self.r = 5

class AbsoluteProjectile(Projectile):
    # thermal projectiles move the second slowest, but can't be resisted
    def __init__(self, x, y, damage, theta, fromPlayer):
        super().__init__(x, y, damage, theta, fromPlayer)
        self.color = 'blue'
        self.speed = 3
        self.r = 5