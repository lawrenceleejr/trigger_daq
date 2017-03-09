#!/usr/bin/python

# Decoded output form for HIT packets out of the GBT decoder
# header
# strip data
# slope data 

# Order of operations:
# split data into groups of 16 bits
# subtract offsets, assuming data is ordered
# decode strip into vmm, channel using "remapping" 

# Options:
# "r" for remapping (relevant only for ART pattern generator),
# "f" for offsets (hardcoded numbers in only),
# octgeo = 1 for octuplet geometry (flipped boards)

# V1 V0
# U1 U0
# X3 X2
# X1 X0

# A.Wang, last edited Nov 21, 2016


import sys, getopt,binstr

def decode(offsetflag, remapflag, octgeo, overall_offset, offsets, remapping, hit, ip, id):
    strip = 0
    if offsetflag == 1:
        print "Added offset!"
        strip = int(hit[id*4:id*4+4],16)-int(overall_offset,16)-int(offsets[iplane],16)
    else:
        strip = int(hit[id*4:id*4+4],16)
    if strip is not 0:
#        if ((ip == 2) or (ip == 3) or (ip == 4) or (ip == 6)) and (octgeo == 1):
        # FTS
        if ((ip == 0) or (ip == 1) or (ip == 5) or (ip == 7)) and (octgeo == 1):
            strip = 512-strip-1
        if remapflag == 1:
            ivmm = remapping[strip/64]%8
        else:
            ivmm = (strip/64)%8
            ich = strip%64+1
    else:
        ivmm = 0
        ich = 0
    return ivmm, ich

def main(argv):

    # option flags
    remapflag = 0
    offsetflag = 0
    octgeo = 1
    
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:r:f:oct", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'decodeFIND_32bit.py -i <inputfile> -o <outputfile> [-r] [-f]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeFIND_32bit.py -i <inputfile> -o <outputfile> [-r] [-f]'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt == '-r':
            remapflag = 1
        elif opt == '-f':
            offsetflag = 1

    datafile = open(inputfile, 'r')
    decodedfile = open(outputfile, 'w')

    eventnum = 0
    n = 5 #starting pt of data
    lines = []
    hits = []
    strips = [] #raw strip number after offsets
    rawvmms = [] #vmm number without remapping
    vmms = [] #vmm number after remapping
    chs = [] #channel number

    remapping = [11, 10, 9, 8, 15, 14, 13, 12, 3, 2, 1, 0, 7, 6, 5, 4, 27, 26, 25, 24, 31, 30, 29, 28, 19, 18, 17, 16, 23, 22, 21, 20]
    offsets = reversed(["856","85B","84A","84F","84A","84F","856","85B"])
    overall_offset = "C00"
    nevent = 0
    for line in datafile:
        if str(line[0:4]) =='TIME':
#            nevent = nevent + 1
            timestamp = int(float(line[6:-1]))
            timestampsec = timestamp/pow(10,9)
            timestampns = timestamp%pow(10,9)
#            decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns))
            continue
        lines.append(line[:len(line)-1])
        if len(lines) == 9: # groups of 9
            nevent = nevent + 1
            decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns))
            print lines
            header = lines[0] #contains constants + BCID
            bcid = header[4:]
            for i in range(4):
                hits.append(lines[i+1])
            iplane = 0
            for hit in hits:
                for j in range(2):
                    ivmm, ich = decode(offsetflag, remapflag, octgeo, overall_offset, offsets, remapping, hit, iplane,j)
                    vmms.append(ivmm)
                    chs.append(ich)
                    iplane = iplane + 1
            decodedfile.write('\n' + str(header)\
                              + " BCID: " + str(int(bcid,16)))
            for ib in range(8):
                decodedfile.write('\n' + str(vmms[ib]) + ' ' + str(chs[ib]))
            decodedfile.write('\n')
            lines = []
            hits = []
            strips = []
            vmms = []
            chs = []
    decodedfile.close()
    datafile.close()
    print "done decoding, exiting \n"
    

if __name__ == "__main__":
    main(sys.argv[1:])
