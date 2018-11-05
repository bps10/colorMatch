from __future__ import division
import numpy as np
import os, pickle, datetime

from colormath.color_objects import LabColor, xyYColor, sRGBColor
from colormath.color_conversions import convert_color
import json
from psychopy import monitors
from psychopy.tools import colorspacetools as ct


def gammaCorrect(invGammaTable, rgb):
    # convert rgb in range -1:1 to range 0:255
    rgb = np.round((rgb + 1) / 2 * 254, 0).astype(int)
    corrected_rgb = invGammaTable[rgb, [0, 1, 2]]
    corrected_rgb = corrected_rgb * 2 - 1
    return corrected_rgb
    
def gammaInverse(monitorName, currentCalibName):
    mon = monitors.Monitor(monitorName)
    mon.setCurrent(currentCalibName)
    gammaGrid = mon.getGammaGrid()
    minLum = gammaGrid[:, 0]
    maxLum = gammaGrid[:, 1]
    gamma = gammaGrid[:, 2]
    a = gammaGrid[:, 3]
    b = gammaGrid[:, 4]
    k = gammaGrid[:, 5]
    xx = np.zeros((255, 4))
    for i in range(4):
        yy = np.linspace(minLum[i], maxLum[i], 255)
        xx[:, i] = -(np.log(1e-6+k[i] / (yy - a[i]) - 1) + b[i]) / gamma[i]
    invGammaTable = xx[:, 1:] # 0 column = luminance which we don't need
    invGammaTable[np.isnan(invGammaTable)] = 0
    invGammaTable /= invGammaTable.max(0)
    return invGammaTable
    
    
def convertHSL2LMS_RGB_LAB_XY(color):
    from psychopy.tools import colorspacetools as cspace
    LMS2RGB = json.load(open('LightCrafter.json','r'))['gamma_29Oct2018']['lms_rgb']['__ndarray__']
    RGB2LMS = np.linalg.inv(LMS2RGB)
    # need to figure out HSL to RGB and then RGB to LMS
    rgb = cspace.hsv2rgb(color)
    rgb = (rgb+1)/2.0
    lms = np.dot(RGB2LMS, rgb)
    rgb = sRGBColor(*rgb)
    lab = np.array(convert_color(rgb, LabColor).get_value_tuple())
    xy = np.array(convert_color(rgb, xyYColor).get_value_tuple())
    return lms, rgb, lab, xy
    
def random_color(colorSpace):
    if colorSpace == 'hsv':
        c = np.array([np.random.randint(0, 360),
                      np.random.random_sample(1),
                      np.random.random_sample(1)])
    elif colorSpace == 'dkl':
        c = np.array([np.random.randint(-180, 180),
                      np.random.randint(-180, 180),
                      np.random.random_sample(1) * 2 - 1]) 
    elif colorSpace == 'rgb':
        c = np.asrray([np.random.random_sample(1) * 2 - 1,
                      np.random.random_sample(1) * 2 - 1,
                      np.random.random_sample(1) * 2 - 1])     
    return c

def set_color_to_white(colorSpace):
    if colorSpace == 'hsv':
        c = np.array([0, 0, 0.5])
    elif colorSpace == 'rgb':
        c = np.array([0.1, 0.1, 0.1])
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
            
    elif colorSpace == 'hsv':
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
        'rshift': [2, -1],
        'lshift': [2, -1],        
        'return': [2, 1],

        'BTN_NORTH': [0, 1],
        'BTN_SOUTH': [0, -1],
        'BTN_EAST': [1, 1],
        'BTN_WEST': [1, -1],
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
                                                    

def drawField(fields, field, invGammaTable):
    # convert hsv to rgb
    hsv = fields[field]['color']
    # double check colors
    hsv = check_color(hsv, 'hsv')
    rgb = ct.hsv2rgb(hsv)
    # gamma correct
    rgb = gammaCorrect(invGammaTable, rgb)

    # update parameters of each field and draw
    handle = fields[field]['handle']
    handle.colorSpace = 'rgb'
    handle.color = rgb
    handle.size = fields[field]['size'][:2]
    handle.pos = fields[field]['position'][:2]
    handle.draw()


def getColorMatchDir():
    '''
    '''
    return os.path.dirname(os.path.abspath(__file__))


def getFields(parameters, colorSpace, blackColor, canvasSize):
    '''
    '''
    if 'lastFields' in parameters:
        # read lastFields from file
        fields = pickle.load(open(parameters['lastFields'], "r"))
    else:
        # set up defaults if subject data does not exist
        fields = {
            'canvas': {
                       'colorSpace': colorSpace,
                       'color': blackColor,
                       'size': canvasSize,
                       'position': np.array([0, 0., 0]),
            },               
            'rect': {
                     'colorSpace': colorSpace,
                     'color': np.array([50, 0.5, 0.5]),
                     'size': np.array([0.95, 0.95, 0]),
                     'position': np.array([-1., 0., 0]),
            },
            'match': {
                      'colorSpace': colorSpace,
                      'color':  set_color_to_white('hsv'),
                      'size': np.array([parameters['OzSize'][0],
                                        parameters['OzSize'][1], 0]),
                      'position': np.array([-1., 0., 0]),
            },
            'fixation': {
                         'colorSpace': colorSpace,                 
                         'color': np.array([90., 0, 0.9]),
                         'size': np.array([0.05, 0.05, 0]),
                         'position': np.array([0., 0., 0]),
            },
            'AObackground': {
                             'colorSpace': colorSpace,
                             'color': np.array([90, 0.1, 0.4]),
                             'size': np.array([0.95, 0.95, 0]),
                             'position': np.array([1., 0., 0]),
            },             
        }    
    return fields


def getDefaultParameters():

    params = {'isBitsSharp': False,
              'noBitsSharp': True,
              'age': 30.0,
              'leftEye': False,
              'rightEye': True,
              'OzWidth': '0.2',
              'OzHeight': '0.45',
              'ID': 'test',
              'screen': 0,
              'offlineMatch': False,
              'onlineMatch': True,
              }
    return params


def saveData(parameters, results, fields):
    
    # save
    basedir = getColorMatchDir()
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
