
                #========           SLOP COMMAND LINE INTERFACE           ========#
                #======== PART OF SLOP (SAMPLE-LIMNING OPERATORS PACKAGE) ========#
                #========              V1.0    16 MAR 2020                ========#

'''
MAIN FUNCTION: - 
MAIN PURPOSE:  CLI version of SLOP
NOTES:         .
               .
               made by: Astro (aka Astro The Fox, Elysian Tunes, SYNTHFOX, etc..)
               original algorythm envision: Nyn Famitory
               special thanks to people who made libraries listed below there in [# imports]
               .
               visit:
                   https://elysiantunes.bandcamp.com      ~ my music
                   https://sfcs.neocities.org             ~ my DIY synthesizers
                   https://astrossoundhell.neocities.org  ~ my personal webpage
                   https://github.com/kouyouelysian       ~ my github profile
				   https://famitory.bandcamp.com/         ~ Famitory's music
			   .
'''

#--------------------------------------------------------------------------------------------------------
# imports

from inc import bitepacker
from inc import sampleslicer
from inc import matchengine
from inc import fftanalyzer
from inc import rangegenerator
from inc import packmanager

from os.path import exists, isfile, join, dirname, basename
import os


#--------------------------------------------------------------------------------------------------------
# check if a menu option is one letter
def checkMenuOption(arg):
	if (arg.strip() == ''):
		return False
	if (len(arg)>1):
		return False
	return arg.upper()


#--------------------------------------------------------------------------------------------------------
# return false if no such dir
def checkDir(arg):
	if (exists(arg)):
		return arg
	return False


#--------------------------------------------------------------------------------------------------------
# return false if no such file
def checkFile(arg):
	if (os.path.isfile(arg)):
		return arg
	return False 


#--------------------------------------------------------------------------------------------------------
# put a postfix between file's name and extension
def postfixFileName(name, postfix):
	parts = os.path.basename(name).split('.')
	return parts[0] + postfix + "." + parts[1] 
 

#--------------------------------------------------------------------------------------------------------
# clear the console screen
def consoleClear():
	os.system('clear')


#--------------------------------------------------------------------------------------------------------
# debug check a var
def check(arg):
	print(arg)
	input("\nany key to run next..")


#--------------------------------------------------------------------------------------------------------
# local vars

defaultBanner = "welcome to SLOP (Sample Limning Operator Package)"
consoleBanner = defaultBanner
badMessage = ""

defaultPackSettingsLocation = "./bitepack/packs.setting"
packPlaces = ["./bitepack/"]

aboutLocation = "./files/about.txt"
changelogLocation = "./files/changelog.txt"

#--------------------------------------------------------------------------------------------------------
# pre-runtime stuff


packSettings = packmanager.importSettings(defaultPackSettingsLocation)

for packTuple in packSettings["packsAvailable"]:
	if (not exists(packTuple["path"])):
		print("AAAA")
		input()
		packSettings = packmanager.rescan(packPlaces)
		break



#--------------------------------------------------------------------------------------------------------
# cli loop

