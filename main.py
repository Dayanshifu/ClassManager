from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import tkinter
import os, sys, threading
from sys import *
import win32con, win32api, win32gui, win32process  # pywin32
import time, Pmw, base64
import random as ran

# from pypinyin import lazy_pinyin
import mypinyin
import easygui as box
import screenshots, subprocess
from datetime import datetime
from PIL import ImageGrab
import time, geticon, ctypes, json

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vl = volume.GetMasterVolumeLevel()
vr = volume.GetVolumeRange()

p = mypinyin.Pinyin()

screenshotstatus = 0

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

scaleispressed = 0

FILEPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
FILEINPATH = os.path.dirname(__file__)

drawboard = FILEPATH + "\\DesktopAnnotation\\DesktopAnnotation.exe"
admin = ""
res = {}
btnlist = btnname = []

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
scaling_factor = user32.GetDpiForSystem()
wp = scaling_factor / 96.0


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
            volume_scale.set(get_volume_percent(get_master_volume_controller()))
        except:
            pass
    if get_volume_percent(get_master_volume_controller()) == 0:
        try:
            set_volume_percent(get_master_volume_controller(), volume_scale.get())
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


def showtool():
    global toolstate, toolframe, miniwin
    if toolstate == 1:
        hidebtn.configure(text="显示", width=6)
        toolframe.pack_forget()
        miniwin.attributes("-alpha", "0.6")
        toolstate = 0
    else:
        hidebtn.configure(text="隐藏", width=4)
        toolframe.pack(side=LEFT)
        miniwin.attributes("-alpha", "0.8")
        toolstate = 1
    pass


def screendraw():
    global screenshotstatus, miniwin
    miniwin.attributes("-alpha", "0")
    # aaa=threading.Thread(target=subprocess.run([drawboard], shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    # aaa.start()
    try:
        subprocess.Popen(drawboard)
        time.sleep(0.6)
    except:
        pass
    miniwin.attributes("-alpha", "0.8")
    return


def screenshot():
    global screenshotstatus, miniwin, config
    screenshotstatus = 1
    miniwin.attributes("-alpha", "0")
    if config["is_screenshotsavedir_desktop"]:
        thread = threading.Thread(target=screenshots.screenshot())
    else:
        thread = threading.Thread(target=screenshots.screenshothy())
    thread.start()
    miniwin.attributes("-alpha", "0.8")
    screenshotstatus = 0
    return


def randomstudent():
    global main
    main.attributes("-disabled", 1)
    lst = []
    for l in res:
        lst.append(l)
    op = box.choicebox(
        "选择人数",
        choices=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "更多"),
        title="班级管理器 抽奖",
    )
    if op == None:
        main.attributes("-disabled", 0)
        return ()
    elif op == "更多":
        op = box.integerbox(
            "输入人数", title="班级管理器 抽奖", lowerbound=1, upperbound=len(lst)
        )
    if op == None:
        main.attributes("-disabled", 0)
        return ()
    op = int(op)
    if op > len(lst):
        op = len(lst)
    main.attributes("-disabled", 0)
    b = ran.sample(lst, op)
    c = ""
    for i in b:
        c += i + "\n"
    setTxt(c)
    fx.createlog(f"进行抽奖，抽奖人数：{len(b)}，抽奖内容：{b}")
    box.msgbox(c, title="抽奖结果")


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
    f = open(FILEPATH + "\\.classdata", "r")
    res = eval(f.read())
    f.close()
    hidef()
    admin = res["admin"]
    res.pop("admin")


