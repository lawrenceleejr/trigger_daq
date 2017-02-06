#!/usr/bin/python

# Writes a message to registers

# A.Wang, last edited Feb 6, 2016
# L.Lee edited Jan 12, 2016

import sys,socket,struct,getopt

def main(argv):
    """User interface for writing to registers"""

    address = ''
    message = ''
    resetGBT = False
    udpOutput = False
    fifoInOn = False
    fifoInOff = False

    ip,port = '192.168.2.10','7'

    try:
        opts, args = getopt.getopt(argv, "hi:p:a:m:rue", ["ip=","port=","address=", "message=",\
                                                          "resetGBT","udoOutput","fe=","fifoInEna="])
    except getopt.GetoptError:
        print 'regWrite.py -a <addr> -m <msg>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'regWrite.py -a <addr> -m <msg>'
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-m", "--message"):
            message = arg
        elif opt in ("-r", "--resetGBT"):
            resetGBT = True
        elif opt in ("-u", "--udpOutput"):
            udpOutput = True
        elif opt in ("-e","--fe", "--fifoInEna"):
            if (int(arg) == 1):
                fifoInOn = True
            else:
                fifoInOff = True

    if resetGBT:
        print "called with opt -r: Resetting GBT transceiver!"
        writeToRegister(ip, port, "00000004", "0000020D")  #20D (global), A0C (re), 60C (tr)
        writeToRegister(ip, port, "00000004", "0000020C")  #bit 10 and bit 11 (transmit/re)
    if udpOutput:
        print "called with opt -u: Turning on UDP output from FIFO 21!"
        writeToRegister(ip, port, "00000005", "00000003")
    if fifoInOn:
        print "called with opt -fe 1: Enabling input FIFOs!"
        writeToRegister(ip, port, "00000006", "FFFFFFFF")
    if fifoInOff:
        print "called with opt -fe 0: Disabling input FIFOs!"
        writeToRegister(ip, port, "00000006", "00000000")
    if address and message:
        writeToRegister(ip, port, address, message)



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
