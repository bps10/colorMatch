from __future__ import division
import os, pickle, datetime
import numpy as np
from psychopy import visual, core, event
from psychopy.hardware import crs
from psychopy import tools

import helper as h
import gui as g
import logitech_gamepad as lt


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
    mouse_sensitivity = 0.2
    # if this is true then you can only adjust one of Hue/Saturation at a time,
    # i.e. the mouse is only allowed to move along one axis (either x or y) at
    # a time.
    mouse_fixed_axes = False 

#create a window
monitorName = 'LightCrafter'
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
trial = 0
results = {'colorSpace': colorSpace, 'match': {}, }
if parameters['offlineMatch']:
    results['reference'] = {}

#initialize mouse:
if use_mouse:
    def_mouse_x = tools.monitorunittools.pix2deg(0, mywin.monitor)
    def_mouse_y = tools.monitorunittools.pix2deg(0, mywin.monitor)
    mouse = event.Mouse(visible=False,newPos=[def_mouse_x, def_mouse_y], 
                        win=mywin)
    mouse_x, mouse_y = def_mouse_x, def_mouse_y

    mouse.setVisible(False)
    
left_down = False
left_click = False
right_down = False
right_click = False

#draw the stimuli and update the window
keepGoing = True
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
        mouse_x, mouse_y = mouse.getPos()
        d_mouse_x = mouse_x - def_mouse_x
        d_mouse_y = mouse_y - def_mouse_y
        
        pressed = mouse.getPressed()
        mouse.setPos([def_mouse_x, def_mouse_y])
        left_click = (pressed[0] == 1 and not left_down)
        right_click = (pressed[2] == 1 and not right_down)
        left_down = (pressed[0] == 1)
        right_down = (pressed[2] == 1)
        if mouse_fixed_axes:
            if abs(d_mouse_x) > abs(d_mouse_y):
                d_mouse_y = 0
            else:
                d_mouse_x = 0
        
        if allKeys != None and len(allKeys) > 0:
            allKeys = allKeys[0]
            key = allKeys[0]
            modifier = allKeys[1]
            #responseTime = allKeys[2]
            #print 'Response time {0:0.3f}'.format(responseTime)
        
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
    if key in ['q', 'escape', 'BTN_MODE']:
        keepGoing = False

    # Save the current setting and move on. Stage 4 == matching stage
    elif (key in ['ABS_HAT', 'space'] or right_click) and stage == 4:
        # record data and save
        results['match'][trial] = fields['match']['color']
        # randomize next match location
        fields['match']['color'] = h.random_color('hsv')
        # increment trial counter
        trial += 1

    # Save the current setting and move on. Stage 4 == matching stage
    elif (key in ['ABS_HAT', 'space'] or right_click) and stage == 3 and parameters['offlineMatch']:
        # record data and save
        results['match'][trial] = fields['rect']['color']
        results['reference'][trial] = fields['AObackground']['color']
        print fields['rect']['color'], fields['AObackground']['color']
        # randomize next ref and match color
        fields['AObackground']['color'] = h.random_color(colorSpace)
        fields['rect']['color'] = h.random_color(colorSpace)        
        # increment trial counter
        trial += 1
        
    # change which field is active
    elif (left_click or (key != None and (key[-1] == '1' or key == 'BTN_START'))) and (
            stage < 4 and parameters['onlineMatch'] or
            stage < 3 and parameters['offlineMatch']):
        stage += 1

    elif ((key != None and (key[-1] == '2' or key == 'BTN_SELECT'))) and stage > 0:
        stage -= 1

    elif key in keymap:
        fields = h.update_value(keymap[key], fields, active_field, attribute, step_gain, step_sizes)
    
    # update fields based on new mouse pos
    if use_mouse and attribute == 'color' and active_field in ['rect', 'match']:
        temp = [0, 0]
        temp[0] = keymap['right'][0]
        temp[1] = keymap['right'][1]
        temp[1] *= mouse_sensitivity*180.0*(tools.monitorunittools.deg2pix(d_mouse_x, mywin.monitor)) / mywin.size[0]
        fields = h.update_value(temp, fields, active_field, attribute, step_gain, step_sizes)
        temp[0] = keymap['up'][0]
        temp[1] = keymap['up'][1]
        temp[1] *= mouse_sensitivity*180.0*(tools.monitorunittools.deg2pix(d_mouse_y, mywin.monitor)) / mywin.size[1]
        fields = h.update_value(temp, fields, active_field, attribute, step_gain, step_sizes)

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

    # print out the active parameters
    """
    print "active field " + active_field
    for f in fields[active_field]:
        if f not in ['handle', 'colorSpace']:
            print fields[active_field][f]
    """

    # before waiting for the next key press, clear the buffer
    event.clearEvents()

# save
basedir = h.getColorMatchDir()
if parameters['offlineMatch']:
    savedir = os.path.join(basedir, 'dat', 'offline', parameters['ID'])
else:
    savedir = os.path.join(basedir, 'dat', parameters['ID'])
if not os.path.exists(savedir):
    os.makedirs(savedir)
date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

# save the results
if len(results) > 0:
    resultsName = os.path.join(savedir, 'results_' + date + '.pkl')
    f = open(resultsName, 'wb')
    pickle.dump(results, f)
    f.close()
print results
# save the fields structure
# delete fields['handles'] can't save those
for field in fields:
    del fields[field]['handle']

fieldsName = os.path.join(savedir, 'fields_' + date + '.pkl')
f = open(fieldsName, 'wb')
pickle.dump(fields, f)
f.close()

# save the subject specific parameters
paramsName = os.path.join(savedir, 'parameters_' + date + '.pkl')
# add the path to fields
parameters['lastFields'] = fieldsName
f = open(paramsName, 'wb')
pickle.dump(parameters, f)
f.close()

# Lastly, update lastParameters.txt to reflect this as the most recent set
f = open(os.path.join(basedir, 'dat', 'lastParameters.txt'), 'w')
f.write(paramsName)
f.close()

#cleanup
mywin.close()
core.quit()
