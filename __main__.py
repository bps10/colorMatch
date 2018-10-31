from __future__ import division
import os, pickle, datetime
import numpy as np
from psychopy import visual, core, event
from psychopy.hardware import crs

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
else:
    inputDevice = 'keyboard'

#create a window
monitorName = 'LightCrafter'
currentCalibName = 'gamma_31Oct2018'

if parameters['screen'] > 0:
    windowSize = [1280,800]
    fullScreen = True
else:
    windowSize = [800, 600]
    fullScreen = False

invGammaTable = h.gammaInverse(monitorName, currentCalibName)

if parameters['isBitsSharp']:

    # we need to be rendering to framebuffer (FBO)
    mywin = visual.Window(windowSize, useFBO=True, fullscr=fullScreen,
                          monitor=monitorName, 
                          units='deg',
                          screen=parameters['screen'], gammaCorrect='hardware')
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
    mywin = visual.Window(windowSize, monitor=monitorName, fullscr=fullScreen,
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

#draw the stimuli and update the window
keepGoing = True
while keepGoing:
    # need to organize in a list so that match drawn on top of rect
    for field in field_list:
        h.drawField(fields, field, invGammaTable)
        
    # flip new screen
    mywin.flip()
        
    # wait for key press
    if inputDevice == 'keyboard':
        allKeys = event.waitKeys(modifiers=True, timeStamped=True)[0]
        key = allKeys[0]
        modifier = allKeys[1]
        responseTime = allKeys[2]
        print 'Response time {0:0.3f}'.format(responseTime)
        
        if modifier['ctrl'] is True:
            step_gain = 5
        else:
            step_gain = 1

    else:
        key, modifier = lt.getKeyPress()
        if modifier == True:
            step_gain = 5
        else:
            step_gain = 1

    # process key press
    if key in ['q', 'escape', 'BTN_MODE']:
        keepGoing = False

    # Save the current setting and move on. Stage 4 == matching stage
    elif key in ['ABS_HAT', 'space'] and stage == 4:
        # record data and save
        results['match'][trial] = fields['match']['color']
        # randomize next match location
        fields['match']['color'] = h.random_color(colorSpace)
        # increment trial counter
        trial += 1

    # Save the current setting and move on. Stage 4 == matching stage
    elif key in ['ABS_HAT', 'space'] and stage == 3 and parameters['offlineMatch']:
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
    elif (key[-1] == '1' or key == 'BTN_START') and (
            stage < 4 and parameters['onlineMatch'] or
            stage < 3 and parameters['offlineMatch']):
        stage += 1
    elif (key[-1] == '2' or key == 'BTN_SELECT') and stage > 0:
        stage -= 1
        
    elif key in keymap:
        fields = h.update_value(keymap[key], fields, active_field, attribute,
                                step_gain, step_sizes)
        
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

    # The position of rect and match are yolked to AO background
    relDist = fields['fixation']['position'] - fields['AObackground']['position']
    fields['rect']['position'] = fields['fixation']['position'] + relDist        
    fields['match']['position'] =fields['fixation']['position'] + relDist

    fields['rect']['size'] = fields['AObackground']['size']
    fields['match']['size'][:2] = parameters['OzSize']

    fields['fixation']['size'] = np.array([0.05, 0.05, 0])

    # print out the active parameters
    print "active field " + active_field
    for f in fields[active_field]:
        if f not in ['handle', 'colorSpace']:
            print fields[active_field][f]

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
    pickle.dump(results, open(resultsName, 'w'))
print results
# save the fields structure
# delete fields['handles'] can't save those
for field in fields:
    del fields[field]['handle']

fieldsName = os.path.join(savedir, 'fields_' + date + '.pkl')
pickle.dump(fields, open(fieldsName, 'w'))

# save the subject specific parameters
paramsName = os.path.join(savedir, 'parameters_' + date + '.pkl')
# add the path to fields
parameters['lastFields'] = fieldsName
pickle.dump(parameters, open(paramsName, 'w'))

# Lastly, update lastParameters.txt to reflect this as the most recent set
f = open(os.path.join(basedir, 'dat', 'lastParameters.txt'), 'w')
f.write(paramsName)
f.close()

#cleanup
mywin.close()
core.quit()
