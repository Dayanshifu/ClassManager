import os
from sys import *
import time
import random as ran
import win32con, win32api

cmdmod = 0  #开启命令行模式选1
title = '班级管理'
FILEPATH = os.path.dirname(os.path.realpath(argv[0]))
print(FILEPATH)

if cmdmod!=1:
    try:
        import easygui as box
        from pypinyin import lazy_pinyin  
    except ImportError:
        op = input('必要的运行库未能导入，是否按“Y”现在开始安装 ')
        if op == 'Y' or op == 'y':
            os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple easygui')
            os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pypinyin')
            os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pypiwin32')
            print('运行库安装成功！请重启程序！')
            exit()
        else:
            print('必要的运行库未能导入，开启命令行模式，要使用完整的程序，请安装运行库')
            cmdmod = 1
            sleep = 3
            for i in range(3):
                print('please wait for '+ str(sleep)+'s')
                sleep -= 1
                time.sleep(0.8)

def showf():win32api.SetFileAttributes(FILEPATH+'\\.classdata', win32con.FILE_ATTRIBUTE_NORMAL)
def hidef():win32api.SetFileAttributes(FILEPATH+'\\.classdata', win32con.FILE_ATTRIBUTE_HIDDEN)

if cmdmod != 1:
    try:
        showf()
        f = open(FILEPATH+'\\.classdata', 'r')
        res = f.read()
        f.close()
        hidef()
        if res == '':
            showf()
            f = open(FILEPATH+'\\.classdata', 'w')
            res = f.write('{}')
            f.close()
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()
            hidef()
        else:
            showf()
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()
            hidef()
    except:
        op = box.ynbox('系统检测到你的文件目录没有 .classdata 文件，是否自动创建？', title=title)
        if op == True:
            try:showf()
            except:pass
            f = open(FILEPATH+'\\.classdata', 'w')
            res = f.write('{}')
            f.close()
            hidef()
            box.msgbox('创建成功！请重新运行本程序', title=title)
            exit()
        else:
            box.msgbox('请自行在当前程序所在目录创建.classdata文件，输入一对英文{}并保存', title=title)
            exit()

    if 'admin' not in res:
        while True:
            ans = box.passwordbox('你还没有创建管理员密码，请输入将要使用的密码(6位及以上)\n账号：admin', title=title)
            if ans==None:
                exit()
            if len(str(ans)) < 6:
                box.msgbox('密码不合法，请重新输入', title=title)
            else:
                break
        code = []
        for w in str(ans):
            num = ord(w)
            code.append(num)
        res['admin'] = code
        showf()
        f = open(FILEPATH+'\\.classdata', 'w')
        res = f.write(str(res))
        f.close()
        f = open(FILEPATH+'\\.classdata', 'r')
        res = eval(f.read())
        f.close()
        hidef()
        code = res['admin']
        key = ''
        for w in code:
            key = key + str(chr(w))
        box.msgbox('请保管好你的管理员密码：\n' + key, title=title)

    admin = res['admin']
    res.pop('admin')
    breakful = 0
    while True:
        op = box.buttonbox('选择你要做什么\n'+ str(res), choices=('计分', '随机', '排行榜', '管理', '退出'), title=title)
        if op == '计分':
            lst = []
            aaa = 0
            bbb = 1
            ccc = {}
            for l in res:
                aaa+=1
                lst.append(l)
                print(lst)
                if aaa >6:
                    lst.append('下一￷页')
                    aaa=0
                    ccc[bbb]=lst
                    bbb+=1
                    lst = []
            
            lst.append('取消￷')
            aaa=0
            ccc[bbb]=lst
            bbb+=1
            lst = []
            for i in ccc:
                op = box.buttonbox('选择学生', choices=ccc[i], title=title)
                if op !='下一￷页':
                    break
                
            if op ==None or op == '取消￷':
                continue
            mk = box.buttonbox('选择分数', choices=('-5','-4','-3','-2','-1','0','1','2','3','4','5'), title=title)
            if mk == None:
                continue
            res[op] = res[op] + int(mk)
            res['admin'] = admin
            showf()
            f = open(FILEPATH+'\\.classdata', 'w')
            res = f.write(str(res))
            f.close()
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()
            hidef()
            res.pop('admin')
            box.msgbox('加分成功！\n'+ str(res), title=title)
        elif op == '管理':
            showf()
            f = open(FILEPATH+'\\.classdata', 'r')
            code = eval(f.read())['admin']
            f.close()
            hidef()
            key = ''
            for w in code:
                key = key + str(chr(w))
            ans = box.passwordbox('请输入管理员密码', title=title)
            if ans == key:
                while True:
                    op = box.buttonbox('选择你要做什么', choices=('添加', '删除', '清空', '排序', '退出'), title=title)
                    if op == '添加':
                        ans = box.enterbox('请输入学生姓名，输入中文“，”可添加多个', title=title)
                        if str(type(ans)) != "<class 'str'>":
                            box.msgbox('取消', title=title)
                            continue
                        res['admin'] = admin
                        if '，'in ans:
                            for i in list(ans.split("，")):
                                res[i] = 0
                        else:
                            res[ans] = 0
                        showf()
                        f = open(FILEPATH+'\\.classdata', 'w')
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH+'\\.classdata', 'r')
                        res = eval(f.read())
                        f.close()
                        hidef()
                        res.pop('admin')
                        box.msgbox('创建成功！\n'+ str(res), title=title)
                    elif op == '删除':
                        ans = box.enterbox('请输入要删除学生姓名，输入中文“，”可添加多个\n'+ str(res), title=title)
                        if '，'in ans:
                            for i in list(ans.split("，")):
                                if i not in res:
                                    box.msgbox(f'没有找到{i}', title=title)
                                    continue
                                res.pop(i)
                        else:
                            if ans not in res:
                                box.msgbox('没有找到', title=title)
                                continue
                            res.pop(ans)
                        res['admin'] = admin
                        showf()
                        f = open(FILEPATH+'\\.classdata', 'w')
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH+'\\.classdata', 'r')
                        res = eval(f.read())
                        f.close()
                        hidef()
                        res.pop('admin')
                        box.msgbox('创建成功！\n'+ str(res), title=title)
                    elif op == '清空':
                        op = box.ynbox('你真舍得清空吗', title=title)
                        if op != True:
                            box.msgbox('取消', title=title)
                            continue
                        for i in res:
                            res[i]=0
                        res['admin'] = admin
                        showf()
                        f = open(FILEPATH+'\\.classdata', 'w')
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH+'\\.classdata', 'r')
                        res = eval(f.read())
                        f.close()
                        hidef()
                        res.pop('admin')
                        box.msgbox('清空成功！\n'+ str(res), title=title)
                    elif op == '排序':
                        sorted_keys = sorted(res.keys(), key=lambda x: ''.join(lazy_pinyin(x)))  
                        sorted_data = {k: res[k] for k in sorted_keys}  
                        res=sorted_data
                        res['admin'] = admin
                        showf()
                        f = open(FILEPATH+'\\.classdata', 'w')
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH+'\\.classdata', 'r')
                        res = eval(f.read())
                        f.close()
                        hidef()
                        res.pop('admin')
                        box.msgbox('排序成功！\n'+ str(res), title=title)
                    elif op == '重置':
                        box.msgbox('删除目录下 .classdata 文件即可（三思而后行）', title=title)
                    else:
                        break
            else:
                box.msgbox('密码错误', title=title)
        elif op == '随机':
            op=box.buttonbox('选择人数', choices=('1','2','3','4','5','6','7','8','9','10'), title=title)
            
            if op ==None:
                continue
            op = int(op)
            lst = []
            print(op)
            for l in res:
                lst.append(l)
            if op > len(lst):
                box.msgbox('选择的人数太多', title=title)
                continue
            box.msgbox(ran.sample(lst, op), title=title)
        elif op == '排行榜':
            showf()
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()
            hidef()
            res.pop('admin')
            aaaa=sorted(res.items(),  key=lambda d:d[1], reverse=True)
            output_str=''
            for index, (key, value) in enumerate(aaaa, start=1):  
                output_str += f"{index}: {key} {value}||￷|" 

            lstt = list(output_str.split('||￷|'))
            
            lst = []
            aaa = 0
            bbb = 1
            ccc = {}
            for l in lstt:
                aaa+=1
                lst.append(l)
                if aaa >=10:
                    aaa=0
                    ccc[bbb]=lst
                    bbb+=1
                    lst = []
                    
            aaa=0
            ccc[bbb]=lst
            bbb+=1
            lst = []
            straaa=''
            for i in ccc:
                for j in range(0,len(ccc[i])):
                    straaa+=ccc[i][j]+'\n'
                box.msgbox(straaa, title=title)
                straaa=''
            pass
        else:
            exit()
