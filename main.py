import pythoncom
from keyhook import registerEvent
from poe import globals_init

def main():
    globals_init()
    registerEvent()
    pythoncom.PumpMessages() 

if __name__ == "__main__":     
    main()
