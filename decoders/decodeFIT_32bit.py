#!/usr/bin/python
# -*- coding: utf-8 -*-

# Decoded output form for FIT packets out of the GBT decoder
# currently header
# strip data
# calculated slopes and stuff 

# Order of operations:
# split data into groups of 16 bits
# subtract offsets, assuming data is ordered

# Options:
# "f" for offsets (hardcoded numbers in only),
# octgeo = 1 for octuplet geometry (flipped boards)

# V1 V0
# U1 U0
# X3 X2
# X1 X0

# A.Wang, last edited Nov 21, 2016


import sys, getopt,binstr, time, visual, commonTrig

def decode(offsetflag, octgeo, overall_offset, offsets, hit, ip, id, flippedboards):
    strip = 0
    if offsetflag == 1:
        if (int(hit[id*4:id*4+4],16) != 0):
            strip = int(hit[id*4:id*4+4],16)-int(overall_offset,16)-int(offsets[ip],16)
    else:
        strip = int(hit[id*4:id*4+4],16)
    if strip is not 0:
#        if ((ip == 2) or (ip == 3) or (ip == 4) or (ip == 6)) and (octgeo == 1):
        # FTS
        if ip in flippedboards and (octgeo == 1):
#        if ((ip == 0) or (ip == 1) or (ip == 5) or (ip == 7)) and (octgeo == 1):
            strip = 512-strip-1
        ivmm = (strip/64)%8
        ich = strip%64+1
    else:
        ivmm = 0
        ich = 0
    return ivmm, ich

def main(argv):

    # option flags
    offsetflag = 0
    octgeo = 1
    fulldata = 0 #prints crap like roi, dtheta, etc
    
    inputfile = ''
    outputfile = ''
    colors = visual.bcolors()
    consts = commonTrig.tconsts()

    try:
        opts, args = getopt.getopt(argv, "hi:o:rf", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'decodeFIT_32bit.py -i <inputfile> -o <outputfile> [-f]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeFIT_32bit.py -i <inputfile> -o <outputfile> [-f]'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt == '-f':
            offsetflag = 1

    if (offsetflag):
        print "Adding offsets!"
    else:
        print colors.WARNING + "No offsets!" + colors.ENDC
    
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

    offsets = ["3A","3A","47","47","40","40","40","40"]
    overall_offset = "000"
    nevent = 0
    print "\n"
    print colors.DARK + "Decoding!       " + "ψ ︿_____︿_ψ_ ☾\t "+ colors.ENDC
    print "\n"
    for line in datafile:
        if str(line[0:4]) == 'TIME' :
            timestamp = int(float(line[6:-1]))
            timestampsec = timestamp/pow(10,9)
            timestampns = timestamp%pow(10,9)
            continue
        if ((len(lines) == 0) and (line[0:2] != "A3")):
            print "\n"
            print colors.WARNING + "We can't find the header and we expect it!" + colors.ENDC
            print "\n"
            sys.exit()
        lines.append(line[:len(line)-1])
        
        if len(lines) == 13: # groups of 13
            nevent = nevent + 1
            if (nevent % (num_lines/(10*13)) == 0):
                visual.update_progress(float(nevent)/num_lines*13.)
#                sys.stdout.write("#")
#                sys.stdout.flush()
            decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns))
            header = lines[0] #contains constants + BCID
            bcid = header[4:]
            for i in range(4):
                hits.append(lines[i+1])
            iplane = 0
            for hit in hits:
                for j in range(2):
                    ivmm, ich = decode(offsetflag, octgeo, consts.OVERALLOFFSET, consts.OFFSETS, hit, iplane,j, consts.FLIPPEDBOARDS)
                    vmms.append(ivmm)
                    chs.append(ich)
                    iplane = iplane + 1

            # trigger calcs
            roi = lines[9][0:4]
            roi_dec = int(lines[9][0:4],16)
            dtheta = lines[9][4:]
            dtheta_dec = int(lines[9][4:],16)
            mx_roi = lines[10][0:4]
            mx_roi_dec = int(lines[10][0:4],16)
            mx_local = lines[10][4:]
            mx_local_dec = int(mx_local,16)
#            mx_local_dec = (mx_local_dec & 0x7FFF) - (mx_local_dec & 0x8000)
            if (mx_local_dec > 0x7fff):
                mx_local_dec -= 0x10000
            mv_global = lines[11][0:4]
            mv_global_dec = int(lines[11][0:4],16)
            mu_global = lines[11][4:]
            mu_global_dec = int(lines[11][4:],16)
            mx_global = lines[12][0:4]
            mx_global_dec = int(lines[12][0:4],16)
            counter = int(lines[12][4:],16)

            decodedfile.write('\n' + str(header) + " BCID: " + str(int(bcid,16)))
            for ib in range(8):
                decodedfile.write('\n' + str(vmms[ib]) + ' ' + str(chs[ib]))
            decodedfile.write('\n' + 'mx_local ' + str(mx_local) + ' ' + str(mx_local_dec/pow(2,14.)))
            if (fulldata):
                decodedfile.write('\n' + 'roi ' + str(roi_dec) )
                decodedfile.write('\n' + 'dtheta ' + str(dtheta_dec/pow(2,30)) )
                decodedfile.write('\n' + 'mx_roi ' + str(mx_roi_dec/pow(2,16)) )
                decodedfile.write('\n' + 'mv_global ' + str(mv_global_dec/pow(2,16)) )
                decodedfile.write('\n' + 'mu_global ' + str(mu_global_dec/pow(2,16)) )
                decodedfile.write('\n' + 'mx_global ' + str(mx_global_dec/pow(2,16)) )
            decodedfile.write('\n' + 'cntr ' + str(counter))
            decodedfile.write('\n')
            lines = []
            hits = []
            strips = []
            vmms = []
            chs = []
    decodedfile.close()
    datafile.close()
    print "\n"
    print colors.DES + "Done decoding!  " + "ψ ︿_____︿_ψ_ ☼\t "+ colors.ENDC
    print "\n"

if __name__ == "__main__":
    main(sys.argv[1:])
