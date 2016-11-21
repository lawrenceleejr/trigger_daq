#!/usr/bin/python

# Decoded output format for GBT packets
# 16 bytes for every "strobe" - 128 bits 
# data: 12 bits of BCID + 8 bits of ERR_FLAGS + 32 bits of HITLIST + 8 bits of art data parity + 8 * 6 bits of art data
# constant C,E written out somewhere

# A.Wang, last edited Nov 2, 2016


import sys, getopt,binstr


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
            decodedfile.write( "BCID: {: >10}  Hitmap: {: >20}  Boards: ".format(int(bcid,16), hitmap ) )
            reversedBoardList = reversed(boardlist)
            reversedBoardList = [str(x) for x in reversedBoardList]
            decodedfile.write( '{: >30}'.format( " ".join( reversedBoardList ) if len(reversedBoardList) else "N/A" ) )

            decodedfile.write('  VMMs:')
            reversedVMMList = reversed(vmmlist)
            reversedVMMList = [str(x) for x in reversedVMMList]
            decodedfile.write( '{: >30}'.format( " ".join( reversedVMMList ) if len(reversedVMMList) else "N/A" ) )

            reversedVMMData = reversed(vmmdata)
            reversedVMMData = [str(x) for x in reversedVMMData]
            decodedfile.write( '  CH: {: >30}\n'.format( " ".join( reversedVMMData ) if len(reversedVMMData) else "N/A" ) )

    decodedfile.close()
    datafile.close()
    print "done decoding, exiting \n"
    

if __name__ == "__main__":
    main(sys.argv[1:])
