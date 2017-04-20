#!/usr/bin/python

# Simple GBT analysis for looking at phase offset
# and plotting some other crap


import numpy as np
import matplotlib.pyplot as plt
import sys, getopt,binstr, decoders.visual
import itertools as it

import os
import copy
import math
import ROOT

import random
ROOT.gErrorIgnoreLevel = ROOT.kWarning

def throwToys():
    '''little function from Alex to throw toys and get a simulated distribution'''
    n_el   = 2
    mean   = 0
    sigmas = range(40, 50, 1)
    events = 100000

    window_dt = []
    window_bc = []
    latexs    = []

    draw_me = True

    for sigma in sigmas:

        print "Generating sigma = %i" % (sigma)
        
        window_dt.append(ROOT.TH1F("window_dt_sigma%03i" % sigma, ";Largest #Deltat (#sigma = %i ns);"  % sigma, 100,    0, 400))
        window_bc.append(ROOT.TH1F("window_bc_sigma%03i" % sigma, ";Largest #DeltaBC (#sigma = %i ns);" % sigma,  21, -0.5, 20.5))

        for ev in xrange(events):
            times = [random.gauss(mean, sigma) for el in xrange(n_el)]
            window_dt[-1].Fill(max(times) - min(times))
            window_bc[-1].Fill(int(max(times))/25 - int(min(times))/25)

        window_dt[-1].Scale(1 / window_dt[-1].Integral())
        window_bc[-1].Scale(1 / window_bc[-1].Integral())

    return window_dt, window_bc
    # if draw_me:
    #     for hist in window_dt + window_bc:
    #         hist.SetMaximum(0.6)
    #         name = hist.GetName()
    #         canv = ROOT.TCanvas(name, name, 800, 800)
    #         canv.Draw()
    #         hist.Draw("histsame")
    #         canv.SaveAs(name+".pdf", "pdf")

def setstyle():
    ROOT.gROOT.SetBatch()
#    ROOT.gStyle.SetOptStat(000000111)
    ROOT.gStyle.SetPadTopMargin(0.1)
    ROOT.gStyle.SetPadRightMargin(0.1)
    ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetPadLeftMargin(0.12)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPaintTextFormat(".2f")
    ROOT.gStyle.SetTextFont(42)
    ROOT.gStyle.SetOptFit(ROOT.kTRUE)

def addCake():
    image = ROOT.TImage.Open("cake.png")
    npad = ROOT.TPad("l","l",0.,0.9,0.09,1.)
    npad.Draw()
    npad.cd()
    image.Draw()
    print "drew cake!"
                      

def findDiffPairs(hit_pos, hit_b, ranflag):
    ''' find possible differences between pairs of hits'''
    possCombs = list(it.combinations(hit_pos,2))
    possboardCombs = list(it.combinations(hit_b,2))
    diff = []
    if not ranflag:
        for comb in possCombs:
            diff.append(comb[1]-comb[0])
        return diff
    else: #randomize by board number
        for i, comb in enumerate(possCombs):
            if (possboardCombs[i][1] > possboardCombs[i][0]):
                diff.append(comb[1]-comb[0])
            else:
                diff.append(comb[0]-comb[1])
        return diff
            

def processData(A, B, inline, flagA, flagB, triggerhits):
    '''Takes a line with hits and parses it'''
    board = int(inline[0])
    vmm = int(inline[1])
    ch = int(inline[2])
    changed = False
    ADDCA_boards = ['u1','v1','x2','x3']
    ADDCB_boards = ['x0','x1','u0','v0']
    vmm_indices = [i for i, x in enumerate(triggerhits["vmm"]) if x == vmm]
    if (len(vmm_indices) > 0):
        for j in vmm_indices:
            if int(ch) == int(triggerhits["ch"][j]):
                if (flagA): # flagA => ADDC A got data
                    if triggerhits["board"][j] != ADDCA_boards[board]:
                        continue
                    A["b"].append(board)
                    A["vmm"].append(vmm)
                    A["ch"].append(ch)
                    if (int(inline[0]) > 1):
                        A["x"].append(board)
                    else:
                        A["uv"].append(board)
                    changed = True
                elif (flagB): # ADDC B got data
                    if triggerhits["board"][j] != ADDCB_boards[board]:
                        continue
                    B["b"].append(board)
                    B["vmm"].append(vmm)
                    B["ch"].append(ch)
                    if (int(inline[0]) < 2):
                        B["x"].append(board)
                    else:
                        B["uv"].append(board)
                    changed = True
    return A,B,changed

