#!/usr/bin/env python

import os,sys

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import FuncFormatter, LinearLocator, FixedFormatter
import matplotlib.patches as patches

# CLI option parser
from optparse import OptionParser

# for nicer looking plots
# import seaborn

import json

from collections import OrderedDict

parser = OptionParser()
parser.add_option("--valinit", help   = "initial z bin", default=0)
parser.add_option("--animate", help = "animate!",action="store_true", default=False)
parser.add_option('--save',    help = "save as a file instead of showing. if saving doesn't work, make sure you have imagemagick installed. `brew install imagemagick` if you have homebrew.",action="store_true", default=False)
parser.add_option("--json",    help   = "input json file", default="test.json")
parser.add_option("--nevents", help   = "number of", default=500)
(options, args) = parser.parse_args()


with open(options.json, 'r') as fp:
    inputData = json.load(fp, object_pairs_hook=OrderedDict)

# source = "simulation"
source = "testStand"

if source=="testStand":
    flippedBoards = [0,3,5,6]
    # flippedBoards = [1,2,5,7]
elif source == "simulation":
    flippedBoards = []

#Plotting
fig, ax = plt.subplots(figsize=(6,10))

resetRectangles = []
for (iBoard,iVMM) in [(x,y) for x in xrange(4) for y in xrange(8)]:
    # print iBoard,iVMM
    color = "blue"
    if iBoard in flippedBoards:
        color = "green"

    resetRectangles.append( patches.Rectangle( (0.01,0), width=0.49, height=0.99 ,fill=False)  )
    resetRectangles.append( patches.Rectangle( (0.51,0), width=0.49, height=0.99 ,fill=False)  )
    for iHalf in [0,1]:
        offset = 0.5
        resetRectangles.append(
            patches.Rectangle(
                ((iBoard/8.)+0.02+iHalf*offset, (iVMM/8.)+0.02 ), (1/8.)-0.04, (1/8.)-0.04,
                alpha=0.1, color=color
            )
        )

def resetDisplay():
    ax.cla()
    labels = ["B%d"%i for i in xrange(8)]
    directions = ["X","X","U","V","U","V","X","X"]
    labels = ["%s %s"%(labels[x], directions[x]) for x in xrange(8)]
    ax.set_xticks(np.arange(1/16., 17/16.,1/8.))
    ax.set_yticks([])
    ax.set_xticklabels(labels)
    for p in resetRectangles:
        ax.add_patch(p)


resetDisplay()

events = []
bcidList = []

if source=="testStand":
    iBCID = 0
    jBCID = 0
    for BCID in inputData:
        if iBCID == jBCID == 0:
            iBCID = BCID
        elif jBCID==0:
            jBCID = BCID
        if not jBCID==0 and not iBCID==0:
            # if len(inputData[jBCID])+len(inputData[iBCID])==0:
            #     continue
            print (len(inputData[jBCID])+len(inputData[iBCID]) )
            if (len(inputData[jBCID])+len(inputData[iBCID]) )>0:
                events.append( (inputData[jBCID],inputData[iBCID]) )
                bcidList.append( (jBCID,iBCID) )
            iBCID = jBCID = 0
elif source=="simulation":
    for BCID in inputData:
        if "_1" in BCID:
            continue
        iBCID = BCID
        jBCID = BCID+"_1"
        if iBCID in inputData and jBCID in inputData:
            events.append( (inputData[iBCID],inputData[jBCID]) )
            bcidList.append( (iBCID,iBCID) )

# events = events[:options.nevents]
# print events
# print bcidList


def plot(i):
    resetDisplay()
    rectangles = []
    x = []
    y = []
    offset = 0.5
    # print "plotting..."
    for iHalf in [0,1]:
        for iHit in events[i][iHalf]:
            # print iHit
            (iBoard, iVMM, iStrip) = iHit
            VMMLocation = iVMM/8.
            if bool(iBoard in flippedBoards) != bool(iHalf):
                VMMLocation = (7-iVMM)/8.

            rectangles.append(
                patches.Rectangle(
                    ((iBoard/8.)+0.02+offset*iHalf, (VMMLocation)+0.02 ), (1/8.)-0.04, (1/8.)-0.04,
                    alpha=0.4, facecolor="red"
                )
            )

            x.append(  (iBoard/8.)+0.06+offset*iHalf   )
            y.append(  (VMMLocation)+0.02 + ((1/8.)-0.04 ) * (iStrip/64.)    )
    for p in rectangles:
        ax.add_patch(p)
    ax.scatter(x, y)
    ax.text(0.1,-0.03,bcidList[i][0])
    ax.text(0.6,-0.03,bcidList[i][1])

plot(0)



#Update Function
def update(val,firstTime=0):
    plot(int(val) )

#Animate Function
def animate(val):
    slider_z.set_val(val)



#Slider
sliderAxes_z = plt.axes([0.3, 0.01, 0.5, 0.05])
slider_z = Slider(sliderAxes_z, 'Event', 0, len(events), valinit=0)
slider_z.on_changed(update)




if __name__ == '__main__':

    if options.save:
        outputDirectory = "Output"
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)

    # FuncAnimation will call the 'update' function for each frame; here
    # animating over N frames, with an interval of 200ms between frames.
    if options.animate:
        anim = FuncAnimation(fig, animate, frames=np.arange(0, len(events)), interval=500)
        if options.save:
            imageName = 'Output/EventDisplay.gif'
            anim.save(imageName, dpi=80, writer='imagemagick')
        else:
            plt.show()
    else:
        if options.save:
            fig.savefig('Output/MaterialMap.pdf')
        else:
            plt.show()


