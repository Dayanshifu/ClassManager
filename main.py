# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import ttk, scrolledtext, colorchooser, messagebox, filedialog
import os
import sys
import threading
from sys import *
import win32con
import win32api
import win32gui
import win32process  # pywin32
import time
import Pmw
import cv2  # 可选安装pmw，由于pyinstaller打包需要，pmw已在程序根目录，作用只有主页上姓名展示不全可以把鼠标放上去查看全部
import random as ran
import pypinyin
from pypinyin import lazy_pinyin  # linux版本使用xpinyin
import easygui as gui
import subprocess
import base64
import imgs
import datetime
import webbrowser
from PIL import ImageGrab, ImageDraw, Image, ImageTk
import time
import ctypes
import json

from pycaw.pycaw import AudioUtilities, IAudioMeterInformation, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pygetwindow as gw
import pyautogui
import chardet

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
scaling_factor = user32.GetDpiForSystem()
wp = scaling_factor / 96.0
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vl = volume.GetMasterVolumeLevel()
vr = volume.GetVolumeRange()

screenshotstatus = 0

scaleispressed = 0
randomstate = 0
FILEPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
FILEINPATH = os.path.dirname(__file__)

admin = ""
res = {}
btnlist = btnname = []

is_media_running = True
has_media_window = False
is_playing_audio = False
system_has_audio = False
meter = None

"播放暂停功能"


def init_audio_meter():
    global meter, pause_btn
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioMeterInformation._iid_, CLSCTX_ALL, None)
        meter = interface.QueryInterface(IAudioMeterInformation)
    except Exception as e:
        print(e)


def check_audio_state():
    try:
        if meter:
            return meter.GetPeakValue() > 0
        return False
    except:
        return False


def check_media_windows():
    keywords = ["player", "video", "vlc", "media", "播放"]
    windows = gw.getAllTitles()
    for title in windows:
        lower_title = title.lower()
        if any(keyword in lower_title for keyword in keywords):
            return True
    return False


def update_status():
    global has_media_window, is_playing_audio, system_has_audio, pause_btn
    while is_media_running:
        has_media_window = check_media_windows()
        is_playing_audio = check_audio_state() if has_media_window else False
        system_has_audio = check_audio_state()


def toggle_media_control():
    if has_media_window:
        try:
            keywords = ["player", "video", "vlc", "media", "播放"]
            windows = gw.getAllTitles()
            target_window = next((t for t in windows if any(
                k in t.lower() for k in keywords)), None)

            if target_window:
                win = gw.getWindowsWithTitle(target_window)[0]
                win.activate()
                pyautogui.press('space')
        except Exception as e:
            print(e)
    else:
        pyautogui.press('playpause')


def update_button_state():
    global pause_btn, miniwin
    if has_media_window:
        if is_playing_audio:
            pause_btn.configure(text="暂停", style="CRED.TButton")
        else:
            pause_btn.configure(text="播放", style="CGREEN.TButton")
    elif system_has_audio:
        pause_btn.configure(text="暂停", style="CRED.TButton")
    else:
        pause_btn.configure(text="暂停", style="CGRAY.TButton")
    miniwin.after(50, update_button_state)


"音量调节功能设置"


def get_master_volume_controller():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_controller = cast(interface, POINTER(IAudioEndpointVolume))
    return volume_controller


def get_volume_percent(volume_controller):
    volume = volume_controller.GetMasterVolumeLevelScalar()
    volume_percent = int(volume * 100)
    return volume_percent


def set_volume_percent(volume_controller, percent):
    volume = percent / 100.0
    volume_controller.SetMasterVolumeLevelScalar(volume, None)


def showvolumepercent():
    global scaleispressed, volume_scale, miniwin, mute_button
    if scaleispressed == 0:
        try:
            volume_scale.set(get_volume_percent(
                get_master_volume_controller()))
        except:
            pass
    if get_volume_percent(get_master_volume_controller()) == 0:
        try:
            set_volume_percent(
                get_master_volume_controller(), volume_scale.get())
            mute_button.configure(text="解除", style="CRED.TButton")
        except:
            pass
    elif volume.GetMute():
        try:
            mute_button.configure(text="解除", style="CRED.TButton")
        except:
            pass
    else:
        try:
            mute_button.configure(text="静音", style="C.TButton")
        except:
            pass
    miniwin.after(50, showvolumepercent)


def adjust_volume(e):
    global sssl, miniwin
    # volume.SetMasterVolumeLevel(
    # vr[0]+ int(volume_scale.get())*(vr[1]-vr[0])/100, None)
    set_volume_percent(get_master_volume_controller(), volume_scale.get())
    if int(volume_scale.get()) < 10:
        a = f"    {int(volume_scale.get())}"
    elif int(volume_scale.get()) < 100:
        a = f"  {int(volume_scale.get())}"
    else:
        a = int(volume_scale.get())
    sssl.configure(text=f"音量\n{a}", font=("微软雅黑", 6))
    pass


def mute_sound():
    if get_volume_percent(get_master_volume_controller()) == 0:
        volume_scale.set(30)
        set_volume_percent(get_master_volume_controller(), volume_scale.get())
        volume.SetMute(0, None)
        mute_button.configure(text="静音", style="C.TButton")
    elif volume.GetMute():
        volume.SetMute(0, None)
        mute_button.configure(text="静音", style="C.TButton")
    else:
        volume.SetMute(1, None)
        mute_button.configure(text="解除", style="CRED.TButton")
    pass


def screenshots(a=''):
    if a == '':
        a = f'screenshot_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    screenshots_folder = os.path.join(desktop, 'Screenshots')
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    img1 = ImageGrab.grab()
    img_path = os.path.join(screenshots_folder, a)
    img1.save(img_path)

    return (img_path)


def screenshothy(a=''):
    if a == '':
        a = f'screenshot_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
    screenshots_folder = os.path.join(FILEPATH, 'Screenshots')
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    img1 = ImageGrab.grab()
    img_path = os.path.join(screenshots_folder, a)
    img1.save(img_path)

    return (img_path)


def screenshot1():
    screenshots_folder = FILEPATH
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    img1 = ImageGrab.grab()
    a = f'screenshot_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
    img_path = os.path.join(screenshots_folder, a)
    img1.save(img_path)
    return (img_path)


c = screenshot1()
os.remove(c)


def screenshot():
    global screenshotstatus, miniwin, config
    screenshotstatus = 1
    miniwin.attributes("-alpha", "0")
    if config["is_screenshotsavedir_desktop"]:
        a = screenshots()
    else:
        a = screenshothy()
    miniwin.attributes("-alpha", "0.8")
    createlog(f"截图保存至{a}")
    screenshotstatus = 0
    return


def screenshot111():
    global screenshotstatus, miniwin, config
    screenshotstatus = 1
    main.attributes("-alpha", "0")
    if config["is_screenshotsavedir_desktop"]:
        a = screenshots()
    else:
        a = screenshothy()
    main.attributes("-alpha", "0.9")
    createlog(f"截图保存至{a}")
    showbox("截图", f"截图保存至{a}")
    screenshotstatus = 0
    return


"白板"