if 1 == 1:

    if os.path.exists(FILEPATH + "\\theprogramisrunning") or os.path.exists(
        FILEPATH + "\\theisrunning"
    ):
        if not box.ynbox(
            "已有一个程序正在运行，是否继续？", title="班级管理器 运行向导"
        ):
            exit()
    else:
        f = open(FILEPATH + "\\theprogramisrunning", "w")
        res = f.write("")
        f.close()
        win32api.SetFileAttributes(
            FILEPATH + "\\theprogramisrunning", win32con.FILE_ATTRIBUTE_HIDDEN
        )

    try:
        showf()
        f = open(FILEPATH + "\\.classdata", "r")
        res = f.read()
        f.close()
        hidef()
        if res == "":
            showf()
            f = open(FILEPATH + "\\.classdata", "w")
            res = f.write("{}")
            f.close()
            f = open(FILEPATH + "\\.classdata", "r")
            res = eval(f.read())
            f.close()
            hidef()
        else:
            showf()
            f = open(FILEPATH + "\\.classdata", "r")
            res = eval(f.read())
            f.close()
            hidef()
    except:
        pass
        op = box.ynbox(
            "系统检测到你的文件目录没有 .classdata 文件或内容错误，是否自动创建或重置？",
            title="班级管理器 初始化向导",
        )
        if op == True:
            try:
                showf()
            except:
                pass
            f = open(FILEPATH + "\\.classdata", "w")
            res = f.write("{}")
            f.close()
            hidef()
            box.msgbox("创建成功！", title="班级管理器 初始化向导")
            showf()
            f = open(FILEPATH + "\\.classdata", "r")
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
        with open(FILEPATH + "\\config.json", "r") as json_file:
            config = json.load(json_file)
            try:
                a = config["enable_hidebtn"]
                a = config["enable_mutebtn"]
                a = config["enable_screenshotbtn"]
                a = config["enable_randomstudentbtn"]
                a = config["enable_screendrawbtn"]
                a = config["enable_volumeadjustment"]
                a = config["is_screenshotsavedir_desktop"]
            except:
                data = {
                    "enable_hidebtn": True,
                    "enable_mutebtn": True,
                    "enable_screenshotbtn": True,
                    "is_screenshotsavedir_desktop": True,
                    "enable_randomstudentbtn": True,
                    "enable_screendrawbtn": True,
                    "enable_volumeadjustment": True
                }
                with open(FILEPATH + "\\config.json", "w") as json_file:
                    json.dump(data, json_file)
                with open(FILEPATH + "\\config.json", "r") as json_file:
                    config = json.load(json_file)
    except:
        data = {
            "enable_hidebtn": True,
            "enable_mutebtn": True,
            "enable_screenshotbtn": True,
            "is_screenshotsavedir_desktop": True,
            "enable_randomstudentbtn": True,
            "enable_screendrawbtn": True,
            "enable_volumeadjustment": True
        }
        with open(FILEPATH + "\\config.json", "w") as json_file:
            json.dump(data, json_file)
        with open(FILEPATH + "\\config.json", "r") as json_file:
            config = json.load(json_file)

    if "admin" not in res:
        while True:
            ans = box.passwordbox(
                "首次使用需创建密码",
                title="班级管理器 初始化向导",
            )
            if ans == None:
                try:
                    os.remove(FILEPATH + "\\theprogramisrunning")
                except:
                    pass
                exit()
            if len(str(ans)) < 6:
                box.msgbox("密码不合法，请重新输入", title="班级管理器 初始化向导")
            else:
                break
        code = []
        for w in str(ans):
            num = ord(w)
            code.append(num)
        res["admin"] = code
        showf()
        f = open(FILEPATH + "\\.classdata", "w")
        res = f.write(str(res))
        f.close()
        f = open(FILEPATH + "\\.classdata", "r")
        res = eval(f.read())
        f.close()
        hidef()
        code = res["admin"]
        key = ""
        for w in code:
            key = key + str(chr(w))
        box.msgbox("请保管好你的管理员密码：\n" + key, title="班级管理器 初始化向导")


def add_button(frame, row, col, text, name):
    global btnlist
    btnlist.append(
        ttk.Button(
            frame,
            width=8,
            text=text,
            style="A.TButton",
            command=lambda: fx.praise(name),
        )
    )
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
    if len(res) > 6:
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
            add_button(frame, 1, j, f"{reslist[j]}:{resscorelist[j]}", reslist[j])


