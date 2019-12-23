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

class POEWindow:
    def __init__(self):
        self.full_screen_left = -8
        self.full_screen_top = -8
        self.full_screen_right = 1928
        self.full_screen_bottom = 1048
        self.full_screen_width = self.full_screen_right - self.full_screen_left
        self.full_screen_height = self.full_screen_bottom - self.full_screen_top
        try:
            self.info = GetWindowInfo("POEWindowClass")
            #print(self.info)
            self.bag_x = int(1304 * self.info["width"] / self.full_screen_width)
            self.bag_y = int(575 * self.info["height"] / self.full_screen_height)
            self.bag_nRows = 12
            self.bag_nCols = 5
            self.bag_grid_width = int(50 * self.info["width"] / self.full_screen_width)
            self.bag_grid_height = int(50 * self.info["height"] / self.full_screen_height)
            self.medicals_base_x = int(300 * self.info["width"] / self.full_screen_width)
            self.medicals_base_y = int(1034 * self.info["height"] / self.full_screen_height)
            self.medicals_width = int(43 * self.info["width"] / self.full_screen_width)
            self.medicals_height = 0
            self.ref_life_x = int(110 * self.info["width"] / self.full_screen_width)
            self.ref_life_y = int(880 * self.info["height"] / self.full_screen_height)
        except:
            #print("can't find POEWindowClass use default value!")
            self.bag_x = 1304
            self.bag_y = 575
            self.bag_nRows = 12
            self.bag_nCols = 5
            self.bag_grid_width = 50
            self.bag_grid_height = 50
            self.medicals_base_x = 300
            self.medicals_base_y = 1034
            self.medicals_width = 43
            self.medicals_height = 0
            self.ref_life_x = 110
            self.ref_life_y = 880

    def ShowWindowInfo(self):
        ShowWindowInfo(self.info)

class Bag(POEWindow):
    def __init__(self):
        super(Bag, self).__init__()
        self.grids = []
        for i in range(self.bag_nRows):
            for j in range(self.bag_nCols):
                g = Grid(self.bag_x+i*self.bag_grid_width,  self.bag_y+j*self.bag_grid_height,  self.bag_grid_width,  self.bag_grid_height)
                self.grids.append(g)
        return
        
    def GetGrid(self, row,  col):
        return self.grids[row + col*self.nCols]

class Medical(POEWindow):
    def __init__(self, num):
        super(Medical, self).__init__()
        self.num = num
        self.attr = 0
        self.ref = ""
        self.link = 0
        self.timer = 0
        self.timer_count = 0
        
    def SetOrigColor(self):
        self.x = self.medicals_base_x + num*self.medicals_width
        self.y = self.medicals_base_y + num*self.medicals_height
        self.orig_color = gdi32.GetPixel(hdc,self.x,self.y)
        print("medical init num=",num,"x=",self.x,"y=",self.y,"orig color=", hex(self.orig_color))
    
    def SetReference(self,  ref):
        #ref=1 -> life , ref=2 -> mana, ref=3 -> shield
        if ref == "life":
            self.ref_x = self.ref_life_x
            self.ref_y = self.ref_life_y
        elif ref == "mana":
            #todo
            pass
        elif ref == "shield":
            #todo
            pass
        else:
            print("Unknown value!")
            return
        self.ref = ref
        self.ref_orig_color = 0
        if self.ref != "":
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

    def SetTimer(self,  t):
        self.timer = t
        self.timer_count = 0
        
    def GetColor(self):
        c = gdi32.GetPixel(hdc, self.x,  self.y)
        return c

    def use(self):
        if self.timer != 0:
            if self.timer_count <= 0:
                k.tap_key(self.num + 1 + 48);
                self.timer_count = self.timer
            self.timer_count -= 0.5  #one cycle is 0.5s
            return
            
        if self.ref != "":
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
    
        #self.window = POEWindow()
        self.medicals = []
        for i in range(5):
            self.medicals.append(Medical(i))
        if False:
            for i in range(5):
                self.medicals[i].SetOrigColor()
            self.medicals[0].SetReference("life")
        else:
            self.medicals[0].SetTimer(0.5)
            self.medicals[1].SetTimer(3.8)
            self.medicals[2].SetTimer(4.0)
            self.medicals[3].SetTimer(5.0)
            self.medicals[4].SetTimer(4.0)
            
        #medicals[1].SetLink(2)
        #medicals[2].SetLink(1)
        #medicals[3].SetLink(4)
        #medicals[4].SetLink(3)
        
        self.bag = Bag()
        
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