def main(argv):

    # things we want to plot
    h1 = ROOT.TH1F("phase", "Phases", 17, -8.5, 8.5)
    h_pairs = ROOT.TH1F("#Delta BCID (pairs)", "#Delta BCID (pairs)", 16, -0.5, 15.5)
    h_Apairs = ROOT.TH1F("#Delta BCID (pairs) for ADDC A", "#Delta BCID (pairs) for ADDC A", 16, -0.5, 15.5)
    h_Bpairs = ROOT.TH1F("#Delta BCID (pairs) for ADDC B", "#Delta BCID (pairs) for ADDC B", 16, -0.5, 15.5)
    h_rpairs = ROOT.TH1F("#Delta BCID (random pairs)", "#Delta BCID (pairs)", 31, -15.5, 15.5)
    h_Arpairs = ROOT.TH1F("#Delta BCID (random pairs) for ADDC A", "#Delta BCID (pairs) for ADDC A", 31, -15.5, 15.5)
    h_Brpairs = ROOT.TH1F("#Delta BCID (random pairs) for ADDC B", "#Delta BCID (pairs) for ADDC B", 31, -15.5, 15.5)
    h_wind = ROOT.TH1F("ART spread", "ART spread", 16, -0.5, 15.5)
    h_beginBuff = ROOT.TH1F("begin Buff", "begin Buff", 15, -0.5, 14.5)
    h_coincBuff = ROOT.TH1F("coinc Buff", "coinc Buff", 15, -0.5, 14.5)
    h_Awind = ROOT.TH1F("ART spread for ADDC A", "ART spread for ADDC A", 16, -0.5, 15.5)
    h_Ahits = ROOT.TH1F("Number of hits for ADDC A", "Number of hits for ADDC A", 21, -0.5, 20.5)
    h_Ahits_wind = ROOT.TH2F("Number of hits for ADDC A vs. ART spread", "Number of hits for ADDC A vs. ART spread", 21, -0.5, 20.5, 16, -0.5, 15.5)
    h_Afirsthit_wind = ROOT.TH2F("First hit for ADDC A vs. ART spread", "First hit for ADDC A vs. ART spread", 15, -0.5, 14.5, 16, -0.5, 15.5)
    h_Bwind = ROOT.TH1F("ART spread for ADDC B", "ART spread for ADDC B", 16, -0.5, 15.5)
    h_Bhits = ROOT.TH1F("Number of hits for ADDC B", "Number of hits for ADDC B", 21, -0.5, 20.5)
    h_Bhits_wind = ROOT.TH2F("Number of hits for ADDC B vs. ART spread", "Number of hits for ADDC B vs. ART spread", 21, -0.5, 20.5, 16, -0.5, 15.5)
    h_Bfirsthit_wind = ROOT.TH2F("First hit for ADDC B vs. ART spread", "First hit for ADDC B vs. ART spread", 15, -0.5, 14.5, 16, -0.5, 15.5)
    h_bufflen = ROOT.TH1F("Buffer Length", "Buffer Length", 20, -0.5, 20.5)
    h_hits_wind = ROOT.TH2F("Number of hits vs. ART spread", "Number of hits vs. ART spread", 21, -0.5, 20.5, 16, -0.5, 15.5)
    
    # handles inputs
    inputfile = ''
    outputfile = ''
    tpfile = ''
    helpmsg = 'gbtAnalysis.py -i <inputfile> -o <outputfile> -t <tpfile>'
    try:
        opts, args = getopt.getopt(argv, "hi:o:t:", ["ifile=", "ofile=", "tfile="])
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
        elif opt in ("-t", "--tfile"):
            tpfile = arg
    datafile = open(inputfile, 'r')
    triggerfile = open(tpfile, 'r')

    colors = decoders.visual.bcolors()

