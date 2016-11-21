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

parser = OptionParser()
parser.add_option("--valinit", help   = "initial z bin", default=0)
parser.add_option("--animate", help = "animate!",action="store_true", default=False)
parser.add_option('--save',    help = "save as a file instead of showing. if saving doesn't work, make sure you have imagemagick installed. `brew install imagemagick` if you have homebrew.",action="store_true", default=False)
parser.add_option("--json",    help   = "input json file", default="test.json")
(options, args) = parser.parse_args()


with open(options.json, 'r') as fp:
    inputData = json.load(fp)





#Plotting
fig, ax = plt.subplots(figsize=(6,10))

resetRectangles = []
for (iBoard,iVMM) in [(x,y) for x in xrange(4) for y in xrange(8)]:
    # resetRectangles.append(
    #     patches.Rectangle(
    #         ((iBoard/8.)+0.02, (iVMM/8.)+0.02 ), (1/8.)-0.04, (1/8.)-0.04,
    #         alpha=1, facecolor="white"
    #     )
    # )
    resetRectangles.append(
        patches.Rectangle(
            ((iBoard/8.)+0.02, (iVMM/8.)+0.02 ), (1/8.)-0.04, (1/8.)-0.04,
            alpha=0.1
        )
    )

def resetDisplay():
    ax.cla()
    for p in resetRectangles:
        ax.add_patch(p)


resetDisplay()

# ax.set_xlabel('Detector Phi')
# ax.set_ylabel('r (xy) [mm]')

events = []

for timestamp in inputData:
    for iEvent in inputData[timestamp]:
        if len(iEvent[1]):
            events.append(iEvent[1])

# print events


def plot(i):
    resetDisplay()
    rectangles = []
    x = []
    y = []
    for iHit in events[i]:
        (iBoard, iVMM, iStrip) = iHit
        rectangles.append(
            patches.Rectangle(
                ((iBoard/8.)+0.02, (iVMM/8.)+0.02 ), (1/8.)-0.04, (1/8.)-0.04,
                alpha=0.4, facecolor="red"
            )
        )
        x.append(  (iBoard/8.)+0.06   )
        y.append(  (iVMM/8.)+0.02 + ((1/8.)-0.04 ) * (iStrip/64.)    )
    for p in rectangles:
        ax.add_patch(p)
    ax.scatter(x, y)

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
    # animating over 10 frames, with an interval of 200ms between frames.
    if options.animate:
        anim = FuncAnimation(fig, animate, frames=np.arange(0, len(events)), interval=200)
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


