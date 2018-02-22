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

# A.Wang, last edited Jan 16, 2018


import sys, getopt,binstr, time, visual, commonTrig

nevent = 0

def decode(offsetflag, octgeo, overall_offset, offsets, hit, ip, id, flippedboards, occ):
    strip = 0
    mybin = "{0:010b}".format(int(hit[id*4:id*4+4],16))
    margin = mybin[0]
    if offsetflag == 1:
        if (int(mybin[1:],2) != 0):
            strip = int(mybin[1:],2)-int(overall_offset,16)-int(offsets[ip],16)
    else:
        strip = int(mybin[1:],2)
    if int(margin,2) > 0:
        #print "MARGIN!"
        strip = strip + 8
    if int(occ[ip])==1:
        if ip in flippedboards and (octgeo == 1):
            strip = 512-strip-1
        ivmm = (strip/64)%8
        ich = strip%64+1
    else:
        if strip is not 0 and int(occ[ip])==0:
            print "Occupancy header is 0 but strip isn't!"
            print "Event",nevent
            print hit,"on plane", ip
        ivmm = 0
        ich = 0
    #if int(margin,2) > 0 and int(occ[ip])!=0:
    #    ivmm += 8

    return ivmm, ich

def main(argv):

    # option flags
    offsetflag = 0
    octgeo = 1
    fulldata = 0 #prints crap like roi, dtheta, etc
    stripflag = 0
    slopeflag = 0
    
    inputfile = ''
    outputfile = ''
    run = -1
    colors = visual.bcolors()
    consts = commonTrig.tconsts()
    start_time = time.time()

    try:
        opts, args = getopt.getopt(argv, "hi:o:r:f", ["ifile=", "ofile=", "run=", 'st', 'sl'])
    except getopt.GetoptError:
        print 'decodeFIT_uvr.py -i <inputfile> -o <outputfile> -r <run> [-f] [--sl] [--st]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeFIT_uvr.py -i <inputfile> -o <outputfile> -r <run> [-f] [--sl] [--st]'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-r", "--run"):
            run = int(arg)
        elif opt == '-f':
            offsetflag = 1
        elif opt == "--sl":
            slopeflag = 1
        elif opt == "--st":
            stripflag = 1

    if not (slopeflag or stripflag):
        print "Please provide --st and/or --sl to decode strips and/or slopes, respectively."
        sys.exit(2)

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

    n = 5 #starting pt of data
    lines = []
    hits = []
    slopes = [] #raw strip number after offsets
    vmms = [] #vmm number
    chs = [] #channel number
    svmms = []
    schs = []
    
    print "\n"
    print colors.DARK + "Decoding!       " + "ψ ︿_____︿_ψ_ ☾\t "+ colors.ENDC
    print "\n"
    for iline,line in enumerate(datafile):

        if iline % 50000 == 0 and iline > 0:
            visual.pbftp(time.time() - start_time, iline, num_lines)

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
            global nevent
            nevent = nevent + 1
            decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns))
            header = lines[0] #contains constants + BCID
            occ = list(format(int(header[2:4],16),"08b"))
            bcid = header[4:]
            for i in range(4):
                hits.append(lines[i+1])
            iplane = 0
            if (stripflag):
                for hit in hits:
                    for j in range(2):
                        if (run > 3521):
                            ivmm, ich = decode(offsetflag, octgeo, consts.OVERALLOFFSET, consts.OFFSETS, hit, iplane, j, consts.FLIPPEDBOARDS, occ)
                        else:
                            ivmm, ich = decode(offsetflag, octgeo, consts.OVERALLOFFSET, consts.OLDOFFSETS, hit, iplane, j, consts.FLIPPEDBOARDS, occ)
                        vmms.append(ivmm)
                        chs.append(ich)
                        iplane = iplane + 1
            if (slopeflag):
                for i in range(4,8):
                    slopes.append(lines[i+1])
                iplane = 0
                for slope in slopes:
                    for j in range(2):
                        if (run > 3521):
                            ivmm, ich = decode(offsetflag, octgeo, consts.OVERALLOFFSET, consts.OFFSETS, slope, iplane, j, consts.FLIPPEDBOARDS, occ)
                        else:
                            ivmm, ich = decode(offsetflag, octgeo, consts.OVERALLOFFSET, consts.OLDOFFSETS, slope, iplane, j, consts.FLIPPEDBOARDS, occ)
                        svmms.append(ivmm)
                        schs.append(ich)
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
                decodedfile.write('\n')
                if (stripflag):
                    if (vmms[ib] > 7 and chs[ib] != 0):
                        decodedfile.write(str(vmms[ib]-8) + ' ' + str(chs[ib]) + ' 1')
                    else:
                        decodedfile.write(str(vmms[ib]) + ' ' + str(chs[ib]))
                if slopeflag and stripflag:
                    decodedfile.write(' ')
                if (slopeflag):
                    if (svmms[ib] > 7 and schs[ib] != 0):
                        decodedfile.write(str(svmms[ib]-8) + ' ' + str(schs[ib]) + ' 1')
                    else:
                        decodedfile.write(str(svmms[ib]) + ' ' + str(schs[ib]))
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
            slopes = []
            vmms = []
            chs = []
            svmms = []
            schs = []
    decodedfile.close()
    datafile.close()
    print "\n"
    print colors.DES + "Done decoding!  " + "ψ ︿_____︿_ψ_ ☼\t "+ colors.ENDC
    print "\n"

if __name__ == "__main__":
    main(sys.argv[1:])
