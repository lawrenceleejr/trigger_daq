#!/usr/bin/python

# Stuff for visuals

import sys, getopt,binstr, time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[34m'
    ANNFAV = '\033[38;5;86;48;5;25m'
    OKGREEN = '\033[92m'
    WARNING = '\033[38;5;227;48;5;232m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def update_progress(progress):
    barLength = 10
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