def screendraw():
    global screenshotstatus, miniwin
    screenshotstatus = 1
    miniwin.attributes("-alpha", "0")

    if config["is_screenshotsavedir_desktop"]:
        filea = 1
    else:
        filea = 0

    def start_draw(e):
        nonlocal last_x, last_y
        last_x, last_y = e.x, e.y

    def draw(e):
        nonlocal last_x, last_y
        if last_x and last_y:
            if tool == "pen":
                width = pen_size.get()
                color = current_color
            else:
                width = eraser_size.get()
                color = "white"

            canvas.create_line(last_x, last_y, e.x, e.y,
                               width=width, fill=color, capstyle=ROUND, smooth=True)
            last_x, last_y = e.x, e.y

    def reset_last(e):
        nonlocal last_x, last_y
        last_x, last_y = None, None

    def set_tool(t):
        nonlocal tool
        tool = t
        update_cursor()

    def choose_color():
        nonlocal current_color, tool
        color = colorchooser.askcolor()[1]
        if color:
            current_color = color
            set_tool("pen")

    def clear_canvas():
        canvas.delete("all")
        set_tool("pen")

    def on_scale_click(event, scale):
        global pen_scale, eraser_scale
        x = event.x - scale.winfo_x()
        slider_width = scale.winfo_width()
        ratio = x / slider_width
        value = ratio * (scale['to'] - scale['from']) + scale['from']
        scale.set(value)
        # if scale==pen_scale:

    def savefile():
        try:
            if filea:
                a = f'writing_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
                desktop = os.path.join(os.path.join(
                    os.environ['USERPROFILE']), 'Desktop')
                screenshots_folder = os.path.join(desktop, 'Screenshots')
                if not os.path.exists(screenshots_folder):
                    os.makedirs(screenshots_folder)
                img_path = os.path.join(screenshots_folder, a)
            else:
                a = f'writing_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
                screenshots_folder = os.path.join(FILEPATH, 'Screenshots')
                if not os.path.exists(screenshots_folder):
                    os.makedirs(screenshots_folder)
                img_path = os.path.join(screenshots_folder, a)

            canvas.update()
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            img = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(img)
            for item in canvas.find_all():
                item_type = canvas.type(item)
                if item_type == "line":
                    coords = [round(x) for x in canvas.coords(item)]
                    color = canvas.itemcget(item, "fill") or "black"
                    width = max(
                        1, int(float(canvas.itemcget(item, "width") or 1)))
                    for i in range(0, len(coords) - 2, 2):
                        x1, y1, x2, y2 = coords[i], coords[i +
                                                           1], coords[i + 2], coords[i + 3]
                        draw.line([(x1, y1), (x2, y2)],
                                  fill=color, width=width)
            img.save(img_path)
            messagebox.showinfo('成功', f"文件已保存至:\n{img_path}")
            createlog(f"笔迹保存至{img_path}")

        except Exception as e:
            messagebox.showerror("保存失败", f"错误信息: {str(e)}")

    def update_cursor():
        if tool == "eraser":
            size = eraser_size.get()
            cursor = "circle"
        else:
            cursor = "arrow"
        canvas.config(cursor=cursor)

    last_x, last_y = None, None
    current_color = "black"
    tool = "pen"

    board = Toplevel()
    board.title("白板")
    board.attributes("-fullscreen", True)
    board.attributes("-alpha", 0.8)

    canvas = Canvas(board, borderwidth=0, bg='white')
    canvas.pack(fill=BOTH, expand=True)

    canvas.bind("<Button-1>", start_draw)
    canvas.bind("<B1-Motion>", draw)
    canvas.bind("<ButtonRelease-1>", reset_last)

    icon = open(FILEINPATH+"\\icon.ico", "wb+")
    icon.write(base64.b64decode(imgs.icon))
    icon.close()
    board.wm_iconbitmap(FILEINPATH+"\\icon.ico")

    control = Toplevel(board)
    style = ttk.Style()
    style.configure("TButton", width=6)
    control.overrideredirect(True)
    control.attributes("-topmost", True)
    control.attributes("-alpha", 0.8)
    board.bind("<Escape>", lambda e: exit_app(board, control))
    control.bind("<Escape>", lambda e: exit_app(board, control))

    icon = open(FILEINPATH+"\\icon.ico", "wb+")
    icon.write(base64.b64decode(imgs.icon))
    icon.close()
    control.wm_iconbitmap(FILEINPATH+"\\icon.ico")

    def exit_app(a=board, b=control):
        global screenshotstatus, miniwin
        miniwin.attributes("-alpha", "0.8")
        screenshotstatus = 0
        a.destroy()
        b.destroy()
    main_frame = Frame(control, bg='white')
    main_frame.pack()

    tool_frame = Frame(main_frame, bg='white')
    tool_frame.pack(side=LEFT)

    ttk.Button(tool_frame, text="画笔", command=lambda: set_tool(
        "pen"), style='TButton').pack()
    ttk.Button(tool_frame, text="橡皮", command=lambda: set_tool(
        "eraser"), style='TButton').pack()

    scaleframe = Frame(main_frame, bg='white')
    scaleframe.pack(side=LEFT)
    pen_size = IntVar(value=10)
    pen_scale = ttk.Scale(scaleframe, from_=1, to=150, variable=pen_size,
                          orient=HORIZONTAL, length=100, command=lambda _: set_tool("pen"))

    pen_scale.bind('<ButtonRelease-1>',
                   lambda e: on_scale_click(e, scale=pen_scale))
    pen_scale.pack(side=TOP)
    eraser_size = IntVar(value=50)
    eraser_scale = ttk.Scale(scaleframe, from_=10, to=450, variable=eraser_size,
                             orient=HORIZONTAL, length=100, command=lambda _: set_tool("eraser"))
    eraser_scale.bind('<ButtonRelease-1>',
                      lambda e: on_scale_click(e, scale=eraser_scale))
    eraser_scale.pack(side=TOP)
    Label(main_frame, text='粗细\n调节').pack(side=LEFT)

    color_frame = Frame(main_frame, bg='white')
    color_frame.pack(side=LEFT)
    ttk.Button(color_frame, text="颜色",
               command=choose_color, style='TButton').pack()
    ttk.Button(color_frame, text="清屏",
               command=clear_canvas, style='TButton').pack()

    alphaframe = Frame(main_frame, bg='white')
    alphaframe.pack(side=LEFT)
    lframe = Frame(alphaframe, bg='white')
    lframe.pack(side=BOTTOM)
    rframe = Frame(alphaframe, bg='white')
    rframe.pack(side=TOP)
    Label(lframe, text='透明度调节').pack(side=LEFT)
    ttk.Button(lframe, text="退出", command=lambda: exit_app(
        board, control)).pack(side=LEFT)

    def set_alpha(event, scale):
        x = event.x - scale.winfo_x()
        slider_width = scale.winfo_width()
        ratio = x / slider_width
        value = ratio * (scale['to'] - scale['from']) + scale['from']
        scale.set(value)
        board.attributes("-alpha", float(value)/10)

    alpha_size = IntVar(value=8)
    alpha_scale = ttk.Scale(
        rframe,
        from_=1,
        to=10,
        variable=alpha_size,
        orient=HORIZONTAL,
        length=110
    )
    # 绑定移动事件
    alpha_scale.bind('<B1-Motion>', lambda e: set_alpha(e, alpha_scale))
    alpha_scale.bind('<ButtonRelease-1>', lambda e: set_alpha(e, alpha_scale))
    alpha_scale.pack(side=LEFT)
    ttk.Button(rframe, text="保存", command=savefile).pack(side=LEFT)

    control.update_idletasks()
    control.geometry(f"+{board.winfo_screenwidth() - control.winfo_width() - 10}+"
                     f"{board.winfo_screenheight() - control.winfo_height() - 10}")

    control.protocol("WM_DELETE_WINDOW", lambda: exit_app())
    board.protocol("WM_DELETE_WINDOW", lambda: exit_app())

    update_cursor()

    board.mainloop()
    miniwin.attributes("-alpha", "0.8")
    screenshotstatus = 0
    return


def screendraw111():
    global screenshotstatus, main
    screenshotstatus = 1
    main.attributes("-alpha", "0")

    if config["is_screenshotsavedir_desktop"]:
        filea = 1
    else:
        filea = 0

    def start_draw(e):
        nonlocal last_x, last_y
        last_x, last_y = e.x, e.y

    def draw(e):
        nonlocal last_x, last_y
        if last_x and last_y:
            if tool == "pen":
                width = pen_size.get()
                color = current_color
            else:
                width = eraser_size.get()
                color = "white"

            canvas.create_line(last_x, last_y, e.x, e.y,
                               width=width, fill=color, capstyle=ROUND, smooth=True)
            last_x, last_y = e.x, e.y

    def reset_last(e):
        nonlocal last_x, last_y
        last_x, last_y = None, None

    def set_tool(t):
        nonlocal tool
        tool = t
        update_cursor()

    def choose_color():
        nonlocal current_color, tool
        color = colorchooser.askcolor()[1]
        if color:
            current_color = color
            set_tool("pen")

    def clear_canvas():
        canvas.delete("all")
        set_tool("pen")

    def set_alpha(val):
        board.attributes("-alpha", float(val))

    def savefile():
        try:
            if filea:
                a = f'writing_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
                desktop = os.path.join(os.path.join(
                    os.environ['USERPROFILE']), 'Desktop')
                screenshots_folder = os.path.join(desktop, 'Screenshots')
                if not os.path.exists(screenshots_folder):
                    os.makedirs(screenshots_folder)
                img_path = os.path.join(screenshots_folder, a)
            else:
                a = f'writing_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png'
                screenshots_folder = os.path.join(FILEPATH, 'Screenshots')
                if not os.path.exists(screenshots_folder):
                    os.makedirs(screenshots_folder)
                img_path = os.path.join(screenshots_folder, a)

            canvas.update()
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            img = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(img)
            for item in canvas.find_all():
                item_type = canvas.type(item)
                if item_type == "line":
                    coords = [round(x) for x in canvas.coords(item)]
                    color = canvas.itemcget(item, "fill") or "black"
                    width = max(
                        1, int(float(canvas.itemcget(item, "width") or 1)))
                    for i in range(0, len(coords) - 2, 2):
                        x1, y1, x2, y2 = coords[i], coords[i +
                                                           1], coords[i + 2], coords[i + 3]
                        draw.line([(x1, y1), (x2, y2)],
                                  fill=color, width=width)
            img.save(img_path)
            messagebox.showinfo('成功', f"文件已保存至:\n{img_path}")
            createlog(f"笔迹保存至{img_path}")

        except Exception as e:
            messagebox.showerror("保存失败", f"错误信息: {str(e)}")

    def update_cursor():
        if tool == "eraser":
            size = eraser_size.get()
            cursor = "circle"
        else:
            cursor = "arrow"
        canvas.config(cursor=cursor)

    last_x, last_y = None, None
    current_color = "black"
    tool = "pen"

    board = Toplevel()
    board.title("白板")
    board.attributes("-fullscreen", True)
    board.attributes("-alpha", 0.8)

    canvas = Canvas(board, bg="white")
    canvas.pack(fill=BOTH, expand=True)

    canvas.bind("<Button-1>", start_draw)
    canvas.bind("<B1-Motion>", draw)
    canvas.bind("<ButtonRelease-1>", reset_last)

    icon = open(FILEINPATH+"\\icon.ico", "wb+")
    icon.write(base64.b64decode(imgs.icon))
    icon.close()
    board.wm_iconbitmap(FILEINPATH+"\\icon.ico")

    control = Toplevel(board)
    style = ttk.Style()
    style.configure("TButton", width=6)
    control.overrideredirect(True)
    control.attributes("-topmost", True)
    control.attributes("-alpha", 0.8)
    board.bind("<Escape>", lambda e: exit_app(board, control))
    control.bind("<Escape>", lambda e: exit_app(board, control))

    icon = open(FILEINPATH+"\\icon.ico", "wb+")
    icon.write(base64.b64decode(imgs.icon))
    icon.close()
    control.wm_iconbitmap(FILEINPATH+"\\icon.ico")

    def exit_app(a=board, b=control):
        global screenshotstatus, main
        main.attributes("-alpha", "0.9")
        screenshotstatus = 0
        a.destroy()
        b.destroy()

    main_frame = Frame(control, bg='white')
    main_frame.pack()

    tool_frame = Frame(main_frame, bg='white')
    tool_frame.pack(side=LEFT)

    ttk.Button(tool_frame, text="画笔", command=lambda: set_tool(
        "pen"), style='TButton').pack()
    ttk.Button(tool_frame, text="橡皮", command=lambda: set_tool(
        "eraser"), style='TButton').pack()

    scaleframe = Frame(main_frame, bg='white')
    scaleframe.pack(side=LEFT)
    pen_size = IntVar(value=10)
    pen_scale = ttk.Scale(scaleframe, from_=1, to=150, variable=pen_size,
                          orient=HORIZONTAL, length=100, command=lambda _: set_tool("pen"))
    pen_scale.pack(side=TOP)
    eraser_size = IntVar(value=50)
    eraser_scale = ttk.Scale(scaleframe, from_=10, to=450, variable=eraser_size,
                             orient=HORIZONTAL, length=100, command=lambda _: set_tool("eraser"))
    eraser_scale.pack(side=TOP)
    Label(main_frame, text='粗细\n调节').pack(side=LEFT)

    color_frame = Frame(main_frame, bg='white')
    color_frame.pack(side=LEFT)
    ttk.Button(color_frame, text="颜色",
               command=choose_color, style='TButton').pack()
    ttk.Button(color_frame, text="清屏",
               command=clear_canvas, style='TButton').pack()

    alphaframe = Frame(main_frame, bg='white')
    alphaframe.pack(side=LEFT)
    lframe = Frame(alphaframe, bg='white')
    lframe.pack(side=BOTTOM)
    rframe = Frame(alphaframe, bg='white')
    rframe.pack(side=TOP)
    Label(lframe, text='透明度调节').pack(side=LEFT)
    ttk.Button(lframe, text="退出", command=lambda: exit_app(
        board, control)).pack(side=LEFT)
    alpha_scale = ttk.Scale(rframe, from_=0.1, to=1.0,
                            command=set_alpha, orient=HORIZONTAL, length=112)
    alpha_scale.set(0.8)
    alpha_scale.pack(side=LEFT)
    ttk.Button(rframe, text="保存", command=savefile).pack(side=LEFT)

    control.update_idletasks()
    control.geometry(f"+{board.winfo_screenwidth() - control.winfo_width() - 10}+"
                     f"{board.winfo_screenheight() - control.winfo_height() - 10}")

    control.protocol("WM_DELETE_WINDOW", lambda: exit_app())
    board.protocol("WM_DELETE_WINDOW", lambda: exit_app())

    update_cursor()

    board.mainloop()
    miniwin.attributes("-alpha", "1")
    screenshotstatus = 0
    return


