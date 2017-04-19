# event display for testFIND
# testFIND events generated from decodeFIND_32bit.py and mmtp_test_23.dat files
# output from FINDER is stored in TP fifo 23, this is a way of visualizing
# those events

# to run live do:
#   > python dispFind.py -l -i <inputfile>

# N. Wuerfel SPRING 2017

import time, os, signal, sys, getopt, binstr, random

helpMessage = 'usage: <cmdline> python dispFIND.py -i <inputfile> -e <eventNo> \n -v for verbose \n -l for live'

# option flags for decoding 
verbose = False
remapFlag = 0
offsetFlag = 1
octGeo = 1

# fixed vals for decoding 
remapping = [11,10,9,8,15,14,13,12,3,2,1,0,7,6,5,4,27,26,25,24,31,30,29,28,19,18,17,16,23,22,21,20]
offsets = ["3A","3A","47","47","40","40","40","40"]
#offsets = reversed(["856","85B","84A","84F","84A","84F","856","85B"])    
overall_offset = "000"

# FIND formatted as V1 V0 U1 U0 X3 X2 X1 X0
# Need formatted as X3 X2 V1 U1 V0 U0 X1 X0
# octBoardMap takes care of this reordering for us
octBoardMap = [4, 5, 0, 2, 1, 3, 6, 7] 

# VMMs on some boards is flipped S.T. channel 64 is where we'd expect 0
# currently, flipped boards are: X2, V1, V0, X0
# flipbedBoards takes care of reordering the presentation in display
# HOWEVER, Ann's decode that I use for raw events already takes care of 
# flipping the channel number, so this is only for the display 
flippedBoards = [5, 0, 1, 7]

# teh love
compliments = ['Teehee...',\
               'Oh my, you\'re too kind!',\
               '*Blushes*',\
               'Honestly, you can\'t spend all day complimenting me...',\
               'What kind of program do you think I am?!',\
               'Right back atcha, hotshot!',\
               'Is this appropriate workplace behaviour?',\
               'Oh stop...',\
               'Traceback (most recent call last):\
               \n  File "dispFind.py", line 412, in <module>\
               \n    main (sys.argv[1:])\n\n\n\
               Haha, I\'m just fucking with you,\
               that was sweet though, thanks!',\
               'You know how to treat a display script right xoxo ;)']

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

# parses raw data from TP FIFO 23
# most of this is from Ann Wang's decode_FIND32bit
def parseRawEvent(rawEventLines):

    lines = []
    hits = []
    event = [1337]

    for line in rawEventLines:
        if str(line[0:4]) == 'TIME' and rawEventLines.index(line) == 0:
            print 'PANICKING: WHERE IS THE TIME MARKER?!?!?!'
            # TODO if time info is important?
            continue
        lines.append(line[:len(line)-1]) 
        if len(lines) == 9:

            # TODO error checking for raw Data file

            header = lines[0]
            bcid = int(header[4:],16)
            event.append(bcid)
            for i in range(4):
                hits.append(lines[i+1])
            iplane = 0
            for hit in hits:
                for j in range(2):
                    ivmm, ich = rawDecode(hit,iplane,j)
                    iplane = iplane + 1
                    event.append([ivmm,ich])

    return event
            
                
# straight from Ann's decoder
# ../decoders/decodeFIND_32bit.py
# would import it but its a pain in the ass importing from other directories
def rawDecode(hit, ip, id):
    strip = 0
    if offsetFlag == 1:
        if verbose:
            print "Added offset!"
        if (int(hit[id*4:id*4+4],16) != 0) and sum([int(x,16) for x in offsets])!= 0:
            strip = int(hit[id*4:id*4+4],16)-int(overall_offset,16)-int(offsets[ip],16)
    else:
        strip = int(hit[id*4:id*4+4],16)
    if strip is not 0:
#        if ((ip == 2) or (ip == 3) or (ip == 4) or (ip == 6)) and (octGeo == 1):
        # FTS
        if ((ip == 0) or (ip == 1) or (ip == 5) or (ip == 7)) and (octGeo == 1):
            strip = 512-strip-1
        if remapFlag == 1:
            ivmm = remapping[strip/64]%8
        else:
            ivmm = (strip/64)%8
            ich = strip%64+1
    else:
        ivmm = 0
        ich = 0
    return ivmm, ich



