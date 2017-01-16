#!/usr/bin/python 

# Adapted from artPgWrite.m
# Writes 32 bit words and writes them to the TP FIFOs

# Input data format: Column 1: 32 bit data word Column 2: FIFO reg address (2 hex digits)

# A.Wang, last edited Jan 16, 2017

# Not yet tested
# basically the same as doPackets with less shit

import sys,socket,struct,getopt,time,regWrite

TCP_IP = "192.168.1.10"
TCP_PORT = 7

def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:", ["i="])
    except getopt.GetoptError:
        print 'artPgWrite.py -i <inputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'artPgWrite.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            print arg
            inputfile = arg

    # Opening file and sending
    datafile = open(inputfile, 'r')
    print "Sending ART Data"
    #sending data
    for rawline in datafile:
        line = rawline.split(" ")
        pktData = str(line[0])
        fifoAddr = str(line[1])
        fifoAddr = "000000"+fifoAddr
        print pktData, fifoAddr        
        regWrite.writeToRegister(TCP_IP,TCP_PORT,fifoAddr,pktData)
        time.sleep(0.3)
    datafile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
