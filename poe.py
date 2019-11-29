from pymouse import *
from pykeyboard import *
from getpixel import gdi32, hdc
import win32api,  win32gui, win32con
import threading
from time import sleep

class grid:
    def __init__(self,  x, y,  width,  height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cx, self.cy = self.GetCenter()
        return
        
    def GetCenter(self):
        x = self.x + self.width/2
        y = self.y + self.height/2
        return x, y
        
    def ctrl_click(self):
        #m.move(int(self.cx), int(self.cy))
        k.press_key(k.ctrl_key)
        m.click(int(self.cx), int(self.cy),  1)
        k.release_key(k.ctrl_key)
        
class bag:
    def __init__(self, x,  y, nRows,  nCols):
        self.grids = []
        self.grid_width = 10  #adjust coordinate
        self.grid_height = 10 #adjust coordinate
        self.nRows = nRows
        self.nCols = nCols
        for i in range(nRows):
            for j in range(nCols):
                g = grid(x+i*self.grid_width,  y+j*self.grid_height,  self.grid_width,  self.grid_height)
                self.grids.append(g)
        return
        
    def GetGrid(self, row,  col):
        return self.grids[row + col*self.nCols]

class medical:
    def __init__(self, num):
        self.basex = 0   #adjust coordinate
        self.basey = 0   #adjust coordinate
        self.width = 10  #vertical arrangement, from top to bottom, width=0  #adjust coordinate
        self.height = 0   #Horizontal, from left to right. height=0
        self.num = num
        self.x = self.basex + num*self.width
        self.y = self.basey + num*self.height
        self.orig_color = 0
        self.attr = 0
        self.ref = 0
        self.link = 0
    
    def SetReference(self,  ref,  x,  y):
        self.ref = ref  #ref=1 -> life , ref=2 -> mana, ref=3 -> shield
        self.ref_x = x
        self.ref_y = y
        self.ref_orig_color = 0
        if self.ref > 0:
           self.ref_orig_color =  gdi32.GetPixel(hdc, self.ref_x,  self.ref_y)
        print("ref", self.ref,  "color:",  hex(self.ref_orig_color))
        
    def SetLink(self,  num):
        if num == self.num:
            return
        self.link = num
        self.link_x = self.x + (num - self.num)*self.width
        self.link_y = self.y + (num - self.num)*self.height
        self.link_orig_color = gdi32.GetPixel(hdc, self.link_x,  self.link_y)

    def use(self):
        if self.ref > 0:
            c = gdi32.GetPixel(hdc, self.ref_x,  self.ref_y)
            if c == self.ref_orig_color: #reference color have not changed
                return
        if self.link > 0:
            c = gdi32.GetPixel(hdc, self.link_x,  self.link_y)
            if c != self.ref_orig_color:  #using the linkage medical
                return

        c = gdi32.GetPixel(hdc, self.x,  self.y)
        if c == self.orig_color:
            k.tap_key(self.num + 1 + 48);
        return

#########################################################################
def get_cursor_pixel():
    x, y = m.position()
    c = hex(gdi32.GetPixel(hdc, x,  y))
    text = "x:{} y:{} color:{}".format(x, y, c)
    win32api.MessageBox(None,  text,  "pywin32",  win32con.MB_YESNO)
    
def ctrl_click_all_bag_grids():
    for i in range(len(b1.grids)):
        b1.grids[i].ctrl_click()
        sleep(0.2)
#    for i in range(b1.nRows):
#        for j in range(b1.nCols):
#            g=b1.GetGrid(i, j)
#            g.ctrl_click()

def shift_click():
    global shiftclick
    shiftclick = True
    x, y = m.position()
    k.press_key(k.shift_key)
    while shiftclick:
        m.click(x, y, 1)
        sleep(0.2)
#        print("test")
#        sleep(1)
    k.release_key(k.shift_key)

def start_shift_click_timer():
    threading.Timer(1, shift_click).start()
    
def stop_shift_click_timer():
    global shiftclick
    shiftclick = False

def shift_click_toggle():
    if shiftclick == False:
        start_shift_click_timer()
    else:
        stop_shift_click_timer()

def send_msg():
    global messaging
    if messaging == False:
        return
    k.tap_key(k.enter_key)
    k.tap_key(k.up_key)
    k.tap_key(k.enter_key)
    threading.Timer(10, send_msg).start()
    
def start_msg_timer():
    global messaging
    messaging = True
    threading.Timer(10, send_msg).start()

def stop_msg_timer():
    global messaging
    messaging = False

def msg_toggle():
    if messaging == False:
        start_msg_timer()
    else:
        stop_msg_timer()

def drug():
    global druging
    if druging == False:
        return
    for i in range(len(medicals)):
        medicals[i].use()
    threading.Timer(1, drug).start()

def start_drug_timer():
    global druging
    druging = True
    threading.Timer(1, drug).start()

def stop_drug_timer():
    global druging
    druging = False

def drug_toggle():
    if druging == False:
        start_drug_timer()
    else:
        stop_drug_timer()

def start_attack():
    global attacking
    if attacking == True:
        return
    attacking = True
    start_drug_timer()
    
def stop_attack():
    global attacking
    attacking = False
    stop_drug_timer()

def attack_toggle():
    if attacking == False:
        start_attack()
    else:
        stop_attack()
        
def globals_init():
    global attacking
    global druging
    global messaging
    global shiftclick

    attacking = False
    druging = False
    messaging = False
    shiftclick = False
    
    global medicals
    medicals = []
    for i in range(5):
        medicals.append(medical(i))
        
    medicals[0].SetReference(1,  10,  10)  #adjust coordinate

    global m
    global k
    m=PyMouse()
    k=PyKeyboard()
    
    global b1
    b1 = bag(0, 0, 12, 5)  #adjust coordinate
        
if __name__ == "__main__":    
    globals_init()
