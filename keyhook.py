# -*- coding: utf-8 -*- # 
import PyHook3
from poe import *

pause = False
def onMouseEvent(event): 
    global pause
    if pause == True:
        return True
    if event.MessageName == "mouse wheel":
        if event.Wheel == 1:
            start_attack()
        elif event.Wheel == -1:
            stop_attack()
            stop_shift_click_timer()
            stop_msg_timer()
#    elif event.MessageName == "":
#        pass
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
    if event.Key == "F8":
        msg_toggle()
    elif event.Key == "F9":
        shift_click_toggle()
    elif event.Key == "F10":
        ctrl_click_all_bag_grids()
    elif event.Key == "F3":
        get_cursor_pixel()
    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True

def registerEvent():
    # create the hook mananger
    hm = PyHook3.HookManager()
    # register two callbacks
    #hm.MouseAll = onMouseEvent
    hm.MouseWheel = onMouseEvent
    hm.KeyDown = onKeyEvent
    # hook into the mouse and keyboard events
    hm.HookMouse()
    hm.HookKeyboard()