while (1):

	# prepare
	consoleClear()
	print("\n" + consoleBanner + "\n")
	if (badMessage):
		badMessage = False
		consoleBanner = defaultBanner

	# print opts
	print("\n---- RUN:")
	print("M: MatchEngine")
	print("P: PackManager")
	print("B: BitePacker")
	print("\n---- READ:")
	print("A: about SLOP")
	print("C: changelog")
	print("\n---- OTHER:")
	print("X: exit software")
	opt = checkMenuOption(input("\n#: "))

	# process input option
	if (opt):

		# run bitepacker
		if (opt == "B"):
			consoleClear()
			print("\n" + "SLOP BitePacker" + "\n")
			print("\n" + "What to use BitePacker on?")

			print("\nS: single file")
			print("F: contents of a folder")
			print("L: list of files")
			print("D: done, go back")
			opt = checkMenuOption(input("\n#: "))
			if (opt):
				if (opt == "D"):
					continue
				if (opt == "S"):
					sourceFile = checkFile(input("\nInput source file path\n\n#: "))
					sourceList = [sourceFile]
				elif (opt == "F"):
					sourceDir = checkDir(input("\nInput source file path\n\n#: "))
					sourceList = bitepacker.getAudioInDir(sourceDir)
				elif (opt == "L"):
					sourceList = []
					failedListing = False
					while 1:
						newSource = input("enter path to sourcefile and hit enter, type stop to exit\n\n#: ")
						newSource = newSource.strip()
						if (newSource == "stop"):
							break
						else:
							if (not checkFile(newSource)):
								failedListing = True
								consoleBanner = "ERROR: while making a list of files - no such file!"
							else:
								sourceList.append(newSource)
					if (failedListing):
						badMessage = True
						continue

				else:
					badMessage = True
					consoleBanner('ERROR: no such option!')
					continue


				destDir = input("\nOutput slices to which directory? (blank for built-in)\n\n#: ")
				if (destDir == ""):
					destDir = "./bitepack/"


				packName = input("\nName of this new bitepack?\n\n#: ")
				if (packName.strip() == ""):
					badMessage = True
					consoleBanner = "ERROR: empty bitepack name!"
					continue

				destDir = join(destDir, packName)

				doubleSampling = checkMenuOption(input("\nUse double density sampling? (Y/N)\n\n#: "))
				if (doubleSampling == "Y"):
					d = True
				elif (doubleSampling == "N"):
					d = False
				else:
					consoleBanner = "ERROR: bad Y/N choice!"
					badMessage = True
					continue

				bitesLimit = False
				limitBitesPerFile = checkMenuOption(input("\nLimit bites per sample? (Y/N)\n\n#: "))
				if (limitBitesPerFile == "Y"):
					bitesLimit = input("\nHow many bites per one sample maximum?\n\n#: ")
					try:
						bitesLimit = int(bitesLimit)
					except Exception as e:
						badMessage = True
						consoleBanner = "ERROR: not an integer number provided!"
						continue
				elif (limitBitesPerFile != "N"):
					consoleBanner = "ERROR: bad Y/N choice!"
					badMessage = True
					continue

				if (not sourceList==False):
					check(bitesLimit)
					bitepacker.packList(sourceList, destDir, d, bitesLimit)
					packSettings = packmanager.register(destDir, packSettings)

			else:
				consoleBanner = "ERROR: bad option"
				badMessage = True

			continue;

		# run matchengine
		elif (opt == "M"):

			consoleClear()
			print("\n" + "SLOP: MatchEngine" + "\n")

			# get pack settings
			packPaths = packmanager.getActivePacksList(packSettings)


			# ask about stuff
			inFile = checkFile(input("\nProvide source file path (.wav supported so far)\n#: "))
			if (not inFile):
				badMessage = True
				consoleBanner = "ERROR: such source file does not exist!"
				continue

			outDir = checkDir(input("\nProvide directory for output (blank to put next to original)\n#: "))
			if (not outDir):
				outDir = dirname(inFile)

			outName = input("\nName of the output file without extension? (blank to use autonaming)\n#: ")
			if (outName == ""):
				outName = postfixFileName(inFile, "-limned")
			else:
				outName = join(outDir, (outName + ".wav"))


			# extended parameters
			chunkSize = 8
			fade = True
			normalize = False
			randomize = False



			extOption = checkMenuOption(input("\nEnter extended parameters? (Y/N)\n\n#: "))
			if (extOption == "Y"):
				# entering parameters here
				chunkOption = input("\nChunk length, integer from 2 to 64 (blank for default 8)\n\n#: ")
				try:
					chunkSize = int(chunkOption)
				except Exception as e:
					badMessage = True
					consoleBanner = "ERROR: non-integer value provided!"
					continue
				else:
					if ((chunkSize < 2) or (chunkSize > 64)):
						badMessage = True
						consoleBanner = "ERROR: chunk size exceeds borders!"
						continue

				tempOpt = checkMenuOption(input("\nEnable microfading? (Y/N)\n\n#: "))
				if (tempOpt == "N"):
					fade = False
				elif (tempOpt != "Y"):
					badMessage = True
					consoleBanner = "ERROR: bad (Y/N) choice"
					continue

				tempOpt = checkMenuOption(input("\nEnable chunk gain compensation? (Y/N)\n\n#: "))
				if (tempOpt == "Y"):
					normalize = True
				elif (tempOpt != "N"):
					badMessage = True
					consoleBanner = "ERROR: bad (Y/N) choice"
					continue

				tempOpt = checkMenuOption(input("\nEnable chunk length randomization? (Y/N)\n\n#: "))
				if (tempOpt == "Y"):
					maxDev = min(chunkSize, (64-chunkSize))-1
					print("\nEnter a value of possible positive AND negative deviation from entered chunk length")
					randomize = input("\nThe highest deviation available right now is: %r" % (maxDev))
					try:
						randomize = int(randomize)
					except Exception as e:
						badMessage = True
						consoleBanner = "ERROR: not an integer was provided!"
						continue
					else:
						if (randomize == 0):
							randomize = False
				elif (tempOpt != "N"):
					badMessage = True
					consoleBanner = "ERROR: bad (Y/N) choice"
					continue

			matchengine.createLimnedVersion(inFile, outDir, outName, packPaths, chunkSize, fade, normalize, randomize)

		# run packmanager
		elif (opt == "P"):

			consoleClear()
			print("\n" + "SLOP PackManager" + "\n")

			print("\nE: enable/disable bitepacks")
			print("A: enable all known bitepacks")
			print("R: rescan all known bitepack places")
			print("D: done")

			opt = checkMenuOption(input("\n#: "))

			if (opt):
				if (opt == "D"):
					continue

				elif (opt == "R"):
					r = packmanager.rescan(packPlaces)
					consoleClear()
					if (r):
						packSettings = r
						input("\nrescan complete, press any key to return...")
					else:
						input("\nRESCAN FAILED! no packs found. press any key to exit, and troubleshoot")
				elif(opt == "A"):
					packSettings = packmanager.settEnableAll(packSettings)

				elif (opt == "E"):
					consoleBanner = "SLOP PackManager: edit"
					while (1):
						consoleClear()
						print("\n" + consoleBanner + "\n")
						if (badMessage):
							badMessage = False
							consoleBanner = "SLOP PackManager: edit"
						print("\n-------- available bitepacks:")
						for num, packTuple in enumerate(packSettings["packsAvailable"]):
							print(num, basename(packTuple["path"]))
						print("\n-------- active bitepacks:")
						for item in packSettings["packsActive"]:
							print(item)
						print("\n--------\nenter the number of the pack to toggle, or done to exit manager")

						targetPack = input("\n#: ")
						if (targetPack == "done"):
							if (len(packSettings["packsActive"]) == 0):
								badMessage = True
								consoleBanner = "ERROR: can't have no packs active!"
								continue
							else:
								break
						try:
							targetPackNum = int(targetPack)
						except Exception as e:
							badMessage = True
							consoleBanner = ("ERROR: Not an integer number!")
							continue
						else:
							if ((targetPackNum > (len(packSettings["packsAvailable"])-1)) or (targetPackNum < 0)):
								badMessage = True
								consoleBanner = ("ERROR: No bitepack under such number!")
								continue
							targetTuple = packSettings["packsAvailable"][targetPackNum]
							packSettings = packmanager.settToggle(packSettings, targetTuple["path"])
					


				else:
					badMessage = True
					consoleBanner = "ERROR: Unexistant packmanager option"


			else:
				badMessage = True
				consoleBanner = "ERROR: Bad packmanager option"
				continue

		# show about
		elif (opt == "A"):
			consoleClear()
			if (not exists(aboutLocation)):
				badMessage = True
				consoleBanner = "ERROR: files are corrupt or missing! Please redownload SLOP!"
			fHandle = open(aboutLocation, "r")
			continue
			displayString = fHandle.read()
			fHandle.close()
			print(displayString)
			input("\n\npress any key to go back...")

		# show changelog
		elif (opt == "C"):
			consoleClear()
			if (not exists(changelogLocation)):
				badMessage = True
				consoleBanner = "ERROR: files are corrupt or missing! Please redownload SLOP!"
				continue
			fHandle = open(changelogLocation, "r")
			displayString = fHandle.read()
			fHandle.close()
			print(displayString)
			input("\n\npress any key to go back...")

		# exit
		elif (opt == "X"):
			packmanager.exportSettings(packSettings)
			consoleClear()
			break

		# non-existing option exception
		else:
			consoleBanner = ("ERROR: non-existent option")
			badMessage = True

	else:
		# bad input exception
		consoleBanner = ("ERROR: bad option")
		badMessage = True

#--------------------------------------------------------------------------------------------------------