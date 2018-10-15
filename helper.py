from __future__ import division
import numpy as np


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
        if color[0] < 0:
            color[0] = 0
            print 'Hue cannot exceed 0: setting to 0'
        if color[0] > 360:
            color[0] = 360
            print 'Hue cannot exceed 360: setting to 360'
        if color[1] < 0:
            color[1] = 0
            print 'Saturation cannot exceed 0: setting to 0'
        if color[1] > 1:
            color[1] = 1
            print 'Saturation cannot exceed 1: setting to 1'
        if color[2] > 1:
            color[2] = 1
            print 'Lightness cannot exceed 1: setting to 1'
        if color[2] < 0:
            color[2] = 0
            print 'Lightness cannot exceed 0: setting to 0'

    return color
