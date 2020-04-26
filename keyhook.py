# -*- coding: utf-8 -*- #
import os
import PyHook3
from poe import *
from winfo import *

pause = False
pf = POEFunctions()

def onMouseEvent(event): 
    global pause
    if pause == True:
        return True
    if event.MessageName == "mouse wheel":
        if event.Wheel == 1:
            pf.drug_start()
            pf.timer_key_start()
        elif event.Wheel == -1:
            pf.timer_key_stop()
            pf.drug_stop()
            #pf.stop_all_func()
    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return False
    
def onKeyEvent(event):
    #print(event.Key)
    global pause
    if event.Key == "F2":
        if pause == False:
            pause = True
        else:
            pause = False
    if pause == True:
        return True
    elif event.Key == "F7":
        #m.move(126, 625)
        pf.affix_alter_toggle()
    elif event.Key == "F9":
        pf.func_click_toggle("ctrl")
    elif event.Key == "F10":
        pf.func_click_toggle("shift")
    elif event.Key == "F11":
        pf.click_grids_toggle()
    elif event.Key == "F12":
        pf.chance_toggle()
    elif event.Key == "F8":
        pf.msg_toggle()
    elif event.Key == "F4":
        #pf.get_cursor_color()
        info = GetForegroundWindowInfo()
        ShowWindowInfo(info)
    elif event.Key == "F6":
        x, y = m.position()
        print(x,y)
        m.click(x,y,1)
    elif event.Key == "F3":
        #print("exit")
        pf.stop_all_func()
        os._exit(0)
    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True

def registerEvent():
    #print("register event")
    # create the hook mananger
    hm = PyHook3.HookManager()
    # register two callbacks
    #hm.MouseAll = onMouseEvent
    hm.MouseWheel = onMouseEvent
    hm.KeyDown = onKeyEvent
    # hook into the mouse and keyboard events
    hm.HookMouse()
    hm.HookKeyboard()