def setTxt(txt):
    txtAr.config(state=NORMAL)
    txtAr.delete(1.0, END)
    txtAr.insert(INSERT, txt)
    txtAr.config(state=DISABLED)
    return 0


class fx:
    def createlog(txt):
        try:
            f = open(FILEPATH + "\\log", "r")
            aaa = f.read()
            f.close()
            f = open(FILEPATH + "\\log", "w")
            f.write(f"{time.asctime()} {txt}\n\n{aaa}")
            f.close()
        except:
            f = open(FILEPATH + "\\log", "w")
            f.write(f"{time.asctime()} {txt}\n\n{time.asctime()} 创建日志")
            f.close()

    def randpick():
        global main
        main.attributes("-disabled", 1)
        lst = []
        for l in res:
            lst.append(l)
        op = box.choicebox(
            "选择人数",
            choices=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "更多"),
            title="班级管理器 抽奖",
        )
        if op == None:
            main.attributes("-disabled", 0)
            win32gui.SetForegroundWindow(main.winfo_id())
            return ()
        elif op == "更多":
            op = box.integerbox(
                "输入人数", title="班级管理器 抽奖", lowerbound=1, upperbound=len(lst)
            )
        if op == None:
            main.attributes("-disabled", 0)
            win32gui.SetForegroundWindow(main.winfo_id())
            return ()
        op = int(op)
        if op > len(lst):
            op = len(lst)
        main.attributes("-disabled", 0)
        win32gui.SetForegroundWindow(main.winfo_id())
        b = ran.sample(lst, op)
        c = ""
        for i in b:
            c += i + "\n"
        setTxt(c)
        fx.createlog(f"进行抽奖，抽奖人数：{len(b)}，抽奖内容：{b}")

    def showlog():
        try:
            f = open(FILEPATH + "\\log", "r")
            aaa = f.read()
            f.close()
            setTxt(aaa)
        except:
            f = open(FILEPATH + "\\log", "w")
            f.write(f"{time.asctime()} 创建日志")
            f.close()
            f = open(FILEPATH + "\\log", "r")
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
        fx.createlog(f"查看排行榜")

    def praise(op):
        global res, main
        main.attributes("-disabled", 1)
        mk = box.choicebox(
            f"选择分数 {op}",
            choices=(
                "1",
                "2",
                "3",
                "4",
                "5",
                "抽奖",
                "抽罚",
                "-1",
                "-2",
                "-3",
                "-4",
                "-5",
            ),
            title=f"班级管理器 点评{op}",
        )
        if mk == None:
            main.attributes("-disabled", 0)
            win32gui.SetForegroundWindow(main.winfo_id())
            return ()
        else:
            if mk == "抽奖":
                if ran.randint(1, 25) == 1:
                    mk = ran.randint(1, 20)
                else:
                    mk = ran.randint(1, 5)
            elif mk == "抽罚":
                if ran.randint(1, 25) == 1:
                    mk = 0 - ran.randint(1, 20)
                else:
                    mk = 0 - ran.randint(1, 5)
            main.attributes("-disabled", 0)
            win32gui.SetForegroundWindow(main.winfo_id())
            readf()
            res[op] = res[op] + int(mk)
            res["admin"] = admin
            showf()
            f = open(FILEPATH + "\\.classdata", "w")
            res = f.write(str(res))
            f.close()
            f = open(FILEPATH + "\\.classdata", "r")
            res = eval(f.read())
            f.close()
            hidef()
            res.pop("admin")
            fx.createlog(f"给予了{op}{mk}分")
            renewmain()
            return ()

    def manage():
        global res, main
        showf()
        f = open(FILEPATH + "\\.classdata", "r")
        code = eval(f.read())["admin"]
        f.close()
        hidef()
        key = ""
        for w in code:
            key = key + str(chr(w))
        main.attributes("-disabled", 1)
        ans = box.passwordbox("请输入管理员密码", title="班级管理器 管理设置")
        if ans == key:
            while 1:
                op = box.choicebox(
                    "选择你要做什么",
                    choices=(
                        "添加",
                        "批量添加",
                        "删除",
                        "清空表现",
                        "排序",
                        "编辑数据文件",
                        "退出",
                    ),
                    title="班级管理器 管理设置",
                )
                if op == "添加":
                    ans = box.enterbox(
                        '请输入学生姓名，输入英文","可添加多个',
                        title="班级管理器 管理设置 添加学生",
                    )
                    if str(type(ans)) != "<class 'str'>":
                        box.msgbox("取消", title="班级管理器 管理设置")
                        continue
                    res["admin"] = admin
                    if "," in ans:
                        for i in list(ans.split(",")):
                            res[i] = 0
                    else:
                        res[ans] = 0
                    showf()
                    f = open(FILEPATH + "\\.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "\\.classdata", "r")
                    res = eval(f.read())
                    f.close()
                    hidef()
                    res.pop("admin")
                    box.msgbox(
                        "添加成功！\n" + str(res), title="班级管理器 管理设置 添加学生"
                    )
                    fx.createlog(f"增加学生：{ans}")
                    renewmain()
                elif op == "删除":
                    ans = box.enterbox(
                        '请输入要删除学生姓名，输入英文","可添加多个\n' + str(res),
                        title="班级管理器 管理设置 删除学生",
                    )
                    dlst = []
                    if str(type(ans)) != "<class 'str'>":
                        box.msgbox("取消", title="班级管理器 管理设置")
                        continue
                    if "," in ans:
                        for i in list(ans.split(",")):
                            if i not in res:
                                box.msgbox(
                                    f"没有找到{i}", title="班级管理器 管理设置 删除学生"
                                )
                                continue
                            res.pop(i)
                            dlst.append(i)
                    else:
                        if ans not in res:
                            box.msgbox("没有找到", title="班级管理器 管理设置 删除学生")
                            continue
                        res.pop(ans)
                        dlst.append(ans)
                    res["admin"] = admin
                    showf()
                    f = open(FILEPATH + "\\.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "\\.classdata", "r")
                    res = eval(f.read())
                    f.close()
                    hidef()
                    res.pop("admin")
                    fx.createlog(f"删除学生：{dlst}")
                    renewmain()
                    box.msgbox(
                        "删除成功！\n" + str(res), title="班级管理器 管理设置 删除学生"
                    )
                elif op == "清空表现":
                    op = box.ynbox(
                        "你真舍得清空吗", title="班级管理器 管理设置 清空表现"
                    )
                    if op != True:
                        box.msgbox("取消", title="班级管理器 管理设置 清空表现")
                        continue
                    for i in res:
                        res[i] = 0
                    res["admin"] = admin
                    showf()
                    f = open(FILEPATH + "\\.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "\\.classdata", "r")
                    res = eval(f.read())
                    f.close()
                    hidef()
                    res.pop("admin")
                    fx.createlog("清空了学生的表现")
                    renewmain()
                    box.msgbox(
                        "清空成功！\n" + str(res), title="班级管理器 管理设置 清空表现"
                    )
                elif op == "排序":
                    sorted_keys = sorted(
                        # res.keys(), key=lambda x: "".join(lazy_pinyin(x))
                        res.keys(),
                        key=lambda x: "".join(p.get_pinyin(x)),
                    )
                    sorted_data = {k: res[k] for k in sorted_keys}
                    res = sorted_data
                    res["admin"] = admin
                    showf()
                    f = open(FILEPATH + "\\.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "\\.classdata", "r")
                    res = eval(f.read())
                    f.close()
                    hidef()
                    res.pop("admin")
                    fx.createlog("学生排序")
                    renewmain()
                    box.msgbox(
                        "排序成功！\n" + str(res), title="班级管理器 管理设置 学生排序"
                    )
                elif op == "批量添加":
                    if box.ccbox(
                        "请将学生们的姓名写在一个文本文件(gb2312编码)中，一行一个姓名，后选择那个文件即可添加",
                        title="班级管理器 管理设置 批量添加",
                    ):
                        namelst = []
                        f = open(box.fileopenbox())
                        for i in f.readlines():
                            res[i.replace("\n", "")] = 0
                            namelst.append(i.replace("\n", ""))
                        f.close()
                        res["admin"] = admin
                        showf()
                        f = open(FILEPATH + "\\.classdata", "w")
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH + "\\.classdata", "r")
                        res = eval(f.read())
                        f.close()
                        hidef()
                        res.pop("admin")
                        fx.createlog(f"增加学生：{namelst}")
                        renewmain()
                        box.msgbox(
                            "批量添加成功！\n" + str(res),
                            title="班级管理器 管理设置 批量添加",
                        )
                elif op == "编辑数据文件":
                    if box.ccbox("谨慎编辑", title="班级管理器 管理设置 编辑数据文件"):
                        fx.createlog("编辑数据文件")
                        os.system(f"notepad {FILEPATH}\\.classdata")
                        renewmain()
                elif op == "编辑配置文件":
                    if box.ccbox("新的配置重启后生效", title="班级管理器 管理设置 编辑数据文件"):
                        fx.createlog("编辑配置文件")
                        os.system(f"notepad {FILEPATH}\\config.json")
                        renewmain()
                else:
                    main.attributes("-disabled", 0)
                    win32gui.SetForegroundWindow(main.winfo_id())
                    return ()
        else:
            main.attributes("-disabled", 0)
            win32gui.SetForegroundWindow(main.winfo_id())
            return ()


def on_scale_press(event):
    global scaleispressed
    scaleispressed = 1


def on_scale_release(event):
    global scaleispressed, volume_scale, mute_button, volume
    scaleispressed = 0
    if volume.GetMute():
        mute_button.configure(text="解除", style="CRED.TButton")
    else:
        mute_button.configure(text="静音", style="C1.TButton")


def miniman():
    global miniwin, volume_scale, mute_button, sssl, screenshot_button, randomstudent_button, toolframe, hidebtn, screenshotstatus, main, toolstate, config
    """if os.path.exists(FILEPATH + "\\theisrunning"):
        if not box.ynbox(
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
    fx.createlog(f"打开双师授课助手")
    toolstate = 1
    miniwin = Toplevel()
    miniwin.attributes("-toolwindow", 2)
    miniwin.attributes("-topmost", "true")
    miniwin.title("")
    miniwin.resizable(0, 0)
    miniwin.attributes("-alpha", "0.8")
    # miniwin.overrideredirect(True)

    def destroy_miniwin():
        global screenshotstatus
        if not screenshotstatus:
            try:
                os.remove(FILEPATH + "\\theisrunning")
            except:
                pass
            miniwin.destroy()
            main.attributes("-alpha", "0.9")

    miniwin.protocol("WM_DELETE_WINDOW", destroy_miniwin)

    hidebtn = ttk.Button(
        miniwin, width=4, text="隐藏", style="C.TButton", command=showtool
    )
    if config["enable_hidebtn"]:
        hidebtn.pack(side=LEFT)

    toolframe = ttk.Frame(miniwin)
    toolframe.pack(side=LEFT)

    mute_button = ttk.Button(
        toolframe, width=4, text="静音", style="C.TButton", command=mute_sound
    )
    if volume.GetMute():
        mute_button.configure(text="解除", style="CRED.TButton")
    else:
        mute_button.configure(text="静音", style="C1.TButton")
    if config["enable_mutebtn"]:
        mute_button.pack(side=LEFT)

    screenshot_button = ttk.Button(
        toolframe, width=4, text="截图", style="C.TButton", command=screenshot
    )
    if config["enable_screenshotbtn"]:
        screenshot_button.pack(side=LEFT)

    randomstudent_button = ttk.Button(
        toolframe, width=4, text="抽奖", style="C.TButton", command=randomstudent
    )
    if config["enable_randomstudentbtn"]:
        randomstudent_button.pack(side=LEFT)

    drawbtn = ttk.Button(
        toolframe, width=4, text="批注", style="C.TButton", command=screendraw
    )
    if os.path.exists(drawboard) and config["enable_screendrawbtn"]:
        drawbtn.pack(side=LEFT)

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
    )
    if config["enable_volumeadjustment"]:
        volume_scale.pack(side=LEFT)
    volume_scale.set(get_volume_percent(get_master_volume_controller()))
    if config["enable_volumeadjustment"]:
        ttk.Label(toolframe, text="+", font=("微软雅黑", 10)).pack(side=LEFT)
    volume_scale.bind("<ButtonPress-1>", on_scale_press)
    volume_scale.bind("<ButtonRelease-1>", on_scale_release)

    # closebtn= ttk.Button(toolframe,width=4,text="关闭",style='C.TButton', command=destroy_miniwin)
    # closebtn.pack(side=LEFT)
    main.attributes("-alpha", "0")

    # setvoice=threading(target=showvolumepercent())
    # setvoice.start()
    miniwin.after(100, showvolumepercent)
    miniwin.mainloop()


main = Tk()

main.tk.call("tk", "scaling", ScaleFactor / 80)

main.title("班级管理器")
icon = open("gui_icon.ico", "wb+")
icon.write(base64.b64decode(geticon.img))
icon.close()
main.iconbitmap("gui_icon.ico")
os.remove("gui_icon.ico")
main.resizable(0, 0)
main.geometry(f"{int(802*wp)}x{int(444*wp)}")
main.attributes("-alpha", "0.9")

ppm3_tips = Pmw.Balloon(main)

s1 = s2 = ttk.Style()
s1.configure("A.TButton", font=("微软雅黑", 12))
s2.configure("B.TButton", font=("微软雅黑", 13))
s2.configure("C.TButton", font=("微软雅黑", 9), foreground="black")
s2.configure("CRED.TButton", font=("微软雅黑", 9), foreground="red")

leftFrame = ttk.Frame(main)
bottomFrame = ttk.Frame(leftFrame)


canvasframe = ttk.Frame(leftFrame)
canvas = Canvas(canvasframe, borderwidth=0)
frame = ttk.Frame(canvas)
vsb = ttk.Scrollbar(canvasframe, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set, width=6 * 80 * 6)
frame_window = canvas.create_window((0, 0), window=frame, anchor="nw")

vsb.pack(side=RIGHT, fill=Y)
canvas.pack(side=TOP, fill=BOTH, expand=True)
frame.bind(
    "<Configure>", lambda event, c=canvas, f=frame: on_frame_configure(event, c, f)
)


btn1 = ttk.Button(
    bottomFrame,
    width=8,
    text="抽  奖",
    style="B.TButton",
    command=lambda: fx.randpick(),
)
btn2 = ttk.Button(
    bottomFrame,
    width=8,
    text="排行榜",
    style="B.TButton",
    command=lambda: fx.showlist(),
)
btn3 = ttk.Button(
    bottomFrame, width=8, text="日  志", style="B.TButton", command=lambda: fx.showlog()
)
btn4 = ttk.Button(
    bottomFrame, width=8, text="管  理", style="B.TButton", command=lambda: fx.manage()
)
btn5 = ttk.Button(
    bottomFrame, width=8, text="授课助手", style="B.TButton", command=lambda: miniman()
)

txtAr = scrolledtext.ScrolledText(main, width=29, font=("微软雅黑", 12), state=DISABLED)
setTxt("欢迎使用班级管理器")


titlelabel = Label(main, height=1)
titlelabel.pack(side=TOP)

btn1.pack(side=LEFT)
btn2.pack(side=LEFT)
btn3.pack(side=LEFT)
btn4.pack(side=LEFT)
if config["enable_mutebtn"] or config["enable_screenshotbtn"] or config["enable_randomstudentbtn"] or config["enable_screendrawbtn"] or config["enable_volumeadjustment"]:
    btn5.pack(side=LEFT)
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
if len(res) > 6:
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
        add_button(frame, 1, j, f"{reslist[j]}:{resscorelist[j]}", reslist[j])

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
    os.remove(FILEPATH + "\\theisrunning")
except:
    pass
exit()
