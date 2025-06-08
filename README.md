# 班级管理

## 班级管理器 上课好利器

### 你说得对，但是班级管家集成了白板、随机点名、积分系统、双师班授课辅助，甚至还有linux版本，适配各种白板，电脑，哪怕有冰点还原，装到有u盘里也能用


## V2.0.3.1419526 wa
 
 - 支持通过修改配置文件(config.json)设置授课助手的功能是否显示
 - 增加nuitka打包
 - 调整屏幕截图功能的时间间隔
 - 更改为使用xpinyin排序(linux只能用xpinyin，现在windows做的时候好像又不行了，于是windows用pypinyin，linux 用xpinyin)
 - [linux版和定制版](https://github.com/)

## 配置文件功能说明

```json
{
    "enable_lhidebtn": true,
    "enable_rhidebtn": false,
    "enable_mutebtn": true,
    "enable_screenshotbtn": true,
    "is_screenshotsavedir_desktop": true,
    "enable_randomstudentbtn": true,
    "enable_screendrawbtn": true,
    "enable_capture": true,
    "capture_num": 0,
    "enable_volumeadjustment": true   
}
``` 
 - enable_lhidebtn/enable_rhidebtn:是否在授课助手中显示左/右”隐藏/显示“按钮
 - enable_mutebtn:是否在授课助手中显示”静音/解除“按钮        
 - enable_screenshotbtn:是否在授课助手中显示”截图“按钮
 - is_screenshotsavedir_desktop:是否将屏幕截图、保存至桌面，如果不是则屏幕截图会保存在程序 所在目录
 - enable_randomstudentbtn:是否在授课助手中显示”抽奖“按钮
 - enable_screendrawbtn:是否在授课助手中显示”批注（白板）“按钮
 - enable_capture: 是否在授课助手中显示“拍照”按钮
 - capture_num": 0 拍照按钮访问的摄像头
 - enable_volumeadjustment:是否在授课助手中显示系统音量调整区域

## 安装说明
### Windows

#### 使用python从源代码运行:

```cmd
cd ClassManager
python -m pip install -r requirements.txt
python main.py
```

#### 运行可执行文件

ClassManager.exe

### Linux

#### 运行可执行文件

下载ClassesManager.tar.xz后在其目录中运行
```
xz -d ClassManager.tar.xz
cd ClassManager
chmod +x Classmanager-linux
Classmanager-linux
```