#    file = ROOT.TFile.Open("GBTanalysis.root","recreate")


    eventN = -1

    # per addc counters
    bufferlen = [-1, -1] #buffer length for each ADDC separately
    firstbuff = [-1,-1]  #when the first hit comes in for each ADDC
    cbuff = [-1,-1] #when the first time we get a coincidence comes
    lastbuff = [-1,-1] #when the last hit comes 
    deltaBCID = [-1,-1] #delta BCID spread in hits for individual ADDC
    deltaC = [-1,-1] #delta BCID spread from first hit to coincidence for each ADDC
    totHits = [0,0] # number of hits each ADDC received


    # "global" buffers
    addbufferlen = -1 #buffer length, counting pairs of ADDCs
    firstaddbuff = -1 #when the first hit comes in
    caddbuff = -1 #when the first time we get a coincidence comes
    lastaddbuff = -1 #when the last hit comes
    deltaBCID_add = -1 #delta BCID spread in hits
    deltaC_add = -1 #delta BCID spread from first hit to coincidence
    totHits_add = 0 # number of hits both ADDCs received
    foundCoinc = False

    # offset in phase
    phaseOffset = -999

    addcBCID = [-1,-1]
    flags = [False,False] # flags for which ADDC we are looking at
    restartBCID_b = False # new event, restart BCID counters
    
    A = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
    B = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
    nhit = -1 #nhits in this packet
    hitPos = []
    hitPosBoards = []
    hitPosA = []
    hitPosABoards = []
    hitPosB = []
    hitPosBBoards = []

    teventnum = 0

    datafilelines = datafile.read().splitlines()
    tpfilelines = triggerfile.read().splitlines()
    nline = 0
    ntpline = 0
    
    foundMatch = False
    tphits = {"board":[],"vmm":[],"ch":[]}
    iboard = 0
    plane_order = ["v1","v0","u1","u0","x3","x2","x1","x0"]

    nhitmatches = 0
    ntphits = 0
    
    df = False

    # first loop through trigger file
    while ntpline < len(tpfilelines):
        tline = tpfilelines[ntpline]
        tinline = tline.split()
        print tline
        if ("Event" in tinline[0]):
            tphits = {"board":[],"vmm":[],"ch":[]}
            tptimesec = int(tinline[3])
            tptimens = int(tinline[5])
            #if (df):
            ntpline = ntpline + 1
            print colors.OKBLUE + "TPfit " + tinline[1] + colors.ENDC
            continue
        if ("BCID" in tinline[0]):
            tpbcid = tinline[1]
            ntpline = ntpline + 1
            continue
        if ("mx_local" in tinline[0]):
            ntpline = ntpline + 1
            continue
        #tphits[plane_order[iboard]] = (tinline[0],tinline[1])
        if (len(tphits["vmm"])) < 8 and (len(tphits["ch"])) < 8:
            tphits["board"].append(plane_order[iboard])
            tphits["vmm"].append(int(tinline[0]))
            tphits["ch"].append(int(tinline[1]))
        if (df):
            print "nboards found!", iboard
        if (iboard != 7): # keep reading tp file until we get all 8 planes
            ntpline = ntpline + 1
            iboard = iboard + 1
            continue
        print tphits["ch"]
        ntphits = 8-tphits["ch"].count(0)
        if (ntphits < 4):
            print colors.FAIL + "WHAT THE FUCK" + colors.ENDC
        if (df):
            print "NTPhits", ntphits
        while (foundMatch is False):
#        for line in datafilelines:
            if nline == len(datafilelines):
                break
            line = datafilelines[nline]
            inline = line.split()
            if (len(inline) == 0):
                nline = nline + 1
                continue
            if ("Event" in inline[0]):
                timesec = int(inline[3])
                timens = int(inline[5])
