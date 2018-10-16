import PySimpleGUI27 as sg
import numpy as np



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
         sg.Radio('true', 'true', key='bitsSharp'),
         sg.Radio('false', 'false', key='bitsSharp', default=True)],        
        [sg.Submit(), sg.Cancel()]
    ]

    event, values = window.Layout(layout).Read()
    values['OzSize'] = np.array([float(values['Oz_height']),
                                 float(values['Oz_width'])])
    values['age'] = float(values['age'])
    return values

'''
class parameters(object):
    def __init__(self):
        self.Start()
        
    def Start(self):
        with gui('Matching parameters') as app:
            #app.setBg('lightBlue')

            with app.labelFrame('Subject information'):
                app.addLabelEntry('ID')
                app.setEntryDefault('ID', 'Test')
                
                app.addLabel('Age', 'Age')    
                app.addNumericEntry('Age')
                app.setEntryDefault('Age', 30)
                
                app.addLabel('Eye')
                app.addRadioButton('Eye', 'right')
                app.addRadioButton('Eye', 'left')
    
            with app.labelFrame('Experiment information', row=1, column=0):
                app.addLabel('Oz_height', 'Oz height')
                app.addNumericEntry('Oz_height')
                app.setEntryDefault('Oz_height', 0.45)
                app.addLabel('Oz_width', 'Oz width')    
                app.addNumericEntry('Oz_width')    
                app.setEntryDefault('Oz_width', 0.2)
            
                app.addButton("submit", self.press)
                app.enableEnter(self.press)
                
            self.app = app    
            app.go()
            print self.parameters
                    
    def press(self, btn):
        self.parameters = {'ID': self.app.getEntry('ID'),
                      'age': self.app.getEntry('Age'),
                      'eye': self.app.getRadioButton('Eye'),
                      'OzSize': np.array([self.app.getEntry('Oz_width'),
                                          self.app.getEntry('Oz_height')])
        }
        #self.app.stop()        
'''
