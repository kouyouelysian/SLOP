
                #========                   BITE PACKER                   ========#
                #======== PART OF SLOP (SAMPLE-LIMNING OPERATORS PACKAGE) ========#
                #========              V1.2    16 MAR 2020                ========#

'''
MAIN FUNCTION: packList (variants: packFile, packFolder)
MAIN PURPOSE:  take a list (folder, just one) of files and process it for usage with SLOP.
               result will be a bunch of samples and an analysis file in a pre-defined folder.
NOTES:         important for making bite packs for the program.
'''

#--------------------------------------------------------------------------------------------------------
# imports

from os import listdir, rename, makedirs
from os.path import isfile, join, exists
import json

try:
	from inc import sampleslicer
	from inc import fftanalyzer
except Exception as e:
	import sampleslicer
	import fftanalyzer


#--------------------------------------------------------------------------------------------------------
# globals

maxBites = 192



#--------------------------------------------------------------------------------------------------------
# takes [directory] path, returns a list

def getAudioInDir(directory):
	supportedFormats = ['wav']
	dirContents = listdir(directory)
	output = []
	for file in dirContents:
		 if isfile(join(directory, file)):
		 	if (file[-3:] in supportedFormats):
		 		output.append(join(directory, file))
	return output


#--------------------------------------------------------------------------------------------------------
# takes in an integer and gives back a string fit to three-digit format

def fillZeroes(arg):
	out = str(arg)
	while (len(out) < 3):
		out = "0" + out
	return out


#--------------------------------------------------------------------------------------------------------
# rename all audiosamples in a folder to format PREFIXnnn, where PREFIX is any str and nnn is a 3-sym string
def renameSlices(directory, prefix="sample", fileFormat="wav"):
	fileList = getAudioInDir(directory)
	global maxBites
	counter = 0
	for file in fileList:
		if (counter > maxBites):
			return
		rename(file, join(directory, (prefix + fillZeroes(counter) + "." + fileFormat)))
		counter += 1
	return


#--------------------------------------------------------------------------------------------------------
# takes in a list of paths to wavesamples, slices them to some directory.

def sliceSampleList(listToSlice, destDir, double=True):
	count = 0
	totalBites = 0

	global maxBites
	for sample in listToSlice:
		if (totalBites == maxBites): # if we already made maxBites bites - exit to renaming them
			break
		elif (totalBites == 0):
			totalBites += sampleslicer.processSample(sample, destDir, double, (str(count) + "_"),  maxBites)
		else:
			totalBites += sampleslicer.processSample(sample, destDir, double, (str(count) + "_"),  (maxBites - totalBites))
		count += 1
	renameSlices(destDir)
	return


#--------------------------------------------------------------------------------------------------------
# takes in a directory name, slices them to some directory.

def sliceSampleDir(sourceDir, destDir, double=True):
	toSlice = getAudioInDir(sourceDir)
	sliceSampleList(toSlice, destDir, double)
	return


#--------------------------------------------------------------------------------------------------------
# creates a list of lists of lists (file: chunk: fft values) of FFT analysis data. oh god...
def getAnalysisData(directory):
	fileList = getAudioInDir(directory)
	fftList = []
	for file in fileList:
		fftList.append(fftanalyzer.analyze(file))
	return fftList


#--------------------------------------------------------------------------------------------------------
# dumps the output of getAnalysisData to console. Don't ask why.

def dumpAnalysisDataToConsole(fftList):
	for i, fftFile in enumerate(fftList):
		print("FILE: " + str(i))
		for j, fftChunk in enumerate(fftFile):
			print("    CHUNK:" + str(j))
			for fftValue in fftChunk:
				print("            " + str(fftValue))

#--------------------------------------------------------------------------------------------------------
# returns a nicely indented JSON of the scary list of lists of lists getAnalysisData() makes.

def analysisDataToJson(adata):
	jstring = json.dumps(adata, sort_keys=True, indent=4, separators=(',', ': '))
	return jstring


#--------------------------------------------------------------------------------------------------------
# target directory gets analized (haha), and  a file is put into it. def name is sampeldata.fft. no toch

def analyzeBiteDir(directory, analysisFileName="sampledata.fft"):
	dat = getAnalysisData(directory)
	fileHandle = open(join(directory, analysisFileName), "w")
	fileHandle.write(analysisDataToJson(dat))
	return


#--------------------------------------------------------------------------------------------------------
# main function that unites it all. Processes a list of files into a folder with bites and analysis data

def packList(listToSlice, destDir, double=True):
	if not exists(destDir):
		makedirs(destDir)
	sliceSampleList(listToSlice, destDir, double)
	analyzeBiteDir(destDir)
	return


#--------------------------------------------------------------------------------------------------------
# Wrapper for packList. Processes a folder of files into a folder with bites and analysis data

def packFolder(sourceDir, destDir, double=True):
	fileList = getAudioInDir(sourceDir)
	packList(fileList, destDir, double)
	return


#--------------------------------------------------------------------------------------------------------
# Wrapper for packList. Processes a single file into a folder with bites and analysis data

def packFile(sourceFile, destDir, double=True):
	fileList = [sourceFile]
	packList(fileList, destDir, double)
	return


#--------------------------------------------------------------------------------------------------------