#                print "TPEvent", tptimesec
#                print "Event", inline[1], timesec
            if (timesec - tptimesec) > 2:
                print colors.FAIL + "failed to find a match! moving on!" + colors.ENDC
                ntpline = ntpline + 1
                iboard = 0
                break
            if abs(timesec - tptimesec) != 0: #continue until we have the same time in seconds, at least
                nline = nline + 1
                continue
            if abs(timens - tptimens) > 1.*pow(10,8): # 0.1 s difference is unacceptable
                nline = nline + 1
                continue
            #if (df):
            foundMatch = True
            print "It's true!!!! We found a match!!!!"
            print colors.OKGREEN + "GBT Event " + inline[1] + colors.ENDC
            print "TP time: " +str(tptimesec) + " " +  str(tptimens) + " GBT time: " + str(timesec) + " "+ str(timens)
            print "\n"
            nline = nline + 1
        # if we reach the end of the file, quit
        if (nline == len(datafilelines)):
            break
        # end loop now
        
        while (foundMatch == True):
            if nline == len(datafilelines):
                break
            inline = (datafilelines[nline]).split()
            if len(inline) == 0:
                nline = nline + 1
                continue
            if ("Event" in inline[0]):
                if (eventN == 0):
                    eventN = eventN + 1
                    continue
                print "found N matches", nhitmatches
                foundMatch = False
                for i in range(2):
                    if (firstbuff[i] > -1):
                        deltaC[i] = cbuff[i]-firstbuff[i]+1 
                        deltaBCID[i] = lastbuff[i]-firstbuff[i]+1
                        if deltaBCID[i] > 8:
                            print colors.FAIL + "what is going on!!!" + colors.ENDC
                if (firstaddbuff > -1):
                    deltaC_add = caddbuff-firstaddbuff+1
                    deltaBCID_add = lastaddbuff-firstaddbuff +1
                    phaseOffset = deltaBCID_add-max(deltaBCID)
                        # print "FIRST HIT",firstaddbuff
                        # print "ART spread",deltaBCID_add
                        # print "ADDCA spread",deltaBCID[0]
                        # print "ADDCB spread",deltaBCID[1]
                        # print "phase offset",phaseOffset
                if (nhitmatches == ntphits):
                    if (nhitmatches < 4):
                        print "WHAT IS GOING ON?!?!?! how did we get data with less than four hits"
                    totalDiffs = findDiffPairs(hitPos, hitPosBoards, False)
                    totalADiffs = findDiffPairs(hitPosA, hitPosABoards, False)
                    totalBDiffs = findDiffPairs(hitPosB, hitPosBBoards, False)
                    totalrDiffs = findDiffPairs(hitPos, hitPosBoards, True)
                    totalArDiffs = findDiffPairs(hitPosA, hitPosABoards, True)
                    totalBrDiffs = findDiffPairs(hitPosB, hitPosBBoards, True)
                    for d in totalDiffs:
                        h_pairs.Fill(d)
                    for d in totalADiffs:
                        h_Apairs.Fill(d)
                    for d in totalBDiffs:
                        h_Bpairs.Fill(d)
                    for d in totalrDiffs:
                        h_rpairs.Fill(d)
                    for d in totalArDiffs:
                        h_Arpairs.Fill(d)
                    for d in totalBrDiffs:
                        h_Brpairs.Fill(d)
                    h1.Fill(phaseOffset)
                    h_wind.Fill(deltaBCID_add)
                    h_Awind.Fill(deltaBCID[0]) 
                    h_Bwind.Fill(deltaBCID[1])
                    h_Ahits.Fill(totHits[0])
                    h_Bhits.Fill(totHits[1])
                    h_Ahits_wind.Fill(totHits[0],deltaBCID[0])
                    if (deltaBCID[0] > 8):
                        print colors.WARNING + "found something with greater than 8 window!!!!!!" + colors.ENDC
                    h_Afirsthit_wind.Fill(firstbuff[0],deltaBCID[0])
                    h_Bhits_wind.Fill(totHits[1],deltaBCID[1])
                    h_Bfirsthit_wind.Fill(firstbuff[1],deltaBCID[1])
                    h_hits_wind.Fill(totHits_add,deltaBCID_add)
                    print colors.ANNFAV + "Filled histograms!" + colors.ENDC
                    h_beginBuff.Fill(firstaddbuff)
                    h_coincBuff.Fill(caddbuff)
                    h_bufflen.Fill(addbufferlen)
                    ntpline = ntpline + 1
                    iboard = 0
                    tphits = {"board":[],"vmm":[],"ch":[]}
                else:
                    print colors.FAIL + "i didn't find everything matching!" + colors.ENDC
                if (eventN % 10000 ==0):
                    print "Processing event",eventN
                    #print eventN
                    #                print "New Cosmic Event!",eventN
                nhitmatches = 0
                eventN = eventN + 1
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
                totHits = [0,0]
                totHits_add = 0
                addcBCID = [-1, -1]
                foundCoinc = False
                # clear out data
                A = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
                B = {"b":[],"vmm":[],"ch":[],"x":[],"uv":[]}
                hitPos = []
                hitPosA = []
                hitPosB = []
                hitPosBoards = []
                hitPosABoards = []
                hitPosBBoards = []
                break
            if ("BCID" in inline[0]):
                bcid = int(inline[1])
                flags = [False,False]
                if (restartBCID_b): # let's restart ADDC B bcid counter
                    addcBCID[1] = bcid
                    flags[1] = True
                    restartBCID_b = False
                if addcBCID[0] == -1:
                    addcBCID[0] = bcid
                    flags[0] = True
                    restartBCID_b = True
                if (int(inline[3]) !=0):
                    nhit = int(inline[3])
                    # reset flags
