
                #========              RANGE VALUE GENERATOR              ========#
                #======== PART OF SLOP (SAMPLE-LIMNING OPERATORS PACKAGE) ========#
                #========              V1.0    15 MAR 2020                ========#

'''
MAIN FUNCTION: generateExpoid
MAIN PURPOSE:  generate an exponential-ish list of frequency values - they are used later as band
               dividers in fftanalyzer.py
NOTES:         just a small additional ware. Might include it as a small utility in the CLI or GUI ver.
'''

#--------------------------------------------------------------------------------------------------------
# imports

#--------------------------------------------------------------------------------------------------------
# return a list of somehow nice exponential band values

def generateExpoid(qty=32, start=0, inc=30, expoid=1.2, magnitude=0.5):
	ranges = []
	num = start
	for i in range(qty):
		ranges.append(int(num*magnitude))
		inc *= expoid
		inc = int(inc)
		num += inc
	return ranges


#--------------------------------------------------------------------------------------------------------
# concoct a string that can be copypasted into your code as a list, out of the list object rangeList

def printAsList(rangeList):
	output = "["
	for i in rangeList:
		output += str(i)
		if (i != rangeList[-1]):
			output += ", "
	output += "]"
	return output


#--------------------------------------------------------------------------------------------------------

# this line will print you the default ranges set:
# print(printAsList(generateExpoid()))