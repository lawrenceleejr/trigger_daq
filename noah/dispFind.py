## event display for testFIND
## testFIND events generated from decodeFIND_32bit.py and mmtp_test_23.dat files
## output from FINDER is stored in TP fifo 23, this is a way of visualizing
## those events

# N. Wuerfel SPRING 2017

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys, getopt, binstr

helpMessage = 'usage: <cmdline> python noahFIND.py -i <inputfile> -e <eventNo> -b <bcidNo> \n -v for verbose'

# get data for specific event number
# our data is nicely arranged as events always take 10 lines
# takes eventNum and filepointer
# TODO worry about efficiency of reads from file (linecache?)
def getEvent(eventNum, openFile):
    lineNum = ((eventNum - 1) * 10) + 1
    


# open gui(?) to display events
# need to give input file
def main(argv):
    inputfile = ''
    targetEventNum = 0
    targetEventReached = True 
    targetBCID = 0
    tmpLines = []
    events = []
    verbose = False
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
            verbose = True
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-e", "--eventNo"):
            targetEventNum = int(arg)
            targetEventReached = False

    if inputfile == '':
        print 'please supply an inputfile, -h for help'
        sys.exit()
    dataFile = open(inputfile, 'r')

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
            if verbose:
                print "targetEventNum: %i, lineEventNum: %i" % (targetEventNum, lineEventNum)
            if targetEventNum != 0 and lineEventNum != targetEventNum:
                continue
            else:
                targetEventReached = True
            continue # TODO store events for the getEvent method

        if not targetEventReached:
            if verbose:
                print "wrong event, skipping"
            continue

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
