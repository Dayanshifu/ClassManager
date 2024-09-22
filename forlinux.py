from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import os, sys
from sys import *
import time, Pmw, subprocess
import random as ran
import mypinyin
import easygui as box


FILEPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
FILEINPATH = os.path.dirname(__file__)
admin = ""
res = {}
btnlist = btnname = []
p = mypinyin.Pinyin()


def readf():
    global res, admin
    f = open(FILEPATH + "/.classdata", "r")
    res = eval(f.read())
    f.close()
    admin = res["admin"]
    res.pop("admin")


if 1 == 1:
    if os.path.exists(FILEPATH + "/theprogramisrunning") or os.path.exists(
        FILEPATH + "/theisrunning"
    ):
        if not box.ynbox(
            "已有一个程序正在运行，是否继续？", title="班级管理器 运行向导"
        ):
            exit()
    else:
        f = open(FILEPATH + "/theprogramisrunning", "w")
        res = f.write("")
        f.close()

    try:

        f = open(FILEPATH + "/.classdata", "r")
        res = f.read()
        f.close()

        if res == "":

            f = open(FILEPATH + "/.classdata", "w")
            res = f.write("{}")
            f.close()
            f = open(FILEPATH + "/.classdata", "r")
            res = eval(f.read())
            f.close()

        else:

            f = open(FILEPATH + "/.classdata", "r")
            res = eval(f.read())
            f.close()

    except:
        pass
        op = box.ynbox(
            "系统检测到你的文件目录没有 .classdata 文件或内容错误，是否自动创建或重置？",
            title="班级管理器 初始化向导",
        )
        if op == True:
            f = open(FILEPATH + "/.classdata", "w")
            res = f.write("{}")
            f.close()

            box.msgbox("创建成功！", title="班级管理器 初始化向导")

            f = open(FILEPATH + "/.classdata", "r")
            res = eval(f.read())
            f.close()

        else:
            try:
                os.remove(FILEPATH + "/theprogramisrunning")
            except:
                pass
            exit()
    if "admin" not in res:
        while True:
            ans = box.passwordbox(
                "首次使用需创建密码",
                title="班级管理器 初始化向导",
            )
            if ans == None:
                try:
                    os.remove(FILEPATH + "/theprogramisrunning")
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

        f = open(FILEPATH + "/.classdata", "w")
        res = f.write(str(res))
        f.close()
        f = open(FILEPATH + "/.classdata", "r")
        res = eval(f.read())
        f.close()

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
    b = 5

    i = 0
    if len(res) > 5:
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
            f = open(FILEPATH + "/log", "r")
            aaa = f.read()
            f.close()
            f = open(FILEPATH + "/log", "w")
            f.write(f"{time.asctime()} {txt}\n\n{aaa}")
            f.close()
        except:
            f = open(FILEPATH + "/log", "w")
            f.write(f"{time.asctime()} {txt}\n\n{time.asctime()} 创建日志")
            f.close()

    def randpick():
        global main

        lst = []
        for l in res:
            lst.append(l)
        op = box.choicebox(
            "选择人数",
            choices=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "更多"),
            title="班级管理器 抽奖",
        )
        if op == None:

            return ()
        elif op == "更多":
            op = box.integerbox(
                "输入人数", title="班级管理器 抽奖", lowerbound=1, upperbound=len(lst)
            )
        if op == None:

            return ()
        op = int(op)
        if op > len(lst):
            op = len(lst)

        b = ran.sample(lst, op)
        c = ""
        for i in b:
            c += i + "\n"
        setTxt(c)
        fx.createlog(f"进行抽奖，抽奖人数：{len(b)}，抽奖内容：{b}")

    def showlog():
        try:
            f = open(FILEPATH + "/log", "r")
            aaa = f.read()
            f.close()
            setTxt(aaa)
        except:
            f = open(FILEPATH + "/log", "w")
            f.write(f"{time.asctime()} 创建日志")
            f.close()
            f = open(FILEPATH + "/log", "r")
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

            readf()
            res[op] = res[op] + int(mk)
            res["admin"] = admin

            f = open(FILEPATH + "/.classdata", "w")
            res = f.write(str(res))
            f.close()
            f = open(FILEPATH + "/.classdata", "r")
            res = eval(f.read())
            f.close()

            res.pop("admin")
            fx.createlog(f"给予了{op}{mk}分")
            renewmain()
            return ()

    def manage():
        global res, main

        f = open(FILEPATH + "/.classdata", "r")
        code = eval(f.read())["admin"]
        f.close()

        key = ""
        for w in code:
            key = key + str(chr(w))
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

                    f = open(FILEPATH + "/.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "/.classdata", "r")
                    res = eval(f.read())
                    f.close()

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

                    f = open(FILEPATH + "/.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "/.classdata", "r")
                    res = eval(f.read())
                    f.close()

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

                    f = open(FILEPATH + "/.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "/.classdata", "r")
                    res = eval(f.read())
                    f.close()

                    res.pop("admin")
                    fx.createlog("清空了学生的表现")
                    renewmain()
                    box.msgbox(
                        "清空成功！\n" + str(res), title="班级管理器 管理设置 清空表现"
                    )
                elif op == "排序":
                    sorted_keys = sorted(
                        res.keys(), key=lambda x: "".join(p.get_pinyin(x))
                    )
                    sorted_data = {k: res[k] for k in sorted_keys}
                    res = sorted_data
                    res["admin"] = admin

                    f = open(FILEPATH + "/.classdata", "w")
                    res = f.write(str(res))
                    f.close()
                    f = open(FILEPATH + "/.classdata", "r")
                    res = eval(f.read())
                    f.close()

                    res.pop("admin")
                    fx.createlog("学生排序")
                    renewmain()
                    box.msgbox(
                        "排序成功！\n" + str(res), title="班级管理器 管理设置 学生排序"
                    )
                elif op == "批量添加":
                    if box.ccbox(
                        "请将学生们的姓名写在一个文本文件(utf8编码)中，一行一个姓名，后选择那个文件即可添加",
                        title="班级管理器 管理设置 批量添加",
                    ):
                        namelst = []
                        f = open(box.fileopenbox())
                        for i in f.readlines():
                            res[i.replace("\n", "")] = 0
                            namelst.append(i.replace("\n", ""))
                        f.close()
                        res["admin"] = admin

                        f = open(FILEPATH + "/.classdata", "w")
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH + "/.classdata", "r")
                        res = eval(f.read())
                        f.close()

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
                        # os.system(f"xdg-open {FILEPATH}/.classdata")
                        subprocess.run(["xdg-open", f"{FILEPATH}/.classdata"])
                        box.buttonbox(
                            choices=["编辑完了"],
                            title="班级管理器 管理设置 编辑数据文件",
                        )
                        renewmain()
                else:

                    return ()
        else:
            return ()


main = Tk()
main.title("班级管理器")
main.resizable(0, 0)
main.geometry("1024x600")


ppm3_tips = Pmw.Balloon(main)

s1 = s2 = ttk.Style()
s1.configure("A.TButton", font=("微软雅黑", 16))
s2.configure("B.TButton", font=("微软雅黑", 18))
s2.configure("C.TButton", font=("微软雅黑", 12))

leftFrame = ttk.Frame(main)
bottomFrame = ttk.Frame(leftFrame)


canvasframe = ttk.Frame(leftFrame)
canvas = Canvas(canvasframe, borderwidth=0)
canvas.config(width=854)
frame = ttk.Frame(canvas)
vsb = ttk.Scrollbar(canvasframe, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)
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

txtAr = scrolledtext.ScrolledText(main, width=24, font=("微软雅黑", 12), state=DISABLED)
setTxt("欢迎使用班级管理器")


titlelabel = Label(main, height=1)
titlelabel.pack(side=TOP)

btn1.pack(side=LEFT)
btn2.pack(side=LEFT)
btn3.pack(side=LEFT)
btn4.pack(side=LEFT)
txtAr.pack(side=RIGHT, expand=True, fill=Y)

leftFrame.pack(side=LEFT, expand=True, fill=BOTH)
canvasframe.pack(side=TOP, expand=True, fill=BOTH)
Label(leftFrame, height=1).pack(side=TOP)
bottomFrame.pack(side=TOP)
Label(leftFrame, height=1).pack(side=TOP)

readf()
reslist = list(res.keys())
resscorelist = list(res.values())
b = 5
i = 0
if len(res) > 5:
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
    os.remove(FILEPATH + "/theprogramisrunning")
except:
    pass
exit()