"拍照"


def capturek(a=0, b=0, c=0):
    global miniwin
    cap = cv2.VideoCapture(a, cv2.CAP_DSHOW)

    if not cap.isOpened():
        cap.release()
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    s, pic = cap.read()
    if not s:
        cap.release()
        return
    a = f'img_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
    if b:
        desktop = os.path.join(os.path.join(
            os.environ['USERPROFILE']), 'Desktop')
        screenshots_folder = os.path.join(desktop, 'Screenshots')
    else:
        screenshots_folder = os.path.join(FILEPATH, 'Screenshots')

    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    img_path = os.path.join(screenshots_folder, a)

    cv2.imwrite(img_path, pic)
    # cap.release()
    '''
    cam = cv2.VideoCapture(a, cv2.CAP_DSHOW)
    a, img=cam.read()
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    cv2.imshow('Camera', img)
    a = f'img_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
    if b:
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        screenshots_folder = os.path.join(desktop, 'Screenshots')
    else:
        screenshots_folder = os.path.join(FILEPATH, 'Screenshots')

    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    img_path = os.path.join(screenshots_folder, a)
    img = cv2.flip(img, 1)
    cv2.imwrite(img_path, img)
    cam.release()
    '''
    cv2.destroyAllWindows()
    createlog(f"照片保存至{img_path}")
    if c:
        showbox("拍照", f"拍照保存至{a}")
    return img_path


def capture():
    global screenshotstatus, miniwin, config
    screenshotstatus = 1
    num = int(config["capture_num"])
    if config["is_screenshotsavedir_desktop"]:
        capturek(num, 1)
    else:
        capturek(num, 0)
    screenshotstatus = 0
    return


def capture111():
    global screenshotstatus, miniwin, config
    screenshotstatus = 1
    num = int(config["capture_num"])
    if config["is_screenshotsavedir_desktop"]:
        capturek(num, 1, 1)
    else:
        capturek(num, 0, 1)
    screenshotstatus = 0
    return


"视频播放"


"隐藏/显示授课助手"


def showtool(r=0):
    global toolstate, toolframe, miniwin, lhidebtn, rhidebtn
    if toolstate == 1:
        rhidebtn.pack_forget()
        lhidebtn.configure(text="显示", width=6)
        toolframe.pack_forget()
        miniwin.attributes("-alpha", "0.6")
        toolstate = 0
    else:
        lhidebtn.configure(text="隐藏", width=4)
        toolframe.pack(side=LEFT)
        miniwin.attributes("-alpha", "0.8")
        if r:
            rhidebtn.pack(side=RIGHT)
        toolstate = 1
    pass


def rshowtool(l=0):
    global toolstate, toolframe, miniwin, rhidebtn, lhidebtn
    if toolstate == 1:
        rhidebtn.configure(text="显示", width=6)
        lhidebtn.pack_forget()
        toolframe.pack_forget()
        miniwin.attributes("-alpha", "0.6")
        toolstate = 0
    else:
        if l:
            lhidebtn.pack(side=LEFT)
        rhidebtn.configure(text="隐藏", width=4)
        toolframe.pack(side=LEFT)
        miniwin.attributes("-alpha", "0.8")
        toolstate = 1
    pass


def center_bottom_window(main, width, height):
    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()
    x = (screen_width - width) // 2
    y = screen_height - height - 250
    main.geometry(f"{width}x{height}+{x}+{y}")


"文本框功能"


def showbox(a, b, c=[("确认", None)], d=0, e=0, p=0):
    global box

    def disable():
        pass

    if e:
        box = Tk()
        box.call("tk", "scaling", ScaleFactor / 80)
        s2 = ttk.Style()
        s2.configure("A.TButton", font=("微软雅黑", 12))
        s2.configure("B.TButton", font=("微软雅黑", 13))
        s2.configure("C.TButton", font=("微软雅黑", 9), foreground="black")
        s2.configure("CRED.TButton", font=("微软雅黑", 9), foreground="red")
        s2.configure("CGREEN.TButton", font=("微软雅黑", 9), foreground="green")
        s2.configure("CGRAY.TButton", font=("微软雅黑", 9), foreground="gray")
        s2.configure(
            "Vertical.TScrollbar",
            background="white",
            troughcolor="white",
            bordercolor="white",
            arrowcolor="black",
            gripcount=0,
        )
    else:
        if p != 0:
            box = Toplevel(p)
        else:
            box = Toplevel()
    box.title(a)
    box.geometry(f"{int(400*wp)}x{int(260*wp)}")
    box.resizable(0, 0)
    box.attributes("-toolwindow", 2)
    box.attributes("-topmost", "true")
    box.attributes("-alpha", "0.8")
    center_bottom_window(box, int(400*wp), int(260*wp))
    if d:
        box.protocol("WM_DELETE_WINDOW", disable)

    icon = open(FILEINPATH+"\\icon.ico", "wb+")
    icon.write(base64.b64decode(imgs.icon))
    icon.close()
    box.wm_iconbitmap(FILEINPATH+"\\icon.ico")
    result = StringVar()

    text_box = scrolledtext.ScrolledText(box, wrap=WORD, height=20, width=36, font=(
        "微软雅黑", 12), borderwidth=0, highlightthickness=0)
    text_box.insert(END, b)
    text_box.config(state=DISABLED)
    text_box.pack(side=LEFT, expand=True)

    button_frame = Frame(box, bg='white')
    button_frame.pack(side=RIGHT, fill=Y)
    for i, (text, command) in enumerate(c):
        btn = ttk.Button(
            button_frame,
            text=text,
            command=lambda t=text, f=command: [
                box.destroy(),
                f() if callable(f) else None,
                result.set(t),
            ],
        )
        btn.pack(side=TOP)

    box.grid_columnconfigure(0, weight=1)
    box.grid_columnconfigure(1, weight=0)
    box.grid_rowconfigure(0, weight=1)
    box.wait_window()

    return result.get()


def showinbk(a, b="", c=0, d=0, e=0, p=0, g=0, l=0):
    global inbk, ans, ans1

    def disable():
        pass

    def distroyinbk():
        inbk.destroy()
        return None
    if e:
        inbk = Tk()
        inbk.call("tk", "scaling", ScaleFactor / 80)
    else:
        if p != 0:
            inbk = Toplevel(p)
        else:
            inbk = Toplevel()
    inbk.title(a)
    inbk.geometry(f"{int(400*wp)}x{int(260*wp)}")
    inbk.resizable(0, 0)
    inbk.attributes("-toolwindow", 2)
    inbk.attributes("-topmost", True)
    inbk.attributes("-alpha", 0.8)
    center_bottom_window(inbk, int(400*wp), int(260*wp))
    if d:
        inbk.protocol("WM_DELETE_WINDOW", disable)
    else:
        inbk.protocol("WM_DELETE_WINDOW", distroyinbk)

    result = StringVar()
    ininput = None

    def confirm(e=None):
        nonlocal ininput
        if l:
            ininput = text_area.get("1.0", "end-1c")
        else:
            ininput = result.get()
        inbk.destroy()

    def cancel():
        nonlocal ininput
        ininput = None
        inbk.destroy()

    leftFrame1 = Frame(inbk, bg="white")
    leftFrame1.pack(side=LEFT, fill=BOTH, expand=True)
    Label(leftFrame1, text=b, font=("微软雅黑", 14)).pack(side=TOP)

    if l:
        text_area = scrolledtext.ScrolledText(
            leftFrame1, wrap="word", font=("微软雅黑", 14), width=30, height=10)
        text_area.pack(fill=BOTH, expand=True, side=TOP)
        text_area.focus_set()
        text_area.bind("<Control-Return>", confirm)
    else:
        inputi = ttk.Entry(leftFrame1, textvariable=result, font=(
            "微软雅黑", 14), show="*" if c else None, width=30)
        inputi.pack(fill=X, side=TOP)
        inputi.focus_set()
        inputi.bind("<Return>", confirm)

    button_frame = Frame(inbk, bg='white')
    button_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)
    ttk.Button(button_frame, text="确认", command=confirm).pack(
        side=TOP, pady=5, fill=X)
    if g:
        ttk.Button(button_frame, text="取消", command=cancel).pack(
            side=TOP, pady=5, fill=X)

    inbk.grid_columnconfigure(0, weight=1)
    inbk.grid_columnconfigure(1, weight=0)
    inbk.grid_rowconfigure(0, weight=1)
    inbk.wait_window()
    return ininput