else:
    if '.classdata' not in os.listdir():
        op = input('系统检测到你的文件目录没有 .classdata 文件，是否按 Y 自动创建？')
        if op == 'Y' or op == 'y':
            f = open(FILEPATH+'\\.classdata', 'w')
            res = f.write('{}')
            f.close()
            print('创建成功！请重新运行本程序')
            time.sleep(10)
            exit()
        else:
            print('请自行在当前程序所在目录创建.classdata文件，输入一对英文{}并保存')
            time.sleep(10)
            exit()
    else:
        f = open(FILEPATH+'\\.classdata', 'r')
        res = f.read()
        f.close()
        if res == '':
            f = open(FILEPATH+'\\.classdata', 'w')
            res = f.write('{}')
            f.close()
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()
        else:
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()

    if 'admin' not in res:
        while True:
            ans = input('你还没有创建管理员密码，请输入将要使用的密码(6位及以上)\n账号：admin')
            if len(str(ans)) < 6:
                print('密码不合法，请重新输入', title=title)
            else:
                break
        code = []
        for w in str(ans):
            num = ord(w)
            code.append(num)
        res['admin'] = code
        f = open(FILEPATH+'\\.classdata', 'w')
        res = f.write(str(res))
        f.close()
        f = open(FILEPATH+'\\.classdata', 'r')
        res = eval(f.read())
        f.close()
        code = res['admin']
        key = ''
        for w in code:
            key = key + str(chr(w))
        print('请保管好你的管理员密码：\n' + key, title=title)

    admin = res['admin']
    res.pop('admin')

    while True:
        op = input('选择你要做什么,\n'+ str(res) + '\n计分0, 随机1, 排行榜2 , 管理3, 退出4 ')
        if op == '0':
            lst = []
            for l in res:
                lst.append(l)
            tpl = tuple(lst)
            op = input('选择学生'+str(tpl))
            if op == None or op not in tpl:
                continue
            mk = input('输入分数，负数前加“-”')
            try:
                mk = int(mk)
                pass
            except ValueError:
                continue
            if mk == None :
                continue
            res[op] = res[op] + int(mk)
            res['admin'] = admin
            f = open(FILEPATH+'\\.classdata', 'w')
            res = f.write(str(res))
            f.close()
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()
            res.pop('admin')
            print('加分成功！\n'+ str(res))
        elif op == '3':
            f = open(FILEPATH+'\\.classdata', 'r')
            code = eval(f.read())['admin']
            f.close()
            key = ''
            for w in code:
                key = key + str(chr(w))
            ans = input('请输入管理员密码')
            if ans == key:
                while True:
                    op = input('选择你要做什么\n,添加 0, 删除 1, 清空 2, 退出 3')
                    if op == '0':
                        ans = input('请输入学生姓名，输入中文“，”可添加多个')
                        if str(type(ans)) != "<class 'str'>":
                            print('取消')
                            continue
                        res['admin'] = admin
                        if '，'in ans:
                            for i in list(ans.split("，")):
                                res[i] = 0
                        else:
                            res[ans] = 0
                        f = open(FILEPATH+'\\.classdata', 'w')
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH+'\\.classdata', 'r')
                        res = eval(f.read())
                        f.close()
                        res.pop('admin')
                        print('创建成功！\n'+ str(res))
                    elif op == '1':
                        ans = input('请输入要删除学生姓名，输入中文“，”可添加多个\n'+ str(res))
                        if '，'in ans:
                            for i in list(ans.split("，")):
                                if i not in res:
                                    box.msgbox(f'没有找到{i}', title=title)
                                    continue
                                res.pop(i)
                        else:
                            if ans not in res:
                                box.msgbox('没有找到', title=title)
                                continue
                            res.pop(ans)
                        res['admin'] = admin
                        f = open(FILEPATH+'\\.classdata', 'w')
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH+'\\.classdata', 'r')
                        res = eval(f.read())
                        f.close()
                        res.pop('admin')
                        print('创建成功！\n'+ str(res))
                    elif op == '2':
                        op = print('你真舍得清空吗按1')
                        if op != '1':
                            print('取消')
                            continue
                        for i in res:
                            res[i]=0
                        res['admin'] = admin
                        f = open(FILEPATH+'\\.classdata', 'w')
                        res = f.write(str(res))
                        f.close()
                        f = open(FILEPATH+'\\.classdata', 'r')
                        res = eval(f.read())
                        f.close()
                        res.pop('admin')
                        print('清空成功！\n'+ str(res))
                    elif op == '3':
                        break
                    else:
                        pass
            else:
                print('密码错误')
        elif op == '1':
            op = input('输入人数')
            try:
                op = int(op)
                pass
            except ValueError:
                continue
            lst = []
            for l in res:
                lst.append(l)
            if op > len(lst):
                print('选择的人数太多')
                continue
            print(ran.sample(lst, op))
        elif op == '2':
            f = open(FILEPATH+'\\.classdata', 'r')
            res = eval(f.read())
            f.close()
            res.pop('admin')
            
            aaaa=sorted(res.items(),  key=lambda d:d[1], reverse=True)
            output_str=''
            for index, (key, value) in enumerate(aaaa, start=1):  
                output_str += f"{index}: {key} {value}||￷|" 

            lstt = list(output_str.split('||￷|'))
            
            lst = []
            aaa = 0
            bbb = 1
            ccc = {}
            for l in lstt:
                aaa+=1
                lst.append(l)
                if aaa >=10:
                    aaa=0
                    ccc[bbb]=lst
                    bbb+=1
                    lst = []
                    
            aaa=0
            ccc[bbb]=lst
            bbb+=1
            lst = []
            straaa=''
            for i in ccc:
                for j in range(0,len(ccc[i])):
                    straaa+=ccc[i][j]+'\n'
            print(straaa)
            pass
        elif op == '4':
            exit()
        else:
            pass