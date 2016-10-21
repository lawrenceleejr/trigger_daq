import sys, signal, struct, time
from udp import udp_fun

global bufsize
bufsize = 65536
global maxpkt
maxpkt = 1024
global UDP_PORT
UDP_PORT = 6008
global UDP_IP
UDP_IP = ""
global timeout
timeout = 5
global readInterval
readInterval = 0.01
def main():
    try:
        udp = udp_fun()
        wordcount = 0
        print "Receiving from TP"
        print "Doesn't delete old file!"
        print "Ctrl+C to stop!"
        udp.set_udp_port(UDP_PORT)
        udp.set_udp_ip(UDP_IP)
        while True:
            data, addr = udp.udp_client(maxpkt,bufsize)
#            print "received from ", addr
            count = 1
            while (count < timeout * 1/readInterval):
                #udpPacket = data
                udpPacket = [data]
#                print udpPacket
                # this assumes we receive the data in packets of 4 bytes, or 32 bits
                datalist = [format(int(hex(ord(c)), 16), '02X') for c in list(udpPacket[0])]
#                print datalist
                if len(udpPacket)>0:
                    addrnum = datalist[7] # address number reading from
#                    print "addr", int(addrnum)
                    del datalist[:9]
#                    print datalist
                    wordcount = 0
                    with open("mmtp_test_%d.dat"%(int(addrnum)), "a") as myfile:
                        wordout = ''
                        for byte in datalist:
                            wordcount = wordcount + 1
                            wordout = wordout + byte
                            if wordcount == 16:
#                                print "WORDOUT", wordout
                                timestamp = time.time()*pow(10,9)
                                myfile.write('%f'%timestamp + '\n')
                                myfile.write(str(wordout) + '\n')
                                wordout = ''
                                wordcount = 0
                    myfile.close()
                    count = 1
                time.sleep(0.01)
                count = count + 1
    except KeyboardInterrupt:
        print "Stopped!"
                
if __name__ == "__main__":
    main()
