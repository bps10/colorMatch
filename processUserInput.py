from __future__ import division
import pandas as pn
import numpy as np
import pickle, os
import copy
import colorSpace as cs
import plotResults as plot


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

def updateValue(mapping, fields, active_field, attribute,
                 step_gain, step_sizes):
    '''
    '''
    step_sizes = step_sizes[attribute][mapping[0]]
    fields[active_field][attribute][mapping[0]] += (
        (step_sizes * mapping[1]) * step_gain)
    return fields

def updateResultsAndPlot(results, fields, confidence, trial_params, trial,
                         background, Lab_lum, subjectID, alpha=0.66):
    '''
    '''
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
    temp_result = copy.deepcopy(results)
    del temp_result['tracked_rect_color']
    
    _results = pn.DataFrame(temp_result)
    
    # update plots in color space
    matchRGB = cs.hsv2rgb(_results.hue, _results.saturation,
                          _results.value)
    matchXYZ = cs.rgb2xyz(matchRGB)
    
    # Convert to LMS and then MB space
    matchLMS = cs.rgb2lms(matchRGB)
    matchMB = cs.lms2mb(matchLMS)
    #matchMB =  matchMB * alpha + (1 - alpha) * np.array([background.l,
    #                                                     background.s])
    # Convert to Lab space
    _matchxyY = cs.xy2xyY(matchXYZ[:, :2], Lab_lum)
    _matchXYZ = cs.xyY2XYZ(_matchxyY)
    matchLab = cs.XYZ2Lab(_matchXYZ)
    _results['L*'] = matchLab[:, 0]
    _results['a*'] = matchLab[:, 1]
    _results['b*'] = matchLab[:, 2]
    
    _results['CIE_x'] = matchXYZ[:, 0]
    _results['CIE_y'] = matchXYZ[:, 1]
    _results['CIE_z'] = matchXYZ[:, 2]

    _results['match_l'] = matchXYZ[:, 0] # matchMB[:, 0]
    _results['match_s'] = matchXYZ[:, 0] # matchMB[:, 1]

    plot.colorSpaces(_results, background, subjectID,
                     plotMeans=False, plotShow=False)

    return results

def updateFields(stage, onlineMatch):
    '''
    '''
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

    elif stage == 4 and onlineMatch:
        active_field = 'match'
        attribute = 'color'
        field_list = ['canvas', 'rect', 'match', 'AObackground',
                      'fixation']

    # stage 5 is where the subject gives an integer
    # confidence score indicating how close the match was
    elif stage == 5 and onlineMatch:
        active_field = 'match'
        attribute = 'color'
        field_list = ['canvas', 'rect', 'match', 'AObackground',
                      'fixation']
    elif stage == 5 and not onlineMatch:
        active_field = 'rect'
        attribute = 'color'
        field_list = ['canvas', 'rect', 'AObackground', 'fixation']

    return active_field, attribute, field_list
