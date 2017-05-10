#!/usr/bin/python

# Common stuff for scripts

import sys, getopt,binstr, time

class tconsts:

    OFFSETS = ["47","47","3A","3A","40","40","40","40"] # in the finder order
#    OFFSETS = ["3A","3A","47","47","40","40","40","40"] # in the finder order
    HITOFFSETS = ["40","40","3A","47","3A","47","40","40"][::-1] # in the hit packet order
#    HITOFFSETS = ["40","40","47","3A","47","3A","40","40"][::-1] # in the hit packet order
    OVERALLOFFSET = "000"
    FLIPPEDBOARDS = [0, 1, 5, 7] # in the finder order
    FLIPPEDHITBOARDS = [1, 2, 4, 7] # in the hit order