#                flags = [False,False] # says which ADDC we are parsing data from
                for i,flag in enumerate(flags):
                    # check which addc bcid the event matches
                    if (abs(bcid-addcBCID[i]) == 1 or abs(bcid-addcBCID[i]) == 4095):
                        addcBCID[i] = bcid
                        flags[i] = True
                        bufferlen[i] = bufferlen[i] + 1
                        if (i == 0): # increment buffer length only once per pair of ADDC packets
                            addbufferlen = addbufferlen + 1
                        if (df):
                            print "ADDC, BCID"
                            print i,bcid
            else: # reading data
                if (nhit > 0 and len(inline) > 1):
                    A,B,flag = processData(A, B, inline, flags[0], flags[1],tphits)
                    if (df):
                        print A, B
                        print tphits
                    nhit = nhit-1
                    if (not flag):
                        continue
                    print "Flags:", flags[0],flags[1]
                    nhitmatches = nhitmatches + 1
                    if (df):
                        print "matched hit!"
                    for i in range(2):
                        if (firstbuff[i] < 0 and flags[i]): # if buffer hasn't been set yet
                            firstbuff[i] = bufferlen[i]
                    hitPos.append(addbufferlen)
                    if (flags[0]):
                        hitPosA.append(bufferlen[0])
                        hitPosBoards.append(A["b"][-1])
                        hitPosABoards.append(A["b"][-1])
                    elif (flags[1]):
                        hitPosB.append(bufferlen[1])
                        hitPosBoards.append(B["b"][-1])
                        hitPosBBoards.append(B["b"][-1])
                    if (firstaddbuff < 0):
                        firstaddbuff = addbufferlen
                    # update end of data point
                    for i in range(2):
                        if (flags[i]):
                            totHits[i] = totHits[i] + 1
                            lastbuff[i] = bufferlen[i]
                            totHits_add = totHits_add + 1
                            lastaddbuff = addbufferlen
                    if (df):
                        print "first, last"
                        print firstaddbuff,lastaddbuff
                        print "first a , last a"
                        print firstbuff[0],lastbuff[0]
                        print "first b , last b"
                        print firstbuff[1],lastbuff[1]

                if ((len(A["uv"])+len(B["uv"])) > 0 and len(A["x"]) > 0 and len(B["x"]) > 0):
                    if not(foundCoinc):
                        cbuff = [bufferlen[i] for i in range(2)]
                        caddbuff = addbufferlen
                        foundCoinc = True

            # this might be useless
            if (nhit == 0):
                nhit = -1
            nline = nline + 1

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

    h_pairs.SetLineColor(ROOT.kBlue+3)
    h_pairs.SetLineWidth(3)
    h_pairs.SetMarkerColor(ROOT.kBlack)
    h_pairs.SetMarkerStyle(20)
    h_pairs.SetMarkerSize(0.7)
    h_pairs.SetTitle("")
    h_pairs.GetXaxis().SetTitle("#Delta BCID (pairs)")
    h_pairs.GetYaxis().SetTitle("Events")
    h_pairs.GetXaxis().SetLabelSize(0.025)
    h_pairs.GetYaxis().SetLabelSize(0.025)
    h_pairs.GetXaxis().SetTitleSize(0.035)
    h_pairs.GetYaxis().SetTitleSize(0.035)
    h_pairs.GetXaxis().SetTitleOffset(1.3)
    h_pairs.GetYaxis().SetTitleOffset(1.8)
    h_pairs.Draw()
    c.Print("artpairs.pdf")
    c.Clear()

    # Normalized version
    h_pairs.SetLineColor(ROOT.kBlue+3)
    h_pairs.SetLineWidth(3)
    h_pairs.SetMarkerColor(ROOT.kBlack)
    h_pairs.SetMarkerStyle(20)
    h_pairs.SetMarkerSize(0.7)
    h_pairs.SetTitle("")
    h_pairs.GetXaxis().SetTitle("#Delta BCID (pairs)")
    h_pairs.GetYaxis().SetTitle("A.U.")
    h_pairs.GetXaxis().SetLabelSize(0.025)
    h_pairs.GetYaxis().SetLabelSize(0.025)
    h_pairs.GetXaxis().SetTitleSize(0.035)
    h_pairs.GetYaxis().SetTitleSize(0.035)
    h_pairs.GetXaxis().SetTitleOffset(1.3)
    h_pairs.GetYaxis().SetTitleOffset(1.8)
    norm = h_pairs.GetEntries()
    h_pairs.Scale(1./norm)
    h_pairs.Draw()
    c.Print("artpairs_norm.pdf")
    c.Clear()

    window_dt, window_bc = throwToys()
    for hist in window_dt + window_bc:
        hist.SetMaximum(0.6)
        name = hist.GetName()
        canv = ROOT.TCanvas(name, name, 800, 800)
        canv.Draw()
        hist.Draw("histsame")
        h_pairs.Draw("histsame")
        canv.SaveAs(name+".pdf", "pdf")
        
    h_Apairs.SetLineColor(ROOT.kBlue+3)
    h_Apairs.SetLineWidth(3)
    h_Apairs.SetMarkerColor(ROOT.kBlack)
    h_Apairs.SetMarkerStyle(20)
    h_Apairs.SetMarkerSize(0.7)
    h_Apairs.SetTitle("")
    h_Apairs.GetXaxis().SetTitle("#Delta BCID (pairs) for ADDC A")
    h_Apairs.GetYaxis().SetTitle("Events")
    h_Apairs.GetXaxis().SetLabelSize(0.025)
    h_Apairs.GetYaxis().SetLabelSize(0.025)
    h_Apairs.GetXaxis().SetTitleSize(0.035)
    h_Apairs.GetYaxis().SetTitleSize(0.035)
    h_Apairs.GetXaxis().SetTitleOffset(1.3)
    h_Apairs.GetYaxis().SetTitleOffset(1.8)
    h_Apairs.Draw()
    c.Print("artpairsA.pdf")
    c.Clear()

    h_Bpairs.SetLineColor(ROOT.kBlue+3)
    h_Bpairs.SetLineWidth(3)
    h_Bpairs.SetMarkerColor(ROOT.kBlack)
    h_Bpairs.SetMarkerStyle(20)
    h_Bpairs.SetMarkerSize(0.7)
    h_Bpairs.SetTitle("")
    h_Bpairs.GetXaxis().SetTitle("#Delta BCID (pairs) for ADDC B")
    h_Bpairs.GetYaxis().SetTitle("Events")
    h_Bpairs.GetXaxis().SetLabelSize(0.025)
    h_Bpairs.GetYaxis().SetLabelSize(0.025)
    h_Bpairs.GetXaxis().SetTitleSize(0.035)
    h_Bpairs.GetYaxis().SetTitleSize(0.035)
    h_Bpairs.GetXaxis().SetTitleOffset(1.3)
    h_Bpairs.GetYaxis().SetTitleOffset(1.8)
    h_Bpairs.Draw()
    c.Print("artpairsB.pdf")
    c.Clear()

    f2 = ROOT.TF1("gaussian","gaus(0)",-6.5,6.5)
    f2.SetParameter(0, h_rpairs.GetMaximum())
    f2.SetParameter(1, h_rpairs.GetMean())
    f2.SetParameter(2, h_rpairs.GetRMS()/2)
    f3 = ROOT.TF1("double gaussian","gaus(0)+gaus(3)",-6.5,6.5)
    f3.SetParameter(0, h_rpairs.GetMaximum())
    f3.SetParameter(1, h_rpairs.GetMean())
    f3.SetParameter(2, h_rpairs.GetRMS()/2)
    f3.SetParameter(3, h_rpairs.GetMaximum()/2/1.5)
    f3.SetParameter(4, h_rpairs.GetMean())
    f3.SetParameter(5, h_rpairs.GetRMS()*1.5)

    h_rpairs.Fit(f2,"RQN")
    print "First three fit parameters:", f2.GetParameter(0), f2.GetParameter(1), f2.GetParameter(2)
    h_rpairs.Fit(f3,"RQN")
    print "First six fit parameters:", f3.GetParameter(0), f3.GetParameter(1), f3.GetParameter(2),\
        f3.GetParameter(3), f3.GetParameter(4), f3.GetParameter(5)
    tfit = ROOT.TText()
    tfit.SetNDC()
    tfit.SetTextFont(42)
    tfit.SetTextColor(ROOT.kAzure+1)
    tfit.SetTextSize(0.03)
    tfit.SetTextAlign(22)
    tfit.SetTextAngle(0)
    newtext = "gaussian fit "
    tfit2 = ROOT.TText()
    tfit2.SetNDC()
    tfit2.SetTextFont(42)
    tfit2.SetTextColor(1)
    tfit2.SetTextSize(0.03)
    tfit2.SetTextAlign(22)
    tfit2.SetTextAngle(0)
    newtext2 = "mean {0:.3f}".format(f2.GetParameter(1)) + ", " + "sig {0:.3f}".format(f2.GetParameter(2))

    tfitf3 = ROOT.TText()
    tfitf3.SetNDC()
    tfitf3.SetTextFont(42)
    tfitf3.SetTextColor(ROOT.kRed)
    tfitf3.SetTextSize(0.03)
    tfitf3.SetTextAlign(22)
    tfitf3.SetTextAngle(0)
    newtextf3 = "double gaussian fit "
    tfitf32 = ROOT.TText()
    tfitf32.SetNDC()
    tfitf32.SetTextFont(42)
    tfitf32.SetTextColor(1)
    tfitf32.SetTextSize(0.03)
    tfitf32.SetTextAlign(22)
    tfitf32.SetTextAngle(0)
    newtextf32 = "mean {0:.3f}".format(f3.GetParameter(1)) + ", " + "sig {0:.3f}".format(f3.GetParameter(2))
    tfitf33 = ROOT.TText()
    tfitf33.SetNDC()
    tfitf33.SetTextFont(42)
    tfitf33.SetTextColor(1)
    tfitf33.SetTextSize(0.03)
    tfitf33.SetTextAlign(22)
    tfitf33.SetTextAngle(0)
    newtextf33 = "mean {0:.3f}".format(f3.GetParameter(4)) + ", " + "sig {0:.3f}".format(f3.GetParameter(5))
    
    h_rpairs.SetLineColor(ROOT.kBlue+3)
    h_rpairs.SetLineWidth(3)
    h_rpairs.SetMarkerColor(ROOT.kBlack)
    h_rpairs.SetMarkerStyle(20)
    h_rpairs.SetMarkerSize(0.7)
    h_rpairs.SetTitle("")
    h_rpairs.GetXaxis().SetTitle("#Delta BCID (random pairs)")
    h_rpairs.GetYaxis().SetTitle("Events")
    h_rpairs.GetXaxis().SetLabelSize(0.025)
    h_rpairs.GetYaxis().SetLabelSize(0.025)
    h_rpairs.GetXaxis().SetTitleSize(0.035)
    h_rpairs.GetYaxis().SetTitleSize(0.035)
    h_rpairs.GetXaxis().SetTitleOffset(1.3)
    h_rpairs.GetYaxis().SetTitleOffset(1.8)
    h_rpairs.Draw()
    f2.SetLineStyle(7)
    f2.SetLineColor(ROOT.kAzure+1)
    f2.Draw("same");
    tfit.DrawText(0.75, 0.4, newtext)
    tfit2.DrawText(0.75, 0.35, newtext2)
    f3.SetLineStyle(7)
    f3.SetLineColor(ROOT.kRed)
    f3.Draw("same");
    tfitf3.DrawText(0.25, 0.4, newtextf3)
    tfitf32.DrawText(0.25, 0.35, newtextf32)
    tfitf33.DrawText(0.25, 0.3, newtextf33)
