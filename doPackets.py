
#!/usr/bin/python

# Adapted from doPackets.m
# takes artPgWrite.py and writes a pcket, and then looks at the data

# A.Wang, last edited Jan 9, 2017

# Not yet tested

import sys,artPgWrite,udpRecDesp_32bit,getopt,time
import multiprocessing as mp

TCP_IP = "192.168.1.10"
TCP_PORT = 7

def do(inputfile):
    # Opening file and sending
    datafile = open(inputfile, 'r')
    opensock = open_tcp(TCP_IP,TCP_PORT)
    print "\n"
    print "*_*_*_*_*_*_*_*_*_*_*"
    print "Resetting BCID"

    # reset on
    artPgWrite.send_data(opensock,"01","00000002")
    time.sleep(0.1)
    # reset off
    artPgWrite.send_data(opensock,"01","00000003")
    time.sleep(0.1)
    # reset BCID
    artPgWrite.send_data(opensock,"01","00000004")
    time.sleep(0.1)

    print "Sending ART Data"
    #sending data
    for rawline in datafile:
        line = rawline.split(" ")
        pktData = str(line[0])
        fifoAddr = str(line[1])
        print pktData, fifoAddr
        artPgWrite.send_data(opensock,addr,pkt)
        time.sleep(0.3)
    datafile.close()

    print "Starting DAQ"
    artPgWrite.send_data(opensock,"01","00000001")
    time.sleep(5)
    print "Stopping DAQ"
    artPgWrite.send_data(opensock,"01","00000011")
    time.sleep(0.1)
    print "*_*_*_*_*_*_*_*_*_*_*"
    
if __name__=="__main__":
    inputfile = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["i="])
    except getopt.GetoptError:
        print 'doPackets.py -i <inputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'artPgWrite.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            print arg
            inputfile = arg
    
    receivedata = mp.Process(target=udpRecDesp_32bit.udprec,args=())
    time.sleep(1)
    writepackets = mp.Process(target=do,args=(inputfile,))
    receivedata.start()
    writepackets.start()
    time.sleep(10)
#    receivedata.shutdown()
