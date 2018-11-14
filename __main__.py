from __future__ import division
import numpy as np
import pandas as pn
import os, zmq, time

from psychopy import visual, core, event
from psychopy.hardware import crs
from psychopy import tools
from psychopy.tools import colorspacetools as cspace

import helper as h
import gui as g
import logitech_gamepad as lt
import colorSpace as cs
import plotResults as plot
import processUserInput as ui

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://192.168.137.4:5556")
socket.setsockopt_string(zmq.SUBSCRIBE, "".decode('ascii'))

eye_track_gain = 1
offset_x, offset_y  = 0.01,0
track_size_ratio = 1.05
tracked_on_time = -1.0 #clock time for when the tracked rectangle must be "on"
tracked_off_time = -1.0 #clock time for when the tracked rectangle must be "off"

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
keymap = ui.key_map()

#toggle whether ICANDI information is recorded
record_ICANDI = parameters['yesICANDI']
#Log of time-stamped events
time_event_log = []
log_file = "LOGFILE"

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

invGammaTable = cs.gammaInverse(monitorName, currentCalibName)

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

# create some stimuli
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
tracked_rect = visual.GratingStim(win=mywin, color=(0, 1, 1), size=match.size,
                               colorSpace=colorSpace, pos=AObackground.pos, sf=0)
# get last set of fields if it exists
fields = h.getFields(parameters, colorSpace, blackColor, canvasSize)


# add handles to stim created above
fields['canvas']['handle'] = canvas
fields['rect']['handle'] = rect
fields['match']['handle'] = match
fields['fixation']['handle'] = fixation
fields['AObackground']['handle'] = AObackground
fields['tracked_rect']['handle'] = tracked_rect

# explicitly set the AObackground color. In the future get this from parameters
fields['AObackground']['color'] = np.array([210, 0.1, 0.3])
fields['match']['color'] = h.set_color_to_white('hsv')
fields['match']['size'] = parameters['OzSize']
#
fields['tracked_rect']['position'] = np.copy(fields['AObackground']['position'])
fields['tracked_rect']['color'] = cspace.hsv2rgb(fields['AObackground']['color'])
fields['tracked_rect']['size'] = parameters['OzSize']

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
Lab_lum = 10 # Assume that luminance is 10x lower than a reference D65?
background = h.getBackground(fields, Lab_lum)

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
del_x, del_y = 0, 0
strip_positions = dict([(i, [0,0]) for i in range(1,33)]) # Latest positions of every strip
tracked_strips = np.array(range(2, 31)) # Which strips to use for updating projector.
default_tracked_color = fields['tracked_rect']['color']
latest_strip_updated = 1
# draw the stimuli and update the window
keepGoing = True
first_frame = True
try:
    while keepGoing:
        # grab frame information from ICANDI
        time_event_log.append(str(time.clock())+" Starting loop")
        if record_ICANDI:
            latest_string, latest_strip_updated, movie_start_time = h.get_ICANDI_update(
                socket, strip_positions)
            if movie_start_time is not None:
                tracked_on_time = movie_start_time + 0.09 #90 milliseconds
                tracked_off_time = movie_start_time + 0.12 #120 milliseconds

            if first_frame:
                x0, y0 = strip_positions[15]
                first_frame = False
            # Find closest tracked strip
            projector_strip = tracked_strips[int((
                tracked_strips <= latest_strip_updated).sum())-1]
            _x, _y = strip_positions[projector_strip]
            del_x, del_y = x0+_x, y0+_y
            fields['tracked_rect']['position'][:2] = (
                np.array([del_x, del_y]) *
                fields['tracked_rect']['size'][0] / 256.0  * eye_track_gain +
                fields['AObackground']['position'][:2] +
                np.array([offset_x, offset_y]))
            # need to organize in a list so that match drawn on top of rect
            time_event_log.append(str(time.clock())+" "+latest_string)

            fields['tracked_rect']['color'] = default_tracked_color * float(
                tracked_on_time <= time.clock() <= tracked_off_time )
        time_event_log.append(str(time.clock())+" About to draw")
        # draw fields to buffer
        for field in field_list:
            h.drawField(fields, field, invGammaTable)
        # tracked rect is special: ui is in RGB
        if record_ICANDI or parameters['offlineMatch']:
            h.drawField(fields, 'tracked_rect', invGammaTable,
                        convertHSVToRGB=False)

        time_event_log.append(str(time.clock())+" Finished drawField")
        # flip new screen
        mywin.flip()
        time_event_log.append(str(time.clock())+" Finished flip")
        # wait for key press

        #set default step_gain
        step_gain = 1

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

        # process user input
        # Save the current setting and move on. Stage 4 == matching stage
        if (key in ['ABS_HAT', 'space'] or right_click) and stage == 4:
            confidence = 0
            stage = 5

        # control the gain on the ICANDI x,y position coordinates
