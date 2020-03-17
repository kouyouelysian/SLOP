
                #========                   MATCH ENGINE                  ========#
                #======== PART OF SLOP (SAMPLE-LIMNING OPERATORS PACKAGE) ========#
                #========              V1.0    16 MAR 2020                ========#

'''
MAIN FUNCTION: matchSample()
MAIN PURPOSE:  build a limned version of an input sample out of available packs
NOTES:         just a small additional ware. Might include it as a small utility in the CLI or GUI ver.
'''

#--------------------------------------------------------------------------------------------------------
# imports

import json
import pydub
from pydub import AudioSegment
from os.path import isfile, join
from math import ceil
from random import randrange

try:
	from inc import fftanalyzer
	from inc.bitepacker import fillZeroes
except:
	import fftanalyzer
	from bitepacker import fillZeroes


#--------------------------------------------------------------------------------------------------------
# make a limned version of inFile and render it to outDirectory under name outName.wav

def createLimnedVersion(inFile, outDir, outName, bitePackList, chunkSize=4, fade=False, normalize=False, randomize=False ):
	sampleFFTData = getSampleFFT(inFile)
	newSample = matchSample(sampleFFTData, bitePackList, chunkSize, fade, normalize, randomize)
	outPath = join(outDir, outName)
	file_handle = newSample.export(outPath, format="wav")


#--------------------------------------------------------------------------------------------------------
# takes in a path to input file, returns its FFT data

def getSampleFFT(sampleName, blockSize=2):
	dat = fftanalyzer.analyze(sampleName, blockSize)
	return dat


#--------------------------------------------------------------------------------------------------------
# takes in two FFT Amplitude lists, 

def getAmpListDistance(l1, l2):
	if (len(l1) != len(l2)):
		raise ValueError("chunk numbers differ in analysis file and current running routine!!!")
	distance = 0
	for num, val1 in enumerate(l1):
		distance += abs(l1[num] - l2[num])
	return distance


#--------------------------------------------------------------------------------------------------------
# read a bitepack analysis file and convert it to list of lists of lists (gosh, i am getting TIRED...)

def jsonToBitePackAnalysisList(inFile):
	fHandle = open(inFile, "r")
	jsonString = fHandle.read()
	fHandle.close()
	analysis = json.loads(jsonString)
	return analysis


#--------------------------------------------------------------------------------------------------------
# get chunk of amplitude lists of a bite number [sampleNum] from a pack described by [fftList] list

def getBiteChunk(sampleNum, fftList, size):
	# if we requesting a negative or a nonexisting sample - tell to go yiff self
	if ((sampleNum < 0) or (sampleNum > (len(fftList)-1))):
		raise ValueError("Sample not exists!")
	out = fftList[sampleNum]
	return out[:size]


#--------------------------------------------------------------------------------------------------------

def matchSample(sampleFFTData, bitePackList, givenChunkSize=4, fade=False, norm=False, rand=False, blockSize=2, dataFileName="sampledata.fft"):

	# had to move the original value into a variable, more or less the CLI calls it 'chunk length', so...
	# chunk size is value used DURING APPENDAGE, chunk length is the original value passed on when called
	chunkSize = givenChunkSize

 	# fade-related values calculation
	fadeInChunks = ceil(chunkSize/4)

	if (fade):
		sampleSize = blockSize*(chunkSize+fadeInChunks)
	else:
		sampleSize = blockSize*chunkSize

	# bitePackList = list of bitepack directories.
	bpDirAndData = []

	for bitePackDir in bitePackList:
		fftFile = join(bitePackDir, dataFileName)
		data = jsonToBitePackAnalysisList(fftFile)
		tuple = [bitePackDir, data]
		bpDirAndData.append(tuple)

	outSample = AudioSegment.silent(duration=0, frame_rate=44100)
	outSample = outSample.empty()

	count = 0
	cfade = 0

	while (count < len(sampleFFTData)):

		if (count+chunkSize < len(sampleFFTData)):
			currentSampleChunk = sampleFFTData[count:count+(chunkSize-1)]
		else:
			currentSampleChunk = sampleFFTData[count:]
		
		goodSampleTuples = []
		for tuple in bpDirAndData:
			goodSampleTuples.append(matchChunk(currentSampleChunk, tuple[1], len(currentSampleChunk)))

		# finally find the BEST bite to represent current chunk of the in sample
		minDistance = 1024
		bestBitePack = 0
		for num, val in enumerate(goodSampleTuples):
			if (val[1] < minDistance):
				minDistance = val[1]
				bestBitePack = num

		appendSampleName = "sample" + fillZeroes(goodSampleTuples[bestBitePack][0]) + ".wav"
		appendSamplePath = join(bpDirAndData[bestBitePack][0], appendSampleName)


		appendSample = AudioSegment.from_file(appendSamplePath, format="wav")


		if ((fade) and (count>0)):
			cfade = blockSize*fadeInChunks

		appendSample = appendSample[:sampleSize]

		if (norm):
			appendSample = normalizeAudioSegment(appendSample)

		outSample = outSample.append(appendSample, crossfade=cfade)

		count += chunkSize

		# post-appendage random chunk and fade length recalculation if needed:
		if (rand):
			chunkSize = givenChunkSize + randrange(-rand, +rand)
			fadeInChunks = ceil(givenChunkSize/4)

	return outSample

#--------------------------------------------------------------------------------------------------------
#

def matchChunk(sampleChunkData, fftList, chunkSize):


	distance = 0
	minDistance = 1024
	bestSampleNum = 0

	for num, bite in enumerate(fftList):
		biteChunkData = getBiteChunk(num, fftList, chunkSize)
		distance = compareChunks(sampleChunkData, biteChunkData)
		if (distance < minDistance):
			minDistance = distance
			bestSampleNum = num

	return [bestSampleNum, minDistance]

#--------------------------------------------------------------------------------------------------------
#

def compareChunks(sampleChunk, biteChunk):

	if (len(sampleChunk) != len(biteChunk)):
		raise ValueError("Awful garbage has happened, blame Astro!")
	overallDistance = 0
	for num, val in enumerate(sampleChunk):
		overallDistance += getAmpListDistance(sampleChunk[num], biteChunk[num])
	return overallDistance


#--------------------------------------------------------------------------------------------------------
# return a volume-normalized copy of the sample

def normalizeAudioSegment(aseg):
	return aseg.apply_gain(-aseg.max_dBFS)




#--------------------------------------------------------------------------------------------------------
