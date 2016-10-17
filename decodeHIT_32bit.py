#!/usr/bin/python

# Decoded output form for HIT packets out of the GBT decoder
# header
# strip data
# slope data 

# A.Wang, last edited Oct 17, 2016


import sys, getopt,binstr


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'decodeHIT_32bit.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeHIT_32bit.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    datafile = open(inputfile, 'r')
    decodedfile = open(outputfile, 'w')

    eventnum = 0
    n = 5 #starting pt of data
    lines = []
    hits = []
    vmms = []
    chs = []
    remapping = [11, 10, 9, 8, 15, 14, 13, 12, 3, 2, 1, 0, 7, 6, 5, 4, 27, 26, 25, 24, 31, 30, 29, 28, 19, 18, 17, 16, 23, 22, 21, 20]
    offsets = ["856","85B","84A","84F","84A","84F","856","85B"]
    overall_offset = "C00"
    for line in datafile:
        lines.append(line[:len(line)-1])
        if len(lines) == 9: # groups of 9
            print lines
#            strobe = ''.join(map(str,lines))
            header = lines[0] #contains constants + BCID
            bcid = header[4:]
            for i in range(4):
                hits.append(lines[i+1])
            iplane = 0
            for hit in hits:
                strip = int(hit[0:4],16)-int(overall_offset,16)-int(offsets[iplane],16)
                print "STRIP: ",strip
                if strip is not 0:
                    ivmm = remapping[strip/64]%8
                    print ivmm
                    ich = strip%64+1
                    print ich
                    iplane = iplane + 1
                    vmms.append(ivmm)
                    chs.append(ich)
                else:
                    iplane = iplane + 1
                    vmms.append(0)
                    chs.append(0)
                strip = int(hit[4:],16)-int(overall_offset,16)-int(offsets[iplane],16)
                print "STRIP: ",strip
                if strip is not 0:
                    ivmm = remapping[strip/64]%8
                    ich = strip%64+1
                    iplane = iplane + 1
                    vmms.append(ivmm)
                    print ivmm
                    chs.append(ich)
                    print ich
                else:
                    iplane = iplane + 1
                    vmms.append(0)
                    chs.append(0)
            decodedfile.write('bcid: ' + str(int(bcid,16))
                              + ' ' + str(vmms[0]) + ' ' + str(chs[0])\
                              + ' ' + str(vmms[1]) + ' ' + str(chs[1])\
                              + ' ' + str(vmms[2]) + ' ' + str(chs[2])\
                              + ' ' + str(vmms[3]) + ' ' + str(chs[3])\
                              + ' ' + str(vmms[4]) + ' ' + str(chs[4])\
                              + ' ' + str(vmms[5]) + ' ' + str(chs[5])\
                              + ' ' + str(vmms[6]) + ' ' + str(chs[6])\
                              + ' ' + str(vmms[7]) + ' ' + str(chs[7])\
                              + '\n')
            lines = []
            hits = []
            vmms = []
            chs = []
#            break
    decodedfile.close()
    datafile.close()
    print "done decoding, exiting \n"
    

if __name__ == "__main__":
    main(sys.argv[1:])
