# event display for testFIND
# testFIND events generated from decodeFIND_32bit.py and mmtp_test_23.dat files
# output from FINDER is stored in TP fifo 23, this is a way of visualizing
# those events

# to run live do:
#   > python dispFind.py -l -i <inputfile>

# N. Wuerfel SPRING 2017

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os, signal, sys, getopt, binstr

helpMessage = 'usage: <cmdline> python dispFIND.py -i <inputfile> -e <eventNo> -b <bcidNo> \n -v for verbose \n -l for live'
verbose = False

# get data for specific event number
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
    
# given 10 lines corresponding to an event
# returns an event object (a list)
def parseEvent(eventLines):    

    assert(len(eventLines) == 10), 'event longer or shorter than 10 lines'

    event = []
    tmpLines = []

    for line in eventLines:

        lineInfo = line.split()

        if verbose:
            print "Processing line: %s" % line

        # handle event lines
        if lineInfo[0] == "Event":
            lineEventNum = int(lineInfo[1])
            continue 
        # bcid lines
        elif lineInfo[1] == "BCID:":
            lineBCID = int(lineInfo[2])
            continue # TODO store BCID for getEvent
        # data lines
        else:
            tmpLines.append([int (x) for x in lineInfo])
            # each event comprised of 8 hits
            if len(tmpLines) == 8:
                event = [lineEventNum] + [lineBCID] + tmpLines
                return event

# "live" display of data, just looks at last event recorded in the file after some
# time
# TODO build a "pause" button
def goLive(fileName):
    numberDisplayed = 1
    while True:
        unused = os.system('clear') # avoid printing return val
        revLines = list(reversed(open(fileName,'r').readlines()))
        lastEventLines = list(reversed(revLines[0:10]))
        lastEvent = parseEvent(lastEventLines)
        if verbose:
            print lastEvent
            print "now sleeping..."
        display_hub([lastEvent])
        print "This is the %ith display I've shown, isn't it time you go home?" % numberDisplayed
        numberDisplayed = numberDisplayed + 1 
        unused = os.system('sleep 2')

# stupid display hub, takes a list of events
def display_hub(eventList):

    eventNos = []
    desiredEvent = 0
    displaying = 0
    displayHistory = []

    # only one event, display it
    if len(eventList) == 1:
        ascii_display_event(eventList[desiredEvent])

    # else, give user ability to see whichever events are desired
    else:
        unused = os.system('clear')
        print "Launching display utility..."
        print "Parsing events..."
        for event in eventList:
            eventNos.append(event[0]) 
        while True:
            # TODO think about a better way of doing this?
            print "Events in the range %i-%i are available for display." % (min(eventNos), max(eventNos))
            print "Please type the event number you'd like to view, or 'quit' to exit."
            print "Use 'help' to get a list of commands"
            # get user input
            userInput = raw_input()
            print

            try:
                os.system('clear')
                if userInput == 'quit' or userInput == 'q':
                    print "Now quitting, have a nice day..."
                    sys.exit()

                elif userInput == 'help' or userInput == 'h':
                    print "Commands:"
                    print "'quit', 'q' - exits the program"
                    print "'help', 'h' - displays this list"
                    print "'clear' - clears terminal"
                    print "'last' - shows last event displayed"
                    print "'a' - decrease displayed event number by 1"
                    print "'d', '' - increase displayed event number by 1"
                    print "'hist' - show eventNo browsing history"
                    print "'wipe' - clean browsing history"
                    print 

                elif userInput == 'clear':
                    os.system('clear')

                elif userInput == 'last':
                    if not displayHistory:
                        print "You have an empty browsing history!"
                        continue
                    else:
                        lastEvent = displayHistory.pop()
                    ascii_display_event(eventList[lastEvent])
                    

                elif userInput == 'a':
                    if not displayHistory: 
                        print "Not currently showing an event"
                        continue
                    desiredEvent = displayHistory[-1] - 1
                    displayHistory.append(desiredEvent)
                    ascii_display_event(eventList[desiredEvent])


                elif userInput == 'd' or userInput == '':
                    if not displayHistory:
                        print "Not currently showing an event"
                        continue
                    desiredEvent = displayHistory[-1] + 1
                    displayHistory.append(desiredEvent)
                    ascii_display_event(eventList[desiredEvent])


                elif userInput == 'hist':                
                    print "Event browsing history:"
                    for item in displayHistory:
                        print item+1

                elif userInput == 'wipe':
                    displayHistory = []
                    print "History cleaned"

                elif 'overlay' in userInput:
                    # TODO
                    print "not yet supported"

                elif int(userInput) in range(min(eventNos),max(eventNos)+1): 
                    desiredEvent = int(userInput)-1
                    displayHistory.append(desiredEvent)
                    ascii_display_event(eventList[desiredEvent])

                else:
                    print "Please supply an event number within the valid range"
    
            # only want to support numbers or 'quit'
            except ValueError:
                print "Please supply an event number or the 'quit' command"


# displays a single event
# events formatted as [eventNo, BCID, [vmm, channel], [vmm, channel], ...]
def ascii_display_event(event):

    eventNo = event[0]
    eventBCID = event[1]
    print "Event Number: %i, Event BCID: %i" % (eventNo, eventBCID)

    # TODO check geography and remap to look like octoplet if needed
    # current board order is XXXXUUVV or something crazy
    eventBoards = event[2:]
    for board in eventBoards:
        vmmID = board[0]
        channel = board[1]
        hitMark = ["."]*8  
        hitMark[vmmID] = "%i" % channel
        print '{:^80}'.format(''.join(hitMark))
        

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

    # deal with flags
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
 
    # check input file
    if not os.path.isfile(inputfile):
        print 'Please supply an input file, -h for help'
        sys.exit()

    # go live
    if live:
        if verbose:
            print "going live!"
        goLive(inputfile)
        sys.exit()

    # open file
    dataFile = open(inputfile, 'r')
    dataLines = dataFile.readlines()

    # if we have a particular event, get it
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
            i = i+1
            if not thisEvent:
                break
            events.append(thisEvent)
    
    if verbose:
        print events

    # show event(s)
    # TODO make it easy to display many different events from file
    display_hub(events)

if __name__ == "__main__":
    main(sys.argv[1:])
