from __future__ import division
import numpy as np


def convertHSL2RGB():
    '''
    from psychopy import monitors
    from psychopy.tools import colorspacetools as cspace
    mon = monitors.Monitor('PX2411W')
    LMS2RGB = mon.getLMS_RGB(recompute=True)
    print LMS2RGB
    RGB2LMS = np.linalg.inv(LMS2RGB)
    # need to figure out HSL to RGB and then RGB to LMS
    rgb = cspace.hsv2rgb([0, 0.5, 0.1])
    lms = np.dot(RGB2LMS, rgb)
    print rgb
    print lms
    '''
    
def random_color(colorSpace):
    if colorSpace == 'hsv':
        c = np.array([np.random.randint(0, 360),
                      np.random.random_sample(1),
                      np.random.random_sample(1)])
    if colorSpace == 'dkl':
        c = np.array([np.random.randint(-180, 180),
                      np.random.randint(-180, 180),
                      np.random.random_sample(1) * 2 - 1])        
    return c

def check_color(color, colorSpace):
    ''' Make sure that color is within bounds of space.
    '''
    if colorSpace == 'dkl':
        if color[0] < -180:
            color[0] = -90
            print 'Elevation cannot exceed -180: setting to -180'
        if color[0] > 180:
            color[0] = 180
            print 'Elevation cannot exceed 180: setting to 180'
        if color[1] < -180:
            color[1] = -180
            print 'Azimuth cannot exceed -180: setting to -180'
        if color[1] > 180:
            color[1] = 180
            print 'Azimuth cannot exceed 180: setting to 180'
        if color[2] > 1:
            color[2] = 1
            print 'Contrast cannot exceed 1: setting to 1'
        if color[2] < -1:
            color[2] = -1
            print 'Contrast cannot exceed -1: setting to -1'
            
    if colorSpace == 'hsv':
        # Make it circular
        color[0] = color[0] % 360
        color[1] = color[1] % 1
        color[2] = color[2] % 1

    return color


def key_map():

    keymap = {           
        'up': [0, 1],
        'down': [0, -1],
        'right': [1, 1],
        'left': [1, -1],
        'shift': [2, -1],
        'return': [2, 1],

        'BTN_WEST': [0, 1],
        'BTN_SOUTH': [0, -1],
        'BTN_EAST': [1, 1],
        'BTN_NORTH': [1, -1],
        'BTN_TL': [2, -1],
        'BTN_TR': [2, 1],

    }

    return keymap

           
def update_value(mapping, fields, active_field, attribute,
                 step_gain, step_sizes):

    '''
    '''
    step_sizes = step_sizes[attribute][mapping[0]]
    fields[active_field][attribute][mapping[0]] += (
        (step_sizes * mapping[1]) * step_gain)
    return fields
                                                    

def drawField(fields, field):
    # update parameters of each field and draw
    handle = fields[field]['handle']
    handle.colorSpace = fields[field]['colorSpace']
    handle.color = fields[field]['color']
    handle.size = fields[field]['size'][:2]
    handle.pos = fields[field]['position'][:2]
    handle.draw()
