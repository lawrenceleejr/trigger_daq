#!/usr/bin/python

# Writes a message to registers

# A.Wang, last edited Oct 28, 2016


import sys,socket,struct


def main(argv):
    address = ''
    message = ''
    try:
        opts, args = getopt.getopt(argv, "ha:m:", ["addr=", "m="])
    except getopt.GetoptError:
        print 'regWrite.py -a <addr> -m <msg>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'regWrite.py -a <addr> -m <msg>'
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-msg", "--message"):
            message = arg


    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    TCP_IP = '192.168.2.10'
    TCP_PORT = 7
    sock.connect((TCP_IP,TCP_PORT))

    msg1 = "abcd1234"
    msg2 = "FE170002"
#    msg3 = "00000005"
#    msg4 = "00000003"
    msg = [socket.htonl(int(msg1,16)),socket.htonl(int(msg2,16)),socket.htonl(int(address,16)),socket.htonl(int(message,16))]
    msg = struct.pack("<4I",*msg)
    print repr(msg)
    sock.sendall(msg)
    sock.close()

if __name__ == "__main__":
    main(sys.argv[1:])
