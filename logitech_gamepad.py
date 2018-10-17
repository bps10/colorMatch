from inputs import devices, get_gamepad, get_key
import time

    
def isGamePad():
    if devices.gamepads != []:
        return True
    else:
        return False

def getKeyPress():
    '''
    '''
    code = None    
    modifier = False

    while True:
        events = get_device()
        for event in events:
            if event.ev_type == 'Key' and event.state == 0:
                code = event.code
            if event.ev_type == 'Absolute':
                if event.code == 'ABS_Z' or event.code == 'ABS_RZ':
                    modifier = True
                if event.code == 'ABS_HAT0X' or event.code == 'ABS_HAT0Y':
                    code = 'ABS_HAT'
        if code != None:
            return code, modifier

        
if isGamePad():
    get_device = get_gamepad
else:
    get_device = get_key
            
if __name__ == '__main__':
    if isGamePad():
        print getKeyPress()
