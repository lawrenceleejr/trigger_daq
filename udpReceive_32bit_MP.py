# Receives UDP packets from the TP
# Writes them into files depending on the address in the header

# A.Wang, last edited Aug 17, 2017

import sys, signal, struct, time
from udp import udp_fun

from optparse import OptionParser
import os.path

from multiprocessing import Pool, Process, Queue

import signal


#bufsize = 65536
bufsize = 100000000
maxpkt = 1024*8
UDP_PORT = 6008
UDP_IP = ""
readInterval = 1
# sleeptime = 0.000001
sleeptime = 0.1
nProc = 2

debug = True

useTestInput = True
inputRate = 1 #Hz


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
    print ( ">>> Sleeping for: ", sleeptime )

    udp.set_udp_port(UDP_PORT)
    udp.set_udp_ip(UDP_IP)
    rawsock = udp.udp_client(maxpkt,bufsize)

    q = Queue()
    Process(target=handleInput, args=(q,files)).start()

    try:
        while True:
            if useTestInput:
                data = '\xf0\x00\x01\x84\x00\x00\x00#\xa2\x00^\xa9\xcd\x10\xe1\xd8'*10
                # '\xf0\x00\x01\x19\x00\x00\x00#\xa2\x01Z\xe9\xda\xa3w\xec\xa2\x00Z\xea\xda\xa3x\xbb'
            else:
                data, addr = udp.udp_recv(rawsock)
            if debug:
                print ("Data being handed to the queue")
                # print data
            # inputCounter+=1
            # nItemsInBuffer+=1
            q.put(data)
            # processPacket(data,files)
            # nItemsInBuffer-=1
            if useTestInput:
                time.sleep(1./inputRate)
            # time.sleep(sleeptime)

            # every 10 seconds
            # if int(time.strftime("%S"))%2==0:
            # msg = "test"
            # print inputCounter
            # print nItemsInBuffer
            # sys.stdout.write(msg)
            # sys.stdout.flush()

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

def handleInput(q, files):
    # signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = Pool(processes=1)
    while True:
        if debug:
            print ( "Number of packets in buffer: N" )
        try:
            # print ("1")
            pool.apply_async(processPacket, (q.get(),files))
            # print ("2")
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
        print( "Raw data: " + data )
        print( datalist )

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


# Things I want outputed to the console:
# * Number of packets received
# * Average Rate of Triggers (previous 30 s)
# * Number of packets in buffer


if __name__ == "__main__":
    main()
