#!/usr/bin/python

# Decoded output format for GBT packets
# assumes 1 full set of data per line
# 16 bytes for every "strobe" - 128 bits 
# data: 12 bits of BCID + 8 bits of ERR_FLAGS + 32 bits of HITLIST + 8 bits of art data parity + 8 * 6 bits of art data
# constant C,E written out somewhere

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
    remapping = [11, 10, 9, 8, 15, 14, 13, 12, 3, 2, 1, 0, 7, 6, 5, 4, 27, 26, 25, 24, 31, 30, 29, 28, 19, 18, 17, 16, 23, 22, 21, 20]
    for line in datafile:
        #need to get rid of 20 bits some how, currently need 112/128
        strobe = line[:len(line)-1]
        artdata = strobe[n+15:n+27]
        artdata = "{0:048b}".format(int(artdata,16))
        parity = strobe[n+13:n+15]
        hitmap = strobe[n+5:n+13]
        hitmap = "{0:032b}".format(int(hitmap,16))
        print "HITMAP!: ",hitmap
        error = strobe[n+3:n+5]
        bcid = strobe[n:n+3]
        vmmdata = []
        for i in range(8):
            print i
            vmmdata.append(int(artdata[i*6:i*6+6],2))
        for i in range(len(remapping)):
            print "VMM" + str(31-remapping[i]) + " " +hitmap[i],
            print " "
        decodedfile.write('bcid: ' + str(int(bcid,16)) + ' hitmap: ' + hitmap\
                          + ' ' + str(vmmdata[7])\
                          + ' ' + str(vmmdata[6])\
                          + ' ' + str(vmmdata[5])\
                          + ' ' + str(vmmdata[4])\
                          + ' ' + str(vmmdata[3])\
                          + ' ' + str(vmmdata[2])\
                          + ' ' + str(vmmdata[1])\
                          + ' ' + str(vmmdata[0])\
                          + '\n')
    decodedfile.close()
    datafile.close()
    print "done decoding, exiting \n"
    

if __name__ == "__main__":
    main(sys.argv[1:])