# "live" display of data, just looks at last event recorded in the file after some
# time
# the live display takes raw data from FIFO 23 and decodes it 
# TODO build a "pause" button
def goLive(fileName):
    print fileName
    numberDisplayed = 1
    while True:
        try:
            unused = os.system('clear') # avoid printing return val
            revLines = list(reversed(open(fileName,'r').readlines()))
            lastEventLines = list(reversed(revLines[0:9]))
            lastEvent = parseRawEvent(lastEventLines)
            if verbose:
                print lastEvent
                print "now sleeping..."
            display_hub([lastEvent])
            print "This is the %ith display I've shown, isn't it time you go home?" % numberDisplayed
            numberDisplayed = numberDisplayed + 1 
            time.sleep(2)
        except KeyboardInterrupt:
            unused = os.system('clear') 
            print "Exiting, have a nice day..."
            sys.exit()

# stupid display hub, takes a list of events
def display_hub(eventList):

    eventNos = []
    displayHistory = []
    desiredEvent = 0
    complimentNo = 0

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

        minEvent = min(eventNos)
        maxEvent = max(eventNos)

        while True:
            # TODO think about a better way of doing this?
            print "Events in the range %i-%i are available for display."\
                     % (minEvent, maxEvent)
            print "Please type the event number to view, or 'quit' to exit."
            print "Use 'help' to get a list of commands"

            # get user input
            userInput = raw_input()
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
                    print "'compliment' - feel the love"
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

                elif userInput == 'compliment':
                    complimentNo = complimentNo + 1
                    if complimentNo == 4:
                        print "You're so persistent, here's my number:"
                        print "1-800- %i EVENTS TO DISPLAY" % maxEvent
                    else:
                        rand = random.randint(0,9)
                        print compliments[rand]

                elif 'overlay' in userInput:
                    # TODO
                    print "not yet supported"

                elif int(userInput) in range(min(eventNos),max(eventNos)+1): 
                    desiredEvent = int(userInput)-1
                    displayHistory.append(desiredEvent)
                    ascii_display_event(eventList[desiredEvent])

                else:
                    print "Please supply an event number within the valid range"
    
            except ValueError:
                print "Please supply an event number or a valid command."


# displays a single event
# events formatted as [eventNo, BCID, [vmm, channel], [vmm, channel], ...]
def ascii_display_event(event):

    i = 0
    octBoardOrder = ['X3', 'X2', 'V1', 'U1', 'V0', 'U0', 'X1', 'X0']

    print event
    eventNo = event[0]
    eventBCID = event[1]
    eventBoards = event[2:]
    print "Event Number: %i, Event BCID: %i" % (eventNo, eventBCID)
    
    for index in octBoardMap:
        board = eventBoards[index]
        vmmID = board[0]
        channel = board[1]
        hitMark = [".. "]*8  
        if (vmmID!=0 or channel!=0):
            if index in flippedBoards:
                hitMark[8-vmmID-1] = "%2i " % channel
            else:
                hitMark[vmmID] = "%2i " % channel
        print octBoardOrder[i], "".join(hitMark)
#        print '{:^20}'.format(''.join(hitMark))
#        print '{:^20}'.format(''.join(octBoardOrder[i]))\
#                    +'{:^20}'.format(''.join(hitMark))
        i = i + 1
        

def main(argv):

    targetEventNum = 0
    inputfile = ''
    tmpLines = []
    events = []
    live = False

    # get options
    # TODO migrate to argparse?
    try: 
        opts, args = getopt.getopt(argv, "hvli:e:",["ifile=","eventNo="])
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
 
    # check for mutually exclusive flags (live and eventNo)
    # resolved by user
    if targetEventNum != 0 and live:
        while True:
            os.system('clear')
            print "Hello, sorry to bother you, but I noticed that you've indicated both live display and a specific event number. Unfortunately, event numbers are meaningless for live display."
            print "Please, choose 'l' for live or 'e' for event now..."
            testArg = raw_input()
            if testArg == 'l':
                targetEventNum = 0
                break
            elif testArg == 'e':
                live = False
                break
            else: 
                print 'Please don\'t be cheeky with me, %s is invalid and you know it...' % testArg
                os.system('sleep 2')

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
