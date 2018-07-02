#!/usr/bin/python

# Decoded output form for HIT packets out of the GBT decoder
# header
# strip data
# slope data 

# Order of operations:
# split data into groups of 16 bits
# subtract offsets, assuming data is ordered
# decode strip into vmm, channel 

# Options:
# "r" for run number,
# "f" for offsets (hardcoded numbers in only),
# currently octgeo = 1, for octuplet geometry (flipped boards)


# Written out as:
# X3 X2
# V1 U1
# V0 U0
# X1 X0

# A.Wang, last edited Nov 21, 2016


import sys, getopt, binstr, visual, commonTrig

def decode(offsetflag, octgeo, overall_offset, offsets, hit, ip, id, occ):
    strip = 0
    if offsetflag == 1:
        if (int(hit[id*4:id*4+4],16) != 0):
            strip = int(hit[id*4:id*4+4],16)-int(overall_offset,16)-int(offsets[ip],16)
    else:
        strip = int(hit[id*4:id*4+4],16)
    if int(occ[ip])==1:
        #if ((ip == 1) or (ip == 2) or (ip == 4) or (ip == 7)) and (octgeo == 1):
        #    strip = 512-strip-1
        ivmm = (strip/64)%8
        ich = strip%64
    else:
        ivmm = 0
        ich = 0
    return ivmm, ich

def main(argv):

    # option flags
    offsetflag = 0
    octgeo = 1
    
    inputfile = ''
    outputfile = ''
    run = -1
    colors = visual.bcolors()
    consts = commonTrig.tconsts()

    try:
        opts, args = getopt.getopt(argv, "hi:o:r:f", ["ifile=", "ofile=", "run="])
    except getopt.GetoptError:
        print 'decodeHIT_32bit.py -i <inputfile> -o <outputfile> -r <run> [-f]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeHIT_32bit.py -i <inputfile> -o <outputfile> -r <run> [-f]'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ('-r', "--run"):
            run = int(arg)
        elif opt == '-f':
            offsetflag = 1
            
    if (offsetflag):
        print "Adding offsets!"
    else:
        print colors.WARNING + "No offsets!" + colors.ENDC
        
    if (run==-1):
        print colors.FAIL + "No run number!" + colors.ENDC
        sys.exit(2)
    if (run < 3522):
        print colors.WARNING + "Using flipped offsets!" + colors.ENDC
        
    num_lines = sum(1 for line in open(inputfile))
    datafile = open(inputfile, 'r')
    decodedfile = open(outputfile, 'w')

    nevent = 0
    n = 5 #starting pt of data
    lines = []
    hits = []
    strips = [] #raw strip number after offsets
    vmms = [] #vmm number after remapping
    chs = [] #channel number

#    offsets = ["40","40","47","3A","47","3A","40","40"][::-1]
#    overall_offset = "000"

    for line in datafile:
        if str(line[0:4]) =='TIME':
            timestamp = int(float(line[6:-1]))
            timestampsec = timestamp/pow(10,9)
            timestampns = timestamp%pow(10,9)
            continue
        if ((len(lines) == 0) and (line[0:2] != "A1")):
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
            occ = list(format(int(header[2:4],16),"08b"))
            bcid = header[4:]
            for i in range(4):
                hits.append(lines[i+1])
            iplane = 0
            for hit in hits:
                for j in range(2):
                    if (run > 3521):
                        ivmm, ich = decode(offsetflag, octgeo, consts.OVERALLOFFSET, consts.HITOFFSETS, hit, iplane, j, occ)
                    else:
                        ivmm, ich = decode(offsetflag, octgeo, consts.OVERALLOFFSET, consts.OLDHITOFFSETS, hit, iplane, j, occ)
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
