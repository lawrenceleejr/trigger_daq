# Receives UDP packets from the TP
# Writes them into files depending on the address in the header

# A.Wang, last edited Aug 17, 2017

import sys, struct, time, datetime
from udp import udp_fun

import argparse
import os.path

from multiprocessing import Pool, Process, Queue, Value, Lock

import threading
import signal


#bufsize = 65536
bufsize = 100000000
maxpkt = 1024*8
UDP_PORT = 6008
UDP_IP = ""
readInterval = 1
nProc = 1

tenToTheNinth = pow(10,9)

printingSleep = 1 #s

# toggle this to print out timestamps (or not)
timeflag = True



parser = argparse.ArgumentParser(usage="usage: %prog [options] outputFileName")
parser.add_argument("-n", "--newFile",
                  action="store_true",
                  dest="newFile",
                  default=False,
                  help="Forces overwriting of output files")
parser.add_argument("-d", "--debug",
                  action="store_true",
                  default=False,
                  help="Turns on debugging console output")
parser.add_argument("-t", "--useTestInput",
                  action="store_true",
                  default=True,
                  help="turns on internal test input")
parser.add_argument("-r", "--inputRate",
                  type=float,
                  default=100,
                  help="internal test input rate in Hz (may not actually represent input rate since this is done with a sleep)")
parser.add_argument("-p","--nProc",
                  type=int,
                  default=1,
                  help="number of worker threads")

args = parser.parse_args()

print (">>> ")

# Print out the settings
for setting in dir(args):
    if not setting[0]=="_":
        print (">>> ... Setting: {: >20}:  {}".format(setting, eval("args.%s"%setting) ))

print (">>> ")


# open all files
outputFileName = 'mmtp_test'
if any([os.path.isfile("%s_%d.dat" % (outputFileName, i)) for i in [20, 21, 22, 23]]):
    if args.newFile:
        print (">>> Removing old files since you specified the -n option")
        os.system("rm %s_*.dat"%outputFileName)
    else:
        sys.exit("Output file(s) already exist! Exiting.")

files = [open("%s_%d.dat" % (outputFileName, i), "a") for i in range(20,24)]

def main():

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
    Process(target=handleInput, args=(q,nProcessedCounter,intervalProcessedCounter) ).start()

    startTime = datetime.datetime.now()
    # print startTime
    print (">>> Starting DAQ at %s"%(startTime.strftime("%H:%M:%S") ))
    print (">>>")

    timer = printCounters(nProcessedCounter,nTriggersCounter, intervalProcessedCounter, intervalTriggersCounter)


    try:
        while True:
            if args.useTestInput:
                data = '\xf0\x00\x01\x84\x00\x00\x00#\xa2\x00^\xa9\xcd\x10\xe1\xd8'*10
            else:
                data, addr = udp.udp_recv(rawsock)
            if args.debug:
                print (">>> Data being handed to the queue")

            nTriggersCounter.increment()
            intervalTriggersCounter.increment()
            q.put(data)
            # processPacket(data,files)
            if args.useTestInput:
                time.sleep(1./args.inputRate)

            if q.full():
                timeSinceStart = datetime.datetime.now() - startTime
                print (">>> ")
                print (">>> WARNING: Buffer full! I've been running for %s"%str(timeSinceStart))
                print (">>> ")
                time.sleep(1)

    except KeyboardInterrupt:

        print ( ">>>" )
        print ( ">>> Stopped!" )

        while not q.empty():
            print (">>> ")
            print (">>> Waiting for buffer to clear...")
            print (">>> ")
            time.sleep(1)

        print ( ">>> " )
        print ( ">>> Closing files..." )
        print ( ">>> " )

        rawsock.close()
        for file in files:
            file.flush()
            os.fsync(file.fileno())
            file.close()

        print ( ">>> Files closed. Have a nice day!" )

    except:

        print (">>> Something screwed up in udp_rec_mp()...")

# define a few new functions. These will be thrown in a multi-threading pool.

def printCounters(nProcessedCounter,nTriggersCounter,intervalProcessedCounter,intervalTriggersCounter):

    timer = threading.Timer(printingSleep, printCounters, args=(nProcessedCounter,nTriggersCounter,intervalProcessedCounter,intervalTriggersCounter))
    timer.daemon = True
    timer.start()

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

    return timer


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def handleInput(q, counter1, counter2):
    pool = Pool(processes=nProc, initializer=init_worker)
    while True:
        if args.debug:
            print ( "Number of packets in buffer: N" )
        try:
            pool.apply_async(processPacket, (q.get(), ))
            counter1.increment()
            counter2.increment()
        except KeyboardInterrupt:
            while not q.empty():
                if args.debug:
                    print ("Clearing Buffer")
                pool.apply_async(processPacket, (q.get(), ))
                counter1.increment()
                counter2.increment()
            break
        except:
            print (">>> handleInput: Something has happened in launching child process")
    return

def processPacket(data):

    # startTime = datetime.datetime.now()

    if args.debug:
        print (">>> processPacket: Processing packet")

    datalist = [format(int(hex(ord(c)), 16), '02X') for c in list(data)]

    try: #for speed
        addrnum = datalist[7] # address number reading from
        del datalist[:8]

        wordcount = 0
        myfile = files[int(addrnum)-20]

        wordout = ''
        if (timeflag):
            fittime = time.time()*tenToTheNinth
            myfile.write('TIME: ' + '%f'%fittime + '\n')
        for byte in datalist:
            wordcount += 1
            wordout += byte
            if wordcount == 4:
                myfile.write(str(wordout) + '\n')
                # print (wordout)
                wordout = ''
                wordcount = 0
        myfile.flush()
        os.fsync(myfile.fileno())
    except:
        return

    # print(datetime.datetime.now() - startTime)
    return


if __name__ == "__main__":
    main()
