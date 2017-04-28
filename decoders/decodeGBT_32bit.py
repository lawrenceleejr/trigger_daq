#!/usr/bin/python

# Decoded output format for GBT packets
# 16 bytes for every "strobe" - 128 bits 
# data: 12 bits of BCID + 8 bits of ERR_FLAGS + 32 bits of HITLIST + 8 bits of art data parity + 8 * 6 bits of art data
# constant C,E written out somewhere

# A.Wang, last edited April 10, 2017


import sys, getopt,binstr
import json
import collections, visual

def main(argv):
    remapflag = 0
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:r:w:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'decodeGBT_32bit.py -i <inputfile> -o <outputfile> -w <windowlength> [-r]'
        print 'window length should be the BCID window for each GBT packet event'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'decodeGBT_32bit.py -i <inputfile> -o <outputfile> -w <windowlength> [-r]'
            print 'window length should be the BCID window for each GBT packet event'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-w"):
            win = 2*int(arg)
        elif opt in ("-r"):
            remapflag = 1

    colors = visual.bcolors()
    num_lines = sum(1 for line in open(inputfile))
    datafile = open(inputfile, 'r')
    decodedfile = open(outputfile, 'w')

    outputData = collections.OrderedDict()

    nevent = 0
    addc1 = -1
    addc2 = -1
    Aflag = True
    
    n = 5 #starting pt of data
    nlines = -1
    lines = []
    nwarning = 0
    remapping = [11, 10, 9, 8, 15, 14, 13, 12, 3, 2, 1, 0, 7, 6, 5, 4, 27, 26, 25, 24, 31, 30, 29, 28, 19, 18, 17, 16, 23, 22, 21, 20]
    print colors.ANNFAV + "\t\t\t\t\t\t\t\t\t " + colors.ENDC
    print colors.ANNFAV + "\tDecoding!\t" + "(>'-')> <('-'<) ^(' - ')^ <('-'<) (>'-')>\t "+ colors.ENDC
    print colors.ANNFAV + "\t\t\t\t\t\t\t\t\t " + colors.ENDC
    for line in datafile:
        if str(line[0:4]) =='TIME':
            timestamp = int(float(line[6:-1]))
            timestampsec = timestamp/pow(10,9)
            timestampns = timestamp%pow(10,9)
            continue
        # if (nlines == -1 or nlines % (win*4) == 0):
        #     decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns) + "\n\n")
        #     nevent = nevent + 1
        #     nlines = 0
        #     if (nevent % (num_lines/(10*win*4)) == 0):
        #         visual.update_progress(float(nevent)/num_lines*win*4.)
#        nlines = nlines + 1
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
            if (abs(addc1-int(bcid,16)) != 1 and abs(addc1-int(bcid,16)) != 4096) and Aflag:
                decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns) + "\n")
                nlines = 0
                if (nevent % (num_lines/(10*win*4)) == 0):
                    visual.update_progress(float(nevent)/num_lines*win*4.)
                nevent = nevent + 1
                Aflag = True
            if (Aflag):
                addc1 = int(bcid,16)
                Aflag = False
            else:
                addc2 = int(bcid,16)
                Aflag = True

            # write to file
            decodedfile.write("BCID: %4i Hits: %i\n" % (int(bcid,16), len(vmmlist)))
            for ibo in xrange(4):
                arts = []
                for board, vmm, art in zip(boardlist[::-1], vmmlist[::-1], vmmdata[::-1]):
                    if int(board) == ibo:
                        arts.append([vmm, art])
                write_me = "%s %s" % (ibo, " ".join(["%s,%s" % (vmm, art) for vmm,art in arts]))
                decodedfile.write(write_me+"\n")

            # warn with aggressive colors
            if len(boardlist) > 7:
                print
                print colors.WARNING
                print "Event: " + str(nevent) + ", Hit map has more hits than room for channels! Stopping early!"
                print colors.ENDC
                print "Hitmap:     ", hitmap
                print "Board list: ", boardlist[::-1]
                print "VMM list:   ", vmmlist[::-1]
                print "VMM data:   ", vmmdata[::-1]
                print
                break

            # json
            tmpKey = str(int(bcid,16))
            if tmpKey in outputData:
                tmpKey = tmpKey+"_1"
            outputData[tmpKey] = zip(boardlist[::-1], vmmlist[::-1],vmmdata[::-1])

    with open(outputfile.split(".")[0]+".json", 'w') as outputJSONFile:
        json.dump(outputData, outputJSONFile)

    decodedfile.close()
    datafile.close()
    print "\n"
    print colors.ANNFAV + "\t\t\t\t\t\t\t\t\t " + colors.ENDC
    print colors.ANNFAV + "\tDone decoding, exiting! \t\t\t\t\t "+ colors.ENDC
    print colors.ANNFAV + "\t\t\t\t\t\t\t\t\t " + colors.ENDC
    

if __name__ == "__main__":
    main(sys.argv[1:])
