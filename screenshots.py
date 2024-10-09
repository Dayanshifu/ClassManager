import os,sys
from sys import *
import time
from PIL import ImageGrab  
import time  ,datetime


FILEPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
FILEINPATH = os.path.dirname(__file__)

def screenshot(a=''):
    if a=='':
        a=f'screenshot_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  
    screenshots_folder = os.path.join(desktop, 'Screenshots') 
    if not os.path.exists(screenshots_folder):  
        os.makedirs(screenshots_folder) 
    img1 = ImageGrab.grab()  
    img_path = os.path.join(screenshots_folder, a)  
    img1.save(img_path) 

    try:
        f = open(FILEPATH+'\\log', 'r')
        aaa = f.read()
        f.close()
        f = open(FILEPATH+'\\log', 'w')
        f.write(f'{time.asctime()} {f"截图保存至{img_path}"}\n\n{aaa}')
        f.close()
    except:
        f = open(FILEPATH+'\\log', 'w')
        f.write(f'{time.asctime()} {f"截图保存至{img_path}"}\n\n{time.asctime()} 创建日志')
        f.close()
    return(img_path)

def screenshot1():
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  
    screenshots_folder = os.path.join(desktop, 'Screenshots') 
    if not os.path.exists(screenshots_folder):  
        os.makedirs(screenshots_folder) 
    img1 = ImageGrab.grab()  
    a=f'screenshot_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
    img_path = os.path.join(screenshots_folder, a)  
    img1.save(img_path) 
    return(img_path)
c=screenshot1()
os.remove(c)