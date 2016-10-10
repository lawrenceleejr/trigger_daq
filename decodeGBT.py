#!/usr/bin/python

# Decoded output format for GBT packets
# 16 bytes for every "strobe" - 128 bits 
# 0b1010 + 12 bits of BCID + 8 bits of ERR_FLAGS + 32 bits of HITLIST + 8 bits of art data parity + 8 * 6 bits of art data

# A.Wang, last edited Oct 6, 2016


import sys, getopt,binstr


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'decodeGBT.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeGBT.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    datafile = open(inputfile, 'r')
    decodedfile = open(outputfile, 'w')

    eventnum = 0
    n = 3 #starting pt of data
    for line in datafile:
        #need to get rid of 16 bits some how, currently need 112/128
        strobe = ''.join(map(str,line))
        strobe = strobe[::-1] #reverse strobe
        artdata = strobe[n+15:n+27] 
        parity = strobe[n+13:n+15]
        hitmap = strobe[n+5:n+13]
        error = strobe[n+3:n+5]
        bcid = strobe[n:n+3]
        lines = []
        artdata = bin(int(artdata,16))[2:] 
        vmmdata = []
        for (i in range(8)):
            vmmdata.append(artdata[i*6:i+6])
        decodedfile.write('\n')
    decodedfile.close()
    datafile.close()
    print "done decoding, exiting \n"
    

if __name__ == "__main__":
    main(sys.argv[1:])
