#!/usr/bin/env python

import os,sys

# inputFileName = sys.argv[1]
inputFileName = "r3517_comb.dat.sample"
# inputFileName = "r3517_comb.dat"

def readInEvents(inputFileName):
	with open(inputFileName) as f:
		myOutput = ""
		for line in f:
			if "===" in line:
				tmpOutput = myOutput
				myOutput = ""
				yield tmpOutput
			else:
				myOutput+=line


def parseEventData(eventData):
	eventData = [s.strip() for s in eventData.splitlines()]
	print eventData

eventListGen = readInEvents(inputFileName)

for iEvent,eventData in enumerate(eventListGen):
	# print eventData
	parseEventData(eventData)
	# break
	print iEvent



