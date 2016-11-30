#!/usr/bin/python

# Decoded output format for GBT packets
# 16 bytes for every "strobe" - 128 bits 
# data: 12 bits of BCID + 8 bits of ERR_FLAGS + 32 bits of HITLIST + 8 bits of art data parity + 8 * 6 bits of art data
# constant C,E written out somewhere

# A.Wang, last edited Nov 2, 2016


import sys, getopt,binstr
import json
import collections

def main(argv):
    remapflag = 0
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:r", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'decodeGBT_32bit.py -i <inputfile> -o <outputfile> [-r]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeGBT_32bit.py -i <inputfile> -o <outputfile> [-r]'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-r"):
            remapflag = 1

    datafile = open(inputfile, 'r')
    decodedfile = open(outputfile, 'w')

    outputData = collections.OrderedDict()

    eventnum = 0
    n = 5 #starting pt of data
    lines = []
    remapping = [11, 10, 9, 8, 15, 14, 13, 12, 3, 2, 1, 0, 7, 6, 5, 4, 27, 26, 25, 24, 31, 30, 29, 28, 19, 18, 17, 16, 23, 22, 21, 20]
    #remapping = range(32)
    for line in datafile:
        if str(line[0:4]) =='TIME':
            decodedfile.write('\n'+line)
            continue
        lines.append(line[:len(line)-1])
        if len(lines) == 4:
            strobe = ''.join(map(str,lines))
            artdata = strobe[n+15:n+27] 
            parity = strobe[n+13:n+15]
            hitmap = strobe[n+5:n+13]
            hitmap = "{0:032b}".format(int(hitmap,16))
            #print "HITMAP!: ",hitmap
            error = strobe[n+3:n+5]
            bcid = strobe[n:n+3]
            lines = []
            artdata = "{0:048b}".format(int(artdata,16))
            vmmdata = []
            vmmlist = []
            boardlist = []
            for i in range(8):
                vmmdata.append(int(artdata[i*6:i*6+6],2)+1)
            if remapflag == 1:
                for i in range(len(remapping)):
                    if (hitmap[i] is "1"):
                        boardlist.append((31-remapping[i])/8)
                        vmmlist.append((31-remapping[i])%8)
            else:
                for i in range(32):
                    if (hitmap[i] is "1"):
                        boardlist.append((31-i)/8)
                        vmmlist.append((31-i)%8)
            decodedfile.write('BCID: ' + str(int(bcid,16)) + '\thitmap: ' + hitmap + '\tBoards:')
            if len(boardlist) is 0:
                decodedfile.write(' N/A')
            for i in reversed(range(len(boardlist))):
                decodedfile.write(' ' + str(boardlist[i]))
            decodedfile.write('\tVMMs:')
            for i in reversed(range(len(vmmlist))):
                decodedfile.write(' ' + str(vmmlist[i]))
            if len(vmmlist) is 0:
                decodedfile.write(' N/A\n')
                continue
            if len(vmmlist) is 1:
                decodedfile.write('\t')
            decodedfile.write('\tCHs ' + str(vmmdata[7])\
                              + ' ' + str(vmmdata[6])\
                              + ' ' + str(vmmdata[5])\
                              + ' ' + str(vmmdata[4])\
                              + ' ' + str(vmmdata[3])\
                              + ' ' + str(vmmdata[2])\
                              + ' ' + str(vmmdata[1])\
                              + ' ' + str(vmmdata[0])\
                              + '\n')

            outputData[int(bcid,16)] = zip(boardlist[::-1], vmmlist[::-1],vmmdata[::-1])


    with open(outputfile.split(".")[0]+".json", 'w') as outputJSONFile:
        json.dump(outputData, outputJSONFile)

    decodedfile.close()
    datafile.close()
    print "done decoding, exiting \n"
    

if __name__ == "__main__":
    main(sys.argv[1:])
