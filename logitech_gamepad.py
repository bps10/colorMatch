from inputs import devices, get_gamepad, get_key
import time, sys

    
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
                # fix windows quirk
                if sys.platform[:3] == 'win':
                    print code
                    # the select and back buttons are reversed for some reason
                    if code == 'BTN_START':
                        code = 'BTN_SELECT'
                    elif code == 'BTN_SELECT':
                        code = 'BTN_START'
                        
            if event.ev_type == 'Absolute':
                if event.code == 'ABS_Y':
                    code = 'BTN_MODE'
                if event.code == 'ABS_Z' or event.code == 'ABS_RZ':
                    modifier = True
                if event.code == 'ABS_HAT0X' or event.code == 'ABS_HAT0Y':
                    code = 'ABS_HAT'
                    # prevent double strikes
                    time.sleep(0.1)
                    # need to allow for release of button
                    get_device()
                    get_device()
                    
        if code != None:
            return code, modifier

        
if isGamePad():
    get_device = get_gamepad
else:
    get_device = get_key
            
if __name__ == '__main__':
    if isGamePad():
        print getKeyPress()
