#!/usr/bin/python
# -*- coding: utf-8 -*-

# Decoder for the scintillator signal time stamp from MMTP

# A.Wang, last edited May 16, 2017


import sys, getopt,binstr, time, visual, commonTrig
import argparse


def main(argv):

    colors = visual.bcolors()
    consts = commonTrig.tconsts()

    parser = argparse.ArgumentParser()
    parser.add_argument("--ifile", "-i", default="", help="input file")
    parser.add_argument("--ofile", "-o", default="", help="output file")
    args = parser.parse_args()
    
    num_lines = sum(1 for line in open(args.ifile))
    datafile = open(args.ifile, 'r')
    decodedfile = open(args.ofile, 'w')

    lines = []
    lastn = -1
    
    print "\n"
    print colors.DARK + "Decoding!       " + "ψ ︿_____︿_ψ_ ☾\t "+ colors.ENDC
    print "\n"
    nevent = 0
    for line in datafile:
        if str(line[0:4]) == 'TIME' :
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
        
        if len(lines) == 2: # groups of 2
            nevent = nevent + 1
            if (nevent % (num_lines/(10*3)) == 0):
                visual.update_progress(float(nevent)/num_lines*3.)
            decodedfile.write("Event " + str(nevent) +" Sec " + str(timestampsec) + " NS " + str(timestampns))
            header = lines[0] #contains constants + trigger number
            overflow = int(header[3])
            ntrig = int(header[4:8],16)
            if (ntrig-lastn-1) != 0 and (ntrig-lastn-1)!= -65536 and lastn != -1:
                print "\nSkipped a trigger! On Event",ntrig
                print "Skipped", ntrig-lastn-1

            lastn = ntrig
            timing = lines[1]
            bcid = int(timing[4:7],16)
            phase = int(timing[7],16)
            phasens = phase*(25/16.) # phase in ns

            decodedfile.write('\n' + "BCID: " + str(bcid) + " ph: " + str(phase))
            decodedfile.write('\n' + "overflow: " + str(overflow))
            decodedfile.write('\n' + "ntrig: " + str(ntrig) + "\n")
            lines = []
    decodedfile.close()
    datafile.close()
    print "\n"
    print colors.DES + "Done decoding!  " + "ψ ︿_____︿_ψ_ ☼\t "+ colors.ENDC
    print "\n"

if __name__ == "__main__":
    main(sys.argv[1:])
