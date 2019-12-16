# -*- coding: utf-8 -*- #
import os
import PyHook3
from poe import *
from getpixel import *

pause = False
def onMouseEvent(event): 
    global pause
    if pause == True:
        return True
    if event.MessageName == "mouse wheel":
        if event.Wheel == 1:
            #print("wheel up")
            start_attack()
        elif event.Wheel == -1:
            #print("wheel down")
            stop_attack()
            stop_func_click_timer()
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
    elif event.Key == "F5":
        chance_toggle()
        #print_all_grids_color()
    elif event.Key == "F9":
        func_click_toggle("ctrl")
    elif event.Key == "F10":
        func_click_toggle("shift")
    elif event.Key == "F11":
        click_grids_toggle()
    elif event.Key == "F6":
        #get_cursor_pixel()
        #ShowWindowInfo()
        info = GetForegroundWindowInfo()
        x = info["right"] - info["left"]
        y = info["bottom"] - info["top"]
        m.move(int(x/2),int(y/2))
    elif event.Key == "F7":
        print_color()
    elif event.Key == "F3":
        #print("exit")
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
