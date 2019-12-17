from ctypes import *
from pymouse import *
from pykeyboard import *
from winfo import *
import win32api,  win32con
import threading
from time import sleep

gdi32 = windll.gdi32
user32 = windll.user32
hdc = user32.GetDC(None)
#c=gdi32.GetPixel(hdc, 745,60)
#print(hex(c))

m=PyMouse()
k=PyKeyboard()

class POEWindow:
    def __init__(self):
        self.info = GetWindowInfo("")

    def ShowWindowInfo(self):
        ShowWindowInfo(self.info)

class Grid:
    def __init__(self,  x, y,  width,  height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cx = int(self.x + self.width/2)
        self.cy = int(self.y + self.height/2)
        return

    def GetCenterColor(self):
        c = gdi32.GetPixel(hdc, self.cx,  self.cy)
        return c

    def move_center(self):
        m.move(self.cx, self.cy)
        
    def click(self,  lr):
        m.move(self.cx, self.cy)
        sleep(0.02)
        m.click(self.cx, self.cy,  lr)
        sleep(0.02)
        
    def left_click(self):
        self.click(1)

    def right_click(self):
        self.click(2)

class Bag:
    def __init__(self, x,  y, nRows,  nCols):
        self.grids = []
        self.grid_width = 50  #adjust coordinate
        self.grid_height = 50 #adjust coordinate
        self.nRows = nRows
        self.nCols = nCols
        for i in range(nRows):
            for j in range(nCols):
                g = Grid(x+i*self.grid_width,  y+j*self.grid_height,  self.grid_width,  self.grid_height)
                self.grids.append(g)
        return
        
    def GetGrid(self, row,  col):
        return self.grids[row + col*self.nCols]

class Medical:
    def __init__(self, num):
        #w = POEWindow()
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
        return c

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

class POEFunctions:
    def __init__(self):
        self.druging = False
        self.messaging = False
        self.fnclick = False
        self.chance = False
        self.clickgrids = False
        self.timerkey = False
    
        self.medicals = []
        for i in range(5):
            self.medicals.append(Medical(i))

        self.medicals[0].SetReference(1,  110,  880)  #adjust coordinate

        #medicals[1].SetLink(2)
        #medicals[2].SetLink(1)
        #medicals[3].SetLink(4)
        #medicals[4].SetLink(3)

        self.bag = Bag(1304, 575, 12, 5)  #adjust coordinate
        
    def stop_all_func(self):
        self.druging = False
        self.messaging = False
        self.fnclick = False
        self.chance = False
        self.clickgrids = False
        self.timerkey = False

    def get_cursor_color(self):
        x, y = m.position()
        c = hex(gdi32.GetPixel(hdc, x,  y))
        text = "x:{} y:{} color:{}".format(x, y, c)
        win32api.MessageBox(None,  text,  "pywin32",  win32con.MB_YESNO)

    def print_all_grids_color(self):
        for i in range(self.bag.nRows):#(1):
            for j in range(self.bag.nCols):
                color = self.bag.grids[i*self.bag.nCols+j].GetCenterColor()
                print(i, j, color)
            print("\n")

    def ctrl_click_all_bag_grids(self):
        self.clickgrids = True
        k.press_key(k.control_key)
        for i in range(len(self.bag.grids)):
            self.bag.grids[i].left_click()
            self.bag.grids[i].left_click()
            if self.clickgrids == False:
                break
        k.release_key(k.control_key)
        self.clickgrids = False

    def click_grids_toggle(self):
        if self.clickgrids == False:
            threading.Timer(0.1, self.ctrl_click_all_bag_grids).start()
        else:
            self.clickgrids = False

    def func_click(self, fn):
        if fn == "shift":
            key= k.shift_key
        elif fn == "ctrl":
            key = k.control_key
        k.press_key(key)
        while self.fnclick:
            x, y = m.position()
            m.click(x, y, 1)
            sleep(0.2)
        k.release_key(key)

    def func_click_toggle(self, fn):
        if self.fnclick == False:
            self.fnclick = True
            threading.Timer(0.1, self.func_click, (fn,)).start()
        else:
            self.fnclick = False

    def send_msg(self):
        while self.messaging:
            k.tap_key(k.enter_key)
            k.tap_key(k.up_key)
            k.tap_key(k.enter_key)
            sleep(10)
        
    def msg_toggle(self):
        if self.messaging == False:
            self.messaging = True
            threading.Timer(10, self.send_msg).start()
        else:
            self.messaging = False

    def chance_and_recoin(self):
        while self.chance:
            self.bag.grids[10].right_click()
            self.bag.grids[0].left_click()
            self.bag.grids[15].right_click()
            self.bag.grids[0].left_click()

    def chance_toggle(self):
        if self.chance == False:
            self.chance = True
            threading.Timer(1, self.chance_and_recoin).start()
        else:
            self.chance = False

    def drug(self):
        while self.druging:
            for i in range(len(self.medicals)):
                self.medicals[i].use()
                sleep(0.1)

    def drug_start(self):
        if self.druging == False:
            self.druging = True
            threading.Timer(0.1, self.drug).start()
            
    def drug_toggle(self):
        if self.druging == False:
            self.druging = True
            threading.Timer(0.1, self.drug).start()
        else:
            self.druging = False

    def timer_key(self):
        while self.timerkey:
            k.tap_key("y")
            sleep(1)
            k.tap_key("r")
            sleep(1)

    def timer_key_start(self):
        if self.timerkey == False:
            self.timerkey = True
            threading.Timer(0.1, self.timer_key).start()

    def timer_key_toggle(self):
        if self.timerkey == False:
            self.timerkey = True
            threading.Timer(0.1, self.timer_key).start()
        else:
            self.timerkey = False

if __name__ == "__main__":
    f = POEFunctions()
    f.get_cursor_color()
    #f.print_all_grids_color()
    for i in range(len(f.bag.grids)):
        print(f.bag.grids[i].x,  f.bag.grids[i].y)
