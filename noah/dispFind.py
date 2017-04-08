## event display for testFIND
## testFIND events generated from decodeFIND_32bit.py and mmtp_test_23.dat files
## output from FINDER is stored in TP fifo 23, this is a way of visualizing
## those events

# N. Wuerfel SPRING 2017

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os, signal, sys, getopt, binstr

helpMessage = 'usage: <cmdline> python noahFIND.py -i <inputfile> -e <eventNo> -b <bcidNo> \n -v for verbose'
verbose = False

# get data for specific event number
# our data is nicely arranged as events always take 10 lines
# takes eventNum and lines read fromfile
# TODO worry about efficiency of reads from file (linecache?)
def getEvent(eventNo, dataLines):

    lineNum = (eventNo-1) * 10
    event = []

    if lineNum+10 > len(dataLines):
        if verbose:
            print "Selected eventNo does not exist... sorry!"
        return event

    if verbose:
        print "Getting eventNo %i from line %i" % (eventNo, lineNum)

    # check if eventNo is valid
    # why does indexError not happen when I exceed indexes?
    #try:
    #    eventLines = dataLines[lineNum:lineNum + 10]
    #    print len(dataLines)
    #except IndexError:
    #    if verbose:
    #        print "Selected eventNo does not exist... sorry!"
    #    return event

    eventLines = dataLines[lineNum:lineNum+10]
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

# "live" display of data, just looks at last event recorded in the file after some
# time
# TODO build a "pause" button
def goLive(fileName):
    while True:
        # TODO change to clear whatever screen I end up using, this is for ascii
        unused = os.system('clear') # avoid printing return val
        revLines = list(reversed(open(fileName,'r').readlines()))
        lastEventLines = list(reversed(revLines[0:10]))
        lastEvent = parseEvent(lastEventLines)
        if verbose:
            print lastEvent
            print "now sleeping..."
        ascii_display([lastEvent])
        unused = os.system('sleep 2')

# stupid ascii display, takes a list of events
# events formatted as [eventNo, BCID, [vmm, channel], [vmm, channel], ...]
def ascii_display(eventList):
    for event in eventList:
        if verbose:
            print event
        
        eventNo = event[0]
        eventBCID = event[1]

        print "Event Number: %i, Event BCID: %i" % (eventNo, eventBCID)

        # current order is XXXXUUVV or something crazy
        eventBoards = event[2:]

        for board in eventBoards:
            vmmID = board[0]
            channel = board[1]
            hitMark = ["."]*8  
            hitMark[vmmID] = "%i" % channel
            print "".join(hitMark)
        

# open gui(?) to display events
# need to give input file
def main(argv):
    targetEventNum = 0
    inputfile = ''
    tmpLines = []
    events = []
    live = False

    # get options
    # TODO migrate to argparse?
    try: 
        opts, args = getopt.getopt(argv, "hvli:e:b:",["ifile=","eventNo=","targetBCID="])
    except getopt.GetoptError:
        print helpMessage
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print helpMessage
            sys.exit()
        elif opt == '-v':
            global verbose
            verbose = True
        elif opt == '-l':
            live = True
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-e", "--eventNo"):
            targetEventNum = int(arg)
 
    if inputfile == '':
        print 'please supply an inputfile, -h for help'
        sys.exit()

    # go live
    if live:
        if verbose:
            print "going live!"
        goLive(inputfile)
        sys.exit()

    dataFile = open(inputfile, 'r')
    dataLines = dataFile.readlines()

    # if we have a particular event that's the only one we'll grab
    if targetEventNum != 0:
        events.append(getEvent(targetEventNum, dataLines))

    # otherwise, just get all the events
    # TODO this is stupid slow because I need to ask questions about python 
    # getEvent either opens and reads all lines again or creates a copy of all
    # the lines on each call which is very bad, linecache?
    else:
        i = 1
        while True:                
            thisEvent = getEvent(i,dataLines)
            if not thisEvent:
                break
            events.append(thisEvent)
    
    if verbose:
        print events

    ascii_display(events)

if __name__ == "__main__":
    main(sys.argv[1:])
