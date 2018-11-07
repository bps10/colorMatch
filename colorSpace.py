from __future__ import division
import numpy as np
import json, os
from psychopy.tools import colorspacetools as cspace


thisdir = os.path.dirname(os.path.abspath(__file__))


def normalize_rows(matrix):
    '''
    '''
    if matrix.ndim > 1:
        matrix = np.dot(matrix.T, np.diag(1 / matrix.sum(1))).T
    else:
        matrix /= matrix.sum()
    return matrix


def getXYZ_LMS_RGB(plot_basis=False):
    '''
    '''
    # set wavelengths to interpolate all spectra into
    wavelengths = np.arange(390, 730, 1)

    # load in the measured gamut
    _rgb = np.asarray(json.load(open(os.path.join(thisdir, 'assets',
        'LightCrafter.json'),'r'))['gamma_29Oct2018']['spectraRGB']['__ndarray__']).T
    wvlen = np.asarray(json.load(open(os.path.join(thisdir, 'assets',
        'LightCrafter.json'),'r'))['gamma_29Oct2018']['spectraNM']['__ndarray__'])
    # interpolate
    RGB = np.zeros((len(wavelengths), 3))
    for i in range(3):
        RGB[:, i] = np.interp(wavelengths, wvlen, _rgb[:, i])

    # load spectral sensitivity of LMS cones
    _spectsens = np.loadtxt(os.path.join(thisdir, 'assets', 'linss2_10e_1_8dp.csv'),
                            delimiter=',')
    wvlen = _spectsens[:, 0]
    # interpolate
    LMS = np.zeros((len(wavelengths), 3))
    for i in range(3):
        LMS[:, i] = np.interp(wavelengths, wvlen, _spectsens[:, i+1])
        LMS[:, i] /= LMS[:, i].max()

    # load XYZ functions
    _xyz = np.loadtxt(os.path.join(thisdir, 'assets', 'lin2012xyz2e_1_7sf.csv'),
                      delimiter=',')
    wvlen = _xyz[:, 0]
    # interpolate
    XYZ = np.zeros((len(wavelengths), 3))
    for i in range(3):
        XYZ[:, i] = np.interp(wavelengths, wvlen, _xyz[:, i+1])

    if plot_basis:
        fig = plt.figure(figsize=(12, 3))
        ax = fig.add_subplot(131)
        plt.plot(wavelengths, XYZ)

        ax = fig.add_subplot(132)
        plt.plot(wavelengths, LMS)

        ax = fig.add_subplot(133)
        plt.plot(wavelengths, RGB)
    return XYZ, LMS, RGB


def genSystemMats(XYZ, LMS, RGB):
    '''
    '''
    # Now create system matrices
    RGB2LMS = np.dot(LMS.T, RGB)
    RGB2XYZ = np.dot(XYZ.T, RGB)
    # a sanity check LMS2XYZ should equal values from Stockman and Sharpe
    # LMS2XYZ = np.array([[1.94735469, -1.41445123, 0.36476327],
    #                    [0.68990272, 0.34832189, 0],
    #                    [0, 0, 1.93485343]])
    LMS2XYZ = np.linalg.inv(np.dot(RGB2LMS, np.linalg.inv(RGB2XYZ)))
    return RGB2LMS, RGB2XYZ, LMS2XYZ


def hsv2rgb(hue, saturation, value):
    '''
    '''
    hsv = np.array([hue, saturation, value]).T
    rgb = cspace.hsv2rgb(hsv)
    return (rgb + 1) / 2.0


def rgb2xyz(rgb):
    '''
    '''
    xyz = np.dot(RGB2XYZ, rgb.T)
    xyz = normalize_rows(xyz.T)
    return xyz


def lms2xyz(lms):
    '''
    '''
    xyz = np.dot(LMS2XYZ, lms.T)
    xyz = normalize_rows(xyz.T)
    return xyz


def rgb2lms(rgb):
    '''
    '''
    return np.dot(RGB2LMS, rgb.T).T


def lms2mb(lms):
    '''
    '''
    if lms.ndim == 1:
        lms = np.reshape(lms, (1, len(lms)))

    # Taken from the Stockman and Sharpe (2000) fundamentals
    # These are the scalars necessary to convert into MB space.
    # Will make L+M scaled correctly to generate luminance
    LMS2MB = np.array([0.674132, 0.356683, 0.0466886])
    lms = LMS2MB * lms
    lms = normalize_rows(lms)

    # luminance is L+M
    luminance = lms[:, :2].sum(1)

    mb = np.zeros((lms.shape[0], 2))
    mb[:, 0] = lms[:, 0] / luminance
    mb[:, 1] = lms[:, 2] / luminance
    return mb


XYZ, LMS, RGB = getXYZ_LMS_RGB()
RGB2LMS, RGB2XYZ, LMS2XYZ = genSystemMats(XYZ, LMS, RGB)

