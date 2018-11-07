from __future__ import division
import numpy as np
import pandas as pn
import matplotlib.pylab as plt

import helper as h
import colorSpace as cs


# Load in spectrum locus and primaries
mb, primariesMB = h.loadMBandLightCrafter()

XYZ, LMS, RGB = cs.getXYZ_LMS_RGB(plot_basis=False)

XYZlocus = cs.lms2xyz(LMS)
primariesXYZ = cs.rgb2xyz(np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))

primariesXYZ = np.concatenate([primariesXYZ, [primariesXYZ[0, :]]])
primariesMB = np.vstack([primariesMB, primariesMB[0, :]])


def hueAndSaturation(data, name):
    '''
    '''
    data.groupby(['L_intensity', 'M_intensity','new_MB_l']
                )['hue', 'saturation'].agg(['mean', 'std'])

    meanHueSat = data.groupby(
        ['new_MB_l'])['hue', 'saturation'].agg(['mean', 'std'])
    meanHueSat

    fig = plt.figure(figsize=(4, 8))
    ax1 = fig.add_subplot(211)

    ax1.plot(data.new_MB_l, data.hue, 'k.')
    meanHueSat['hue']['mean'].plot(
        axes=ax1, yerr=meanHueSat['hue']['std'].values)

    ax1.set_xlabel('OZ specified L/(L+M)')
    ax1.set_ylabel('hue angle')

    ax1.set_ylim([0, 180])

    ax2 = fig.add_subplot(212)

    ax2.plot(data.new_MB_l, data.saturation, 'k.')
    meanHueSat['saturation']['mean'].plot(
        axes=ax2, yerr=meanHueSat['saturation']['std'].values)

    ax2.set_xlabel('OZ specified L/(L+M)')
    ax2.set_ylabel('saturation')

    ax2.set_ylim([0, 1])

    fig.savefig('Oz_Exp_hue_saturation_' + name + '.pdf')


def colorSpaces(data, background, savename=None, plotMeans=True):
    '''
    '''
    if not savename:
        savename = datatime.today().strftime('%Y_%d_%m')

    # plot
    fig = plt.figure(figsize=(14, 4))
    fig.tight_layout()
    ax1 = fig.add_subplot(131)

    ax1.plot(XYZlocus[:, 0], XYZlocus[:, 1], 'k-')
    ax1.plot(primariesXYZ[:, 0], primariesXYZ[:, 1], 'k--')
    ax1.plot(background.CIE_x, background.CIE_y, 'bs')

    ax1.plot(data.CIE_x, data.CIE_y, 'k.')

    ax1.set_xlim([0, 0.85])
    ax1.set_ylim([0, 0.85])
    ax1.set_xlabel('CIE x')
    ax1.set_ylabel('CIE y')

    ax2 = fig.add_subplot(132)

    ax2.plot(mb.l, mb.s, 'k-')
    ax2.plot(primariesMB[:, 0], primariesMB[:, 1], 'k--')
    ax2.plot(data.new_MB_l,
             np.ones(len(data.new_MB_l)) * background.s.values, 'b.')
    ax2.plot(background.l, background.s, 'ks')
    ax2.plot([0, background.l], [0, background.s], 'g-')
    ax2.plot([1, background.l], [0, background.s], 'r-')

    ax2.plot(data.match_l, data.match_s, 'k+')

    ax2.set_xlim([0.5, 1])
    ax2.set_ylim([0, 0.15])
    ax2.set_xlabel('L/(L+M)')
    ax2.set_ylabel('S/(L+M)')

    ax3 = fig.add_subplot(133)

    ax3.plot(mb.l, mb.s, 'k-')
    ax3.plot(primariesMB[:, 0], primariesMB[:, 1], 'k--')
    ax3.plot(data.new_MB_l,
             np.ones(len(data.new_MB_l)) * background.s.values, 'b.')
    ax3.plot(background.l, background.s, 'ks')

    ax3.plot(data.match_l, data.match_s, 'k+')


    ax3.set_xlim([0.6, 0.75])
    ax3.set_ylim([0, 0.05])
    ax3.set_xlabel('L/(L+M)')
    ax3.set_ylabel('S/(L+M)')

    if plotMeans:
        meanData = data.groupby('new_MB_l')[
            ['CIE_x', 'CIE_y', 'match_l', 'match_s']].agg(['mean', 'std'])
        average_l = meanData['match_l']['mean'].values
        average_s = meanData['match_s']['mean'].values
        average_x = meanData['CIE_x']['mean'].values
        average_y = meanData['CIE_y']['mean'].values

        ax1.plot(average_x, average_y, 'r.-')
        ax3.plot(average_l, average_s, 'r.-')

    fig.savefig(savename + 'Oz_Exp_trials.svg')
    fig.savefig(savename + 'Oz_Exp_trials.pdf')
    fig.savefig('Color_Space_Visualization_Oz.png')