#    addCake()
    c.Print("artrpairs.pdf")
    c.Clear()

    h_Arpairs.SetLineColor(ROOT.kBlue+3)
    h_Arpairs.SetLineWidth(3)
    h_Arpairs.SetMarkerColor(ROOT.kBlack)
    h_Arpairs.SetMarkerStyle(20)
    h_Arpairs.SetMarkerSize(0.7)
    h_Arpairs.SetTitle("")
    h_Arpairs.GetXaxis().SetTitle("#Delta BCID (random pairs) for ADDC A")
    h_Arpairs.GetYaxis().SetTitle("Events")
    h_Arpairs.GetXaxis().SetLabelSize(0.025)
    h_Arpairs.GetYaxis().SetLabelSize(0.025)
    h_Arpairs.GetXaxis().SetTitleSize(0.035)
    h_Arpairs.GetYaxis().SetTitleSize(0.035)
    h_Arpairs.GetXaxis().SetTitleOffset(1.3)
    h_Arpairs.GetYaxis().SetTitleOffset(1.8)
    h_Arpairs.Draw()
    c.Print("artrpairsA.pdf")
    c.Clear()

    h_Brpairs.SetLineColor(ROOT.kBlue+3)
    h_Brpairs.SetLineWidth(3)
    h_Brpairs.SetMarkerColor(ROOT.kBlack)
    h_Brpairs.SetMarkerStyle(20)
    h_Brpairs.SetMarkerSize(0.7)
    h_Brpairs.SetTitle("")
    h_Brpairs.GetXaxis().SetTitle("#Delta BCID (random pairs) for ADDC B")
    h_Brpairs.GetYaxis().SetTitle("Events")
    h_Brpairs.GetXaxis().SetLabelSize(0.025)
    h_Brpairs.GetYaxis().SetLabelSize(0.025)
    h_Brpairs.GetXaxis().SetTitleSize(0.035)
    h_Brpairs.GetYaxis().SetTitleSize(0.035)
    h_Brpairs.GetXaxis().SetTitleOffset(1.3)
    h_Brpairs.GetYaxis().SetTitleOffset(1.8)
    h_Brpairs.Draw()
    c.Print("artrpairsB.pdf")
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

    h_Ahits.SetLineColor(ROOT.kBlue+3)
    h_Ahits.SetLineWidth(3)
    h_Ahits.SetMarkerColor(ROOT.kBlack)
    h_Ahits.SetMarkerStyle(20)
    h_Ahits.SetMarkerSize(0.7)
    h_Ahits.SetTitle("")
    h_Ahits.GetXaxis().SetTitle("Number of hits for ADDC A")
    h_Ahits.GetYaxis().SetTitle("Events")
    h_Ahits.GetXaxis().SetLabelSize(0.025)
    h_Ahits.GetYaxis().SetLabelSize(0.025)
    h_Ahits.GetXaxis().SetTitleSize(0.035)
    h_Ahits.GetYaxis().SetTitleSize(0.035)
    h_Ahits.GetXaxis().SetTitleOffset(1.3)
    h_Ahits.GetYaxis().SetTitleOffset(1.8)
    h_Ahits.Draw()
    c.Print("arthitsA.pdf")
    c.Clear()

    h_Bhits.SetLineColor(ROOT.kBlue+3)
    h_Bhits.SetLineWidth(3)
    h_Bhits.SetMarkerColor(ROOT.kBlack)
    h_Bhits.SetMarkerStyle(20)
    h_Bhits.SetMarkerSize(0.7)
    h_Bhits.SetTitle("")
    h_Bhits.GetXaxis().SetTitle("Number of hits for ADDC B")
    h_Bhits.GetYaxis().SetTitle("Events")
    h_Bhits.GetXaxis().SetLabelSize(0.025)
    h_Bhits.GetYaxis().SetLabelSize(0.025)
    h_Bhits.GetXaxis().SetTitleSize(0.035)
    h_Bhits.GetYaxis().SetTitleSize(0.035)
    h_Bhits.GetXaxis().SetTitleOffset(1.3)
    h_Bhits.GetYaxis().SetTitleOffset(1.8)
    h_Bhits.Draw()
    c.Print("arthitsB.pdf")
    c.Clear()

    # h_Ahits_wind.SetLineColor(ROOT.kBlue+3)
    # h_Ahits_wind.SetLineWidth(3)
    # h_Ahits_wind.SetMarkerColor(ROOT.kBlack)
    # h_Ahits_wind.SetMarkerStyle(20)
    # h_Ahits_wind.SetMarkerSize(0.7)
    h_Ahits_wind.SetTitle("ADDC A")
    h_Ahits_wind.GetXaxis().SetTitle("Number of hits")
    h_Ahits_wind.GetYaxis().SetTitle("ART spread (BCID)")
    h_Ahits_wind.GetXaxis().SetLabelSize(0.025)
    h_Ahits_wind.GetYaxis().SetLabelSize(0.025)
    h_Ahits_wind.GetXaxis().SetTitleSize(0.035)
    h_Ahits_wind.GetYaxis().SetTitleSize(0.035)
    h_Ahits_wind.GetXaxis().SetTitleOffset(1.3)
    c.SetLogz()
    #h_Ahits_wind.GetYaxis().SetTitleOffset(1.8)
    h_Ahits_wind.Draw("colz")
    c.Print("arthits_windA.pdf")
    c.Clear()

    # h_Ahits_wind.SetLineColor(ROOT.kBlue+3)
    # h_Ahits_wind.SetLineWidth(3)
    # h_Ahits_wind.SetMarkerColor(ROOT.kBlack)
    # h_Ahits_wind.SetMarkerStyle(20)
    # h_Ahits_wind.SetMarkerSize(0.7)
    h_Bhits_wind.SetTitle("ADDC B")
    h_Bhits_wind.GetXaxis().SetTitle("Number of hits")
    h_Bhits_wind.GetYaxis().SetTitle("ART spread (BCID)")
    h_Bhits_wind.GetXaxis().SetLabelSize(0.025)
    h_Bhits_wind.GetYaxis().SetLabelSize(0.025)
    h_Bhits_wind.GetXaxis().SetTitleSize(0.035)
    h_Bhits_wind.GetYaxis().SetTitleSize(0.035)
    h_Bhits_wind.GetXaxis().SetTitleOffset(1.3)
    #h_Bhits_wind.GetYaxis().SetTitleOffset(1.8)
    c.SetLogz()
    h_Bhits_wind.Draw("colz")
    c.Print("arthits_windB.pdf")
    c.Clear()

    h_hits_wind.SetTitle("ADDC A and ADDC B")
    h_hits_wind.GetXaxis().SetTitle("Number of hits")
    h_hits_wind.GetYaxis().SetTitle("ART spread (BCID)")
    h_hits_wind.GetXaxis().SetLabelSize(0.025)
    h_hits_wind.GetYaxis().SetLabelSize(0.025)
    h_hits_wind.GetXaxis().SetTitleSize(0.035)
    h_hits_wind.GetYaxis().SetTitleSize(0.035)
    h_hits_wind.GetXaxis().SetTitleOffset(1.3)
    c.SetLogz()
    #h_hits_wind.GetYaxis().SetTitleOffset(1.8)
    h_hits_wind.Draw("colz")
    c.Print("arthits_wind.pdf")
    c.Clear()

    h_Afirsthit_wind.SetTitle("ADDC A")
    h_Afirsthit_wind.GetXaxis().SetTitle("First hit position")
    h_Afirsthit_wind.GetYaxis().SetTitle("ART spread (BCID)")
    h_Afirsthit_wind.GetXaxis().SetLabelSize(0.025)
    h_Afirsthit_wind.GetYaxis().SetLabelSize(0.025)
    h_Afirsthit_wind.GetXaxis().SetTitleSize(0.035)
    h_Afirsthit_wind.GetYaxis().SetTitleSize(0.035)
    h_Afirsthit_wind.GetXaxis().SetTitleOffset(1.3)
    #h_Afirsthit_wind.GetYaxis().SetTitleOffset(1.8)
    c.SetLogz()
    h_Afirsthit_wind.Draw("colz")
    c.Print("artfirsthit_windA.pdf")
    c.Clear()

    h_Bfirsthit_wind.SetTitle("ADDC B")
    h_Bfirsthit_wind.GetXaxis().SetTitle("First hit position")
    h_Bfirsthit_wind.GetYaxis().SetTitle("ART spread (BCID)")
    h_Bfirsthit_wind.GetXaxis().SetLabelSize(0.025)
    h_Bfirsthit_wind.GetYaxis().SetLabelSize(0.025)
    h_Bfirsthit_wind.GetXaxis().SetTitleSize(0.035)
    h_Bfirsthit_wind.GetYaxis().SetTitleSize(0.035)
    h_Bfirsthit_wind.GetXaxis().SetTitleOffset(1.3)
    #h_Bfirsthit_wind.GetYaxis().SetTitleOffset(1.8)
    c.SetLogz()
    h_Bfirsthit_wind.Draw("colz")
    c.Print("artfirsthit_windB.pdf")
    c.Clear()

    #c.cd()
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
