## event display for testFIND
## testFIND events generated from decodeFIND_32bit.py and mmtp_test_23.dat files
## output from FINDER is stored in TP fifo 23, this is a way of visualizing
## those events

# N. Wuerfel SPRING 2017

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys, getopt, binstr

helpMessage = 'usage: <cmdline> python noahFIND.py -i <inputfile> -e <eventNo> -b <bcidNo> \n -v for verbose'
verbose = False

# get data for specific event number
# our data is nicely arranged as events always take 10 lines
# takes eventNum and filepointer
# TODO worry about efficiency of reads from file (linecache?)
def getEvent(eventNum, openFile):
    lineNum = (eventNum-1) * 10
    lines = openFile.readlines()
    eventLines = lines[lineNum:lineNum + 10]
    if verbose:
        print "here are the event lines"
        print eventLines

    event = parseEvent(eventLines)
    return event
    
def parseEvent(eventLines):    

    assert(len(eventLines) == 10), 'event longer or shorter than 10 lines'

    event = []
    tmpLines = []

    for line in eventLines:

        lineInfo = line.split()

        if verbose:
            print "Processing line: %s" % line

        # handle event lines
        # later this should save events or something so we can get them efficiently
        # currently doesn't do that LOL
        # TODO
        if lineInfo[0] == "Event":
            lineEventNum = int(lineInfo[1])
            continue # TODO store events for the getEvent method
        # bcid lines
        elif lineInfo[1] == "BCID:":
            lineBCID = int(lineInfo[2])
            continue # TODO store BCID for getEvent
        else:
            tmpLines.append([int (x) for x in lineInfo])
            # each event comprised of 8 things
            if len(tmpLines) == 8:
                event = [lineEventNum] + [lineBCID] + tmpLines
                if verbose:
                    print "Event %i:" % lineEventNum
                    print event
                return event



# open gui(?) to display events
# need to give input file
def main(argv):
    inputfile = ''
    tmpLines = []
    events = []
    try: 
        opts, args = getopt.getopt(argv, "hvi:e:b:",["ifile=","eventNo=","targetBCID="])
    except getopt.GetoptError:
        print helpMessage
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helpMessage
            sys.exit()
        elif opt == '-v':
            global verbose
            verbose = True;
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-e", "--eventNo"):
            targetEventNum = int(arg)

    if inputfile == '':
        print 'please supply an inputfile, -h for help'
        sys.exit()
    dataFile = open(inputfile, 'r')

    if targetEventNum != 0:
        event = getEvent(targetEventNum, dataFile)

    lines = dataFile.readlines()
    for line in lines:

        lineInfo = line.split()

        if verbose:
            print "Processing line: %s" % line

        # handle event lines
        # later this should save events or something so we can get them efficiently
        # currently doesn't do that LOL
        # TODO
        if lineInfo[0] == "Event":
            lineEventNum = int(lineInfo[1])
            continue # TODO store events for the getEvent method
        # bcid lines
        elif lineInfo[1] == "BCID:":
            lineBCID = lineInfo[2]
            continue # TODO store BCID for getEvent
        else:
            tmpLines.append(lineInfo)
            # each event comprised of 8 things
            if len(tmpLines) == 8:
                if verbose:
                    print tmpLines
                tmpLines = []
                
                if targetEventNum:
                    print "Desired event found..."
                    exit()

if __name__ == "__main__":
    main(sys.argv[1:])
