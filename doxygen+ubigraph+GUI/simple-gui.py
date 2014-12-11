#!/usr/bin/python
#encoding=utf8
__author__ = 'sjh'

from Tkinter import *   #引入Tkinter工具包
import tkFileDialog as filedialog

import os,sys,re,time

DOXYGEN_BIN="doxygen-1.8.6/bin/doxygen"
DOXYGEN_CONFIG_FILE="doxygen.config"
UBIGRAPH_BIN='''lxterminal -e "UbiGraph-alpha-0.2.4-Linux64-Ubuntu-8.04/bin/ubigraph_server"'''
WORKING_DIR="/tmp"
PROJECT_DIR = "" # the javacc project

# PROJECT_DIR = "/home/gnusong/myproject/going正在进行项目/毕业设计/download/org"
# PROJECT_DIR = "/home/gnusong/myproject/going正在进行项目/毕业设计/download/software/pysonar2-master/src/main/java" #pysonar
# PROJECT_DIR = "/home/gnusong/myproject/going正在进行项目/毕业设计/download/software/javaparser-1.0.8-src/src" #javaparser
# PROJECT_DIR="/media/G86/gnusong/myproject/going正在进行项目/毕业设计/download/software/org"

# CURRENT_STEP=0

# def AsyncFunc(function,params=None):


def Call(p,s=None):
    if s==None:
        r=os.fork()
        if r==0:
            os.system(p)
            exit()
        else:
            return
    else:
        os.system(p)
    return


def StartViewServer():
    global UBIGRAPH_BIN
    Msg("正在启动网络3D可视化界面Ubigraph及错误显示终端")
    Call(UBIGRAPH_BIN+' 2>&1 >/dev/null')
    MsgDone()
    win.after(800,Run)

gtime=0
def Msg(string):
    global textarea
    global gtime
    gtime=time.time()
    textarea.insert(END,Now()+' '+string+'......')
    textarea.see(END)

def Msgln(string):
    global textarea
    textarea.insert(END,Now()+' '+string+'\n')
    textarea.see(END)

def MsgDone():
    global textarea
    global gtime
    textarea.insert(END,'完成!(耗时 %.3f 秒)\n' % float(time.time()-gtime))
    textarea.see(END)
    gtime=0

def CleanAll():
    global WORKING_DIR
    global CURRENT_STEP
    global win
    Msg("正在清理垃圾文件，请稍后")
    Call('rm -rf '+WORKING_DIR+'/xml','wait-until-finish')
    Call('rm -rf '+'all.xml *.pyc warn.log','wait-until-finish')
    MsgDone()
    win.after(20, ParseCode)  # reschedule event in 2 seconds
    # CURRENT_STEP=1

def ConfigFile(pattern,changeTo,fileName):
    Msg("配置%s文件" % fileName)
    with open(fileName, "r") as sources:
        lines = sources.readlines()
    with open(fileName, "w") as sources:
        for line in lines:
            sources.write(re.sub(pattern, changeTo, line))
    MsgDone()

def ParseCode():
    global DOXYGEN_BIN
    global WORKING_DIR
    global PROJECT_DIR
    global win
    ConfigFile('OUTPUT_DIRECTORY.*$','OUTPUT_DIRECTORY='+WORKING_DIR, DOXYGEN_CONFIG_FILE)
    ConfigFile('INPUT.*$','INPUT='+PROJECT_DIR, DOXYGEN_CONFIG_FILE)
    Msg("正在运行doxygen处理您的项目")
    Call(DOXYGEN_BIN+' '+DOXYGEN_CONFIG_FILE,'wait-until-finish')
    MsgDone()
    Msg("正在合并过滤处理相关中间文件")
    Call('cd '+WORKING_DIR+'/xml;'+'''sed -i "s/compound/compound[@kind='class']/" combine.xslt; xsltproc combine.xslt index.xml > all.xml''','wait-until-finish')
    MsgDone()
    Call('mv '+WORKING_DIR+'/xml/all.xml ./','wait-until-finish')
    Msgln('已在当前文件夹生成项目索引文件all.xml')
    win.after(20,StartViewServer)

