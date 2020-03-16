
                #========                  FFT ANALYZER                   ========#
                #======== PART OF SLOP (SAMPLE-LIMNING OPERATORS PACKAGE) ========#
                #========              V1.1    16 MAR 2020                ========#

'''
MAIN FUNCTION: analyze
MAIN PURPOSE:  take in a path to a *.wav file, and return a special list:
               it would contain lists of an FFT analysis of every N milliseconds of the audio
               default block size N is 2 milliseconds. So the sound better be of a multiple of 2
               milliseconds length. Unsuitable for a random sound, but it only deals with samples
               generated with the sampleslicer.py
NOTES:         this one is used in bitepacker for analysing a folder with freshly generated samples.
'''

#--------------------------------------------------------------------------------------------------------
# imports

import pydub
from pydub import AudioSegment
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fftpack import fft,fftfreq
import numpy as np


#--------------------------------------------------------------------------------------------------------
# returns a mean of a list filled with floats (pwease don't put other stuff in thewe....)

def meanOfList(arg):
	return sum(arg) / len(arg) 


#--------------------------------------------------------------------------------------------------------
# get a list of amplitude describing lists, one per block, for a sample located at [sampleName]

def analyze(sampleName, blockSize=2):
	sample = AudioSegment.from_file(sampleName)
	sampleAmplitudes = []
	for i, chunk in enumerate(sample[::blockSize]):
		# if a chunk is shorter than blockSize, append some silence to it
		if (len(chunk) < blockSize):
			padLength = blockSize - len(chunk)
			silencePad = AudioSegment.silent(frame_rate=44100, duration=padLength)
			chunk = chunk.append(silencePad, crossfade=0)

		chunkAmplitudes = analyzeChunk(chunk)	
		sampleAmplitudes.append(chunkAmplitudes)
	return sampleAmplitudes


#--------------------------------------------------------------------------------------------------------
# get results of FFT analysis of a pydub AudioSegment. default sampleRanges list gen'd with rangegenerator.py

def analyzeChunk(targetSample, sampleRate=44100, sampleRanges=[0, 18, 39, 65, 95, 132, 175, 227, 289, 363, 452, 558, 685, 837, 1019, 1237, 1498, 1812, 2188, 2639, 3180, 3829, 4607, 5541, 6662, 8006, 9619, 11555, 13877, 16664, 20008, 24021]):
	
	data = targetSample.get_array_of_samples()
	data = np.array(data)
	samples = int(targetSample.frame_count())
	
	datafft = fft(data) # perform an fft
	fftabs = abs(datafft) # get its real part
	fftMax = max(fftabs) # get the maximum value of it
	freqs = fftfreq(samples,1/(sampleRate)) # get frequencies of fft

	amplitudeList = [] # list to which we put all amplitudes within a range and then average them
	meanAmplitudes = [] # list that we return, 12 averaged amplitude values end up here
	currentRange = 0 # number of the left range barrier we currently at

	# now process by every frequency that we have in the FFT result
	for count, freq in enumerate(freqs):
		# break out the moment we see a negative frequency
		if (freq < 0):
			break
		# get the amplitude that corresponds to this freq, normalize it to [0,1] range
		if (fftMax != 0):
			amplitude = fftabs[count]/fftMax
		else:
			amplitude = 0

		# if we reached a value from the next range
		if (freq > sampleRanges[currentRange+1]):
			currentRange += 1 # move to the next range
			meanAmplitudes.append(meanOfList(amplitudeList)) # average current amp. list, append it	
			amplitudeList = [] # then clear it for the next range
			if (currentRange == len(sampleRanges)-1): # if we crossed the last range right barrier - break
				break

		# put the amplitude to the current list of amplitudes for ongoing range

		amplitudeList.append(amplitude)
	return meanAmplitudes
		

#--------------------------------------------------------------------------------------------------------
