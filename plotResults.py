from __future__ import division
import datetime, os
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


def hueAndSaturation(data, savename, groupbyVar='new_MB_l'):
    '''
    '''
    data.groupby(['L_intensity', 'M_intensity','new_MB_l']
                )['hue', 'saturation'].agg(['mean', 'std'])

    meanHueSat = data.groupby(
        [groupbyVar])['hue', 'saturation'].agg(['mean', 'std'])
    meanHueSat

    fig = plt.figure(figsize=(4, 8))
    fig.set_tight_layout(True)
    ax1 = fig.add_subplot(211)

    ax1.plot(data.new_MB_l, data.hue, 'k.')
    meanHueSat['hue']['mean'].plot(
        axes=ax1, yerr=meanHueSat['hue']['std'].values)

    ax1.set_xlabel('OZ specified L/(L+M)')
    ax1.set_ylabel('hue angle')
    ax1.set_ylim([0, 180])
    ax1.set_frame_on(False)

    ax2 = fig.add_subplot(212)

    ax2.plot(data.new_MB_l, data.saturation, 'k.')
    meanHueSat['saturation']['mean'].plot(
        axes=ax2, yerr=meanHueSat['saturation']['std'].values)

    ax2.set_xlabel('OZ specified L/(L+M)')
    ax2.set_ylabel('saturation')
    ax2.set_ylim([0, 1])
    ax2.set_frame_on(False)

    directory = os.path.join('dat', savename)
    h.checkDir(directory)
    fig.savefig(os.path.join(directory, savename + '_Oz_Exp_Hue_Saturation.pdf'))
    fig.savefig(os.path.join(directory, savename + '_Oz_Exp_Hue_Saturation.png'))
    plt.show(block=False)


def specifiedVsObserved(data, savename, comparison='match_l'):
    '''
    '''
    sem = lambda x: np.std(x) / np.sqrt(len(x))
    group = data.groupby('new_MB_l')[
        ['match_l', 'match_s']].agg(
            [('mean', np.mean), ('sem', sem)])

    fig = plt.figure()
    fig.set_tight_layout(False)
    ax = fig.add_subplot(111)
    ax.set_frame_on(False)

    ax.set_aspect(8)

    ax.errorbar(group.index, group[comparison]['mean'],
                yerr=group[comparison]['sem'], fmt='k.-')

    ax.set_xlabel('Oz specified ' + comparison[-1].upper() + '/(L+M)')
    ax.set_ylabel('Projector matched ' + comparison[-1].upper() + '/(L+M)')

    directory = os.path.join('dat', savename)
    h.checkDir(directory)
    fig.savefig(os.path.join(directory,
                             comparison + '_DeliveredVSMeasured.png'))
    fig.savefig(os.path.join(directory,
                             comparison + '_DeliveredVSMeasured.pdf'))


def colorSpaces(data, background, savename=None, plotMeans=True,
                plotShow=True, groupbyVar='new_MB_l'):
    '''
    '''
    # plot
    fig = plt.figure(figsize=(10, 10))
    fig.set_tight_layout(True)
    ax1 = fig.add_subplot(221)
    ax1.set_aspect('equal')

    ax1.plot(XYZlocus[:, 0], XYZlocus[:, 1], 'k-')
    ax1.plot(primariesXYZ[:, 0], primariesXYZ[:, 1], 'k--')
    ax1.plot(background.CIE_x, background.CIE_y, 'bs')

    ax1.plot(data.CIE_x, data.CIE_y, 'k.')

    ax1.set_xlim([0, 0.85])
    ax1.set_ylim([0, 0.85])
    ax1.set_xlabel('CIE x')
    ax1.set_ylabel('CIE y')
    ax1.set_title('CIE xy')

    ax2 = fig.add_subplot(222)
    ax2.set_aspect('equal')
    ax2.plot(background['a*'], background['b*'], 'bs')
    ax2.plot(data['a*'], data['b*'], 'k.')

    ax2.set_xlim(-65, 40)
    ax2.set_ylim(-40, 65)
    ax2.set_xlabel('a*')
    ax2.set_ylabel('b*')
    ax2.set_title('CIE Lab')

    ax3 = fig.add_subplot(223)

    ax3.plot(mb.l, mb.s, 'k-')
    ax3.plot(primariesMB[:, 0], primariesMB[:, 1], 'k--')
    ax3.plot(data.new_MB_l,
             np.ones(len(data.new_MB_l)) * background.s.values, 'b.')
    ax3.plot(background.l, background.s, 'bs')
    ax3.plot([0, background.l], [0, background.s], 'g-')
    ax3.plot([1, background.l], [0, background.s], 'r-')

    ax3.plot(data.match_l, data.match_s, 'k+')

    ax3.set_xlim([0., 1])
    ax3.set_ylim([0, 0.15])
    ax3.set_xlabel('L/(L+M)')
    ax3.set_ylabel('S/(L+M)')
    ax3.set_title('MacLeod-Boynton')

    ax4 = fig.add_subplot(224)

    ax4.plot(mb.l, mb.s, 'k-')
    ax4.plot(primariesMB[:, 0], primariesMB[:, 1], 'k--')
    ax4.plot(data.new_MB_l,
             np.ones(len(data.new_MB_l)) * background.s.values, 'b.')
    ax4.plot(background.l, background.s, 'bs')

    ax4.plot(data.match_l, data.match_s, 'k+')

    ax4.set_xlim([0.6, 0.75])
    ax4.set_ylim([0, 0.05])
    ax4.set_xlabel('L/(L+M)')
    ax4.set_ylabel('S/(L+M)')
    ax4.set_title('MacLeod-Boynton (zoom)')

    if plotMeans:
        sem = lambda x: np.std(x) / np.sqrt(len(x))
        meanData = data.groupby(groupbyVar)[
            ['CIE_x', 'CIE_y', 'match_l', 'match_s', 'a*', 'b*']].agg(
                [('mean', np.mean), ('sem', sem)])

        average_l = meanData['match_l']['mean'].values
        sem_l = meanData['match_l']['sem'].values
        average_s = meanData['match_s']['mean'].values
        sem_s = meanData['match_s']['sem'].values
        average_x = meanData['CIE_x']['mean'].values
        sem_x = meanData['CIE_x']['sem'].values
        average_y = meanData['CIE_y']['mean'].values
        sem_y = meanData['CIE_y']['sem'].values

        average_a = meanData['a*']['mean'].values
        sem_a = meanData['a*']['sem'].values
        average_b = meanData['b*']['mean'].values
        sem_b = meanData['b*']['sem'].values

        ax1.errorbar(average_x, average_y, xerr=sem_x, yerr=sem_y, fmt='r.-')
        ax2.errorbar(average_a, average_b, xerr=sem_a, yerr=sem_b, fmt='r.-')
        ax4.errorbar(average_l, average_s, xerr=sem_l, yerr=sem_s, fmt='r.-')

    ax1.set_frame_on(False)
    ax2.set_frame_on(False)
    ax3.set_frame_on(False)
    ax4.set_frame_on(False)

    directory = os.path.join('dat', savename)
    h.checkDir(directory)
    fig.savefig(os.path.join(directory, savename + '_Oz_Exp_trials.pdf'))
    fig.savefig(os.path.join(directory, savename + '_Oz_Exp_trials.png'))
    fig.savefig('Color_Space_Visualization_Oz.png')

    if not plotShow:
        plt.close()
