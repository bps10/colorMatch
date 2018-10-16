import PySimpleGUI27 as sg
import numpy as np


# write a function to load pickle files
# get fname from directory input
# values = pickle.load(open('save.p', "rb"))
# call function that sets new values for each input box

def parameters():

    window = sg.Window('Matching parameters')
    layout = [
        [sg.Text('Subject information')],
        [sg.Text('ID', size=(15, 1)),
         sg.InputText('10001', key='ID')],
        [sg.Text('Age', size=(15, 1)),
         sg.InputText('30', key='age')],
        [sg.Text('Eye', size=(15, 1)),
         sg.Radio('left', 'left', key='eye'),
         sg.Radio('right', 'right', key='eye', default=True)],
        [sg.Text('Experiment information')],
        [sg.Text('Oz height', size=(15, 1)),
         sg.InputText('0.45', key='Oz_height')],
        [sg.Text('Oz width', size=(15, 1)),
         sg.InputText('0.2', key='Oz_width')],
        [sg.Text('Bits #', size=(15, 1)),
         sg.Radio('true', 'bitsSharp', key='bitsSharp'),
         sg.Radio('false', 'bitsSharp', key='bitsSharp')],
        [sg.Submit(), sg.Cancel()]
    ]

    event, values = window.Layout(layout).Read()
    values['OzSize'] = np.array([float(values['Oz_height']),
                                 float(values['Oz_width'])])
    values['age'] = float(values['age'])
    print values['bitsSharp']
    return values

