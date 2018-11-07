from __future__ import division
import numpy as np
import pandas as pn
import os

from psychopy import visual, core, event
from psychopy.hardware import crs
from psychopy import tools

import helper as h
import gui as g
import logitech_gamepad as lt
import colorSpace as cs
import plotResults as plot


thisdir = os.path.dirname(os.path.abspath(__file__))

#load trial parameters
trial_params = pn.read_csv(os.path.join(thisdir, 'assets', 'Oz_Exp_trials.csv'),
                           header=0, index_col=0)

MB_history_match, AB_history_match, XY_history_match = [], [],[]
MB_history_stim, AB_history_stim, XY_history_stim = [], [],[]

Ntrials = len(trial_params)

# set color space
# user will operate in HSV, but we will convert to rgb before sending to device
colorSpace = 'rgb'

# call a parameters gui
parameters = g.parameters()

# get key map
keymap = h.key_map()

# check if logitech is installed
if lt.isGamePad():
    inputDevice = 'logitech'
    use_mouse = False
else:
    inputDevice = 'keyboard'
    use_mouse = True
    # increase this for more mouse sensitivity
    mouse_sensitivity = 1.0
    # if this is true then you can only adjust one of Hue/Saturation at a time,
    # i.e. the mouse is only allowed to move along one axis (either x or y) at
    # a time.
    mouse_fixed_axes = False

#create a window
monitorName = 'LightCrafter'
#monitorName = 'testMonitor'

currentCalibName = 'gamma_31Oct2018'

if parameters['screen'] > 0:
    window_x = 1280
    window_y = 800
    windowSize = [window_x,window_y]
    fullScreen = True
else:
    window_x = 800
    window_y = 600
    windowSize = [window_x, window_y]
    fullScreen = False

invGammaTable = h.gammaInverse(monitorName, currentCalibName)

if parameters['isBitsSharp']:

    # we need to be rendering to framebuffer (FBO)
    mywin = visual.Window(windowSize, useFBO=True,
                          fullscr=fullScreen,
                          monitor=monitorName,
                          units='deg',
                          screen=parameters['screen'],
                    gammaCorrect='hardware', winType='pygame')
    bits = crs.BitsSharp(mywin, mode='mono++')
    # You can continue using your window as normal and OpenGL shaders
    # will convert the output as needed
    print(bits.info)
    if not bits.OK:
        print('failed to connect to Bits box')
        core.quit()
    # now, you can change modes using
    bits.mode = 'color++'
else:
    mywin = visual.Window(windowSize, monitor=monitorName,
                          fullscr=fullScreen,
                          units="deg", screen=parameters['screen'])

#create some stimuli
blackColor = np.array([0, 0, 0])
canvasSize = np.array([30, 30, 0])

canvas = visual.GratingStim(win=mywin, color=blackColor, size=canvasSize[:2],
                          colorSpace=colorSpace, pos=[0.,0.], sf=0)
rect = visual.GratingStim(win=mywin, color=(0., 0.5, 1.), size=5,
                          colorSpace=colorSpace, pos=[-4.,0.], sf=0)
match = visual.GratingStim(win=mywin, color=(0., 0.5, 0.1), size=2,
                          colorSpace=colorSpace, pos=[-4.,0.], sf=0)
fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0.,0.], sf=0, rgb=-1)
AObackground = visual.GratingStim(win=mywin, color=(0., 0.5, 0.5), size=5,
                                  colorSpace=colorSpace, pos=rect.pos * -1.0, sf=0)

# get last set of fields if it exists
fields = h.getFields(parameters, colorSpace, blackColor, canvasSize)

# add handles to stim created above
fields['canvas']['handle'] = canvas
fields['rect']['handle'] = rect
fields['match']['handle'] = match
fields['fixation']['handle'] = fixation
fields['AObackground']['handle'] = AObackground

# explicitly set the AObackground color. In the future get this from parameters
fields['AObackground']['color'] = np.array([210, 0.1, 0.3])
fields['match']['color'] = h.set_color_to_white('hsv')

field_list = ['canvas', 'fixation']
step_sizes = {
    'color': np.array([1, 0.01, 0.01]),
    'size': np.array([0.015, 0.015, 0]),
    'position': np.array([0.015, 0.015, 0])
    }

# for controlling each component of the scene
active_field = 'fixation'
attribute = 'position'

stage = 0
confidence = 0
trial = 0

# --- set background values for plotting
backgroundHSV = fields['rect']['color']
backgroundRGB = cs.hsv2rgb(backgroundHSV[0], backgroundHSV[1], backgroundHSV[2])
# now compute LMS values for background
backgroundXYZ = cs.rgb2xyz(backgroundRGB)
backgroundLMS = cs.rgb2lms(backgroundRGB)
backgroundMB = cs.lms2mb(backgroundLMS)[0]
background = pn.DataFrame(columns=['l', 's', 'CIE_x', 'CIE_y'])
background.loc[0] = np.hstack([backgroundMB, backgroundXYZ[:2]])
background

