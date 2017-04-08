#!/usr/bin/python

# Simple GBT analysis for looking at phase offset
# and plotting some other crap


import numpy as np
import matplotlib.pyplot as plt
import sys, getopt,binstr

import os
import copy
import math
import ROOT

def setstyle():
    ROOT.gROOT.SetBatch()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPadTopMargin(0.05)
    ROOT.gStyle.SetPadRightMargin(0.05)
    ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPaintTextFormat(".2f")
    ROOT.gStyle.SetTextFont(42)

def processData(A, B, inline, flagA):
    'Takes a line with hits and parses it'
    if (flagA): # flagA => ADDC A got data
        A["b"].append(int(inline[0]))
        A["vmm"].append(int(inline[1]))
        A["ch"].append(int(inline[2]))
        if (int(inline[0]) < 2):
            A["x"].append(int(inline[0]))
        else:
            A["uv"].append(int(inline[0]))
    else: # ADDC B got data
        B["b"].append(int(inline[0]))
        B["vmm"].append(int(inline[1]))
        B["ch"].append(int(inline[2]))
        if (int(inline[0]) > 1):
            B["x"].append(int(inline[0]))
        else:
            B["uv"].append(int(inline[0]))
    return A,B

def main(argv):

    # things we want to plot
    h1 = ROOT.TH1F("phase", "Phases", 17, -8.5, 8.5)
    h_wind = ROOT.TH1F("ART spread", "ART spread", 15, -0.5, 14.5)
    h_beginBuff = ROOT.TH1F("begin Buff", "begin Buff", 15, -0.5, 14.5)
    h_coincBuff = ROOT.TH1F("coinc Buff", "coinc Buff", 15, -0.5, 14.5)
    h_Awind = ROOT.TH1F("ART spread for ADDC A", "ART spread for ADDC A", 15, -0.5, 14.5)
    h_Bwind = ROOT.TH1F("ART spread for ADDC B", "ART spread for ADDC B", 15, -0.5, 14.5)
    h_bufflen = ROOT.TH1F("Buffer Length", "Buffer Length", 20, -0.5, 20.5)
    
    # handles inputs
    inputfile = ''
    outputfile = ''
    helpmsg = 'gbtAnalysis.py -i <inputfile> -o <outputfile>'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print helpmsg
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helpmsg
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    datafile = open(inputfile, 'r')

#    file = ROOT.TFile.Open("GBTanalysis.root","recreate")

    
    eventN = -1

    # per addc counters
    bufferlen = [-1, -1] #buffer length for each ADDC separately
    firstbuff = [-1,-1]  #when the first hit comes in for each ADDC
    cbuff = [-1,-1] #when the first time we get a coincidence comes
    lastbuff = [-1,-1] #when the last hit comes 
    deltaBCID = [-1,-1] #delta BCID spread in hits for individual ADDC
    deltaC = [-1,-1] #delta BCID spread from first hit to coincidence for each ADDC
    
    # "global" buffers
    addbufferlen = -1 #buffer length, counting pairs of ADDCs
    firstaddbuff = -1 #when the first hit comes in
    caddbuff = -1 #when the first time we get a coincidence comes
    lastaddbuff = -1 #when the last hit comes
    deltaBCID_add = -1 #delta BCID spread in hits
    deltaC_add = -1 #delta BCID spread from first hit to coincidence
    foundCoinc = False

    # offset in phase
    phaseOffset = -999

    addcBCID = [-1,-1]
    flags = [False,False] # flags for which ADDC we are looking at
    restartBCID_b = False # new event, restart BCID counters
    
    A = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
    B = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
    nhit = -1 #nhits in this packet
    
    for line in datafile:
#        print line
        inline = line.split()
        if (len(inline) == 0):
            continue
        if ("TIME" in inline[0]):
            timesec = int(float(inline[1]))/pow(10,9)
            timens = int(float(inline[1]))%pow(10,9)
        elif ("BCID" in inline[0]):
            bcid = int(inline[1])
            if (int(inline[3]) !=0):
                nhit = int(inline[3])
            # reset flags
            flags = [False,False] # says which ADDC we are parsing data from
            for i,flag in enumerate(flags):
                # check which addc bcid the event matches
                if (abs(bcid-addcBCID[i]) == 1 or abs(bcid-addcBCID[i]) == 4095):
                    addcBCID[i] = bcid
                    flags[i] = True
                    bufferlen[i] = bufferlen[i] + 1
                    if (i == 0): # increment buffer length only once per pair of ADDC packets
                        addbufferlen = addbufferlen + 1
