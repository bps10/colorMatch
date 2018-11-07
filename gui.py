import PySimpleGUI27 as sg
import numpy as np
import os, pickle, sys

import helper as h


basedir = h.getColorMatchDir()
try:
    # get path to last used params
    f = open(os.path.join(basedir, 'dat', 'lastParameters.txt'), 'r')
    fpath = f.read()
    f.close()
    # get fname from directory input
    f = open(fpath, "rb")
    savedParams = pickle.load(f)
    f.close()

except IOError:
    # get fname from directory input
    savedParams = h.getDefaultParameters()


def setup_layout(params):

    layout = [
        [sg.Text('Subject information')],
        [sg.Text('new ID', size=(30, 1)),
         sg.InputText(params['ID'], key='ID')],
        [sg.Text('Load prior subject data')],
        [sg.In(),
         sg.FileBrowse(button_text='Browse',
                       initial_folder=os.path.join('colorMatch', 'dat'),
                       file_types=(('pickle', '*.pkl'),)),
         sg.ReadButton('Load')],
        [sg.Text('Age', size=(30, 1)),
         sg.InputText(params['age'], key='age')],

        [sg.Text('Eye', size=(30, 1)),
         sg.Radio('left', 'eye', key='leftEye'),
         sg.Radio('right', 'eye', key='rightEye', default=True)],
        [sg.Text('_'  * 60)],
        [sg.Text('Experiment information')],
        [sg.Text('Oz height', size=(30, 1)),
         sg.InputText(params['OzHeight'], key='OzHeight')],
        [sg.Text('Oz width', size=(30, 1)),
         sg.InputText(params['OzWidth'], key='OzWidth')],

        [sg.Text('Bits #', size=(30, 1)),
         sg.Radio('true', 'bitsSharp', key='isBitsSharp'),
         sg.Radio('false', 'bitsSharp', key='noBitsSharp', default=True)],

        [sg.Text('Screen (0=local, 1=projector)', size=(30,1)),
         sg.InputText(params['screen'], key='screen')],

        [sg.Text('Online match mode', size=(30, 1)),
         sg.Radio('true', 'matchMode', key='onlineMatch', default=True),
         sg.Radio('false', 'matchMode', key='offlineMatch')],

        [sg.Submit(), sg.Cancel()]
    ]
    return layout


def updateParams(window, params):
    for p in ['age', 'ID', 'OzHeight', 'OzWidth', 'leftEye',
              'rightEye', 'isBitsSharp', 'noBitsSharp', 'screen',
              'offlineMatch', 'onlineMatch']:
        window.FindElement(p).Update(params[p])

def parameters():

    layout = setup_layout(savedParams)
    window = sg.Window('Matching parameters').Layout(layout)
    # need to run this to update radio buttons
    updateParams(window, savedParams)

    # You need to perform a ReadNonBlocking on your window every now and then or
    # else it won't refresh.
    #
    # your program's main loop
    while (True):
        # This is the code that reads and updates your window
        event, values = window.ReadNonBlocking()
        if event == 'Submit':
            break
        elif event in ['Quit', 'Cancel', 'Exit'] or values is None:
            values = None
            break
        elif event == 'Load':
            if len(values[0]) > 5:
                print('Opening parameters: ' + values[0])
                loadParams = pickle.load(open(values[0], "r"))
                updateParams(window, loadParams)

    window.CloseNonBlocking()   # Don't forget to close your window!

    if values is not None:
        values['OzSize'] = np.array([float(values['OzHeight']),
                                     float(values['OzWidth'])])
        values['age'] = float(values['age'])
        values['screen'] = int(values['screen'])
        if 'lastFields' in savedParams:
            values['lastFields'] = savedParams['lastFields']

        return values

    else:
        print 'Program cancelled by user.'
        # program was cancelled
        sys.exit()