"选择窗口"


def showchbk(a, b, c=0, d=0, p=0):
    global chbk, Listbox

    def disable():
        pass

    def distroychbk():
        chbk.destroy()
        return None

    if p != 0:
        chbk = Toplevel(p)
    else:
        chbk = Toplevel()
    chbk.title(a)
    chbk.geometry(f"{int(400*wp)}x{int(260*wp)}")
    chbk.resizable(0, 0)
    chbk.attributes("-toolwindow", 2)
    chbk.attributes("-topmost", "true")
    chbk.attributes("-alpha", "0.8")

    center_bottom_window(chbk, int(400*wp), int(260*wp))
    if d:
        chbk.protocol("WM_DELETE_WINDOW", disable)
    else:
        chbk.protocol("WM_DELETE_WINDOW", distroychbk)

    icon = open(FILEINPATH+"\\icon.ico", "wb+")
    icon.write(base64.b64decode(imgs.icon))
    icon.close()
    chbk.wm_iconbitmap(FILEINPATH+"\\icon.ico")

    optns = []

    list = Frame(chbk, bg='white')
    list.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

    if c:
        llistbox = Listbox(list, selectmode=MULTIPLE)
    else:
        llistbox = Listbox(list, selectmode=SINGLE)
    for option in b:
        llistbox.insert(END, option)
    llistbox.pack(fill=BOTH, expand=True)
    button_frame = Frame(chbk, bg='white')
    button_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)

    confirm_button = ttk.Button(
        button_frame,
        text="确认",
        command=lambda: [
            optns.extend(llistbox.get(i) for i in llistbox.curselection()),
            chbk.destroy(),
        ],
    )
    confirm_button.pack(side=TOP, pady=5, fill=X)

    cancel_button = ttk.Button(
        button_frame, text="取消", command=distroychbk
    )
    cancel_button.pack(side=TOP, pady=5, fill=X)
    chbk.wait_window()
    return optns


"授课助手抽奖功能"


def gjpraise(a):
    miniwin.attributes("-disabled", 1)
    global res, main
    op = showchbk("请选择学生", a, 1, p=miniwin)
    if op == [] or op == "" or op[0] == None:
        miniwin.attributes("-disabled", 0)
        return
    mk = showchbk(
        f"点评{op}",
        (
            1,
            2,
            3,
            4,
            5,
            -1,
            -2,
            -3,
            -4,
            -5,
        ), p=miniwin
    )
    if mk == [] or mk == "" or mk[0] == None:
        miniwin.attributes("-disabled", 0)
        return ()
    else:
        readf()
        for i in op:
            res[i] = res[i] + int(mk[0])
            res["admin"] = admin
        showf()
        f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
        res = f.write(str(res))
        f.close()
        f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
        res = eval(f.read())
        f.close()
        hidef()
        res.pop("admin")
        createlog(f"给予了\n{op}{int(mk[0])}分")
        renewmain()

        res = showbox(
            f"点评",
            f"给予了{op}{mk}分",
            [("OK", None), ("继续点评", lambda: gjpraise(a))], p=miniwin
        )

        createlog(f"给予了{op}{mk}分")
        miniwin.attributes("-disabled", 0)
        return 0


def gjpraise111(a):
    global res, main
    main.attributes("-disabled", 1)
    op = showchbk("请选择学生", a, 1, p=main)
    if op == [] or op == "" or op[0] == None:
        main.attributes("-disabled", 0)
        showmain()
        return
    mk = showchbk(
        f"点评{op}",
        (
            1,
            2,
            3,
            4,
            5,
            -1,
            -2,
            -3,
            -4,
            -5,
        ), p=main
    )
    if mk == [] or mk == "" or mk[0] == None:
        main.attributes("-disabled", 0)
        showmain()
        return ()
    else:
        readf()
        for i in op:
            res[i] = res[i] + int(mk[0])
            res["admin"] = admin
        showf()
        f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
        res = f.write(str(res))
        f.close()
        f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
        res = eval(f.read())
        f.close()
        hidef()
        res.pop("admin")
        createlog(f"给予了\n{op}{int(mk[0])}分")
        renewmain()

        res = showbox(
            f"点评",
            f"给予了{op}{mk}分",
            [("OK", None), ("继续点评", lambda: gjpraise(a))], p=main
        )

        createlog(f"给予了{op}{mk}分")
        main.attributes("-disabled", 0)
        showmain()
        return 0


"抽奖功能"


def randomstudent(aaa):
    global main, randomstate, miniwin
    if randomstate:
        return ()
    miniwin.attributes("-disabled", 1)
    randomstudent_button.configure(style="CGRAY.TButton")
    lst = []
    for l in res:
        lst.append(l)
    if aaa == 0:
        nums = []
        for i in range(1, len(res)+1):
            nums.append(i)
        op = showchbk(
            "选择人数", nums, p=miniwin
        )
        if op == []:
            miniwin.attributes("-disabled", 0)
            return ()
        elif op == "更多":
            op = gui.integerbox(
                "输入人数", title="班级管理器 抽奖", lowerbound=1, upperbound=len(lst)
            )
        if op == None:
            miniwin.attributes("-disabled", 0)
            return ()
        op = int(op[0])
    else:
        op = int(aaa)
    if op > len(lst):
        op = len(lst)
    b = ran.sample(lst, op)
    c = ""
    for i in b:
        c += i + "\n"
    setTxt(c)
    createlog(f"进行抽奖，抽奖人数：{len(b)}，抽奖内容：{b}")

    a = showbox(
        "抽奖结果",
        c,
        [
            ("点评", lambda: gjpraise(b)),
            ("重新抽奖", lambda: randomstudent(op)),
            ("再抽1个", lambda: randomstudent(1)),
            ("OK", None)
        ], p=miniwin
    )
    miniwin.attributes("-disabled", 0)
    randomstate = 0
    randomstudent_button.configure(style="C.TButton")


def randomstudent111(aaa=0):
    global main, randomstate, miniwin
    if randomstate:
        return ()
    main.attributes("-disabled", 1)
    lst = []
    for l in res:
        lst.append(l)
    if aaa == 0:
        nums = []
        for i in range(1, len(res)+1):
            nums.append(i)
        op = showchbk(
            "选择人数", nums, p=main
        )
        if op == []:
            main.attributes("-disabled", 0)
            showmain()
            return ()
        elif op == "更多":
            op = gui.integerbox(
                "输入人数", title="班级管理器 抽奖", lowerbound=1, upperbound=len(lst)
            )
        if op == None:
            main.attributes("-disabled", 0)
            showmain()
            return ()
        op = int(op[0])
    else:
        op = int(aaa)
    if op > len(lst):
        op = len(lst)
    b = ran.sample(lst, op)
    c = ""
    for i in b:
        c += i + "\n"
    setTxt(c)
    createlog(f"进行抽奖，抽奖人数：{len(b)}，抽奖内容：{b}")

    a = showbox(
        "抽奖结果",
        c,
        [
            ("点评", lambda: gjpraise111(b)),
            ("重新抽奖", lambda: randomstudent111(op)),
            ("再抽1个", lambda: randomstudent111(1)),
            ("OK", None)
        ], p=main
    )
    main.attributes("-disabled", 0)
    randomstate = 0


def showmain():
    try:
        win32gui.SetForegroundWindow(main.winfo_id())
    except:
        pass


"文件操作时显示文件，否则隐藏文件，防止篡改"


def showf():
    win32api.SetFileAttributes(
        FILEPATH + "\\.classdata", win32con.FILE_ATTRIBUTE_NORMAL
    )


def hidef():
    win32api.SetFileAttributes(
        FILEPATH + "\\.classdata", win32con.FILE_ATTRIBUTE_HIDDEN
    )


def readf():
    global res, admin
    f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
    res = eval(f.read())
    f.close()
    hidef()
    admin = res["admin"]
    res.pop("admin")


aaaaaaa = 1


def breakdown():
    global aaaaaaa
    aaaaaaa = 0
    quit()


