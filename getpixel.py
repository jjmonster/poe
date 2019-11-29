from ctypes import *
import win32api,  win32gui, win32con

gdi32 = windll.gdi32
user32 = windll.user32


hdc = user32.GetDC(None)
#c=gdi32.GetPixel(hdc, 745,60)
#print(hex(c))

def GetForegroundWindowInfo():
    #hwnd = win32gui.GetDesktopWindow()
    hwnd = win32gui.GetForegroundWindow()
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    classname = win32gui.GetClassName(hwnd)
    windowtext = win32gui.GetWindowText(hwnd)
    info = {"classname":classname, "windowtext":windowtext,  "left":left,  "right":right,  "top":top,  "bottom":bottom}
    return info

def ShowWindowInfo():
    info = GetForegroundWindowInfo()
    #text = "classname:\t{}\nwindowtext:\t{}\nleft:{} top:{} right:{} bottom:{}\n".format(classname, windowtext,  left, top, right, bottom)
    text = "classname:\t{classname}\nwindowtext:\t{windowtext}\nleft:{left} top:{top} right:{right} bottom:{bottom}\n".format(**info)
    win32api.MessageBox(None,  text,  "pywin32",  win32con.MB_YESNO)

