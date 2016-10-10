# udp receiving, python version
# A. Wang, Oct 2016
# adapted from MMFE8 Readout UDP class

import socket

class udp_fun:

    def __init__(self):
        self.UDP_IP = "192.168.0.10"
        self.UDP_PORT = 6008
        return

    def set_udp_ip(self,NEW_UDP_IP):
        self.UDP_IP = NEW_UDP_IP
        print "New IP set: " + str(self.UDP_IP)

    def set_udp_port(self,NEW_UDP_PORT):
        self.UDP_PORT = NEW_UDP_PORT
        print "New port set: " + str(self.UDP_PORT)

    def udp_client(self,max_pkt_len, buffer_size):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.UDP_IP, self.UDP_PORT))
        data, addr = sock.recvfrom(4096)
        return data, addr
