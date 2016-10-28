import sys, signal, struct, time
from udp import udp_fun

global bufsize
#bufsize = 65536
bufsize = 1000000
global maxpkt
maxpkt = 1024*4
global UDP_PORT
UDP_PORT = 6008
global UDP_IP
UDP_IP = ""
global timeout
timeout = 5
global readInterval
readInterval = 1
def main():
    try:
        udp = udp_fun()
        wordcount = 0
        print "Receiving from TP"
        print "Doesn't delete old file!"
        print "Ctrl+C to stop!"
        udp.set_udp_port(UDP_PORT)
        udp.set_udp_ip(UDP_IP)
        rawsock = udp.udp_client(maxpkt,bufsize)
        while True:
            data, addr = udp.udp_recv(rawsock)
#            print "received from ", addr
            count = 1
#            print data
            udpPacket = [data]
            # this assumes we receive the data in packets of 4 bytes, or 32 bits
            datalist = [format(int(hex(ord(c)), 16), '02X') for c in list(udpPacket[0])]
            if len(udpPacket)>0:
                addrnum = datalist[7] # address number reading from
#                    print "addr", int(addrnum)
                del datalist[:8]
#                    print datalist
                wordcount = 0
                header = [0,0,0,0] #20,21,22,23
                with open("mmtp_test_%d.dat"%(int(addrnum)), "a") as myfile:
                    wordout = ''
                    for byte in datalist:
                        if byte == 'A2':
                            header[3] = 1
                        wordcount = wordcount + 1
#                        timecnt[int(addrnum)-20] = timecnt[int(addrnum)-20] + 1
                        wordout = wordout + byte
                        if wordcount == 4:
                            #                                print "WORDOUT", wordout
#                                myfile.write(str(wordout) + '\n')
                            timestamp = time.time()*pow(10,9)
                            # if timecnt[int(addrnum)-20] == 36 and int(addrnum) != 21:
                            #     myfile.write('%f'%timestamp + '\n')
                            #     timecnt[int(addrnum)-20] = 0
                            # if timecnt[int(addrnum)-20] == 16 and int(addrnum) == 21:
                            #     myfile.write('%f'%timestamp + '\n')
                            #     timecnt[int(addrnum)-20] = 0
                            if header[3] == 1:
                                myfile.write('TIME: ' + '%f'%timestamp + '\n')
                                header[3] = 0
                            myfile.write(str(wordout) + '\n')
                            wordout = ''
                            wordcount = 0
                myfile.close()
                count = 1
                time.sleep(0.01)
                count = count + 1
    except KeyboardInterrupt:
        print "Stopped!"
        rawsock.close()
                
if __name__ == "__main__":
    main()