##        elif key == 'v':
##            if eye_track_gain > 0.00005:
##                eye_track_gain -= 0.00005
##            print eye_track_gain
##        elif key == 't':
##            eye_track_gain += 0.00005
##            print eye_track_gain

        elif key == 'c':
            if track_size_ratio > 0.01:
                track_size_ratio -= 0.01
            fields['tracked_rect']['size'] = fields['match']['size'] * track_size_ratio
            print track_size_ratio
        elif key == 'r':
            track_size_ratio += 0.01
            fields['tracked_rect']['size'] = fields['match']['size'] * track_size_ratio
            print track_size_ratio

        elif key == 'h':
            offset_x -= 0.01
            print (offset_x, offset_y)
        elif key == 'j':
            offset_y -= 0.01
            print (offset_x, offset_y)
        elif key == 'u':
            offset_y += 0.01
            print (offset_x, offset_y)
        elif key == 'n':
            offset_x += 0.01
            print (offset_x, offset_y)

        elif key == 'period':
            # update the lightness
            AObkgdRGB = cspace.hsv2rgb(fields['AObackground']['color'])
            fields['tracked_rect']['color'][1:] = AObkgdRGB[1:]
            if fields['tracked_rect']['color'][0] <= 1.0 - 0.02 * step_gain:
                fields['tracked_rect']['color'][0] += 0.02 * step_gain
            print fields['tracked_rect']['color']

        elif key == 'comma':
            # update the lightness
            AObkgdRGB = cspace.hsv2rgb(fields['AObackground']['color'])
            fields['tracked_rect']['color'][1:] = AObkgdRGB[1:]
            if fields['tracked_rect']['color'][0] >= AObkgdRGB[0] + 0.02 * step_gain:
                fields['tracked_rect']['color'][0] -= 0.02 * step_gain
            print fields['tracked_rect']['color']

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
                ui.updateResultsAndPlott(results, fields, confidence, trial_params,
                                        trial, background, Lab_lum,
                                        parameters['ID'], alpha=0.66)

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
        elif (left_click or (key != None and
                             (key[-1] == '1' or key == 'BTN_START'))) and (
                stage < 4 and parameters['onlineMatch'] or
                stage < 3 and parameters['offlineMatch']):
            stage += 1

        elif ((key != None and (key[-1] == '2' or key == 'BTN_SELECT'))) and stage > 0:
            stage -= 1

        elif key != None and key == 'up' and stage == 5:
            confidence += 1

        elif key != None and key == 'down' and stage == 5:
            confidence -= 1

        elif key in keymap:
            fields = ui.updateValue(keymap[key], fields, active_field,
                                    attribute, step_gain, step_sizes)

        elif key in ['q', 'escape', 'BTN_MODE']:
            keepGoing = False

        time_event_log.append(str(time.clock())+" about to enter mouse loop")

        # update fields based on new mouse pos
        if use_mouse and attribute == 'color' and active_field in ['rect', 'match']:
            temp = [0, 0]
            temp[0] = keymap['right'][0]
            temp[1] = keymap['right'][1]
            temp[1] *= mouse_sensitivity * 180.0 * (
                tools.monitorunittools.deg2pix(
                    d_mouse_x, mywin.monitor)) / mywin.size[0]
            fields = ui.updateValue(temp, fields, active_field,
                                    attribute, step_gain, step_sizes)
            temp[0] = keymap['up'][0]
            temp[1] = keymap['up'][1]
            temp[1] *= mouse_sensitivity * 180.0 * (
                tools.monitorunittools.deg2pix(
                    d_mouse_y, mywin.monitor)) / mywin.size[1]

            fields = ui.updateValue(temp, fields, active_field,
                                    attribute, step_gain, step_sizes)

        # Now update the active fields and list of fields to be displayed.
        active_field, attribute, field_list = ui.updateFields(
            stage, parameters['onlineMatch'])

        # check that color hasn't gone out of gamut
        for field in fields:
            fields[field]['color'] = h.check_color(
                fields[field]['color'], colorSpace)

        # The position of rect and match are yoked to AO background
        relDist = fields['fixation']['position'] - fields['AObackground']['position']
        fields['rect']['position'] = fields['fixation']['position'] + relDist
        fields['match']['position'] = fields['fixation']['position'] + relDist
        fields['rect']['size'] = fields['AObackground']['size']
        #fields['match']['size'][:2] = parameters['OzSize']
        fields['fixation']['size'] = np.array([0.05, 0.05, 0])
        time_event_log.append(str(time.clock())+" Done with mouse loop")

        # before waiting for the next key press, clear the buffer
        event.clearEvents()
        time_event_log.append(str(time.clock())+" Done clearing events")
    with open(log_file, 'w+') as f:
       f.write("\n".join(time_event_log))
    time_event_log = []
    time_event_log.append(str(time.clock())+" Finished Writing to file")

except Exception as e:
    print e
    h.saveData(parameters, results, fields)

    mywin.close()
    core.quit()

print 'Saving'
h.saveData(parameters, results, fields)

if results[results.keys()[0]] != []:
    results = pn.DataFrame(results)
    plot.hueAndSaturation(results, parameters['ID'])

#cleanup
mywin.close()
core.quit()

