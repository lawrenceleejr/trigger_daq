#!/usr/bin/python

# Writes + reads a message to registers

# A.Wang, last edited Dec 2, 2016


import sys,socket,struct,getopt


def read(address):

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    TCP_IP = '192.168.2.10'
    print "Writing/Reading to ", TCP_IP
    TCP_PORT = 7
    BUFFER_SIZE = 1024
    
    sock.connect((TCP_IP,TCP_PORT))

    msg1 = "abcd1234"
    msg2 = "FE170001"
    msg = [socket.htonl(int(msg1,16)),socket.htonl(int(msg2,16)),socket.htonl(int(address,16))]
    msg = struct.pack("<3I",*msg)
    print repr(msg)
    sock.sendall(msg)

    sock.listen(1)
    #conn,addr = s.accept()
    data, addr = sock.recvfrom(4096*4)
    print "received from: ", addr
    tcpPacket = [data]
    datalist = [format(int(hex(ord(c)), 16), '02X') for c in list(tcpPacket[0])]
    datahex = datalist[3:]
    print "DATA: ",datahex
    sock.close()
    return datahex

def write(address,message):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    TCP_IP = '192.168.2.10'
    print "Writing to ", TCP_IP
    TCP_PORT = 7
    sock.connect((TCP_IP,TCP_PORT))
    
    msg1 = "abcd1234"
    msg2 = "FE170002"
    #msg3 = "00000005"
    #msg4 = "00000003"
    msg = [socket.htonl(int(msg1,16)),socket.htonl(int(msg2,16)),socket.htonl(int(address,16)),socket.htonl(int(message,16))]
    msg = struct.pack("<4I",*msg)
    print repr(msg)
    sock.sendall(msg)
    sock.close()


# if __name__ == "__main__":
#     main(sys.argv[1:])