def Now():
    t=time.localtime()
    tmp="%s年%s月%s日 %s:%s:%s" % (t[0],t[1],t[2],t[3],t[4],t[5])
    return tmp

def hello():
    print('hello world!')


def FileSelect():
    global PROJECT_DIR
    filepath = filedialog.askdirectory()     #调用filedialog模块的askdirectory()函数去打开文件夹
    if filepath:
        entry.delete(0,END) #清空entry里面的内容
        entry.insert(0,filepath) #将选择好的路径加入到entry里面
        PROJECT_DIR=filepath.encode('utf-8')
        print(PROJECT_DIR)
        Msgln('选择了Java项目文件夹'+PROJECT_DIR)

def about():
    print('我是开发者')

def Run():
    Msgln("正在生成网络，可能需要几分钟，请稍后......")
    Call('python demo.py')



def Go():
    global win
    win.after(20, CleanAll)  # reschedule event in 2 seconds
    # r=os.fork()
    # if r==0:

    #     ParseCode()
    #     StartViewServer()
    #     time.sleep(0.8)
    #     exit()
    # else: return






if __name__=="__main__":
    # if len(sys.argv)==1:
    #     # Go()
    #     print(type(PROJECT_DIR))
    #     exit()
    # for arg in sys.argv:
    #     if arg=='clean': CleanAll()
    #     if arg=='test': StartViewServer()
    #     if arg=='draw':
    #         import demo
    #         import networkx as nx
    #         demo.NetworkXDraw(nx.read_gml("a.gml.gz"))

    win = Tk()  #定义一个窗体
    win.title('软件复杂网络构建分析可视化工具')    #定义窗体标题
    win.geometry('860x420')     #定义窗体的大小，是400X200像素
    # print(type(win))
    btn = Button(win, text='选择Java项目所在目录', command=FileSelect)
    btn.grid(row=0, column=0, sticky=W)
    # btn.pack(side=LEFT,anchor="nw")

    gobtn = Button(win, text='开始分析！', command=Go)
    gobtn.grid(row=0, column=1, sticky=W)
    # gobtn.pack(side=LEFT,fill=X,anchor="nw")

    txtVar=StringVar()
    ltxt = Label(win, textvariable=txtVar)
    txtVar.set(Now())
    ltxt.grid(row=0,column=2, sticky=W)
    entry = Entry(win, width=120)
    # entry.pack(anchor="center")
    entry.grid(row=1,columnspan=4)

    textarea = Text(win)
    s = Scrollbar(win)
    # textarea.focus_set()
    s.grid(row=2,column=4, sticky=N+S+E)
    # s.pack(side=RIGHT, fill=Y)
    # textarea.pack(side=LEFT, fill=Y)
    s.config(command=textarea.yview)
    textarea.config(yscrollcommand=s.set,width=120)


    # textarea.insert(END,'asdf\n')
    # textarea.insert(END,'32323\n')
    # for i in range(100):
    #     textarea.insert(END,'01234567890\n')
    #     textarea.see(END)
    textarea.grid(row=2, columnspan=4)

    time.sleep(2)

    menubar = Menu(win)

    #创建下拉菜单File，然后将其加入到顶级的菜单栏中
    filemenu = Menu(menubar,tearoff=0)
    filemenu.add_command(label="Open", command=hello)
    filemenu.add_command(label="Save", command=hello)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=win.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    #创建另一个下拉菜单Edit
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Cut", command=hello)
    editmenu.add_command(label="Copy", command=hello)
    editmenu.add_command(label="Paste", command=hello)
    menubar.add_cascade(label="Edit",menu=editmenu)
    #创建下拉菜单Help
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=about)
    menubar.add_cascade(label="Help", menu=helpmenu)

    #显示菜单
    win.config(menu=menubar)


    def UpdateTime():
        txtVar.set(Now())
        win.after(1000,UpdateTime)
    win.after(1000,UpdateTime)
    mainloop()
