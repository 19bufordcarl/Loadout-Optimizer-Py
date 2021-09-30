#################################################
# ShieldClasses.py
#
# Your name: Carl Buford
# Your andrew id: cbuford
# Credit for inspiration and original calculations and implementation 
# of which this attempts to recreate in python goes to DownToEarthAstronomy
# Link to his powershell program: 
# https://github.com/DownToEarthAstronomy/D2EA_Shield_tester
#################################################

import math, copy, os

# The actual tester, takes the dictionary of choices that the user made
# then uses them to run trials and compute the best combination

def testShields(choices):
    ShieldTesterInstance = ShieldTester(choices)
    ShieldTesterInstance.optimize()
    return ShieldTesterInstance.optimalLoadout

# Function that returns a dictionary of all the ships
def getShipDict(choices):
    ShieldTesterInstance = ShieldTester(choices)
    return ShieldTesterInstance.Ships

# The class that holds the data for an individual Shield generator module

class ShieldGeneratorModule(object):
    def __init__(self, rowIndex, d):
        self.id = int(d['ID'][rowIndex])
        self.size = int(d['class'][rowIndex])
        self.rating = d['rating'][rowIndex]
        self.typ = d['type'][rowIndex]
        self.maxMass = int(d['maxmass'][rowIndex])
        self.optMass = int(d['optmass'][rowIndex])
        self.minMass = int(d['minmass'][rowIndex])
        self.maxMult = float(d['maxmul'][rowIndex])
        self.optMult = float(d['optmul'][rowIndex])
        self.minMult = float(d['minmul'][rowIndex])
        self.regen = float(d['regen'][rowIndex])
        self.brokenRegen = float(d['maxmul'][rowIndex])
        self.upgrade = None

    def addUpgrade(upgrade):
        self.upgrade = upgrade

    def __repr__(self):
        return str(self.id)

    def __hash__(self):
        return hash((self.id,))

    def __eq__(self, other):
        return isinstance(other, ShieldGeneratorModule) and self.id == other.id

# This class holds the data for an upgrade to be applied to a generator

class ShieldGeneratorUpgrade(object):
    def __init__(self, rowIndex, d):
        self.id = int(d['ID'][rowIndex])
        self.typ = d['Type'][rowIndex]
        self.eng = d['Engineering'][rowIndex]
        self.exp = d['Experimental'][rowIndex]
        self.regen = float(d['RegenRateBonus'][rowIndex])
        self.expRes = float(d['ExpRes'][rowIndex])
        self.kinRes = float(d['KinRes'][rowIndex])
        self.thmRes = float(d['ThermRes'][rowIndex])
        self.optMult = float(d['OptimalMultiplierBonus'][rowIndex])

    def __repr__(self):
        engAbbr = ''
        expAbbr = ''
        for word in self.eng.split(' '):
            engAbbr += word[0]
        for word in self.exp.split(' '):
            expAbbr += word[0]
        return self.typ + '— ' + engAbbr + ': ' + expAbbr

    def __hash__(self):
        return hash((self.id,))

    def __eq__(self, other):
        return isinstance(other, ShieldGeneratorUpgrade) and self.id == other.id

# This class that holds the data for an individual Shield booster combo

class ShieldBooster(object):
    def __init__(self, rowIndex, d):
        self.id = int(d['ID'][rowIndex])
        self.eng = d['Engineering'][rowIndex]
        self.exp = d['Experimental'][rowIndex]
        self.hpBonus = float(d['ShieldStrengthBonus'][rowIndex])
        self.expRes = float(d['ExpResBonus'][rowIndex])
        self.kinRes = float(d['KinResBonus'][rowIndex])
        self.thmRes = float(d['ThermResBonus'][rowIndex])

    def __repr__(self):
        engAbbr = ''
        expAbbr = ''
        for word in self.eng.split(' '):
            engAbbr += word[0]
        for word in self.exp.split(' '):
            expAbbr += word[0]
        return engAbbr + ':' + expAbbr

    def __hash__(self):
        return hash((self.id,))

    def __eq__(self, other):
        return isinstance(other, ShieldBoosterModule) and self.id == other.id

class SimpleShip(object):
    # This is separate from the real ship class, it holds a minimal amount of
    # data for the tester to use and optimize the loadout which will be sent
    # to the real ship class
    def __init__(self, rowIndex, d):
        self.id = int(d['ID'][rowIndex])
        self.name = d['ShipName'][rowIndex]
        self.hullMass = int(d['HullMass'][rowIndex])
        self.baseShield = int(d['baseShieldStrength'][rowIndex])

    def __repr__(self):
        return str(self.id) + ': ' + self.name

