
#!/usr/bin/python

# Adapted from doPackets.m
# takes artPgWrite.py and writes a pcket, and then looks at the data

# A.Wang, last edited Jan 16, 2017

# Not yet tested

import sys,artPgWrite,udpRecDesp_32bit,getopt,time,regWrite
import multiprocessing as mp

TCP_IP = "192.168.2.10"
TCP_PORT = 7

def main(argv):
    inputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:", ["i="])
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
    
    receivedata = mp.Process(target=udpRecDesp_32bit.udp_rec,args=())
    time.sleep(1)
    writepackets = mp.Process(target=do,args=(inputfile,))
    #receivedata.start()
    #writepackets.start()
    do(inputfile)
    time.sleep(10)
#    receivedata.shutdown()

def reset_bcid():
    # reset on
    regWrite.writeToRegister(TCP_IP,TCP_PORT,"00000001","00000002")
    time.sleep(1)
    # reset off
    regWrite.writeToRegister(TCP_IP,TCP_PORT,"00000001","00000003")
    time.sleep(0.1)
    # reset BCID
    regWrite.writeToRegister(TCP_IP,TCP_PORT,"00000001","00000004")
    time.sleep(0.1)

def do(inputfile):
    # Opening file and sending
    datafile = open(inputfile, 'r')
    print "\n"
    print "*_*_*_*_*_*_*_*_*_*_*"
    print "Resetting BCID"

    reset_bcid()

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

    print "Starting DAQ"
    regWrite.writeToRegister(TCP_IP,TCP_PORT,"00000001","00000001")
    time.sleep(5)
    print "Stopping DAQ"
    regWrite.writeToRegister(TCP_IP,TCP_PORT,"00000001","00000011")
    time.sleep(0.1)
    print "*_*_*_*_*_*_*_*_*_*_*"

if __name__=="__main__":
    main(sys.argv[1:])