if __name__ == "__main__":
    if os.path.exists(FILEPATH + "\\theprogramisrunning") or os.path.exists(
        FILEPATH + "\\theisrunning"
    ):

        showbox(
            f"管理",
            "程序可能已有一个实例在运行\n或由于上次意外退出程序\n导致出现此弹窗\n是否继续启动？",
            [
                ("是的", None),
                ("算了", breakdown),
            ], 1, 1
        )
    else:
        f = open(FILEPATH + "\\theprogramisrunning", "w")
        res = f.write("")
        f.close()
        win32api.SetFileAttributes(
            FILEPATH + "\\theprogramisrunning", win32con.FILE_ATTRIBUTE_HIDDEN
        )

    try:
        showf()
        with open(FILEPATH + "\\.classdata", 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
        f = open(FILEPATH + "\\.classdata", "r", encoding=encoding)
        res = f.read()
        f.close()
        hidef()
        if res == "":
            showf()
            f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
            res = f.write("{}")
            f.close()
            f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
            res = eval(f.read())
            f.close()
            hidef()
        else:
            showf()
            f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
            res = eval(f.read())
            f.close()
            hidef()
    except Exception as e:
        print(e)
        op = showbox(
            f"管理",
            f"检测到文件目录没有 .classdata 文件或内容错误，是否自动创建或重置？",
            [("继续", None), ("取消", None)],
            e=1,
        )
        if op == "继续":
            try:
                showf()
            except:
                pass
            f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
            res = f.write("{}")
            f.close()
            hidef()
            showbox(f"管理", f"成功", [("继续", None)], e=1)

            showf()
            f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
            res = eval(f.read())
            f.close()
            hidef()
        else:
            try:
                os.remove(FILEPATH + "\\theprogramisrunning")
            except:
                pass
            exit()

    try:
        with open(FILEPATH + "\\config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
            try:
                a = config["enable_lhidebtn"]
                a = config["enable_rhidebtn"]
                a = config["enable_mutebtn"]
                a = config["enable_pausebtn"]
                a = config["enable_screenshotbtn"]
                a = config["enable_randomstudentbtn"]
                a = config["enable_screendrawbtn"]
                a = config["is_screenshotsavedir_desktop"]
                a = config["enable_capture"]
                a = config["capture_num"]
                a = config["enable_volumeadjustment"]
            except:
                data = {
                        "//是否在授课助手中显示左/右 “隐藏/显示”按钮": 1,
                        "enable_lhidebtn": False,
                        "enable_rhidebtn": False,
                        "//是否在授课助手中显示“静音/解除”按钮": 1,
                        "enable_mutebtn": True,
                        "//是否在授课助手中显示“播放/暂停”按钮": 1,
                        "enable_pausebtn": True,
                        "//是否在授课助手中显示“截图”按钮": 1,
                        "enable_screenshotbtn": True,
                        "//是否将屏幕截图、保存至桌面，如果不是则屏幕截图会保存在程序 所在目录": 1,
                        "is_screenshotsavedir_desktop": True,
                        "//是否在授课助手中显示”抽奖“按钮": 1,
                        "enable_randomstudentbtn": True,
                        "//是否在授课助手中显示”批注（白板）“按钮": 1,
                        "enable_screendrawbtn": True,
                        "//是否在授课助手中显示“拍照”按钮": 1,
                        "enable_capture": True,
                        "//拍照按钮访问的摄像头编号": 1,
                        "capture_num": 0,
                        "//是否在授课助手中显示系统音量调整区域": 1,
                        "enable_volumeadjustment": True
                }
                with open(FILEPATH + "\\config.json", "w", encoding="utf-8") as json_file:
                    json.dump(data, json_file, ensure_ascii=False)
                with open(FILEPATH + "\\config.json", "r", encoding="utf-8") as json_file:
                    config = json.load(json_file)
                f = open(FILEPATH + "\\config.json", "r", encoding="utf-8")
                conf = str(f.read()).replace("'", '"').replace(
                    ',', ',\n').replace('{', '{\n').replace('}', '\n}')
                f.close()
                f = open(FILEPATH + "\\config.json", "w", encoding="utf-8")
                f.write(conf)
                f.close()

    except:
        pass
        data = {
                "//是否在授课助手中显示左/右 “隐藏/显示”按钮": 1,
                "enable_lhidebtn": False,
                "enable_rhidebtn": False,
                "//是否在授课助手中显示“静音/解除”按钮": 1,
                "enable_mutebtn": True,
                "//是否在授课助手中显示“播放/暂停”按钮": 1,
                "enable_pausebtn": True,
                "//是否在授课助手中显示“截图”按钮": 1,
                "enable_screenshotbtn": True,
                "//是否将屏幕截图、保存至桌面，如果不是则屏幕截图会保存在程序 所在目录": 1,
                "is_screenshotsavedir_desktop": True,
                "//是否在授课助手中显示”抽奖“按钮": 1,
                "enable_randomstudentbtn": True,
                "//是否在授课助手中显示”批注（白板）“按钮": 1,
                "enable_screendrawbtn": True,
                "//是否在授课助手中显示“拍照”按钮": 1,
                "enable_capture": True,
                "//拍照按钮访问的摄像头编号": 1,
                "capture_num": 0,
                "//是否在授课助手中显示系统音量调整区域": 1,
                "enable_volumeadjustment": True
        }
        with open(FILEPATH + "\\config.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False)
        with open(FILEPATH + "\\config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
        f = open(FILEPATH + "\\config.json", "r", encoding="utf-8")
        conf = str(f.read()).replace("'", '"').replace(
            ',', ',\n').replace('{', '{\n').replace('}', '\n}')
        f.close()
        f = open(FILEPATH + "\\config.json", "w", encoding="utf-8")
        f.write(conf)
        f.close()

    if "admin" not in res:
        while 1:
            ans = ans1 = ''
            ans = showinbk("管理",
                           "首次使用需创建密码",
                           c=1, d=1, e=1
                           )
            ans1 = showinbk("管理",
                            "请确认密码",
                            c=1, d=1, e=1
                            )
            if ans1 == ans:
                if ans == None:
                    pass
                else:
                    code = []
                    for w in str(ans):
                        num = ord(w)
                        code.append(num)
                    res["admin"] = code
                    showf()
                    f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
                    res = eval(f.read())
                    f.close()
                    hidef()
                    code = res["admin"]
                    key = ""
                    for w in code:
                        key = key + str(chr(w))
                break
            else:
                continue


def add_button(frame, row, col, text, name):
    global btnlist, wp
    a = 0
    if wp >= 2:
        a = 8
    elif wp >= 1.25:
        a = 9
    else:
        a = 8
    btnlist.append(
        ttk.Button(
            frame,
            width=a,
            text=text,
            style="A.TButton",
            command=lambda: praise(name),
        )
    )
    btnlist[len(btnlist) - 1].bind("<MouseWheel>", on_mouse_wheel)
    ppm3_tips.bind(btnlist[len(btnlist) - 1], text)
    btnlist[len(btnlist) - 1].grid(row=row, column=col, sticky="nsew")


def on_frame_configure(event, canvas, frame):
    canvas.configure(scrollregion=canvas.bbox("all"))


def renewmain():
    global btnlist
    for i in btnlist:
        i.destroy()
    btnlist = []

    readf()
    reslist = list(res.keys())
    resscorelist = list(res.values())
    b = 6

    i = 0
    if len(res) > b:
        for i in range(len(res) // b):
            for j in range(b):
                add_button(
                    frame,
                    i,
                    j,
                    f"{reslist[b*i+j]}:{resscorelist[b*i+j]}",
                    reslist[b * i + j],
                )
        for j in range(len(res) - b * (i + 1)):
            add_button(
                frame,
                i + 1,
                j,
                f"{reslist[b*(i+1)+j]}:{resscorelist[b*(i+1)+j]}",
                reslist[b * (i + 1) + j],
            )
    else:
        for j in range(len(res)):
            add_button(
                frame, 1, j, f"{reslist[j]}:{resscorelist[j]}", reslist[j])


def setTxt(txt):
    txtAr.config(state=NORMAL)
    txtAr.delete(1.0, END)
    txtAr.insert(INSERT, txt)
    txtAr.config(state=DISABLED)
    return 0


def minititle(txt):
    global miniwin
    miniwin.title(txt.replace('\n', ' '))
    time.sleep(2)
    miniwin.title('')


def createlog(txt):
    global miniwin

    def title():
        try:
            global miniwin
            miniwin.title(txt)
            time.sleep(2)
            miniwin.title('')
        except:
            pass
    try:
        f = open(FILEPATH + "\\log", "r", encoding="utf-8")
        aaa = f.read()
        f.close()
        f = open(FILEPATH + "\\log", "w", encoding="utf-8")
        f.write(f"{time.asctime()} {txt}\n\n{aaa}")
        f.close()
    except:
        pass
        f = open(FILEPATH + "\\log", "w", encoding="utf-8")
        f.write(f"{time.asctime()} {txt}\n\n{time.asctime()} 创建日志")
        f.close()
    threading.Thread(target=lambda: title()).start()


def randpick():
    global main
    main.attributes("-disabled", 1)
    lst = []
    for l in res:
        lst.append(l)
    nums = []
    for i in range(1, len(res) + 1):
        nums.append(i)
    op = showchbk("选择人数", nums, p=main)
    if op == [] or op == "":
        main.attributes("-disabled", 0)
        showmain()
        return ()
    if op == None:
        main.attributes("-disabled", 0)
        showmain()
        return ()
    op = int(op[0])
    if op > len(lst):
        op = len(lst)
    main.attributes("-disabled", 0)
    showmain()
    b = ran.sample(lst, op)
    c = ""
    for i in b:
        c += i + "\n"
    setTxt(c)
    createlog(f"进行抽奖，抽奖人数：{len(b)}，抽奖内容：{b}")


def showlog():
    try:
        f = open(FILEPATH + "\\log", "r", encoding="utf-8")
        aaa = f.read()
        f.close()
        setTxt(aaa)
    except:
        pass
        f = open(FILEPATH + "\\log", "w", encoding="utf-8")
        f.write(f"{time.asctime()} 创建日志")
        f.close()
        f = open(FILEPATH + "\\log", "r", encoding="utf-8")
        aaa = f.read()
        f.close()
        setTxt(aaa)


def showlist():
    readf()
    aaaa = sorted(res.items(), key=lambda d: d[1], reverse=True)
    output_str = ""
    for index, (key, value) in enumerate(aaaa, start=1):
        output_str += f"{index}: {key} {value}||￷|"

    lstt = list(output_str.split("||￷|"))

    lst = []
    aaa = 0
    bbb = 1
    ccc = {}
    for l in lstt:
        aaa += 1
        lst.append(l)
        if aaa >= 10:
            aaa = 0
            ccc[bbb] = lst
            bbb += 1
            lst = []

    aaa = 0
    ccc[bbb] = lst
    bbb += 1
    lst = []
    straaa = ""
    for i in ccc:
        for j in range(0, len(ccc[i])):
            straaa += ccc[i][j] + "\n"
    setTxt(straaa)


def praise(op):
    global res, main
    main.attributes("-disabled", 1)
    mk = showchbk(
        f"点评{op}",
        (
            1,
            2,
            3,
            4,
            5,
            -1,
            -2,
            -3,
            -4,
            -5,
        ), p=main
    )
    if mk == None or mk == "":
        main.attributes("-disabled", 0)
        showmain()
        return ()
    else:
        main.attributes("-disabled", 0)
        showmain()
        readf()
        res[op] = res[op] + int(mk[0])
        res["admin"] = admin
        showf()
        f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
        res = f.write(str(res))
        f.close()
        f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
        res = eval(f.read())
        f.close()
        hidef()
        res.pop("admin")
        createlog(f"给予了\n{op}{int(mk[0])}分")
        showbox("点评", f"给予了\n{op}{int(mk[0])}分")
        renewmain()
        main.attributes("-disabled", 0)
        showmain()
        return 0


def manage():
    global res, main
    showf()
    f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
    code = eval(f.read())["admin"]
    f.close()
    hidef()
    key = ""
    for w in code:
        key = key + str(chr(w))
    main.attributes("-disabled", 1)
    ans = showinbk("管理",
                   "请输入管理员密码",
                   c=1, p=main)
    if ans == key:
        while 1:
            op = showbox(
                "管理",
                "管理员页面\n请在右侧选择功能\n谨慎编辑" + str(res),
                [
                    ("添加", addstu),
                    #("批量添加", batadd),
                    ("删除", delstu),
                    ("清空表现", cleamk),
                    ("排序", sortt),
                    ("编辑数据文件", dataedit),
                    ("编辑配置文件", setedit),
                    ("退出", None),
                ], p=main
            )
            if op == "退出" or op == "" or op == []:
                main.attributes("-disabled", 0)
                showmain()
                return ()
    else:
        main.attributes("-disabled", 0)
        showmain()
        return ()


def on_scale_press(event):
    global scaleispressed
    scaleispressed = 1


def on_scale_release(event):
    global scaleispressed, volume_scale, mute_button, volume, slider_width, volume_scale
    scaleispressed = 0
    slider_width = volume_scale.winfo_width()
    value = (event.x / slider_width) * \
        (volume_scale['to'] - volume_scale['from']) + volume_scale['from']
    volume_scale.set(value)
    if volume.GetMute():
        mute_button.configure(text="解除", style="CRED.TButton")
    else:
        mute_button.configure(text="静音", style="C1.TButton")


def addstu():
    global res, ans
    ans = showinbk("管理", '请输入学生姓名，\n使用英文","或换行分开姓名可添加多个', p=main, l=1, g=1)
    if str(type(ans)) != "<class 'str'>" or len(ans) < 1:
        showbox(
            f"管理",
            f"取消操作",
            [("继续", None)], p=main
        )
        return
    res["admin"] = admin
    if "," or "\n" in ans:
        for i in list(ans.replace("\n", ",").replace(' ', '').split(",")):
            if i != "":
                res[i] = 0
    else:
        res[ans] = 0
    showf()
    f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
    res = f.write(str(res))
    f.close()
    f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
    res = eval(f.read())
    f.close()
    hidef()
    res.pop("admin")
    showbox(
        f"管理",
        f"添加成功" + str(res),
        [("继续", None)], p=main
    )
    createlog(f"增加学生：{ans}")
    renewmain()


def delstu():
    global res, ans
    ans = showchbk("请勾选需要删除的学生", res, 1, p=main)
    if ans == [] or ans == "" or ans[0] == None:
        showbox(
            f"管理",
            f"取消操作",
            [("继续", None)], p=main
        )
        return
    dlst = []
    for i in ans:
        res.pop(i)
        dlst.append(i)
    res["admin"] = admin
    showf()
    f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
    res = f.write(str(res))
    f.close()
    f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
    res = eval(f.read())
    f.close()
    hidef()
    res.pop("admin")
    createlog(f"删除学生：{dlst}")
    renewmain()
    showbox(
        f"管理",
        f"删除成功！\n" + str(res),
        [("继续", None)], p=main
    )


def cleamk():
    global res, ans
    showbox(
        f"管理",
        f"你真舍得清空吗",
        [("继续", None), ("取消", None)], p=main
    )
    try:
        if op != "继续":
            showbox(
                f"管理",
                f"取消操作",
                [("继续", None)], p=main
            )
            return
    except:
        showbox(
            f"管理",
            f"取消操作",
            [("继续", None)], p=main
        )
        return

    for i in res:
        res[i] = 0
    res["admin"] = admin
    showf()
    f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
    res = f.write(str(res))
    f.close()
    f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
    res = eval(f.read())
    f.close()
    hidef()
    res.pop("admin")
    createlog("清空了学生的表现")
    renewmain()
    showbox(
        f"管理",
        f"操作成功！",
        [("继续", None)], p=main
    )


def sortt():
    global res, ans
    sorted_keys = sorted(res.keys(), key=lambda x: "".join(lazy_pinyin(x)))
    sorted_data = {k: res[k] for k in sorted_keys}
    res = sorted_data
    res["admin"] = admin
    showf()
    with open(FILEPATH + "\\.classdata", "w", encoding="utf-8") as f:
        f.write(str(res))
    with open(FILEPATH + "\\.classdata", "r", encoding="utf-8") as f:
        res = eval(f.read())
    hidef()
    res.pop("admin")
    renewmain()
    showbox(
        f"管理",
        f"操作成功",
        [("继续", None)], p=main
    )


def batadd():
    global res, ans
    if (
        showbox(
            f"管理",
            f"请将学生们的姓名写在一个文本文件中，一行一个姓名，后选择那个文件即可添加\n（可以在excel里复制一列姓名粘贴进新建文本文档内，再导入添加👍",
            [("继续", None), ("取消", None)], p=main
        )
        == "继续"
    ):
        namelst = []
        try:
            path = filedialog.askopenfilename().replace("/", "\\")
            with open(path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding']
            f = open(path, 'r', encoding=encoding)
            for i in f.readlines():
                res[i.replace("\n", "")] = 0
                namelst.append(i.replace("\n", ""))
            f.close()
            res["admin"] = admin
            showf()
            f = open(FILEPATH + "\\.classdata", "w", encoding="utf-8")
            res = f.write(str(res))
            f.close()
            f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
            res = eval(f.read())
            f.close()
            hidef()
            res.pop("admin")
            createlog(f"增加学生：{namelst}")
            renewmain()
            showbox(
                f"管理",
                f"成功\n" + str(res),
                [("继续", None)], p=main
            )
        except:
            pass
            showbox(
                f"管理",
                f"失败\n" + str(res),
                [("继续", None)], p=main
            )
    return


def dataedit():
    global res, ans, box
    if (
        showbox(
            f"管理",
            f"谨慎编辑",
            [("继续", None), ("取消", None)], p=main
        )
        == "继续"
    ):
        createlog("编辑数据文件")
        os.system(f"notepad {FILEPATH}\\.classdata")
        try:
            showf()
            f = open(FILEPATH + "\\.classdata", "r", encoding="utf-8")
            res = eval(f.read())
            f.close()
            hidef()
            a = res["admin"]
            res.pop("admin")
            renewmain()
        except:

            showbox(
                f"管理",
                f"密码已更改 即将关闭程序",
                [("继续", None)], p=main
            )
            try:
                os.remove(FILEPATH + "\\theprogramisrunning")
            except:
                pass
            box.destroy()
            quit()
            pass
        renewmain()
    return


def showhelp():
    global wp
    helpw = Toplevel(main)
    helpw.title("帮助")
    helpw.geometry(f"{int(450*wp)}x{int(600*wp)}")
    helpw.resizable(False, 1)
    helpw.attributes("-toolwindow", 2)
    helpw.attributes("-topmost", "true")
    helpw.attributes("-alpha", "0.9")
    main.attributes("-disabled", 1)
    s3 = ttk.Style()
    s3.configure("a.TFrame", background="white")
    s3.configure("Title.TLabel",
                 font=("微软雅黑", 16, "bold"),
                 background="white",
                 foreground="#2c3e50")
    s3.configure("Subtitle.TLabel",
                 font=("微软雅黑", 12, "bold"),
                 background="white",
                 foreground="#3498db")
    s3.configure("Content.TLabel",
                 font=("微软雅黑", 10),
                 background="white",
                 foreground="#2c3e50",
                 wraplength=750,
                 justify="left")
    s3.configure("Close.TButton",
                 font=("微软雅黑", 10),
                 padding=5)

    main_frame = Frame(helpw, bg="white")
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    lframe = Frame(main_frame, bg='white')
    title_label = ttk.Label(lframe,
                            text="班级管理器 - 使用帮助",
                            style="Title.TLabel")
    title_label.pack(pady=(0, 20), fill=X, expand=False)

    canvas = Canvas(lframe, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(
        main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas,  bg='white')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    closebtn = ttk.Button(
        lframe, width=8, text="关闭", style="A.TButton", command=lambda: helpw.destroy()
    )

    canvas.pack(side=TOP, fill=BOTH, expand=True)
    lframe.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    closebtn.pack(side=BOTTOM)
    Label(lframe, font=('微软雅黑', 2)).pack(side=BOTTOM)

    sections = [
        {
            "title": "1. 基本功能",
            "content": """\
            —————————————————————————————
            - 班级管理
                添加、删除学生，管理学生表现分
            - 随机抽奖
                从班级中随机抽取学生
            - 排行榜
                查看学生表现分排名
            - 日志记录
                记录程序操作历史
            """
        },
        {
            "title": "2. 授课助手功能",
            "content": """
            —————————————————————————————
            - 静音/取消
                快速静音系统声音
            - 截图
                截取屏幕内容并保存
            - 拍照
                使用摄像头拍照
            - 抽奖
                快速随机抽取学生
            - 批注
                在屏幕上绘制批注
            - 音量调节
                调整系统音量大小
            """
        },
        {
            "title": "3. 数据保存位置",
            "content": """
            —————————————————————————————
            - 截图和拍照默认保存在桌面/Screenshots文件夹
            - 可以在配置文件(config.json)中修改保存位置
            - 班级数据保存在程序目录的.classdata文件(隐藏)
            - 日志记录保存在程序目录的log文件
            """
        },
        {
            "title": "4. 配置文件(config.json)选项",
            "content": """
            —————————————————————————————
            可以在config.json文件中修改以下配置文件(config.json)
                
            - enable_lhidebtn:
                是否显示左侧隐藏按钮
            - enable_rhidebtn: 
                是否显示右侧隐藏按钮
            - enable_mutebtn: 
                是否显示静音按钮
            - enable_screenshotbtn: 
                是否显示截图按钮
            - enable_randomstudentbtn: 
                是否显示抽奖按钮
            - enable_screendrawbtn: 
                是否显示批注按钮
            - enable_capture: 
                是否显示拍照按钮
            - capture_num: 
                摄像头编号(默认为0)
            - enable_volumeadjustment: 
                是否显示音量调节
            - is_screenshotsavedir_desktop: 
                截图是否保存到桌面 
                否则为程序根目录
            """
        },
        {
            "title": "5. 管理功能",
            "content": """
            —————————————————————————————
            - 添加
                输入学生姓名，支持批量添加。
            - 批量添加
                从文件导入学生名单。
                可以从excel软件中打开点名表, 将一列姓名选中复制
                粘贴至“添加”选项窗口文本框内即可成功导入
            - 删除
                从列表中选择(多选)学生并删除。
            - 清空表现
                重置所有学生的表现分。
            - 排序
                学生按姓名拼音排序。
            - 编辑数据文件
                直接打开 .classdata 文件进行编辑。
            - 编辑配置文件
                直接打开 config.json 文件进行编辑。
            """
        },
        {
            "title": "5. 常见问题",
            "content": """
            —————————————————————————————
            Q: 拍照功能无法使用？
            A: 请检查摄像头是否连接正常，
                并确认在配置文件(config.json)中
                选择了正确的摄像头编号。
            
            Q: 如何重置学生表现分？
            A: 在管理菜单中选择"清空表现"功能。
            
            Q: 批量导入失败？
            A: 检查文件编码是否为GBK。

            Q: 配置文件编辑后无效果？
            A: 重启软件或检查格式。

            Q: 忘记密码
            A: 系统打开显示隐藏文件
                编辑.classdata文件, 将admin对象删除
            """
        },
    ]

    for section in sections:
        ttk.Label(scrollable_frame,
                  text=section["title"],
                  style="Subtitle.TLabel").pack(anchor="w", pady=(15, 5), padx=60)

        ttk.Label(scrollable_frame,
                  text=section["content"].strip(),
                  style="Content.TLabel").pack(anchor="w", padx=0, pady=(0, 0))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    helpw.wait_window()

    main.attributes("-disabled", 0)
    showmain()


def setedit():
    global res, ans
    if (
        showbox(
            f"管理",
            f"新的配置重启程序后生效",
            [("继续", None), ("取消", None)], p=main
        )
        == "继续"
    ):
        createlog("编辑配置文件")
        os.system(f"notepad {FILEPATH}\\config.json")
        renewmain()


def showab():
    global main, wp
    aboutbg = Toplevel(main)
    aboutbg.title("背景")
    aboutbg.attributes("-fullscreen", True)
    # aboutbg.attributes("-topmost", -2)

    main.attributes("-alpha", "0")
    try:

        icon = open(FILEINPATH+"\\background.jpg", "wb+")
        icon.write(base64.b64decode(imgs.bg))
        icon.close()
        img = Image.open(FILEINPATH+"\\background.jpg")
        screen_width = aboutbg.winfo_screenwidth()
        screen_height = aboutbg.winfo_screenheight()
        ratio = max(screen_width / img.width, screen_height / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        left = (img.width - screen_width) / 2
        top = (img.height - screen_height) / 2
        right = left + screen_width
        bottom = top + screen_height
        img = img.crop((left, top, right, bottom))
        bg_img = ImageTk.PhotoImage(img)
        label = Label(aboutbg, image=bg_img)
        label.image = bg_img
        label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        pass

    aboutw = Toplevel(aboutbg)
    aboutw.title("关于")
    aboutw.geometry(f"{int(300*wp)}x{int(420*wp)}")
    aboutw.attributes("-topmost", -1)
    # aboutbg.lower(aboutw)

    window_width = int(300*wp)
    window_height = int(420*wp)
    screen_width = aboutw.winfo_screenwidth()
    screen_height = aboutw.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    aboutw.geometry(f"+{x}+{y}")
    s4 = ttk.Style()
    s4.configure("About.TFrame", background="white")
    s4.configure("Title.TLabel", font=("微软雅黑", 16, "bold"),
                 background="white", foreground="#2c3e50")
    s4.configure("Label.TLabel", font=("微软雅黑", 12), background="white")
    s4.configure("Link.TLabel", font=(
        "微软雅黑", 11, "underline"), background="white")

    abframe = ttk.Frame(aboutw, style="About.TFrame")
    abframe.pack(fill=BOTH, expand=True, padx=20, pady=20)

    ttk.Label(abframe, text="班级管理器", style="Title.TLabel").pack(pady=30)

    ttk.Label(abframe, text="v2.1a", style="Label.TLabel").pack(pady=5)
    linkl = ttk.Label(abframe,
                      text="项目主页",
                      cursor="hand2", style="Link.TLabel")
    linkl.bind("<Button-1>", lambda e: openurl())
    linkl.pack()
    linkl1 = ttk.Label(abframe,
                       text="copyright 2025",
                       cursor="hand2", style="Link.TLabel")
    linkl1.bind("<Button-1>", lambda e: openurl1())
    linkl1.pack()

    def deswin():
        try:
            aboutbg.destroy()
            aboutw.destroy()
        except:
            pass

    def openurl():
        webbrowser.open_new("https://github.com/Dayanshifu/ClassManager")
        deswin()
        return

    def openurl1():
        webbrowser.open_new("https://home.lolicon.xin")
        deswin()
        return

    ttk.Label(abframe, text="——————————————————",
              style="Label.TLabel").pack(pady=10)

    ttk.Label(abframe, text="你说得对，但是班级管家\n集成了白板、随机点名、\n积分系统、双师班授课辅助，\n甚至还有linux版本，\n适配各种白板，电脑，\n哪怕有冰点还原，\n装到有u盘里也能用",
              style="Label.TLabel").pack(pady=10)
    ttk.Button(abframe, text="关闭", command=deswin).pack(pady=10)
    aboutbg.protocol("WM_DELETE_WINDOW", deswin)
    aboutw.protocol("WM_DELETE_WINDOW", deswin)
    aboutbg.overrideredirect(True)
    aboutw.overrideredirect(True)
    aboutw.attributes("-alpha", "0.8")
    aboutw.bind("<Escape>", lambda e: deswin())
    aboutbg.bind("<Escape>", lambda e: deswin())
    aboutbg.wait_window()
    try:
        aboutw.wait_window()
    except:
        pass

    main.attributes("-alpha", "0.9")


def miniman():
    global miniwin, volume_scale, mute_button, sssl, screenshot_button, randomstudent_button, toolframe, lshow, rshow, lhidebtn, rhidebtn, screenshotstatus, main, toolstate, config, capture_button, pause_btn
    """if os.path.exists(FILEPATH + "\\theisrunning"):
        if not gui.ynbox(
            "已有一个程序正在运行，是否继续？", title="双师授课助手 运行向导"
        ):
            return ()
    else:
        f = open(FILEPATH + "\\theisrunning", "w")
        res = f.write("")
        f.close()
        win32api.SetFileAttributes(
            FILEPATH + "\\theisrunning", win32con.FILE_ATTRIBUTE_HIDDEN
        )"""
    toolstate = 1
    miniwin = Toplevel(main)
    miniwin.attributes("-toolwindow", 2)
    miniwin.attributes("-topmost", "true")
    miniwin.title("")
    miniwin.resizable(0, 0)
    miniwin.attributes("-alpha", "0.8")
    # miniwin.overrideredirect(True)
    width = 0

    def destroy_miniwin():
        global screenshotstatus, miniwin
        if not screenshotstatus:
            miniwin.destroy()
            main.attributes("-alpha", "0.9")
            global is_media_running
            is_media_running = False
            try:
                showmain()
            except:
                pass

    miniwin.protocol("WM_DELETE_WINDOW", destroy_miniwin)

    if config["enable_lhidebtn"]:
        lshow = 1
    else:
        lshow = 0
    if config["enable_rhidebtn"]:
        rshow = 1
        width += 35
    else:
        rshow = 0
    lhidebtn = ttk.Button(
        miniwin, width=4, text="隐藏", style="C.TButton", command=lambda: showtool(rshow)
    )
    if config["enable_lhidebtn"]:
        lhidebtn.pack(side=LEFT)

        width += 35
    rhidebtn = ttk.Button(
        miniwin, width=4, text="隐藏", style="C.TButton", command=lambda: rshowtool(lshow)
    )
    if config["enable_rhidebtn"]:

        width += 35
        rhidebtn.pack(side=RIGHT)

    toolframe = Frame(miniwin, bg='white')
    toolframe.pack(side=LEFT)

    mute_button = ttk.Button(
        toolframe, width=4, text="静音", style="C.TButton", command=mute_sound
    )
    if volume.GetMute():
        mute_button.configure(text="解除", style="CRED.TButton")
    else:
        mute_button.configure(text="静音", style="C1.TButton")
    if config["enable_mutebtn"]:
        width += 35
        mute_button.pack(side=LEFT)

    pause_btn = ttk.Button(
        toolframe, width=4, text="暂停", style="C.TButton", command=toggle_media_control
    )
    if config["enable_pausebtn"]:
        width += 35
        pause_btn.pack(side=LEFT)
        init_audio_meter()
        threading.Thread(target=update_status, daemon=True).start()
        update_button_state()

    screenshot_button = ttk.Button(
        toolframe, width=4, text="截图", style="C.TButton", command=screenshot
    )
    if config["enable_screenshotbtn"]:
        width += 35
        screenshot_button.pack(side=LEFT)

    randomstudent_button = ttk.Button(
        toolframe,
        width=4,
        text="抽奖",
        style="C.TButton",
        command=lambda: randomstudent(0),
    )
    if config["enable_randomstudentbtn"]:
        width += 35
        randomstudent_button.pack(side=LEFT)

    drawbtn = ttk.Button(
        toolframe, width=4, text="批注", style="C.TButton", command=screendraw
    )
    if config["enable_screendrawbtn"]:
        width += 35
        drawbtn.pack(side=LEFT)

    capture_button = ttk.Button(
        toolframe, width=4, text="拍照", style="C.TButton", command=lambda: capture()
    )
    if config["enable_capture"]:
        width += 35
        capture_button.pack(side=LEFT)

    sssl = ttk.Label(toolframe, text="音量\n调整", font=("微软雅黑", 4))
    if config["enable_volumeadjustment"]:
        sssl.pack(side=LEFT)
        ttk.Label(toolframe, text="-", font=("微软雅黑", 10)).pack(side=LEFT)

    volume_scale = ttk.Scale(
        toolframe,
        from_=0,
        to=100,
        length=int(round(67 * wp, 0)),
        orient="horizontal",
        command=adjust_volume,
        style="Horizontal.TScale"
    )
    volume_scale.set(get_volume_percent(get_master_volume_controller()))
    if config["enable_volumeadjustment"]:
        width += 110
        volume_scale.pack(side=LEFT)
        ttk.Label(toolframe, text="+", font=("微软雅黑", 10)).pack(side=LEFT)

    # volume_scale.bind("<ButtonPress-1>", on_scale_press)
    volume_scale.bind("<ButtonRelease-1>", on_scale_release)
    # volume_scale.bind('<Button-1>', on_scale_release)

    randomstudent_button = ttk.Button(
        toolframe,
        width=4,
        text="抽奖",
        style="C.TButton",
        command=lambda: randomstudent(0),
    )
    width = int(wp*width)
    height = int(wp*27)
    # closebtn= ttk.Button(toolframe,width=4,text="关闭",style='C.TButton', command=destroy_miniwin)
    # closebtn.pack(side=LEFT)
    main.attributes("-alpha", "0")
    screen_width = miniwin.winfo_screenwidth()
    screen_height = miniwin.winfo_screenheight()
    window_width = miniwin.winfo_reqwidth()
    window_height = miniwin.winfo_reqheight()
    x = screen_width - window_width
    y = screen_height - window_height
    x = int(x)
    y = int(y)
    miniwin.geometry(f"+{x-width}+{y-height}")

    # setvoice=threading(target=showvolumepercent())
    # setvoice.start()

    miniwin.after(100, showvolumepercent)
    miniwin.mainloop()
    try:
        box.destroy()
    except:
        pass


if aaaaaaa and __name__ == "__main__":

    main = Tk()

    main.call("tk", "scaling", ScaleFactor / 80)

    main.title("班级管理器")

    icon = open(FILEINPATH+"\\icon.ico", "wb+")
    icon.write(base64.b64decode(imgs.icon))
    icon.close()

    main.wm_iconbitmap(FILEINPATH+"\\icon.ico")

    main.resizable(0, 0)
    window_width = int(802 * wp)
    window_height = int(444 * wp)
    main.geometry(f"{window_width}x{window_height}")
    main.attributes("-alpha", "0.9")
    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = screen_height - window_height - 50
    main.geometry(f"+{x_position}+{y_position}")

    ppm3_tips = Pmw.Balloon(main)

    s1 = ttk.Style()
    s1.configure("A.TButton", font=("微软雅黑", 12))
    s1.configure("B.TButton", font=("微软雅黑", 13))
    s1.configure("C.TButton", font=("微软雅黑", 9), foreground="black")
    s1.configure("CRED.TButton", font=("微软雅黑", 9), foreground="red")
    s1.configure("CGREEN.TButton", font=("微软雅黑", 9), foreground="green")
    s1.configure("CGRAY.TButton", font=("微软雅黑", 9), foreground="gray")
    s1.configure("Horizontal.TScale",
                 troughcolor='gray',  # 轨道颜色
                 background='lightgray',        # 滑块背景色
                 troughrelief='gray',    # 轨道边框样式
                 sliderlength=25,          # 滑块长度
                 sliderthickness=10)

    menubar = Menu(main)
    file_menu = Menu(menubar, tearoff=0)

    file_menu.add_command(label="退出", command=main.quit)
    menubar.add_cascade(label="文件", menu=file_menu)

    function_menu = Menu(menubar, tearoff=0)
    function_menu.add_command(label="截图", command=lambda: screenshot111())
    function_menu.add_command(label="拍照", command=lambda: capture())
    function_menu.add_command(label="抽奖", command=lambda: randomstudent111())
    function_menu.add_command(label="静音/取消", command=lambda: mute_sound())
    function_menu.add_command(label="批注", command=lambda: screendraw111())
    function_menu.add_command(label="管理", command=lambda: manage())

    menubar.add_cascade(label="工具", menu=function_menu)
    about_menu = Menu(menubar, tearoff=0)

    menubar.add_cascade(label="帮助", menu=about_menu)
    about_menu.add_command(label="帮助", command=showhelp)
    about_menu.add_command(label="关于", command=showab)

    main.config(menu=menubar)
    main.configure(bg='white')
    toolbar = Frame(main, bg='white')
    toolbar.pack(side=TOP, fill="x")

    leftFrame = Frame(main, bg='white')
    bottomFrame = Frame(leftFrame, bg='white')

    canvasframe = Frame(leftFrame, bg='white')
    canvasframe.configure()
    canvas = Canvas(canvasframe, borderwidth=0, takefocus=0,
                    highlightthickness=0, bg='white')

    def on_mouse_wheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    canvas.bind("<MouseWheel>", on_mouse_wheel)
    frame = Frame(canvas, bg="white")
    vsb = ttk.Scrollbar(canvasframe, orient=VERTICAL,
                        command=canvas.yview, style="Vertical.TScrollbar")
    canvas.configure(yscrollcommand=vsb.set)
    canvas.configure()
    frame_window = canvas.create_window((0, 0), window=frame, anchor="nw")

    vsb.pack(side=RIGHT, fill=Y)
    canvas.pack(side=TOP, fill=BOTH, expand=True)
    frame.bind(
        "<Configure>", lambda event, c=canvas, f=frame: on_frame_configure(
            event, c, f)
    )

    btn1 = ttk.Button(
        bottomFrame,
        width=8,
        text="抽  奖",
        style="B.TButton",
        command=lambda: randpick(),
    )
    btn2 = ttk.Button(
        bottomFrame,
        width=8,
        text="排行榜",
        style="B.TButton",
        command=lambda: showlist(),
    )
    btn3 = ttk.Button(
        bottomFrame, width=8, text="日  志", style="B.TButton", command=lambda: showlog()
    )
    btn4 = ttk.Button(
        bottomFrame, width=8, text="管  理", style="B.TButton", command=lambda: manage()
    )
    btn5 = ttk.Button(
        bottomFrame, width=8, text="授课助手", style="B.TButton", command=lambda: miniman()
    )

    txtAr = scrolledtext.ScrolledText(
        main, width=29, font=("微软雅黑", 12), state=DISABLED)
    setTxt("欢迎使用班级管理器")

    btn1.pack(side=LEFT, padx=5)
    btn2.pack(side=LEFT, padx=5)
    btn3.pack(side=LEFT, padx=5)
    btn4.pack(side=LEFT, padx=5)
    if (
        config["enable_mutebtn"]
        or config["enable_pausebtn"]
        or config["enable_screenshotbtn"]
        or config["enable_randomstudentbtn"]
        or config["enable_screendrawbtn"]
        or config["enable_volumeadjustment"]
        or config["enable_capture"]
    ):
        btn5.pack(side=LEFT, padx=5)
    txtAr.pack(side=RIGHT, fill=BOTH)

    leftFrame.pack(side=LEFT, expand=True, fill=BOTH)
    Label(leftFrame, height=1).pack(side=BOTTOM)
    bottomFrame.pack(side=BOTTOM)
    Label(leftFrame, height=1).pack(side=BOTTOM)
    canvasframe.pack(side=BOTTOM, expand=True, fill=BOTH)

    readf()
    reslist = list(res.keys())
    resscorelist = list(res.values())
    b = 6
    i = 0

    if len(res) > b:
        for i in range(len(res) // b):
            for j in range(b):
                add_button(
                    frame,
                    i,
                    j,
                    f"{reslist[b*i+j]}:{resscorelist[b*i+j]}",
                    reslist[b * i + j],
                )
        for j in range(len(res) - b * (i + 1)):
            add_button(
                frame,
                i + 1,
                j,
                f"{reslist[b*(i+1)+j]}:{resscorelist[b*(i+1)+j]}",
                reslist[b * (i + 1) + j],
            )
    else:
        for j in range(len(res)):
            add_button(
                frame, 1, j, f"{reslist[j]}:{resscorelist[j]}", reslist[j])

    main.update_idletasks()
    on_frame_configure(None, canvas, frame)
    main.mainloop()

try:
    os.remove(FILEPATH + "\\theprogramisrunning")
except:
    pass
try:
    miniwin.destroy()
except:
    pass
try:
    box.destroy()
except:
    pass
try:
    os.remove(FILEPATH + "\\theisrunning")
except:
    pass
exit()
