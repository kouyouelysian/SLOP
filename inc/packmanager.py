
                #========                SLOP PACK MANAGER                ========#
                #======== PART OF SLOP (SAMPLE-LIMNING OPERATORS PACKAGE) ========#
                #========              V1.0    16 MAR 2020                ========#

'''
MAIN FUNCTION: none
MAIN PURPOSE:  Manage the packs.setting file and the settings dictionary object it represents
               it controls what bitepacks the progam sees and uses 
NOTES:         -
'''

#--------------------------------------------------------------------------------------------------------
# imports

from os import listdir
from os.path import exists, isfile, join, basename
import json

try:
	from inc.bitepacker import getAudioInDir
	import inc.fftanalyzer
except Exception as e:
	from bitepacker import getAudioInDir
	import fftanalyzer


#--------------------------------------------------------------------------------------------------------
# globals

defaultAnalysisFileName = "sampledata.fft"


#--------------------------------------------------------------------------------------------------------
# returns a list of bitepack paths inside target directory. False if none found.

def listPacksInDir(dirName):
	# if no target dir return bad
	if (not exists(dirName)):
		return False

	# hook up global analysis file name setting
	global defaultAnalysisFileName

	# get all files, init output list
	dirContents = listdir(dirName)
	dirPacks = []

	# iterate, put only folders which have [defaultAnalysisFileName] file in them to out list
	for item in dirContents:
		if (not isfile(join(dirName, item))):
			if (exists(join(join(dirName, item), defaultAnalysisFileName))):
				dirPacks.append(join(dirName, item))

	# if found nothing return bad 
	if (len(dirPacks) == 0):
		return False

	return dirPacks


#--------------------------------------------------------------------------------------------------------
#

def makePackEntry(path):
	entry = {'path': path, 'sampleCount': len(getAudioInDir(path))}
	return entry


#--------------------------------------------------------------------------------------------------------
# returns a list of dicts made by makePackEntry, which describes available bitepacks

def makePackList(pathList):
	packList = []
	for packsDir in pathList:
		if (not exists(packsDir)):
			return False
		if (isfile(packsDir)):
			return False
		packsInDir = listPacksInDir(packsDir)
		if (packsInDir):
			for pack in packsInDir:
				packList.append(makePackEntry(pack))

	if (len(packList) == 0):
		return False

	return packList


#--------------------------------------------------------------------------------------------------------
# make a settings dict

def makeSettings(available, active):
	return {"packsAvailable":available, "packsActive":active}

#--------------------------------------------------------------------------------------------------------
# read settings from a file (default ./files/packs.setting)

def importSettings(inFile="./bitepack/packs.setting"):
	if (not exists(inFile)):
		return False
	fHandle = open(inFile, "r")
	jsonString = fHandle.read()
	fHandle.close()
	outSettings = json.loads(jsonString) 
	return outSettings

#--------------------------------------------------------------------------------------------------------
# write settings to a file (default ./files/packs.setting)

def exportSettings(settings, outFile="./bitepack/packs.setting"):
	outSettings = settings
	jsonString = json.dumps(outSettings, indent=4, separators=(',', ': '))
	fHandle = open(outFile, "w")
	fHandle.write(jsonString)
	fHandle.close()
	return


#--------------------------------------------------------------------------------------------------------
# settings modifier: enables all available bitepacks in the settings list

def settEnableAll(set):
	settings = set;
	settings["packsActive"] = []
	for i in settings["packsAvailable"]:
		settings["packsActive"].append(basename(i["path"]))
	return settings


#--------------------------------------------------------------------------------------------------------
# settings modifier: enables a pack by path

def settToggle(set, path):
	settings = set
	for i in settings["packsAvailable"]:
		# if there is such a pack
		if (i["path"] == path):
			if (basename(path) in settings["packsActive"]):
				settings["packsActive"].remove(basename(path))
			else:
				settings["packsActive"].append(basename(path))
			return settings
	return False


#--------------------------------------------------------------------------------------------------------
# returns a list with paths to bitepacks that are enable in the settings dict

def getActivePacksList(settings):
	outList = []
	for packTuple in settings["packsAvailable"]:
		if (basename(packTuple["path"]) in settings["packsActive"]):
			outList.append(packTuple["path"])
	return outList


#--------------------------------------------------------------------------------------------------------
# rescan palces for bitepacks and rebuild a setting

def rescan(places):
	# places are folders where bitepack folders MIGHT be. we rescan every of them
	packData = makePackList(places)

	if (len(packData) == 0):
		return False
	settings = makeSettings(packData, [])
	settings = settEnableAll(settings)
	return settings

#--------------------------------------------------------------------------------------------------------
# register a new pack into the running setting

def register(path, set):
	packData = makePackEntry(path)
	newSet = set
	newSet["packsAvailable"].append(packData)
	newSet["packsActive"].append(basename(path))
	return newSet
