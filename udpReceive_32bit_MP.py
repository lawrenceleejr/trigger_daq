# Receives UDP packets from the TP
# Writes them into files depending on the address in the header

# A.Wang, last edited Aug 17, 2017

import sys, signal, struct, time
from udp import udp_fun

from optparse import OptionParser
import os.path

from multiprocessing import Pool, Process, Queue



#bufsize = 65536
bufsize = 100000000
maxpkt = 1024*8
UDP_PORT = 6008
UDP_IP = ""
readInterval = 1
sleeptime = 0.000001
nProc = 2

debug = True


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

    udp_rec()

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

    q = Manager().Queue()
    Process(target=self.handleInput, args=(q,files)).start()

    try:
        while True:
            data, addr = udp.udp_recv(rawsock)
            q.put([data])
    except KeyboardInterrupt:
        print ( ">>> Stopped!" )
        print ( ">>> Have a nice day!" )
        rawsock.close()
        for file in files:
            file.flush()
            os.fsync(myfile.fileno())
            file.close()

# define a few new functions. These will be thrown in a multi-threading pool.

def handleInput(q, files):
    with Pool(processes=nProc) as pool:
        while True:
            pool.apply_async(processPacket, (q.get(),files))
    return

def processPacket(data, files):

    datalist = [format(int(hex(ord(c)), 16), '02X') for c in list(data)]

    if debug:
        print( "Raw data: " , data )
        print( "Formatted Data List: " , datalist )

    if len(datalist) > 7:
        addrnum = datalist[7] # address number reading from
        del datalist[:8]

        wordcount = 0
        myfile = files[int(addrnum)-20]

        if debug:
            print( ">>> Writing packet to file " , int(addrnum) )

        wordout = ''
        fittime = time.time()*pow(10,9)
        if (timeflag):
            myfile.write('TIME: ' + '%f'%fittime + '\n')
        for byte in datalist:
            wordcount = wordcount + 1
            wordout = wordout + byte
            if wordcount == 4:
                myfile.write(str(wordout) + '\n')
                print (wordout)
                wordout = ''
                wordcount = 0

        # myfile.flush()
        # os.fsync(myfile.fileno())
        # time.sleep(sleeptime)

    return


if __name__ == "__main__":
    main()
