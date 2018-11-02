# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 14:32:07 2018

@author: AOVIS projector
"""

from __future__ import division
import numpy as np
from psychopy import visual, core, event
from psychopy.hardware import crs
from psychopy.tools import colorspacetools as ct

import helper as h
import logitech_gamepad as lt


# set color space
colorSpace = 'rgb'

# get key map
keymap = h.key_map()

# check if logitech is installed
if lt.isGamePad():
    inputDevice = 'logitech'
else:
    inputDevice = 'keyboard'

#create a window
monitorName = 'LightCrafter'
currentCalibName = 'gamma_31Oct2018'

windowSize = [1080, 800]
fullScreen = False
screen = 1
useBitsSharp = False

if useBitsSharp:

    # we need to be rendering to framebuffer (FBO)
    mywin = visual.Window(windowSize, useFBO=True, fullscr=fullScreen,
                          monitor=monitorName, 
                          units='deg',
                          screen=screen, gammaCorrect='hardware')
    bits = crs.BitsSharp(mywin, mode='mono++')
    # You can continue using your window as normal and OpenGL shaders
    # will convert the output as needed
    if not bits.OK:
        print('failed to connect to Bits box')
        core.quit()
    print(bits.info)
    # now, you can change modes using
    bits.mode = 'color++'
else:
    mywin = visual.Window(windowSize, monitor=monitorName, fullscr=fullScreen,
                          units="deg", screen=screen)

invGammaTable = h.gammaInverse(monitorName, currentCalibName)

#create some stimuli
blackColor = np.array([0, 0, 0])
canvasSize = np.array([30, 30, 0])

canvas = visual.GratingStim(win=mywin, color=blackColor, size=canvasSize[:2],
                          colorSpace=colorSpace, pos=[0.,0.], sf=0)
rect = visual.GratingStim(win=mywin, color=(0., 0.5, 1.), size=canvasSize[:2],
                          colorSpace=colorSpace, pos=[-4.,0.], sf=0)
                          

ramp = np.linspace(0.01, 1, 8)
hsv_vals = np.array([np.zeros(len(ramp)), np.zeros(len(ramp)), ramp]).T
for hsv in hsv_vals:
    rgb = ct.hsv2rgb(hsv)
    rgb = h.gammaCorrect(invGammaTable, rgb)
    print(rgb)
    rect.color = rgb
    canvas.draw()
    rect.draw()
    mywin.flip()
    
    allKeys = event.waitKeys(modifiers=True, timeStamped=True)[0]


mywin.close()
core.quit()


