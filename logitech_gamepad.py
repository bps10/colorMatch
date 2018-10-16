import evdev

def getKeyPress():
    device = evdev.InputDevice('/dev/input/event17')
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:            
            keycode = evdev.categorize(event).keycode[0]
            timestamp = event.timestamp()
            return keycode, timestamp        

if __name__ == '__main__':
    print getKeyPress()