#                    print "ADDC, BCID"
#                    print i,bcid
            if (restartBCID_b): # let's restart ADDC B bcid counter
                addcBCID[1] = bcid
                flags[1] = True
                restartBCID_b = False
            if not any(flags): # BCIDs make a jump, so we expect a new event
                if (eventN > 0):
                    deltaC = [cbuff[i]-firstbuff[i]+1 for i in range(2)]
                    deltaBCID = [lastbuff[i]-firstbuff[i]+1 for i in range(2)]
                    deltaC_add = caddbuff-firstaddbuff+1
                    deltaBCID_add = lastaddbuff-firstaddbuff +1
                    phaseOffset = deltaBCID_add-max(deltaBCID)
                    # print "FIRST HIT",firstaddbuff
                    # print "ART spread",deltaBCID_add
                    # print "ADDCA spread",deltaBCID[0]
                    # print "ADDCB spread",deltaBCID[1]
                    # print "phase offset",phaseOffset
                    h1.Fill(phaseOffset)
                    h_wind.Fill(deltaBCID_add)
                    h_Awind.Fill(deltaBCID[1]) #fuck this these are switched for some fucking reason
                    h_Bwind.Fill(deltaBCID[0])
#                    h_Awind.Fill(deltaBCID[0])
#                    h_Bwind.Fill(deltaBCID[1])
                    h_beginBuff.Fill(firstaddbuff)
                    h_coincBuff.Fill(caddbuff)
                    h_bufflen.Fill(addbufferlen)
                eventN = eventN + 1
                if (eventN % 10000 ==0):
                    print "Processing event",eventN
