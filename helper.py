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

    map = {
        'q': lambda keepGoing: keepGoing = False,
        
        'up': lambda x: x['color'][0] + 1 * step_gain,
        'down': lambda x: x['color'][0] - 1 * step_gain,
        'right': lambda x: x['color'][1] + 0.02 * step_gain,
        'left': lambda x: x['color'][1] - 0.02 * step_gain,
        'shift': lambda x: x['color'][2] - 0.02 * step_gain,
        'return': lambda x: x['color'][2] + 0.02 * step_gain,

        'f': lambda x: x['position'][0] - 0.1 * step_gain,
        'g': lambda x: x['position'][0] + 0.1 * step_gain,
        't': lambda x: x['position'][1] - 0.1 * step_gain,
        'v': lambda x: x['position'][1] + 0.1 * step_gain,

        'h': lambda x: x['size'][0] - 0.05 * step_gain,
        'j': lambda x: x['size'][0] + 0.05 * step_gain,
        'n': lambda x: x['size'][1] - 0.05 * step_gain,
        'u': lambda x: x['size'][1] + 0.05 * step_gain,
    }

        
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
    
