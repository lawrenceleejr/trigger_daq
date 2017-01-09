#!/usr/bin/python 

# Adapted from artPgWrite.m
# Writes 32 bit words and writes them to the TP FIFOs

# Input data format: Column 1: 32 bit data word Column 2: FIFO reg address (2 hex digits)

# A.Wang, last edited Jan 9, 2017

# Not yet tested

import sys,socket,struct,getopt,time

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
    opensock = open_tcp(TCP_IP,TCP_PORT)
    for rawline in datafile:
        line = rawline.split(" ")
        pktData = str(line[0])
        fifoAddr = str(line[1])
        print pktData, fifoAddr
        send_data(opensock,addr,pkt)
        time.sleep(0.3)

def open_tcp(ip,port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip,port))
    return sock

def send_data(sock,addr,pkt):
    header = "abcd1234"
    type = "FE170002"
    addr = "000000"+addr
    msg = [socket.htonl(int(msg1,16)),socket.htonl(int(msg2,16)),socket.htonl(int(addr,16)),socket.htonl(int(pkt,16))]
    msg = struct.pack("<4I",*msg)
    sock.sendall(msg)
    sock.close()

if __name__ == "__main__":
    main(sys.argv[1:])
