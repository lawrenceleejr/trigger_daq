# Receives UDP packets from the TP
# Writes them into files depending on the address in the header

# A.Wang, last edited Aug 17, 2017

import sys, struct, time
from udp import udp_fun

from optparse import OptionParser
import os.path

from multiprocessing import Pool, Process, Queue, Value, Lock

import threading


#bufsize = 65536
bufsize = 100000000
maxpkt = 1024*8
UDP_PORT = 6008
UDP_IP = ""
readInterval = 1
nProc = 1


debug = False
useTestInput = True
inputRate = 1000 #Hz

printingSleep = 1 #s

# toggle this to print out timestamps (or not)
timeflag = True

global outputFileName
outputFileName = ''

def main():

    parser = OptionParser(usage="usage: %prog [options] outputFileName")
    parser.add_option("-n", "--newFile",
                      action="store_true",
                      dest="newFile",
                      default=False,
                      help="if the output file already exists don't overwrite it")
    (options, args) = parser.parse_args()
    global outputFileName
    if len(args)==0:
        outputFileName = "mmtp_test"
    else:
        outputFileName = args[0].split(".")[0] if ("." in args[0]) else args[0]

    if options.newFile:
        counter = 1
        while os.path.exists(outputFileName + ".dat"):
            outputFileName = outputFileName.split("__")[0]+"__%d"%counter
            counter += 1
    print (outputFileName)
    if not options.newFile:
        print ( "Doesn't delete old file! If new file desired, add -n option." )

    udp_rec_mp()

    return

class Counter(object):
    def __init__(self, initval=0):
        self.val = Value('i', initval)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value

    def reset(self):
        with self.lock:
            self.val.value = 0

def udp_rec_mp():

    # open all files
    file_20 = open("%s_%d.dat"%(outputFileName,20),"a")
    file_21 = open("%s_%d.dat"%(outputFileName,21),"a")
    file_22 = open("%s_%d.dat"%(outputFileName,22),"a")
    file_23 = open("%s_%d.dat"%(outputFileName,23),"a")

    files = [file_20, file_21, file_22, file_23]

    udp = udp_fun()
    wordcount = 0

    print ( ">>> Receiving From MMTP!" )
    print ( ">>> Type Ctrl+C to stop." )

    udp.set_udp_port(UDP_PORT)
    udp.set_udp_ip(UDP_IP)
    rawsock = udp.udp_client(maxpkt,bufsize)

    nProcessedCounter = Counter(0)
    nTriggersCounter  = Counter(0)

    intervalProcessedCounter = Counter(0)
    intervalTriggersCounter  = Counter(0)

    q = Queue()
    Process(target=handleInput, args=(q,files,nProcessedCounter,intervalProcessedCounter) ).start()

    printCounters(nProcessedCounter,nTriggersCounter, intervalProcessedCounter, intervalTriggersCounter)

    try:
        while True:
            if useTestInput:
                data = '\xf0\x00\x01\x84\x00\x00\x00#\xa2\x00^\xa9\xcd\x10\xe1\xd8'*10
            else:
                data, addr = udp.udp_recv(rawsock)
            if debug:
                print (">>> Data being handed to the queue")

            nTriggersCounter.increment()
            intervalTriggersCounter.increment()
            q.put(data)
            # processPacket(data,files)
            if useTestInput:
                time.sleep(1./inputRate)

            if q.full():
                print (">>> ")
                print (">>> WARNING: Buffer full!")
                print (">>> ")
                time.sleep(1)

    except KeyboardInterrupt:
        print ( ">>> Stopped!" )
        print ( ">>> Have a nice day!" )
        rawsock.close()
        for file in files:
            file.flush()
            os.fsync(file.fileno())
            file.close()
    except:
        print (">>> Something screwed up in udp_rec_mp()...")

# define a few new functions. These will be thrown in a multi-threading pool.

def printCounters(nProcessedCounter,nTriggersCounter,intervalProcessedCounter,intervalTriggersCounter):

    threading.Timer(printingSleep, printCounters, args=(nProcessedCounter,nTriggersCounter,intervalProcessedCounter,intervalTriggersCounter)).start()

    msg = ">>> nTriggers: {:>5}, nPacketsInBuffer: {:>5}, inputRate: {:>5} Hz, outputRate: {:>5} Hz   (Integration Time: {} s)".format(nTriggersCounter.value(),
        nTriggersCounter.value()-nProcessedCounter.value(),
        intervalTriggersCounter.value()/printingSleep,
        intervalProcessedCounter.value()/printingSleep,
        printingSleep
        )
    print (msg)
    sys.stdout.write("\033[F")

    intervalProcessedCounter.reset()
    intervalTriggersCounter.reset()

    return



def handleInput(q, files, counter1, counter2):
    pool = Pool(processes=nProc)
    while True:
        if debug:
            print ( "Number of packets in buffer: N" )
        try:
            pool.apply_async(processPacket, (q.get(),files))
            counter1.increment()
            counter2.increment()
        except KeyboardInterrupt:
            # pool.terminate()
            # pool.join()
            break
        except:
            print (">>> handleInput: Something has happened in launching child process")
    return

def processPacket(data, files):

    if debug:
        print (">>> processPacket: Processing packet")

    datalist = [format(int(hex(ord(c)), 16), '02X') for c in list(data)]

    if debug:
        print( " ".join(datalist) )

    if len(datalist) > 7:
        addrnum = datalist[7] # address number reading from
        del datalist[:8]

        wordcount = 0
        myfile = files[int(addrnum)-20]

        if debug:
            print( ">>> processPacket: Writing packet to file " , int(addrnum) )

        wordout = ''
        fittime = time.time()*pow(10,9)
        if (timeflag):
            myfile.write('TIME: ' + '%f'%fittime + '\n')
        for byte in datalist:
            wordcount = wordcount + 1
            wordout = wordout + byte
            if wordcount == 4:
                myfile.write(str(wordout) + '\n')
                # print (wordout)
                wordout = ''
                wordcount = 0
    return


if __name__ == "__main__":
    main()