class ShieldTester(object):
    def __init__(self, choices):
        # choices is a dict of the following structure
        # choices = {'Thermal DPS':     int,        'Kinetic DPS':      int, 
        #            'Explosive DPS':   int,        'Absolute DPS':     int,
        #            'Ship':            str,        'Shield Boosters':  int}
        # All data csv files were sourced from DTEA's project
        # Link: https://github.com/DownToEarthAstronomy/D2EA_Shield_tester
        self.choices = choices
        self.ShieldBoosterData = 'ShieldTester/Data/ShieldBoosterVariants.csv'
        self.ShieldBoosters = dict()
        self.ShieldGeneratorData = 'ShieldTester/Data/ShieldStats.csv'
        self.ShieldGeneratorModules = dict()
        self.ShieldGeneratorUpgradesData = 'ShieldTester/Data/ShieldGeneratorVariants.csv'
        self.ShieldGeneratorUpgrades = dict()
        self.ShipData = 'ShieldTester/Data/ShipStats.csv'
        self.Ships = dict()
        self.csvFileInit(self.ShieldBoosterData)
        self.csvFileInit(self.ShieldGeneratorData)
        self.csvFileInit(self.ShieldGeneratorUpgradesData)
        self.csvFileInit(self.ShipData)
        self.ship = self.Ships[self.choices['Ship']]
        self.timeOnTarget = .2
        self.optimalLoadout = None
        
    def optimize(self):
        self.removeExtras()
        self.optimalLoadout = self.findOptimalLoadout()

    def removeExtras(self):
        # A function that removes all the ships, upgrades, and shields that 
        # do not satisifies the constraints for the given test
        shieldSize = 1
        if self.ship.hullMass < 20: shieldSize = 2
        elif self.ship.hullMass < 100: shieldSize = 3
        elif self.ship.hullMass < 220: shieldSize = 4
        elif self.ship.hullMass < 270: shieldSize = 5
        elif self.ship.hullMass < 600: shieldSize = 6
        elif self.ship.hullMass < 1000: shieldSize = 7
        else: shieldSize = 8
        shieldGeneratorsTemp = copy.deepcopy(self.ShieldGeneratorModules)
        for key in shieldGeneratorsTemp:
            shieldGen = self.ShieldGeneratorModules[key]
            if(shieldGen.size != shieldSize):
                del self.ShieldGeneratorModules[key]

    def csvFileInit(self, path):
        # Opens and reads a csv file, converts it to a dictionary where the
        # keys are the column names and the values are lists which are that 
        # column in order so that indexing into the list with a column name
        # then using the row number to index into the list will retrieve
        # that particular attribute for an item in the csv data
        with open(path, 'rt') as f:
            # Convert csv to dict
            contents = f.read()
            csvList = contents.splitlines()
            columnString = csvList[0]
            csvList.pop(0)
            cols = columnString.split(',')
            masterDict = dict()
            for s in range(len(cols)):
                masterDict[cols[s]] = [ ]
                for csvRow in csvList:
                    csvRowList = csvRow.split(',')
                    masterDict[cols[s]].append(csvRowList[s])
            for rowIndex in range(len(csvList)):
                # Initialize class instances and populate appropriate dict
                if(path == self.ShieldBoosterData):
                    combo = ShieldBooster(rowIndex, masterDict)
                    self.ShieldBoosters[combo.id] = combo
                elif(path == self.ShieldGeneratorData):
                    combo = ShieldGeneratorModule(rowIndex, masterDict)
                    self.ShieldGeneratorModules[combo.id] = combo
                elif(path == self.ShieldGeneratorUpgradesData):
                    combo = ShieldGeneratorUpgrade(rowIndex, masterDict)
                    self.ShieldGeneratorUpgrades[combo.id] = combo
                elif(path == self.ShipData):
                    combo = SimpleShip(rowIndex, masterDict)
                    self.Ships[combo.name] = combo

    def nextCombo(self, combo, numBoosters, index, totalBoosters):
        # A combo generator that returns the next ID combination recursively
        newCombo = copy.deepcopy(combo)
        if newCombo[index] < totalBoosters:
            newCombo[index] += 1
        elif(index != numBoosters - 1):
            newCombo = self.nextCombo(newCombo, numBoosters, index + 1, totalBoosters)
            newCombo[index] = newCombo[index + 1]
        return newCombo

    def getShieldBoosterLoadouts(self):
        # uses combination logic to generate the possible shield booster combos
        numBoosters = self.choices['Shield Boosters']
        totalBoosters = len(self.ShieldBoosters)
        # boosters order by IDs start with all id of 1
        combo = [1] * numBoosters
        combos = [combo]
        i = 1
        while True:
            i += 1
            combo = self.nextCombo(combo, numBoosters, 0, totalBoosters)
            combos.append(combo)
            if(combo[-1] == totalBoosters):
                break
        loadouts = set()
        for combo in combos:
            loadout = tuple()
            for ID in combo:
                loadout = loadout + (self.ShieldBoosters[ID],)
            loadouts.add(loadout)
        return loadouts

    def getBaseShieldStats(self, upgrade):
        # Function that calculates the base shield's hit points and regen
        shieldGen = None
        for shieldGenKey in self.ShieldGeneratorModules:
            if(self.ShieldGeneratorModules[shieldGenKey].typ == upgrade.typ):
                shieldGen = self.ShieldGeneratorModules[shieldGenKey]
        # The arithmetic functions are from the elite dangerous game code
        # used to calculate survivability, found in the code by DTEA
        # he originally coded it in powershell, this is my port to python
        # Link: # https://github.com/DownToEarthAstronomy/D2EA_Shield_tester
        normalizedMass = min(1, (shieldGen.maxMass - self.ship.hullMass) / \
                                (shieldGen.maxMass - shieldGen.minMass))
        exponent = math.log10((shieldGen.optMult - shieldGen.minMult) / \
                              (shieldGen.maxMult - shieldGen.minMult)) / \
                   math.log10(min(1, (shieldGen.maxMass - shieldGen.optMass) / \
                                     (shieldGen.maxMass - shieldGen.minMass)))
        multiplier = shieldGen.minMult + math.pow(normalizedMass, exponent) * \
                     (shieldGen.maxMult - shieldGen.minMult)
        return (self.ship.baseShield * multiplier, shieldGen.regen)

    def computeLoadoutData(self, loadout):
        # Function that calculates the relevant dat for a loadout
        # The arithmetic functions are from the elite dangerous game code
        # used to calculate survivability, found in the code by DTEA
        # he originally coded it in powershell, this is my port to python
        # Link: # https://github.com/DownToEarthAstronomy/D2EA_Shield_tester
        (shieldGeneratorUpgrade, shieldBoosterLoadout) = loadout
        loadoutData = dict()
        expModifier = 1
        kinModifier = 1
        thmModifier = 1
        hpBonus = 0
        for booster in shieldBoosterLoadout:
            expModifier = expModifier * (1 - booster.expRes)
            kinModifier = kinModifier * (1 - booster.kinRes)
            thmModifier = thmModifier * (1 - booster.thmRes)
            hpBonus = hpBonus + booster.hpBonus
        if(expModifier < .7): expModifier = .7 - (.7 - expModifier) / 2
        if(kinModifier < .7): kinModifier = .7 - (.7 - kinModifier) / 2
        if(thmModifier < .7): thmModifier = .7 - (.7 - thmModifier) / 2
        finalExpRes = 1 - ((1 - shieldGeneratorUpgrade.expRes) * expModifier)
        finalKinRes = 1 - ((1 - shieldGeneratorUpgrade.kinRes) * kinModifier)
        finalThmRes = 1 - ((1 - shieldGeneratorUpgrade.thmRes) * thmModifier)
        (baseShieldHP, baseShieldRegen) = self.getBaseShieldStats(shieldGeneratorUpgrade)
        finalHP = baseShieldHP * (1 + hpBonus) * (1 + shieldGeneratorUpgrade.optMult)
        finalRegen = baseShieldRegen * (1 + shieldGeneratorUpgrade.regen)
        effectiveDPS = self.timeOnTarget * (
            self.choices['Explosive DPS'] * (1 - finalExpRes) + \
            self.choices['Kinetic DPS'] * (1 - finalKinRes) + \
            self.choices['Thermal DPS'] * (1 - finalThmRes) + \
            self.choices['Absolute DPS']
            ) - finalRegen * (1 - self.timeOnTarget)
        lifespan = finalHP / effectiveDPS
        # Puts the relevant loadout data into its dictionary
        loadoutData['Upgrade'] = shieldGeneratorUpgrade
        loadoutData['Boosters'] = shieldBoosterLoadout
        loadoutData['HP'] = finalHP
        loadoutData['Regen'] = finalRegen
        loadoutData['Explosive Resistance'] = finalExpRes
        loadoutData['Kinetic Resistance'] = finalKinRes
        loadoutData['Thermal Resistance'] = finalThmRes
        loadoutData['Lifespan'] = lifespan
        return loadoutData

    def findOptimalLoadout(self):
        # First generate the possible permutations of the shield boosters 
        # given constraints - order of the list does not matter
        shieldBoosterLoadouts = self.getShieldBoosterLoadouts()
        bestLifespan = 0
        bestLoadout = tuple()
        for shieldGeneratorUpgradeID in self.ShieldGeneratorUpgrades:
            shieldGeneratorUpgrade = self.ShieldGeneratorUpgrades[shieldGeneratorUpgradeID]
            for shieldBoosterLoadout in shieldBoosterLoadouts:
                loadout = (shieldGeneratorUpgrade, shieldBoosterLoadout)
                loadoutData = self.computeLoadoutData(loadout)
                if(loadoutData['Lifespan'] > bestLifespan):
                    bestLoadout = loadoutData
                    bestLifespan = loadoutData['Lifespan']
        return bestLoadout