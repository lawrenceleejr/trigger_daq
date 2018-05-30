#/usr/bin/python
# -*- coding: utf-8 -*-

# Decoded output format for GBT packets
# 16 bytes for every "strobe" - 128 bits
# data: 12 bits of BCID + 8 bits of ERR_FLAGS + 32 bits of HITLIST + 8 bits of art data parity + 8 * 6 bits of art data
# constant C,E written out somewhere   

# A.Wang, last edited May 16, 2017


import sys, getopt,binstr, time, visual, commonTrig
import argparse


def main(argv):

    colors = visual.bcolors()
    consts = commonTrig.tconsts()

    args = options()
    
    num_lines = sum(1 for line in open(args.ifile))
    datafile = open(args.ifile, 'r')
    decodedfile = open(args.ofile, 'w')

    # option to dump raw events
    if args.dfile:
        dfile = open(args.dfile, 'r').readlines()
        events_to_dump = []
        for df in dfile:
            if not df:
                continue
            df = df.strip()
            events_to_dump.append(int(df))
        events_to_dump = sorted(list(set(events_to_dump)))

    lines = []

    # previous bcids
    (addc1,addc2) = (-1,-1)
    
    Aflag = True
    win = 30 # expected buffer length
    buflen = win-1
    oldtime = -1
    (nexcess, nshort, dropped) = (0,0,0)
    badgbt = []
    gbtlen = []
    times = []

    print "\n"
    print colors.DARK + "Decoding!       " + "ψ ︿_____︿_ψ_ ☾\t "+ colors.ENDC
    print "\n"

    print "Will not catch > 15+ bugs!"
    start_time = time.time()
    
    nevent = 0
    (timestamp,timestampsec,timestampns) = (-1,-1,-1)

    for iline,line in enumerate(datafile):
        if str(line[0:4]) == 'TIME' :
            timestamp = int(float(line[6:-1]))
            timestampsec = timestamp/pow(10,9)
            timestampns = timestamp%pow(10,9)
            continue
        lines.append(line[:len(line)-1])

        if iline % 50000 == 0 and iline > 0 and not args.dfile:
            visual.pbftp(time.time() - start_time, iline, num_lines)

        n = 5 # start pt of data
        if len(lines) == 4: # groups of 4
            strobe = "".join(map(str,lines))
            artdata = strobe[n+15:n+27]
            parity = strobe[n+13:n+15]
            hitmap = strobe[n+5:n+13]
            hitmap = "{0:032b}".format(int(hitmap,16))
            error = strobe[n+3:n+5]
            bcid = strobe[n:n+3]
            artdata = "{0:048b}".format(int(artdata,16))

            vmmdata = []
            vmmlist = []
            boardlist = []

            buflen += 1
            #print buflen, int(bcid, 16)

            for i in range(8):
                vmmdata.append(int(artdata[i*6:i*6+6],2)+1)

            for i in range(32):
                if (hitmap[i] is "1"):
                    boardlist.append((31-i)/8)
                    vmmlist.append((31-i)%8)

            excluded = [286202,306851,446152,532552,570143,757921,825138,1038996,1134297,
                        1155745,1169477,1170888,1177961]
            
            #######################################################################################################
            # alternative implementation of logic for starting new event:
            # jumps in bcid and we expect it to jump
            # or it jumps a lot in bcid (>2) and we don't expect it to
            # or it doesn't jump but we expect it to and the timestamp changed, at least
            # or it was one of those stupid events where it doesn't jump but we are pretty sure it's a new trigger
            # if ((int(bcid,16)-addc1) != 1 and addc1-int(bcid,16) != 4095 and Aflag and buflen == win)\
            #    or (abs(int(bcid,16)-addc1) > 2 and abs(addc1-int(bcid,16)) < 4095 and Aflag)\
            #    or (((int(bcid,16)-addc1) == 1 or addc1-int(bcid,16) == 4095) and Aflag and timestamp != oldtime and buflen == win)\
            #    or (((int(bcid,16)-addc1) == 1 or addc1-int(bcid,16) == 4095) and Aflag and nevent in excluded and buflen == win):
            #######################################################################################################
            
            # current implementation of logic for starting new event
            # we collect 15 packets
            # or it jumps a lot in bcid and we don't expect it to
            if (buflen == win) or (abs(int(bcid,16)-addc1) > 2 and abs(addc1-int(bcid,16)) < 4095 and Aflag):
                if (buflen < win):
                    nshort += 1
                    badgbt.append(nevent)
                    gbtlen.append(buflen)
                    times.append(int(timestamp))
                    #print colors.WARNING + "Event " + str(nevent) + " has fewer than 15 GBT packets!" + colors.ENDC
                    
                    
                # starting new event
                nevent += 1
                #print "Event", nevent
                Aflag = True
                buflen = 0

                write_me = "Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns) + "\n"
                decodedfile.write(write_me)
                if args.dfile and nevent in events_to_dump:
                    print write_me.rstrip("\n")

            if (Aflag):
                addc1 = int(bcid,16)
                Aflag = False
            else:
                addc2 = int(bcid,16)
                Aflag = True
            oldtime = timestamp
            if (buflen >= win):
                if (buflen == (win)):
                    nexcess += 1
                    print "\n"
                    print colors.WARNING + "Event " + str(nevent) + " has more than 15 GBT packets!" + colors.ENDC
            else:
                decodedfile.write("BCID: %4i Hits: %i\n" % (int(bcid,16),len(vmmlist)))
                for ibo in xrange(4):
                    arts = []
                    for board,vmm,art in zip(boardlist[::-1][0:8],vmmlist[::-1][0:8],vmmdata[::-1]):
                        if int(board) == ibo:
                            arts.append([vmm,art])
                    write_me = "%s %s" % (ibo, " ".join(["%s,%s" % (vmm, art) for vmm,art in arts]))
                    decodedfile.write(write_me+"\n")
                if args.dfile and nevent in events_to_dump:
                    print "\n".join(lines)
            lines = []
            
    decodedfile.close()
    datafile.close()
    print "\n"
    print colors.DES + "Done decoding!  " + "ψ ︿_____︿_ψ_ ☼\t "+ colors.ENDC
    print "Found " + str(nshort)+ " bad GBT buffers, writing into gbterr.txt"
    print "\n"

    errfile = open("gbterr.txt", 'w')
    for x in zip(badgbt,gbtlen,times):
          errfile.write(str(x) + "\n")
    errfile.close()
    

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifile", "-i", default="", help="input file")
    parser.add_argument("--ofile", "-o", default="", help="output file")
    parser.add_argument("--dfile", "-d", default="", help="input file of event numbers to dump")
    return parser.parse_args()
    
if __name__ == "__main__":
    main(sys.argv[1:])
