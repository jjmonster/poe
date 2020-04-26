from ctypes import *
from pymouse import *
from pykeyboard import *
from winfo import *
import win32api,win32con
import win32clipboard as wc
import re,threading
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
            self.winfo = GetWindowInfo("POEWindowClass")
            print(self.winfo)
        except:
            print("can't find POEWindowClass use default value!")

    def ShowWindowInfo(self):
        ShowWindowInfo(self.winfo)

class Bag(POEWindow):
    def __init__(self):
        super(Bag, self).__init__()
        #bag coordinate
        try:
            self.bag_x = int(1304 * self.winfo["width"] / self.full_screen_width)
            self.bag_y = int(575 * self.winfo["height"] / self.full_screen_height)
            self.bag_nRows = 12
            self.bag_nCols = 5
            self.bag_grid_width = int(50 * self.winfo["width"] / self.full_screen_width)
            self.bag_grid_height = int(50 * self.winfo["height"] / self.full_screen_height)
        except:
            self.bag_x = 1304
            self.bag_y = 575
            self.bag_nRows = 12
            self.bag_nCols = 5
            self.bag_grid_width = 50
            self.bag_grid_height = 50
        
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
        #coordinate
        try:
            self.medicals_base_x = int(300 * self.winfo["width"] / self.full_screen_width)
            self.medicals_base_y = int(1034 * self.winfo["height"] / self.full_screen_height)
            self.medicals_width = int(43 * self.winfo["width"] / self.full_screen_width)
            self.medicals_height = 0
            self.ref_life_x = int(110 * self.winfo["width"] / self.full_screen_width)
            self.ref_life_y = int(880 * self.winfo["height"] / self.full_screen_height)
        except:
            self.medicals_base_x = 300
            self.medicals_base_y = 1034
            self.medicals_width = 43
            self.medicals_height = 0
            self.ref_life_x = 110
            self.ref_life_y = 880
        
        self.num = num
        self.attr = 0
        self.ref = ""
        self.link = 0
        self.timer = 0
        self.timer_count = 0
        
    def SetOrigColor(self):
        self.x = self.medicals_base_x + self.num*self.medicals_width
        self.y = self.medicals_base_y + self.num*self.medicals_height
        self.orig_color = gdi32.GetPixel(hdc,self.x,self.y)
        print("medical init num=",self.num,"x=",self.x,"y=",self.y,"orig color=", hex(self.orig_color))
    
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
        self.link_x = self.x + (num - self.num)*self.medicals_width
        self.link_y = self.y + (num - self.num)*self.medicals_height
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
        
class CurrencyRepository(POEWindow):
    def __init__(self):
        super(CurrencyRepository, self).__init__()
        #coordinate
        try:
            self.mirror = 0 #Mirror of Kalandra 卡兰德的魔镜
            self.scour = 0 #Orb of Scour 重铸
            self.reg = 0 #Orb of Reg 后悔
            self.c = 0 #Chaos Orb 混沌
            self.regal = 0 #Regal Orb 富豪
            self.vaal = 0 #Vaal Orb 瓦尔宝珠
            self.div = 0 #Div Orb 神圣
            self.ex = 0 #Exalted Orb 崇高
            self.alt = 0 #Orb of Alteration 改造
            self.alt_x = 107
            self.alt_y = 300
            self.aug = 0#Orb of Augmentation
            self.aug_x = 220
            self.aug_y = 350
            self.chance = 0 #Orb of Chance 机会
            self.alc = 0 #Orb of Alchemy 点金
            self.chrom = 0 #Chromatic Orb 五彩
            self.jew = 0 #jeweller's Orb 工匠
            self.fus = 0 #Orb of Fusing 链接
            self.chis = 0 #Cartographer's Chisel 图钉
            self.gmp = 0 #Gemcutter's Prism 宝石匠的棱镜
            self.biggrid = 0
            self.biggrid_x = 314
            self.biggrid_y = 466
        except:
            print("Fail init Currency Repository!")

