#!/usr/bin/python

# Writes a message to registers

# A.Wang, last edited Dec 2, 2016


import sys,socket,struct,getopt

#turn on receiver
#address is 32 bit  0005
# l two sig bits: 3 (or 1) should enable

def main(argv):
    address = ''
    message = ''
    try:
        opts, args = getopt.getopt(argv, "ha:m:", ["addr", "m"])
    except getopt.GetoptError:
        print 'regWrite.py -a <addr> -m <msg>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'regWrite.py -a <addr> -m <msg>'
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-m", "--message"):
            message = arg

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    TCP_IP = '192.168.2.10'
    print "Writing to ", TCP_IP
    TCP_PORT = 7
    sock.connect((TCP_IP,TCP_PORT))

    msg1 = "abcd1234"
    msg2 = "FE170002"
    msg3 = "00000005" #turn on UDP output
    msg4 = "00000003"
    # msg3 = "00000004" #reset
    # msg4 = "0000020D" #20D (global), A0C (re), 60C (tr)
    # msg4 = "0000020C" #bit 10 and bit 11 (transmit/re)
    # msg = [socket.htonl(int(msg1,16)),socket.htonl(int(msg2,16)),socket.htonl(int(address,16)),socket.htonl(int(message,16))]
    msg = [socket.htonl(int(msg1,16)),
            socket.htonl(int(msg2,16)),
            socket.htonl(int(msg3,16)),
            socket.htonl(int(msg4,16))]
    msg = struct.pack("<4I",*msg)
    print repr(msg)
    sock.sendall(msg)
    sock.close()

if __name__ == "__main__":
    main(sys.argv[1:])
# 