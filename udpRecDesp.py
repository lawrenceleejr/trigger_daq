import sys, signal
from udp import udp_fun

global bufsize
bufsize = 65536
global maxpkt
maxpkt = 1024
global UDP_PORT
UDP_PORT = 6008
global UDP_IP
UDP_IP = "192.168.0.10"
global timeout
timeout = 5
def main():
    try:
        udp = udp_fun()
        wordcount = 0
        print "Receiving from TP"
        print "Ctrl+C to stop!"
        udp.set_udp_port(UDP_PORT)
        udp.set_udp_ip(UDP_IP)
        while True:
            data, addr = udp.udp_client(maxpkt,bufsize)
            print "received from " + addr
            count = 1
            while (count < timeout * 1/readInterval):
                #udpPacket = data
                udpPacket = data.split()
                # this assumes we receive the data in packets of 4 bytes, or 32 bits
                header = int(udpPacket[0],16)
                #splitPacket = [udpPacket[i:i+8] for i in range(0, len(udpPacket), 8)] #groups into 8
                if not udpPacket:
                    addrnum = header[6:] # address number reading from
                    with open("mmtp_test_%d.dat"%(addrnum), "a") as myfile:
                        for i in xrange(1, len(udpPacket), 1):
                            word = int(udpPacket[i], 16)
                            wordcount = wordcount + 1
                            if (wordcount%4==0):
                                myfile.write(word + '\n')
                            else:
                                myfile.write(word)
                    myfile.close()
                    count = 1
                sleep(0.01)
                count = count + 1
    except KeyboardInterrupt:
        print "Stopped!"
                
if __name__ == "__main__":
    main()