# --- set up results
results = {'confidence': [], 'hue': [], 'saturation': [], 'value': [],
           'L_intensity': [], 'M_intensity': [], 'S_intensity': [],
           'delta_MB': [], 'new_MB_l': [], 'new_MB_s': [], }

if parameters['offlineMatch']:
    results = {'confidence': [], 'reference': {}, 'match': {}, }

# initialize mouse:
if use_mouse:
    def_mouse_x = -tools.monitorunittools.pix2deg(
        mywin.size[0] * 0.5, mywin.monitor) * 0.5
    def_mouse_y = -tools.monitorunittools.pix2deg(
        mywin.size[1] * 0.5, mywin.monitor) * 0.5
    mouse = event.Mouse(visible=False,
                        newPos=[def_mouse_x,def_mouse_y], win=mywin)
    mouse.setPos([def_mouse_x, def_mouse_y])
    def_mouse_x2, def_mouse_y2 = mouse.getPos()
    mouse_x = def_mouse_x2
    mouse_y = def_mouse_y2
    mouse.setVisible(False)

left_down = False
left_click = False
right_down = False
right_click = False

#draw the stimuli and update the window
keepGoing = True
try:
    while keepGoing:
        # need to organize in a list so that match drawn on top of rect
        for field in field_list:
            h.drawField(fields, field, invGammaTable)

        # flip new screen
        mywin.flip()

        # wait for key press

        #set default step_gain
        step_gain = 1

        if inputDevice != 'logitech':
            allKeys = event.getKeys(modifiers=True, timeStamped=True)
            if use_mouse:
                if mouse.mouseMoved():
                    mouse_x, mouse_y = mouse.getPos()
                    d_mouse_x = mouse_x - def_mouse_x2
                    d_mouse_y = mouse_y - def_mouse_y2
                    mouse.setPos([def_mouse_x, def_mouse_y])
                    if mouse_fixed_axes:
                        if abs(d_mouse_x) > abs(d_mouse_y):
                            d_mouse_y = 0
                        else:
                            d_mouse_x = 0
                else:
                    d_mouse_x = 0.0
                    d_mouse_y = 0.0

                pressed = mouse.getPressed()

                left_click = (pressed[0] == 1 and not left_down)
                right_click = (pressed[2] == 1 and not right_down)
                left_down = (pressed[0] == 1)
                right_down = (pressed[2] == 1)

            if allKeys != None and len(allKeys) > 0:
                allKeys = allKeys[0]
                key = allKeys[0]
                modifier = allKeys[1]

                if modifier['ctrl'] is True or modifier['alt'] is True:
                    step_gain = 5

            else:
                allKeys = None
                key = None
                modifier = None

        else:
            key, modifier = lt.getKeyPress()
            if modifier == True:
                step_gain = 5

        # process user input
        # Save the current setting and move on. Stage 4 == matching stage
        if (key in ['ABS_HAT', 'space'] or right_click) and stage == 4:
            confidence = 0
            stage = 5

        elif (key in ['ABS_HAT', 'space'] or right_click) and stage == 5:

            if parameters['offlineMatch']:
                # record data and save
                results['match'][trial] = fields['rect']['color']
                results['reference'][trial] = fields['AObackground']['color']
                print fields['rect']['color'], fields['AObackground']['color']

                # randomize next ref and match color
                fields['AObackground']['color'] = h.random_color('hsv')
                fields['rect']['color'] = h.random_color('hsv')
                stage = 3
            else:
                # results
                hue = fields['match']['color'][0]
                saturation = fields['match']['color'][1]
                value = fields['match']['color'][2]

                # add trial to the results structure
                results['confidence'].append(confidence)
                results['hue'].append(hue)
                results['saturation'].append(saturation)
                results['value'].append(value)
                results['L_intensity'].append(trial_params.loc[trial].L_intensity)
                results['M_intensity'].append(trial_params.loc[trial].M_intensity)
                results['S_intensity'].append(trial_params.loc[trial].S_intensity)
                results['delta_MB'].append(trial_params.loc[trial].delta_MB)
                results['new_MB_l'].append(trial_params.loc[trial].new_MB_l)
                results['new_MB_s'].append(trial_params.loc[trial].new_MB_s)

                # print out some of the results
                print 'Trial #{0:d}'.format(trial)
                print 'confidence: {0:d}'.format(confidence)
                print 'MATCH HSV: ', fields['match']['color']

                _results = pn.DataFrame(results)
                # update plots in color space
                matchRGB = cs.hsv2rgb(_results.hue, _results.saturation, _results.value)
                matchXYZ = cs.rgb2xyz(matchRGB)

                # Convert to LMS and then MB space
                matchLMS = cs.rgb2lms(matchRGB)
                matchMB = cs.lms2mb(matchLMS)

                alpha = 0.9
                matchMB =  matchMB * alpha + (1 - alpha) * backgroundMB

                _results['CIE_x'] = matchXYZ[:, 0]
                _results['CIE_y'] = matchXYZ[:, 1]
                _results['CIE_z'] = matchXYZ[:, 2]

                _results['match_l'] = matchMB[:, 0]
                _results['match_s'] = matchMB[:, 1]

                plot.colorSpaces(_results, background, parameters['ID'], plotMeans=False)

                # randomize next match location
                fields['match']['color'] = h.set_color_to_white('hsv')
                stage = 4

            # reset confidence to zero for next trial
            confidence = 0

            trial += 1
            if trial == Ntrials:
                keepGoing = False

        # Save the current setting and move on. Stage 4 == matching stage
        elif (key in ['ABS_HAT', 'space'] or right_click) and (
                stage == 3 and parameters['offlineMatch']):
            confidence = 0
            stage = 5

        # change which field is active
        elif (left_click or (key != None and (key[-1] == '1' or key == 'BTN_START'))) and (
                stage < 4 and parameters['onlineMatch'] or
                stage < 3 and parameters['offlineMatch']):
            stage += 1

        elif ((key != None and (key[-1] == '2' or key == 'BTN_SELECT'))) and stage > 0:
            stage -= 1

        elif key != None and key == 'up' and stage == 5:
            confidence += 1
            noteA.play()
            noteC.play()

        elif key != None and key == 'down' and stage == 5:
            confidence -= 1

        elif key in keymap:
            fields = h.update_value(keymap[key], fields, active_field,
                                    attribute, step_gain, step_sizes)

        elif key in ['q', 'escape', 'BTN_MODE']:
            keepGoing = False

        # update fields based on new mouse pos
        if use_mouse and attribute == 'color' and active_field in ['rect', 'match']:
            temp = [0, 0]
            temp[0] = keymap['right'][0]
            temp[1] = keymap['right'][1]
            temp[1] *= mouse_sensitivity * 180.0 * (
                tools.monitorunittools.deg2pix(
                    d_mouse_x, mywin.monitor)) / mywin.size[0]
            fields = h.update_value(temp, fields, active_field,
                                    attribute, step_gain, step_sizes)
            temp[0] = keymap['up'][0]
            temp[1] = keymap['up'][1]
            temp[1] *= mouse_sensitivity * 180.0 * (
                tools.monitorunittools.deg2pix(
                    d_mouse_y, mywin.monitor)) / mywin.size[1]
            fields = h.update_value(temp, fields, active_field,
                                    attribute, step_gain, step_sizes)

        # now update parameters based on key stroke
        if stage == 0:
            active_field = 'fixation'
            attribute = 'position'
            field_list = ['canvas', 'fixation']
        elif stage == 1:
            active_field = 'AObackground'
            attribute = 'position'
            field_list = ['canvas', 'AObackground', 'fixation']
        elif stage == 2:
            active_field = 'AObackground'
            attribute = 'size'
            field_list = ['canvas', 'AObackground', 'fixation']
        elif stage == 3:
            active_field = 'rect'
            attribute = 'color'
            field_list = ['canvas', 'rect', 'AObackground', 'fixation']
        elif stage == 4 and parameters['onlineMatch']:
            active_field = 'match'
            attribute = 'color'
            field_list = ['canvas', 'rect', 'match', 'AObackground', 'fixation']

        # stage 5 is where the subject gives an integer
        # confidence score indicating how close the match was
        elif stage == 5 and parameters['onlineMatch']:
            active_field = 'match'
            attribute = 'color'
            field_list = ['canvas', 'rect', 'match', 'AObackground', 'fixation']

        elif stage == 5 and not parameters['onlineMatch']:
            active_field = 'rect'
            attribute = 'color'
            field_list = ['canvas', 'rect', 'AObackground', 'fixation']

        # check that color hasn't gone out of gamut
        for field in fields:
            fields[field]['color'] = h.check_color(
                fields[field]['color'], colorSpace)

        # The position of rect and match are yoked to AO background
        relDist = fields['fixation']['position'] - fields['AObackground']['position']
        fields['rect']['position'] = fields['fixation']['position'] + relDist
        fields['match']['position'] = fields['fixation']['position'] + relDist
        fields['rect']['size'] = fields['AObackground']['size']
        fields['match']['size'][:2] = parameters['OzSize']
        fields['fixation']['size'] = np.array([0.05, 0.05, 0])

        # before waiting for the next key press, clear the buffer
        event.clearEvents()
except Exception as e:
    print e
    h.saveData(parameters, results, fields)
    mywin.close()
    core.quit()

h.saveData(parameters, results, fields)

#cleanup
mywin.close()
core.quit()
