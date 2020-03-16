
                #========                 SAMPLE SLICER                   ========#
                #======== PART OF SLOP (SAMPLE-LIMNING OPERATORS PACKAGE) ========#
                #========              V1.1    16 MAR 2020                ========#

'''
MAIN FUNCTION: processSample
MAIN PURPOSE:  take in a sample name, an output directory, and a prefix for generated slices.
               then slice the sample to even slices of sampleLength milliseconds (def. 128).
               frame rate is basically discretization frequency, and even though i included it
               everywhere, i doubt it's a good idea to touch it at all.
NOTES:         uhhhhh PINGAS
'''

#--------------------------------------------------------------------------------------------------------
# imports

import pydub
from pydub import AudioSegment
from os.path import isfile, join
from math import floor


#--------------------------------------------------------------------------------------------------------
# processes sample at [sampleName] into equal slices and puts them to [outputDirectory] returns # slices made

def processSample(sampleName, outputDirectory, double=True, slicePrefix=False, maxBites=1024, sampleLength=128, frameRate=44100):
	if (double):
		maxBites = floor(maxBites/2)
	if (not slicePrefix):
		slicePrefix = os.path.splitext(sampleName)[0]

	if (sampleLength % 16 != 0):
		raise ValueError("Sample length is not a multiple of 16!")

	orig = AudioSegment.from_file(sampleName)
	sample = setFormat(orig, frameRate)
	bitesMade = 0

	bitesMade += sliceSample(sample, outputDirectory, slicePrefix, maxBites)
	if (double): #slice the sample once more at a grid shifted by half, if we want to.
		sample = sample[(sampleLength/2):]
		bitesMade += sliceSample(sample, outputDirectory, (slicePrefix + "Alt"), maxBites)

	return bitesMade

#--------------------------------------------------------------------------------------------------------
# the actual AudioFragment [audioSample] slicing and exporting function. returns how many slices it made

def sliceSample(audioSample, outputDirectory, slicePrefix="sample", maxBites=1024, sampleLength=128, frameRate=44100):
	counter = 0
	# escape rope in case we get too many samples
	done = False
	# split sound in [sampleLength] millisecond slices and export
	for i, chunk in enumerate(audioSample[::sampleLength]):
		if (done):
			break
		with open((join(outputDirectory, (slicePrefix + "%s.wav" % i))), "wb") as f:
			chunk.export(f, format="wav")
			counter += 1
			if (counter == maxBites):
				done = True
				break
	lastChunkName = join(outputDirectory, (slicePrefix + str(counter-1) + ".wav")) 
	reexportPaddedSample(lastChunkName, sampleLength, frameRate)
	return counter


#--------------------------------------------------------------------------------------------------------
# takes an [audioSample] and returns a [44.1KHZ / 16BIT / MONO / MAXIMIZED] copy of it

def setFormat(audioSample, frameRate=44100):
	if (audioSample.channels == 2):
		sampleLeft = audioSample.split_to_mono()[0]
		sampleRight = audioSample.split_to_mono()[1]
		sample = sampleRight.overlay(sampleLeft)
	else:
		sample = audioSample
	sample = sample.set_sample_width(2)
	sample = sample.set_frame_rate(frameRate)
	sample = sample.apply_gain(-sample.max_dBFS)
	return sample



#--------------------------------------------------------------------------------------------------------
# takes in an AudioFragment [sampleName] and reexports it with silence at the end to match [targetLength]

def reexportPaddedSample(sampleName, targetLength=128, frameRate=44100):
	target = AudioSegment.from_file(sampleName)
	if (len(target) != targetLength):
		padLength = targetLength - len(target)
		silencePad = AudioSegment.silent(frame_rate=frameRate, duration=padLength)
		output = target.append(silencePad, crossfade=0)
		output.export(sampleName, format="wav")
	return


#--------------------------------------------------------------------------------------------------------
