import win32api,  win32gui, win32con
#from collections import defaultdict

def WindowInfo(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    classname = win32gui.GetClassName(hwnd)
    windowtext = win32gui.GetWindowText(hwnd)
    info = {"classname":classname, "windowtext":windowtext,  \
    "left":left,  "right":right,  \
    "top":top,  "bottom":bottom,  \
    "width":width,  "height":height}
    return info

def GetWindowInfo(classname):
    hwnd = win32gui.FindWindow(classname, None)
    if(hwnd):
        return WindowInfo(hwnd)
    else:
        win32api.MessageBox(None,  classname+" not found!",  "pywin32",  win32con.MB_YESNO)

def GetForegroundWindowInfo():
    hwnd = win32gui.GetForegroundWindow()
    #hwnd = win32gui.GetDesktopWindow()
    if(hwnd):
        return WindowInfo(hwnd)

def ShowWindowInfo(info):
    if info == None:
        return
    text = "\
    classname:\t{classname}\n\
    windowtext:\t{windowtext}\n\
    left:{left}  top:{top}  right:{right}  bottom:{bottom}\n\
    width:{width}  height:{height}".format(**info)
    win32api.MessageBox(None,  text,  "pywin32",  win32con.MB_YESNO)

def WindowHide():
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE|win32con.SW_MINIMIZE)

if __name__ == "__main__":
    #info = GetWindowInfo("Notepad++")
    #info = GetForegroundWindowInfo()
    #ShowWindowInfo(info)
    #hwnd = win32gui.FindWindow("Notepad++", None)
    #win32gui.SetForegroundWindow(hwnd)
    hwnd = win32gui.GetForegroundWindow()
    #hwnd=win32gui.GetWindow(hwnd,win32con.GW_CHILD)
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE|win32con.SW_MINIMIZE)
    info = GetForegroundWindowInfo()
    ShowWindowInfo(info)

    
