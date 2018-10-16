from __future__ import division
import numpy as np
from psychopy import visual, core, event
from psychopy.hardware import crs

import helper as h
import gui as g


# set color space
colorSpace = 'hsv'

# call a parameters gui
parameters = g.parameters()

#create a window
window_size = [800,600]
monitorName = 'testMonitor'
fullScreen = False
screen = 0
if parameters['bits_sharp']:

    # we need to be rendering to framebuffer (FBO)
    mywin = visual.Window(window_size, useFBO=True, fullscr=fullScreen,
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
    mywin = visual.Window(window_size, monitor=monitorName, fullscr=fullScreen,
                          units="deg", screen=screen)


#create some stimuli
rect = visual.GratingStim(win=mywin, color=(0., 0.5, 1.), size=5,
                          colorSpace=colorSpace, pos=[-4.,0.], sf=0)
match = visual.GratingStim(win=mywin, color=(0., 0.5, 0.1), size=2,
                          colorSpace=colorSpace, pos=[-4.,0.], sf=0)
fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0.,0.], sf=0, rgb=-1)
AObackground = visual.GratingStim(win=mywin, color=(0., 0.5, 0.5), size=5,
                                  colorSpace=colorSpace, pos=rect.pos * -1.0, sf=0)

# set up defaults if subject data does not exist
fields = {
    'rect': {'handle': rect,
             'colorSpace': colorSpace,
             'color': np.array([50, 0.5, 0.5]),
             'size': np.array([0.95, 0.95]),
             'position': np.array([-1., 0.]), },
    'match': {'handle': match,
              'colorSpace': colorSpace,
              'color': np.array([150, 0.5, 0.15]),
              'size': parameters['OzSize'],
              'position': np.array([-1., 0.]), },
    'fixation': {'handle': fixation,
                 'colorSpace': colorSpace,                 
                 'color': np.array([90., 0, 1]),
                 'size': np.array([0.05, 0.05]),
                 'position': np.array([0., 0.]),},
    'AObackground': {'handle': AObackground,
                     'colorSpace': colorSpace,
                     'color': np.array([90, 0, 0.1]),
                     'size': np.array([0.95, 0.95]),
                     'position': np.array([1., 0.]), },    
}

# for controlling each component of the scene
active_field = 'rect'

#draw the stimuli and update the window
keepGoing = True
while keepGoing:
    # need to organize in a list so that match drawn on top of rect
    for field in ['fixation', 'rect', 'match', 'AObackground']:
        # update parameters of each field
        handle = fields[field]['handle']
        handle.colorSpace = fields[field]['colorSpace']
        handle.color = fields[field]['color']
        handle.size = fields[field]['size']
        handle.pos = fields[field]['position']
        handle.draw()

    # flip new screen
    mywin.flip()

    # wait for key press
    allKeys = event.waitKeys(modifiers=True, timeStamped=True)[0]
    key = allKeys[0]
    modifier = allKeys[1]
    responseTime = allKeys[2]
    print key, modifier['ctrl'], responseTime
    if modifier['ctrl'] is True:
        step_gain = 4
    else:
        step_gain = 1

    # process key press
    if key in ['q', 'escape']:
        keepGoing = False

    # control chromaticity of field
    elif key == 'up':
        fields[active_field]['color'][0] += 1 * step_gain
    elif key == 'down':
        fields[active_field]['color'][0] -= 1 * step_gain        
    elif key == 'right':
        fields[active_field]['color'][1] += 0.02 * step_gain
    elif key == 'left':
        fields[active_field]['color'][1] -= 0.02 * step_gain
    elif key[1:] == 'shift':
        fields[active_field]['color'][2] -= 0.02 * step_gain
    elif key == 'return':
        fields[active_field]['color'][2] += 0.02 * step_gain

    # control position of field
    elif key == 'f':
        fields[active_field]['position'][0] -= 0.1 * step_gain
    elif key == 'g':
        fields[active_field]['position'][0] += 0.1 * step_gain
    elif key == 't':
        fields[active_field]['position'][1] -= 0.1 * step_gain
    elif key == 'v':
        fields[active_field]['position'][1] += 0.1 * step_gain

    # control size of field
    elif key == 'h':
        fields[active_field]['size'][0] -= 0.05 * step_gain
    elif key == 'j':
        fields[active_field]['size'][0] += 0.05 * step_gain
    elif key == 'n':
        fields[active_field]['size'][1] -= 0.05 * step_gain
    elif key == 'u':
        fields[active_field]['size'][1] += 0.05 * step_gain
        
    # change which field is active
    elif key[-1] == '1':
        active_field = 'rect'
    elif key[-1] == '2':
        active_field = 'match'
    elif key[-1] == '3':
        active_field = 'AObackground'        
    elif key[-1] == '4':
        active_field = 'fixation'

    elif key == 'space':
        # record data and save

        # randomize next match location
        fields['match']['color'] = h.random_color(colorSpace)
        pass
    
    # check that color hasn't gone out of gamut
    for field in fields:
        fields[field]['color'] = h.check_color(
            fields[field]['color'], colorSpace)    

    # The position of rect and match are yolked to AO background
    fields['rect']['position'] = -1.0 * fields['AObackground']['position']
    fields['match']['position'] = -1.0 * fields['AObackground']['position']

    fields['rect']['size'] = fields['AObackground']['size']
    fields['match']['size'] = parameters['OzSize']

    fields['fixation']['size'] = 0.05

    # print out the active parameters
    print "active field " + active_field
    for f in fields[active_field]:
        if f not in ['handle', 'colorSpace']:
            print fields[active_field][f]

    # before waiting for the next key press, clear the buffer
    event.clearEvents()

#cleanup
mywin.close()
core.quit()
