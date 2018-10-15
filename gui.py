from psychopy import gui
import numpy as np


def parameters():

    handle = gui.Dlg(title='Matching parameters')
    handle.addText('Subject information')
    handle.addField('ID:', 'Test')
    handle.addField('Age:', 30)
    handle.addField('Eye:', 'right')
    handle.addText('Experiment information')
    handle.addField('Oz height:', 0.45)
    handle.addField('Oz width:', 0.2)
    
    parameters = handle.show()
    
    if handle.OK:
        parameters = {'ID': parameters[0],
                      'age': parameters[1],
                      'eye': parameters[2],
                      'OzSize': np.array([parameters[3], parameters[4]])
                      }
        
        return parameters
    else:
        print 'user cancelled'
