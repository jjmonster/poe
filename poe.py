from pymouse import *
from pykeyboard import *
from getpixel import gdi32, hdc
import win32api,  win32gui, win32con
import threading
from time import sleep

m=PyMouse()
k=PyKeyboard()

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
    def move_center(self):
        m.move(int(self.cx), int(self.cy))
        
    def left_click(self):
        m.move(int(self.cx), int(self.cy))
        sleep(0.05)
        m.click(int(self.cx), int(self.cy),  1)
        sleep(0.05)

    def right_click(self):
        m.move(int(self.cx), int(self.cy))
        sleep(0.05)
        m.click(int(self.cx), int(self.cy),  2)
        sleep(0.05)

    def get_corner_color(self):
        color = gdi32.GetPixel(hdc, self.x+self.width-3, self.y+self.height-3)
        return color

        
class bag:
    def __init__(self, x,  y, nRows,  nCols):
        self.grids = []
        self.grid_width = 50  #adjust coordinate
        self.grid_height = 50 #adjust coordinate
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
        self.basex = 300   #adjust coordinate
        self.basey = 1034   #adjust coordinate
        self.width = 43  #vertical arrangement, from top to bottom, width=0  #adjust coordinate
        self.height = 0   #Horizontal, from left to right. height=0
        self.num = num
        self.x = self.basex + num*self.width
        self.y = self.basey + num*self.height
        self.orig_color = gdi32.GetPixel(hdc,self.x,self.y)
        self.attr = 0
        self.ref = 0
        self.link = 0
        print("medical init num=",num,"x=",self.x,"y=",self.y,"orig color=", hex(self.orig_color))
    
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
        print("link", self.num, "->", num, "color:", hex(self.link_orig_color))

    def GetColor(self):
        c = gdi32.GetPixel(hdc, self.x,  self.y)
        print("num=",self.num, "color=",hex(c))


    def use(self):
        if self.ref > 0:
            c = gdi32.GetPixel(hdc, self.ref_x,  self.ref_y)
            if c == self.ref_orig_color: #reference color have not changed
                return
        if self.link > 0:
            c = gdi32.GetPixel(hdc, self.link_x,  self.link_y)
            if c != self.link_orig_color:  #using the linkage medical
                #print(hex(c), hex(self.link_orig_color))
                return

        c = gdi32.GetPixel(hdc, self.x,  self.y)
        if c == self.orig_color:
            k.tap_key(self.num + 1 + 48);
        return


###############################################################
def print_color():
    for i in range(len(medicals)):
        medicals[i].GetColor()

#########################################################################
def get_cursor_pixel():
    x, y = m.position()
    c = hex(gdi32.GetPixel(hdc, x,  y))
    text = "x:{} y:{} color:{}".format(x, y, c)
    win32api.MessageBox(None,  text,  "pywin32",  win32con.MB_YESNO)
###################################################################
    
def ctrl_click_all_bag_grids():
    global clickgrids
    clickgrids = True
    k.press_key(k.control_key)
    for i in range(len(b1.grids)):
        b1.grids[i].left_click()
        b1.grids[i].left_click()
        if clickgrids == False:
            break

    k.release_key(k.control_key)
    clickgrids = False

def click_grids_toggle():
    global clickgrids
    if clickgrids == False:
        threading.Timer(0.1, ctrl_click_all_bag_grids).start()
    else:
        clickgrids = False

################################################################
def func_click(fn):
    global fnclick
    fnclick = True
    if fn == "shift":
        k.press_key(k.shift_key)
    elif fn == "ctrl":
        k.press_key(k.control_key)
    while fnclick:
        x, y = m.position()
        m.click(x, y, 1)
        sleep(0.2)
    if fn == "shift":
        k.release_key(k.shift_key)
    elif fn == "ctrl":
        k.release_key(k.control_key)
   
def start_func_click_timer(fn):
    threading.Timer(1, func_click, (fn,)).start()
    
def stop_func_click_timer():
    global fnclick
    fnclick = False

def func_click_toggle(fn):
    if fnclick == False:
        start_func_click_timer(fn)
    else:
        stop_func_click_timer()

################################################################
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
################################################################
def print_all_grids_color():
    for i in range(1):#(b1.nRows):
        for j in range(b1.nCols):
            color = b1.grids[i*b1.nCols+j].get_corner_color()
            print(i, j, color)
        print("\n")

def chance():
    while chancing:
        b1.grids[1].right_click()
        b1.grids[0].left_click()
        b1.grids[2].right_click()
        b1.grids[0].left_click()

def start_chance_timer():
    global chancing
    chancing = True
    threading.Timer(1, chance).start()

def stop_chance_timer():
    global chancing
    chancing = False

def chance_toggle():
    if chancing == False:
        start_chance_timer()
    else:
        stop_chance_timer()
#################################################################
def drug():
    global druging
    if druging == 0:
        return
    druging += 1
    for i in range(len(medicals)):
        medicals[i].use()
        sleep(0.1)
    if druging%3 == 1:
        k.tap_key("y")
    if druging%3 == 2:
        k.tap_key("r")
    threading.Timer(0.2, drug).start()

def start_drug_timer():
    global druging
    druging = 1
    threading.Timer(0.2, drug).start()

def stop_drug_timer():
    global druging
    druging = 0

def drug_toggle():
    if druging == 0:
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
    global fnclick
    global chancing
    global clickgrids

    attacking = False
    druging = 0
    messaging = False
    fnclick = False
    chancing = False
    clickgrids = False
    
    global medicals
    medicals = []
    for i in range(5):
        medicals.append(medical(i))
        
    medicals[0].SetReference(1,  110,  880)  #adjust coordinate

    #medicals[1].SetLink(2)
    #medicals[2].SetLink(1)

    #medicals[3].SetLink(4)
    #medicals[4].SetLink(3)

    global b1
    b1 = bag(1304, 575, 12, 5)  #adjust coordinate
        
if __name__ == "__main__":
    globals_init()
