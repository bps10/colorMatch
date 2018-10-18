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
    savedParams = pickle.load(open(fpath, "r"))

except IOError:
    fpath = os.path.join(basedir, 'dat', 'default', 'parameters_default.pkl')    
    # get fname from directory input
    savedParams = pickle.load(open(fpath, "r"))

def setup_layout(params):

    layout = [
        [sg.Text('Subject information')],
        [sg.Text('new ID', size=(15, 1)),
         sg.InputText(params['ID'], key='ID')],
        [sg.Text('Load prior subject data')],
        [sg.In(),
         sg.FileBrowse(button_text='Browse',
                       initial_folder=os.path.join('colorMatch', 'dat'),
                       file_types=(('pickle', '*.pkl'),)),
         sg.ReadButton('Load')],
        [sg.Text('Age', size=(15, 1)),
         sg.InputText(params['age'], key='age')],
        
        [sg.Text('Eye', size=(15, 1)),
         sg.Radio('left', 'eye', key='leftEye'),
         sg.Radio('right', 'eye', key='rightEye', default=True)],
        [sg.Text('_'  * 60)],
        [sg.Text('Experiment information')],
        [sg.Text('Oz height', size=(15, 1)),
         sg.InputText(params['Oz_height'], key='Oz_height')],
        [sg.Text('Oz width', size=(15, 1)),
         sg.InputText(params['Oz_width'], key='Oz_width')],
        
        [sg.Text('Bits #', size=(15, 1)),
         sg.Radio('true', 'bitsSharp', key='isBitsSharp'),
         sg.Radio('false', 'bitsSharp', key='noBitsSharp', default=True)],
        
        [sg.Submit(), sg.Cancel()]
    ]
    return layout

def parameters():
 
    layout = setup_layout(savedParams)
    window = sg.Window('Matching parameters').Layout(layout)
    
    #event, values = window.Layout(layout).Read()
    
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
                print 'Opening parameters: ' + values[0]
                loadParams = pickle.load(open(values[0], "rb"))
                for p in ['age', 'ID', 'Oz_height', 'Oz_width', 'leftEye',
                          'rightEye', 'isBitsSharp', 'noBitsSharp']:
                    window.FindElement(p).Update(loadParams[p])

    window.CloseNonBlocking()   # Don't forget to close your window!

    if values is not None:
        values['OzSize'] = np.array([float(values['Oz_height']),
                                     float(values['Oz_width'])])
        values['age'] = float(values['age'])
        if 'lastFields' in savedParams:
            values['lastFields'] = savedParams['lastFields']

        return values
    
    else:
        print 'Program cancelled by user.'
        # program was cancelled
        sys.exit()