#                print "New Cosmic Event!",eventN
                addcBCID[0] = bcid

                # reset literally everything
                bufferlen = [1, 1] #restart buffer length
                addbufferlen = 1
                firstbuff = [-1,-1] # clear out where the first data comes in
                firstaddbuff = -1
                lastbuff = [-1,-1]
                lastaddbuff = -1
                cbuff = [-1,-1]
                caddbuff = -1
                deltaBCID = [-1,-1]
                deltaBCID_add = -1
                deltaC = [-1,-1]
                deltaC_add = -1

                foundCoinc = False
                restartBCID_b = True # next event, we can automatically reset BCID for ADDC B
                
                # clear out data
                A = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
                B = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
            if all(flags):
                print "Error! BCIDs of ADDCs became synched!"
                sys.exit(2)
        else: # reading data
            if (nhit != 0 and len(inline) > 1):
                for i in range(2):
                    if (firstbuff[i] < 0 and flags[i]): # if buffer hasn't been set yet
                        firstbuff[i] = bufferlen[i]
                if (firstaddbuff < 0):
                    firstaddbuff = addbufferlen

                A,B = processData(A, B, inline, flags[0])
                nhit = nhit - 1

                # update end of data point
                for i in range(2):
                    if (flags[i]):
                        lastbuff[i] = bufferlen[i]
                lastaddbuff = addbufferlen

                # print "first, last"
                # print firstaddbuff,lastaddbuff
                # print "first a , last a"
                # print firstbuff[0],lastbuff[0]
                # print "first b , last b"
                # print firstbuff[1],lastbuff[1]
                
            if ((len(A["uv"])+len(B["uv"])) > 0 and len(A["x"]) > 0 and len(B["x"]) > 0):
                if not(foundCoinc):
                    cbuff = [bufferlen[i] for i in range(2)]
                    caddbuff = addbufferlen
                foundCoinc = True

        # this might be useless
        if (nhit == 0):
            nhit = -1

    # plotting!
    
    setstyle()

    c = ROOT.TCanvas("c", "canvas", 800, 600)
    c.cd()
    h1.SetLineColor(ROOT.kBlue+3)
    h1.SetLineWidth(3)
    h1.SetMarkerColor(ROOT.kBlack)
    h1.SetMarkerStyle(20)
    h1.SetMarkerSize(0.7)
    h1.SetTitle("")
    h1.GetXaxis().SetTitle("Phase between ADDCs")
    h1.GetYaxis().SetTitle("Events")
    h1.GetXaxis().SetLabelSize(0.025)
    h1.GetYaxis().SetLabelSize(0.025)
    h1.GetXaxis().SetTitleSize(0.035)
    h1.GetYaxis().SetTitleSize(0.035)
    h1.GetXaxis().SetTitleOffset(1.3)
    h1.GetYaxis().SetTitleOffset(1.8)
    h1.Draw()
    c.Print("phase.pdf")
    c.Clear()

    h_bufflen.SetLineColor(ROOT.kBlue+3)
    h_bufflen.SetLineWidth(3)
    h_bufflen.SetMarkerColor(ROOT.kBlack)
    h_bufflen.SetMarkerStyle(20)
    h_bufflen.SetMarkerSize(0.7)
    h_bufflen.SetTitle("")
    h_bufflen.GetXaxis().SetTitle("GBT Buffer Length")
    h_bufflen.GetYaxis().SetTitle("Events")
    h_bufflen.GetXaxis().SetLabelSize(0.025)
    h_bufflen.GetYaxis().SetLabelSize(0.025)
    h_bufflen.GetXaxis().SetTitleSize(0.035)
    h_bufflen.GetYaxis().SetTitleSize(0.035)
    h_bufflen.GetXaxis().SetTitleOffset(1.3)
    h_bufflen.GetYaxis().SetTitleOffset(1.8)
    h_bufflen.Draw()
    c.Print("bufflen.pdf")
    c.Clear()

    h_wind.SetLineColor(ROOT.kBlue+3)
    h_wind.SetLineWidth(3)
    h_wind.SetMarkerColor(ROOT.kBlack)
    h_wind.SetMarkerStyle(20)
    h_wind.SetMarkerSize(0.7)
    h_wind.SetTitle("")
    h_wind.GetXaxis().SetTitle("ART Spread (BCID)")
    h_wind.GetYaxis().SetTitle("Events")
    h_wind.GetXaxis().SetLabelSize(0.025)
    h_wind.GetYaxis().SetLabelSize(0.025)
    h_wind.GetXaxis().SetTitleSize(0.035)
    h_wind.GetYaxis().SetTitleSize(0.035)
    h_wind.GetXaxis().SetTitleOffset(1.3)
    h_wind.GetYaxis().SetTitleOffset(1.8)
    h_wind.Draw()
    c.Print("artwind.pdf")
    c.Clear()

    h_Awind.SetLineColor(ROOT.kBlue+3)
    h_Awind.SetLineWidth(3)
    h_Awind.SetMarkerColor(ROOT.kBlack)
    h_Awind.SetMarkerStyle(20)
    h_Awind.SetMarkerSize(0.7)
    h_Awind.SetTitle("")
    h_Awind.GetXaxis().SetTitle("ART Spread (BCID) for ADDC A")
    h_Awind.GetYaxis().SetTitle("Events")
    h_Awind.GetXaxis().SetLabelSize(0.025)
    h_Awind.GetYaxis().SetLabelSize(0.025)
    h_Awind.GetXaxis().SetTitleSize(0.035)
    h_Awind.GetYaxis().SetTitleSize(0.035)
    h_Awind.GetXaxis().SetTitleOffset(1.3)
    h_Awind.GetYaxis().SetTitleOffset(1.8)
    h_Awind.Draw()
    c.Print("artwindA.pdf")
    c.Clear()

    h_Bwind.SetLineColor(ROOT.kBlue+3)
    h_Bwind.SetLineWidth(3)
    h_Bwind.SetMarkerColor(ROOT.kBlack)
    h_Bwind.SetMarkerStyle(20)
    h_Bwind.SetMarkerSize(0.7)
    h_Bwind.SetTitle("")
    h_Bwind.GetXaxis().SetTitle("ART Spread (BCID) for ADDC B")
    h_Bwind.GetYaxis().SetTitle("Events")
    h_Bwind.GetXaxis().SetLabelSize(0.025)
    h_Bwind.GetYaxis().SetLabelSize(0.025)
    h_Bwind.GetXaxis().SetTitleSize(0.035)
    h_Bwind.GetYaxis().SetTitleSize(0.035)
    h_Bwind.GetXaxis().SetTitleOffset(1.3)
    h_Bwind.GetYaxis().SetTitleOffset(1.8)
    h_Bwind.Draw()
    c.Print("artwindB.pdf")
    c.Clear()

    h_beginBuff.SetLineColor(ROOT.kBlue+3)
    h_beginBuff.SetLineWidth(3)
    h_beginBuff.SetMarkerColor(ROOT.kBlack)
    h_beginBuff.SetMarkerStyle(20)
    h_beginBuff.SetMarkerSize(0.7)
    h_beginBuff.SetTitle("")
    h_beginBuff.GetXaxis().SetTitle("First Hit Position")
    h_beginBuff.GetYaxis().SetTitle("Events")
    h_beginBuff.GetXaxis().SetLabelSize(0.025)
    h_beginBuff.GetYaxis().SetLabelSize(0.025)
    h_beginBuff.GetXaxis().SetTitleSize(0.035)
    h_beginBuff.GetYaxis().SetTitleSize(0.035)
    h_beginBuff.GetXaxis().SetTitleOffset(1.3)
    h_beginBuff.GetYaxis().SetTitleOffset(1.8)
    h_beginBuff.Draw()
    c.Print("beginBuff.pdf")
    c.Clear()

    h_coincBuff.SetLineColor(ROOT.kBlue+3)
    h_coincBuff.SetLineWidth(3)
    h_coincBuff.SetMarkerColor(ROOT.kBlack)
    h_coincBuff.SetMarkerStyle(20)
    h_coincBuff.SetMarkerSize(0.7)
    h_coincBuff.SetTitle("")
    h_coincBuff.GetXaxis().SetTitle("Coincidence Position")
    h_coincBuff.GetYaxis().SetTitle("Events")
    h_coincBuff.GetXaxis().SetLabelSize(0.025)
    h_coincBuff.GetYaxis().SetLabelSize(0.025)
    h_coincBuff.GetXaxis().SetTitleSize(0.035)
    h_coincBuff.GetYaxis().SetTitleSize(0.035)
    h_coincBuff.GetXaxis().SetTitleOffset(1.3)
    h_coincBuff.GetYaxis().SetTitleOffset(1.8)
    h_coincBuff.Draw()
    c.Print("coincBuff.pdf")
    c.Clear()

if __name__ == "__main__":
    main(sys.argv[1:])
