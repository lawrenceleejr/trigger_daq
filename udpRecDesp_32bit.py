# Receives UDP packets from the TP
# Writes them into files depending on the address in the header

# A.Wang, last edited Dec 2, 2016

import sys, signal, struct, time
from udp import udp_fun

from optparse import OptionParser
import os.path

#bufsize = 65536
bufsize = 100000000
maxpkt = 1024*8
UDP_PORT = 6008
UDP_IP = ""
readInterval = 1
sleeptime = 0.0001

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
    print outputFileName
    if not options.newFile:
        print "Doesn't delete old file! If new file desired, add -n option."
    udp_rec()

def udp_rec():
    try:
        udp = udp_fun()
        wordcount = 0
        print "Receiving from TP"
        print "Ctrl+C to stop!"
        print "Sleeping for: ", sleeptime
        udp.set_udp_port(UDP_PORT)
        udp.set_udp_ip(UDP_IP)
        rawsock = udp.udp_client(maxpkt,bufsize)

        while True:
            data, addr = udp.udp_recv(rawsock)
    #            print "received from ", addr
            udpPacket = [data]
                # this assumes we receive the data in packets of 4 bytes, or 32 bits
            datalist = [format(int(hex(ord(c)), 16), '02X') for c in list(udpPacket[0])]
            if len(udpPacket)>0:
                addrnum = datalist[7] # address number reading from
                    # print "addr", int(addrnum)
                del datalist[:8]
                    # print datalist
                wordcount = 0
                header = [0,0,0,0] #20,21,22,23
                with open("%s_%d.dat"%(outputFileName,int(addrnum)),"a") as myfile:
                    wordout = ''
                    fittime = time.time()*pow(10,9)
                    if (int(addrnum)) == 22:
                        myfile.write('TIME: ' + '%f'%fittime + '\n')
                    for byte in datalist:
                        if byte == 'A2': #finder data
                            header[3] = 1
                        if byte == 'A1': #decoded GBT packets
                            header[0] = 1
                        wordcount = wordcount + 1
                        wordout = wordout + byte
                        timestamp = time.time()*pow(10,9)
                        if (wordout == '000C') and (int(addrnum) == 21): #raw GBT packets
                            if (timeflag):
                                myfile.write('TIME: ' + '%f'%timestamp + '\n')
                        if wordcount == 4:
                            if header[3] == 1:
                                if (timeflag):
                                    myfile.write('TIME: ' + '%f'%timestamp + '\n')
                                    header[3] = 0
                            if header[0] == 1:
                                if (timeflag):
                                    myfile.write('TIME: ' + '%f'%timestamp + '\n')
                                header[0] = 0
                            myfile.write(str(wordout) + '\n')
                            print wordout
                            wordout = ''
                            wordcount = 0
                myfile.close()
                time.sleep(sleeptime)

    except KeyboardInterrupt:
        print "Stopped!"
        rawsock.close()
        myfile.close()

if __name__ == "__main__":
    main()
