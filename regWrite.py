#!/usr/bin/python

# Writes a message to registers

# A.Wang, last edited Mar 13, 2017
# L.Lee edited Jan 12, 2017

import sys,socket,struct,getopt,os,itertools

def main(argv):
    """User interface for writing to registers"""

    address = []
    message = []
    resetGBT = False
    gbtInput = False
    fifoOff = False
    fifoOn = False
    fifos = ""
    jtag = False

    ip,port = '192.168.2.10','7'

    try:
        opts, args = getopt.getopt(argv, "hi:p:a:m:rue:", ["ip=","port=","address=", "message=",\
                                                          "resetGBT","gbtInput","fe=","fifoOutEna=",\
                                                          "df=",\
                                                          "jtag"])
    except getopt.GetoptError:
        print 'regWrite.py -a <addr> -m <msg> [--jtag]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Usage: regWrite.py -a <addr> -m <msg> [--jtag]'
            print 'Options: '
            print '-a            specifies address to send to'
            print '-m            specifies message sent'
            print '-i            specifies IP'
            print '-p            specifies port'
            print '-r            resets GBT transciever'
            print '-u            enables gbt input to FIFOs'
            print '-e <0 or 1>   enables all or no FIFO outputs'
            print '--df "1111"   enables select FIFO outputs, specified by 4 bits'
            sys.exit()
        elif opt in ("--jtag"):
            jtag = True
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-a", "--address"):
            address.append(arg)
        elif opt in ("-m", "--message"):
            message.append(arg)
        elif opt in ("-r", "--resetGBT"):
            resetGBT = True
        elif opt in ("-u", "--gbtInput"):
            gbtInput = True
        elif opt in ("-e","--fe", "--fifoOutEna"):
            if (int(arg) == 1):
                fifoOn = True
            else:
                fifoOff = True
        elif opt in ("--df"):
            if (len(arg))==4:
                fifos = arg
            else:
                print "Invalid argument for --df!"
                sys.exit()

    if resetGBT:
        print "called with opt -r: Resetting GBT transceiver!"
        address.append("00000004")
        message.append("0000020D") #20D (global), A0C (re), 60C (tr)
        address.append("00000004")
        message.append("0000020C") #bit 10 and bit 11 (transmit/re)
    if gbtInput:
        print "called with opt -u: Turning on GBT input!"
        address.append("00000005")
        message.append("00000003")
    if fifoOn:
        print "called with opt --fe 1: Enabling all output FIFOs!"
        address.append("00000006")
        message.append("FFFFFFFF")
    if fifoOff:
        print "called with opt --fe 0: Disabling all output FIFOs!"
        address.append("00000006")
        message.append("00000000")
    if len(fifos) > 0:
        print "called with opt --df, enabling the following FIFOs:"
        for ind,elem in enumerate(list(fifos)[::-1]):
            if (int(elem)==1):
                print "fifo 2"+str(ind)
        address.append("00000006")
        message.append("FFFFFFF"+"{0:1X}".format((int(fifos,2))))
    if (jtag is False):
        for (a,m) in itertools.izip(address,message):
            print (a,m)
            writeToRegister(ip, port, a, m)
    else:
        for (a,m) in itertools.izip(address,message):
#            os.system("ls")
            os.system("vivado -mode batch -source tcl_scripts/regWrite.tcl -tclargs " + str(a) + " " + str(m))

        


def writeToRegister(ip,port,address,message):
    """Little function that actually takes care of the transmission"""

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print "Writing to %s:%s"%(ip,port)
    print "\t %s %s"%(address, message)
    sock.connect((ip,int(port) )  )
    msg1 = "abcd1234"
    msg2 = "FE170002"
    msg = [socket.htonl(int(msg1,16)),
            socket.htonl(int(msg2,16)),
            socket.htonl(int(address,16)),
            socket.htonl(int(message,16))]
    print repr(msg)
    msg = struct.pack("<4I",*msg)
    print repr(msg)
    sock.sendall(msg)
    sock.close()

if __name__ == "__main__":
    main(sys.argv[1:])
# 
