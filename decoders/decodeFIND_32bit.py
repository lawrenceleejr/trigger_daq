#!/usr/bin/python

# Decoded output form for FIND packets out of the trigger processor
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


import sys, getopt,binstr,visual

def decode(offsetflag, remapflag, octgeo, overall_offset, offsets, remapping, hit, ip, id):
    strip = 0
    if offsetflag == 1:
        print "Added offset!"
        if (int(hit[id*4:id*4+4],16) != 0) and sum([int(x,16) for x in offsets])!= 0:
            strip = int(hit[id*4:id*4+4],16)-int(overall_offset,16)-int(offsets[ip],16)
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
        opts, args = getopt.getopt(argv, "hi:o:rf", ["ifile=", "ofile="])
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

    colors = visual.bcolors()
    num_lines = sum(1 for line in open(inputfile))
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
    offsets = ["3A","3A","47","47","40","40","40","40"]
#    offsets = ["40","40","47","3A","47","3A","40","40"][::-1]
#    offsets = reversed(["856","85B","84A","84F","84A","84F","856","85B"])
    overall_offset = "000"
    nevent = 0
    for line in datafile:
        if str(line[0:4]) =='TIME':
            timestamp = int(float(line[6:-1]))
            timestampsec = timestamp/pow(10,9)
            timestampns = timestamp%pow(10,9)
            continue
        if ((len(lines) == 0) and (line[0:2] != "A2")):
            print "\n"
            print colors.WARNING + "We can't find the header and we expect it!" + colors.ENDC
            print "\n"
            sys.exit()
        lines.append(line[:len(line)-1])
        if len(lines) == 9: # groups of 9
            nevent = nevent + 1
            if (nevent % (num_lines/(10*9)) == 0):
                visual.update_progress(float(nevent)/num_lines*9.)
            decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns))
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
    print "\n"
    print colors.ANNFAV + "\t\t\t\t\t\t\t\t\t " + colors.ENDC
    print colors.ANNFAV + "\tDone decoding, exiting! \t\t\t\t\t "+ colors.ENDC
    print colors.ANNFAV + "\t\t\t\t\t\t\t\t\t " + colors.ENDC
    

if __name__ == "__main__":
    main(sys.argv[1:])