class POEFunctions:
    def __init__(self):
        self.druging = False
        self.messaging = False
        self.fnclick = False
        self.chance = False
        self.clickgrids = False
        self.timerkey = False
        self.medicals_timer = False
        self.altering = False
        self.role = 1
    
        #self.window = POEWindow()
        self.medicals = []
        for i in range(5):
            self.medicals.append(Medical(i))
        if self.medicals_timer:
            self.medicals[0].SetTimer(0.5)
            self.medicals[1].SetTimer(3.8)
            self.medicals[2].SetTimer(4.0)
            self.medicals[3].SetTimer(5.0)
            self.medicals[4].SetTimer(4.0)
        else:##use color identify instead of timer
            #if self.role == 0:
            #self.medicals[0].SetReference("life")
            for i in range(5):
                self.medicals[i].SetOrigColor()
            
        #medicals[1].SetLink(2)
        #medicals[2].SetLink(1)
        #self.medicals[3].SetLink(4)
        #self.medicals[4].SetLink(3)
        
        self.bag = Bag()
        self.cr = CurrencyRepository()
        
    def stop_all_func(self):
        self.druging = False
        self.messaging = False
        self.fnclick = False
        self.chance = False
        self.clickgrids = False
        self.timerkey = False
        self.altering = False

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
            sleep(20)
        
    def msg_toggle(self):
        if self.messaging == False:
            self.messaging = True
            threading.Timer(10, self.send_msg).start()
        else:
            self.messaging = False

    def chance_and_scour(self):
        while self.chance:
            self.bag.grids[10].right_click()
            self.bag.grids[0].left_click()
            self.bag.grids[15].right_click()
            self.bag.grids[0].left_click()

    def chance_toggle(self):
        if self.chance == False:
            self.chance = True
            threading.Timer(1, self.chance_and_scour).start()
        else:
            self.chance = False
            
    def affix_alter(self):
        #prefix = "▲" suffix = "▽"
        affix = "▲"
        target = "爆炸"
        while self.altering:
            #copy clipboard
            m.move(self.cr.biggrid_x,self.cr.biggrid_y)
            sleep(0.1)
            k.press_key(k.control_key)
            k.tap_key("c")
            k.release_key(k.control_key)
            sleep(0.1)
            wc.OpenClipboard()
            text = wc.GetClipboardData(win32con.CF_UNICODETEXT)
            wc.CloseClipboard()
            #print(text)
            if re.search("奉献地面", text) is not None:
                #use Orb of Alteration
                m.move(self.cr.alt_x, self.cr.alt_y)
                sleep(0.2)
                m.click(self.cr.alt_x, self.cr.alt_y, 2)
                sleep(0.2)
                m.move(self.cr.biggrid_x,self.cr.biggrid_y)
                sleep(0.2)
                m.click(self.cr.biggrid_x,self.cr.biggrid_y, 1)
                sleep(0.2)
                continue
            if re.search(affix, text) is None:
                #use Orb of Augmentation
                m.move(self.cr.aug_x, self.cr.aug_y)
                sleep(0.2)
                m.click(self.cr.aug_x, self.cr.aug_y, 2)
                sleep(0.2)
                m.move(self.cr.biggrid_x,self.cr.biggrid_y)
                sleep(0.2)
                m.click(self.cr.biggrid_x,self.cr.biggrid_y, 1)
                sleep(0.2)
            elif re.search(target, text) is None:
                #use Orb of Alteration
                m.move(self.cr.alt_x, self.cr.alt_y)
                sleep(0.2)
                m.click(self.cr.alt_x, self.cr.alt_y, 2)
                sleep(0.2)
                m.move(self.cr.biggrid_x,self.cr.biggrid_y)
                sleep(0.2)
                m.click(self.cr.biggrid_x,self.cr.biggrid_y, 1)
                sleep(0.2)
            else:
                break
        self.altering = False
        
    def affix_alter_toggle(self):
        if self.altering == False:
            self.altering = True
            threading.Timer(1, self.affix_alter).start()
        else:
            self.altering = False

    def drug(self):
        while self.druging:
            for i in range(len(self.medicals)):
                self.medicals[i].use()
                sleep(0.1)

    def drug_start(self):
        if self.druging == False:
            self.druging = True
            threading.Timer(0.1, self.drug).start()

    def drug_stop(self):
        self.druging = False

    def drug_toggle(self):
        if self.druging == False:
            self.druging = True
            threading.Timer(0.1, self.drug).start()
        else:
            self.druging = False

    def timer_key(self):
        while self.timerkey:
            if self.role == 0:
                k.tap_key("y")
                sleep(2)
                k.tap_key("r")
                sleep(2)
                k.tap_key("t")
                sleep(2)
            elif self.role == 1 or self.role == 2:
                k.tap_key("y")
                sleep(0.2)
                k.tap_key("r")
                sleep(0.2)
                k.tap_key("t")
                sleep(0.2)


    def timer_key_start(self):
        if self.timerkey == False:
            self.timerkey = True
            threading.Timer(0.1, self.timer_key).start()
            k.press_key("f")

    def timer_key_stop(self):
        k.release_key("f")
        self.timerkey = False


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
