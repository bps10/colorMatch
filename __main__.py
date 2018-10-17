from __future__ import division
import os, pickle
import numpy as np
from psychopy import visual, core, event
from psychopy.hardware import crs

import helper as h
import gui as g
import logitech_gamepad as lt


# set color space
colorSpace = 'hsv'

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
windowSize = [800,600]
monitorName = 'testMonitor'
fullScreen = False
screen = 0
if parameters['bitsSharp']:

    # we need to be rendering to framebuffer (FBO)
    mywin = visual.Window(windowSize, useFBO=True, fullscr=fullScreen,
                          monitor=monitorName, units='deg',
                          screen=screen)
    bits = crs.BitsSharp(win, mode='color++')
    # You can continue using your window as normal and OpenGL shaders
    # will convert the output as needed
    print(bits.info)
    if not bits.OK:
        print('failed to connect to Bits box')
        core.quit()

else:
    mywin = visual.Window(windowSize, monitor=monitorName, fullscr=fullScreen,
                          units="deg", screen=screen)


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

# set up defaults if subject data does not exist
fields = {
    'canvas': {'handle': canvas,
               'colorSpace': colorSpace,
               'color': blackColor,
               'size': canvasSize,
               'position': np.array([0, 0., 0]), },               
    'rect': {'handle': rect,
             'colorSpace': colorSpace,
             'color': np.array([50, 0.5, 0.5]),
             'size': np.array([0.95, 0.95, 0]),
             'position': np.array([-1., 0., 0]), },
    'match': {'handle': match,
              'colorSpace': colorSpace,
              'color': np.array([150, 0.5, 0.15]),
              'size': np.array([parameters['OzSize'][0], parameters['OzSize'][1], 0]),
              'position': np.array([-1., 0., 0]), },
    'fixation': {'handle': fixation,
                 'colorSpace': colorSpace,                 
                 'color': np.array([90., 0, 0.9]),
                 'size': np.array([0.05, 0.05, 0]),
                 'position': np.array([0., 0., 0]),},
    'AObackground': {'handle': AObackground,
                     'colorSpace': colorSpace,
                     'color': np.array([90, 0.1, 0.4]),
                     'size': np.array([0.95, 0.95, 0]),
                     'position': np.array([1., 0., 0]), },

}
field_list = ['canvas', 'fixation']
step_sizes = {
    'color': np.array([1, 0.025, 0.025]),
    'size': np.array([0.025, 0.025, 0]),
    'position': np.array([0.025, 0.025, 0])
    }
    
# for controlling each component of the scene
active_field = 'fixation'
attribute = 'position'

stage = 0
#draw the stimuli and update the window
keepGoing = True
while keepGoing:
    # need to organize in a list so that match drawn on top of rect
    for field in field_list:
        h.drawField(fields, field)
        
    # flip new screen
    mywin.flip()
        
    # wait for key press
    if inputDevice == 'keyboard':
        allKeys = event.waitKeys(modifiers=True, timeStamped=True)[0]
        key = allKeys[0]
        modifier = allKeys[1]
        responseTime = allKeys[2]
        print key, modifier['ctrl'], responseTime
        if modifier['ctrl'] is True:
            step_gain = 4
        else:
            step_gain = 1

    else:
        key, modifier = lt.getKeyPress()
        if modifier == True:
            step_gain = 4
        else:
            step_gain = 1
                
    # process key press
    if key in ['q', 'escape', 'BTN_MODE']:
        keepGoing = False
        
    elif key == 'space':
        # record data and save

        # randomize next match location
        fields['match']['color'] = h.random_color(colorSpace)

    # change which field is active
    print key
    print stage > 0
    if (key[-1] == '1' or key == 'BTN_START') and stage < 4:        
        stage += 1
    elif (key[-1] == '2' or key == 'BTN_SELECT') and stage > 0:
        stage -= 1
    print stage
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
        field_list = ['canvas', 'rect', 'AObackground', 'fixation']        
    elif stage == 3:
        active_field = 'rect'
        attribute = 'color'
        field_list = ['canvas', 'rect', 'AObackground', 'fixation']        
    elif stage == 4:
        active_field = 'match'
        attribute = 'color'
        field_list = ['canvas', 'rect', 'match', 'AObackground', 'fixation']
        
    if key in keymap:
        fields = h.update_value(keymap[key], fields, active_field, attribute,
                                step_gain, step_sizes)

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
if not os.path.exists(os.path.join('dat', parameters['ID'])):
    os.makedirs(os.path.join('dat', parameters['ID']))

# delete fields['handles'] can't save those
for field in fields:
    del fields[field]['handle']
    
fname = os.path.join('dat', parameters['ID'], 'fields.pkl')
pickle.dump(fields, open(fname, 'wb'))
fname = os.path.join('dat', parameters['ID'],  'parameters.pkl')
pickle.dump(parameters, open(fname, 'wb'))

#cleanup
mywin.close()
core.quit()
