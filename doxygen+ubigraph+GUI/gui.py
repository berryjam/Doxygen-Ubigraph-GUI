#!/usr/bin/python
#encoding=utf8
__author__ = 'sjh'

from Tkinter import *   #引入Tkinter工具包
import tkFileDialog as filedialog
import os,sys,time,re
import subprocess,threading
import networkx
import code_analysis as CA
import thread
reload(sys)
sys.setdefaultencoding('utf-8')


DOXYGEN_BIN="/opt/local/bin/doxygen"
DOXYGEN_CONFIG_FILE="/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/doxygen.config"
UBIGRAPH_BIN='''"/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/UbiGraph-alpha-0.2.4-MacOSX10.4Intel/bin/ubigraph_server"'''
WORKING_DIR="/tmp"
PROJECT_DIR = "" # the javacc project


# ========================= 
G={}                            # networkx 有向网络
M=[]                            # 标记删除或保存的节点id
NETWORK=G
G_reversed={}


# ################## operations on click an node #################

# ============== RM connected graph =============
def RmGraph(node_name):
    global M
    global G
    M=[]
    for node in G.nodes_iter():G[node]['mark']=False
    MarkGraph(node_name)
    app.Msgln(str(len(M))+'个节点将从视图中移除')
    for node in M:
        CA.DeleteNode(CA.GetID(node)) # 从视图中删除
        app.Msgln('删除节点：'+str(node),'output')
        # G.remove_node(node) # 在网络中也删除，慎用！

# ============== save connected graph ===============
def SaveGraph(node_name):
    global M
    global G
    global app
    M=[]
    for node in G.nodes_iter():G[node]['mark']=False
    MarkGraph(node_name)
    W = G.subgraph(M)
    filename=GetCmdOutput('zenity --title="保存选择的连通子图" --file-selection --filename="connected-subgraph.gml.gz" --save --confirm-overwrite',msg=False)[2].replace('\n','')
    networkx.write_gml(W,filename)
    app.Msgln('包含'+str(len(M))+'个节点的连通子图以GML格式保存至文件:'+filename,'info')


# ============== mark nodes connected with given node ============
def MarkGraph(node_name):       # 递归调用标记节点
    global G                    # 在G中寻找标记
    global M                    # M必须在递归前清空！
    if G[node_name].has_key('mark') and G[node_name]['mark']: return
    G[node_name]['mark']=True
    # CA.DeleteNode(CA.GetID(node_name)) # 边找边删？
    # print(node_name)
    M.append(node_name)
    for node in G.nodes_iter():
        if G.has_edge(node,node_name) or G.has_edge(node_name,node):
            MarkGraph(node)

# ================= Show definition in Source Code =============

def ShowSource(node_name):
    global G
    global M
    global app
    # print node_name
    if G.has_node(node_name):
        node = G.node[node_name]
        fileStr=node['file']
        line=node['line']
        column=node['column']
        app.Msgln('<节点信息>行:'+line+' 列:'+column+' 文件名:'+fileStr,'output')
        RunSubProcess('geany -l '+line+' --column '+column+' '+fileStr+' &')
    else:
        return 0

def ShowInfo(node):
    global app
    indegree = G.in_degree(node)
    outdegree = G.out_degree(node)
    degree = G.degree(node)
    app.Msgln('节点入度：'+str(indegree)+' 出度：'+str(outdegree),'info')


def CallBack(node_id):
    global G
    global M
    global app
    try:
        CA.ChangeNodeStyle(node_id)
        nodeName = CA.GetNode(node_id)
        app.Msgln('点击节点：'+str(nodeName))
        if app.action.get()=='保存连通图':
            SaveGraph(nodeName)
        elif app.action.get()=='显示定义':
            ShowSource(nodeName)
        elif app.action.get()=='删除连通图':
            RmGraph(nodeName)
        elif app.action.get()=='显示信息':
            ShowInfo(nodeName)
        return 0
    except Exception,e:
        print('callback failed')
        print(str(e))
        return -1


def Run():
    global DOXYGEN_BIN
    global WORKING_DIR
    global PROJECT_DIR
    global CURRENT_STEP
    global UBIGRAPH_BIN
    global app
    global G
    global M
    global NETWORK
    global G_reversed

    app.Msg("正在清理垃圾文件，请稍后")
    ForkRun('rm -rf '+WORKING_DIR+'/xml','skip')
    ForkRun('rm -rf '+'all.xml *.gml.gz *.pyc warn.log','skip')
    app.MsgDone()

    ConfigFile('OUTPUT_DIRECTORY.*$','OUTPUT_DIRECTORY='+WORKING_DIR, DOXYGEN_CONFIG_FILE)
    ConfigFile('INPUT.*$','INPUT='+PROJECT_DIR, DOXYGEN_CONFIG_FILE)
    app.Msg("正在运行doxygen处理您的项目")
    app.MsgRaw('\n')
    GetCmdOutput(DOXYGEN_BIN+' '+DOXYGEN_CONFIG_FILE)
    app.MsgDone()

    app.Msg("正在合并过滤处理相关中间文件")
    app.MsgRaw('\n')
    GetCmdOutput('cd '+WORKING_DIR+'/xml;'+'''sed -i '' "s/compound/compound[@kind='class']/g" combine.xslt; xsltproc combine.xslt index.xml > all.xml''')
    GetCmdOutput('mv '+WORKING_DIR+'/xml/all.xml ./')
    app.MsgDone()
    app.Msgln('已在当前文件夹生成项目索引文件all.xml','info')


    app.Msg("正在启动网络3D可视化界面Ubigraph及错误显示终端")
    app.MsgRaw('\n运行命令：'+UBIGRAPH_BIN+' 2>&1 >/dev/null\n','cmd')
    ForkRun(UBIGRAPH_BIN+' 2>&1 >/dev/null')
    app.MsgDone()


    app.Msg("正在解析项目索引XML文件，生成复杂网络")
    if app.network_type.get()=="function_call_graph":
        G = CA.ParseCode('doxygen','/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/all.xml','function') # 返回函数调用图
        thread.start_new_thread(GetCmdOutput, ('java -jar /Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/show_function_class.jar 1',))
    else:
        G = CA.ParseCode('doxygen','/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/all.xml','class') # 这样返回的是类的关系图
        thread.start_new_thread(GetCmdOutput, ('java -jar /Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/show_function_class.jar 2',))
    # print(app.network_type.get())
    # print(type(app.network_type.get()))
    app.MsgDone()
    app.Msgln('节点数：'+str(G.number_of_nodes())+' 边数：'+str(G.number_of_edges()),'info')
    NETWORK=G
    G_reversed=G.reverse()
    # 分析所有节点的出入度
    app.Msg("正在分析所有节点的出入度")
    
    app.MsgDone()

    # # find the largest network in that list
    app.Msg("正在分析，寻找最大连通子网络")
    H = G.to_undirected()
    if not networkx.is_connected(H):
        sub_graphs = networkx.connected_component_subgraphs(H)
        main_graph = sub_graphs.next()
        for sg in sub_graphs:
            if sg.number_of_nodes() > main_graph.number_of_nodes():
                main_graph=sg
        W = G.subgraph(main_graph.nodes())
    app.MsgRaw('\n最大连通子图节点数：'+str(W.number_of_nodes())+' 边数：'+str(W.number_of_edges()),'info')
    app.MsgDone()

    app.Msg("正在保存网络文件")
    networkx.write_gml(W,'a.gml.gz')
    app.MsgRaw('已在当前文件夹生成最大连通子网络文件a.gml.gz ','info')
    app.MsgDone()
    # print NETWORK.nodes(data=True)
    time.sleep(0.8)
    # app.win.after(20,lambda:UbigraphDraw(CallBack))
    UbigraphDraw(CallBack)

    # NetworkXDraw(W)
    # print('total nodes: ',W.number_of_nodes())
    return

def NetworkXDraw(G):
    import matplotlib.pyplot as plt
    # pos = networkx.circular_layout(G)
    # pos = networkx.random_layout(G)
    # pos = networkx.shell_layout(G)
    pos = networkx.spring_layout(G)
    plt.figure(figsize=(8,6))
    networkx.draw_networkx_edges(G,pos,width=0.6,alpha=0.6)
    networkx.draw_networkx_nodes(
        G,
        pos,
        node_size=15,
        node_color="red",
        linewidths=0.4
        )
    plt.axis('off')
    plt.savefig("javacc-default.png")
    # plt.show()

def UbigraphDraw(CallBack=None):
    global NETWORK
    global app
    try:
        if CallBack==None:
            app.Msg('正在可视化')
            CA.Show(NETWORK)
            app.MsgDone()
        else:
            app.Msg('正在可视化')
            CA.Show(NETWORK,CallBack) # 如果要显示回调必须在调用show的时候也传入callback函数
            app.MsgDone()
            app.Msgln('可视化完成,正在启动回调服务器')
            CA.RunCallBackServer()
            # app.toggle_call_back_server()
    except Exception,e:
        # print('program terminated====================')
        app.Msgln(str(e),'error')
        # print(dir(e))
    

class RunAsync(threading.Thread):
    def __init__(self,function=None,arg=None,CallBackFunction=None,callBackArg=None,count=True,DoneFunction=None,msg=''):
        threading.Thread.__init__(self)
        self.f = function
        self.f_arg = arg
        self.f_callback = CallBackFunction
        self.f_callback_arg = callBackArg
        self.f_done=DoneFunction
        self.msg=msg
        self.daemon=True
        self.start()

    def run(self):
        global app

        # try:
        begin_time=time.time()
        if (self.f_arg==None):self.f()
        else:  self.f(self.f_arg)
        end_time=time.time()
        app.Msgln('已完成全部分析工作，(耗时 %.3f 秒)' % float(end_time-begin_time))

        # except MyError,e:
        #     app.Msgln(str(e)+e.content,'error')
        # except Exception,e:
        #     app.Msgln(str(e)+e.message,'error')
        # except:
        #     app.Msgln('未知错误','error')

        # if (self.f_callback==None):pass
        # else:
        #     if (self.f_callback_arg==None):self.f_callback()
        #     else:
        #         self.f_callback(self.f_callback_arg)



class MyError(Exception):
    def __init__(self, content):
        Exception.__init__(self)
        self.content = content


def RunSubProcess(p):
    os.system(p)
    return


def ForkRun(p,s=None):
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

def GetCmdOutput(commandString,onError='throw',msg=True):
    global app
    try:
        if msg: app.MsgRaw('运行命令：'+commandString+'\n','cmd')
        proc = subprocess.Popen([commandString], stdin=subprocess.PIPE, stdout=subprocess.PIPE,shell=True )
        data = proc.communicate()
        outputString = data[0]
        if msg: app.MsgRaw(outputString,'output')
        if msg: app.MsgRaw('\n')
        errorString = data[1]
        if errorString==None:pass
        else:
            if msg: app.MsgRaw(errorString,'error')
            if msg: app.MsgRaw('\n')

        # if proc.returncode == 0:
        #     return (0, commandString, outputString)
        # else:
        return (proc.returncode, commandString, outputString)

    except subprocess.CalledProcessError,e:
        app.MsgRaw(e.output,'error')
        if onError=='throw':
            pass
            # raise MyError,'内部命令执行错误'
        else:pass
        return (e.returncode, e.cmd, e.output)



def ConfigFile(pattern,changeTo,fileName):
    global app
    app.Msg("配置%s文件" % fileName)
    with open(fileName, "r") as sources:
        lines = sources.readlines()
    with open(fileName, "w") as sources:
        for line in lines:
            sources.write(re.sub(pattern, changeTo, line))
    app.MsgDone()


def Now():
    t=time.localtime()
    tmp="%s年%s月%s日 %s:%s:%s" % (t[0],t[1],t[2],t[3],t[4],t[5])
    return tmp

def DoNothing(): print('do nothing')




class App:
    
    def __init__(self,):
        self.win = Tk()  #定义一个窗体
        self.win.title('软件复杂网络构建分析可视化工具')    #定义窗体标题
        self.win.geometry('860x440')     #定义窗体的大小，是400X200像素

        self.btn = Button(self.win, text='选择Java项目所在目录', command=self.FileSelect)
        self.btn.grid(row=0, column=0, sticky=W)

        self.gobtn = Button(self.win, text='开始分析！', command=self.Go)
        self.gobtn.grid(row=0, column=0, sticky=E)

        self.txtVar=StringVar()
        self.ltxt = Label(self.win, textvariable=self.txtVar)
        self.txtVar.set(Now())
        self.ltxt.grid(row=0,column=1, sticky=W)


        # self.callback = StringVar()
        # self.callback.set("回调服务器已关闭")
        # self.callback_server_status = Checkbutton(self.win,
        #                                           textvariable=self.callback,
        #                                           indicatoron=0,
        #                                           state=NORMAL,
        #                                           command=self.toggle_call_back_server
        #                                           )
        # self.callback_server_status.grid(row=0,column=1,sticky=E)


        self.network_type = StringVar()
        self.network_type.set('function_call_graph')
        Radiobutton(self.win,text="函数调用图",variable=self.network_type,value='function_call_graph').grid(row=0,column=3,sticky=W)
        Radiobutton(self.win, text="类关系图", variable=self.network_type, value='class_graph').grid(row=0,column=3,sticky=E)




        self.entry = Entry(self.win, width=120)
        self.entry.grid(row=1,columnspan=4)

        self.textarea = Text(self.win)
        self.s = Scrollbar(self.win)
        self.s.grid(row=2,rowspan=3,column=4, sticky=N+S+E)
        self.s.config(command=self.textarea.yview)
        self.textarea.config(yscrollcommand=self.s.set)
        self.textarea.grid(row=2, rowspan=3, columnspan=4,sticky=N+E+S+W)
        self.textarea.tag_config('error',foreground='red')
        self.textarea.tag_config('output',foreground='#CCCCCC')
        self.textarea.tag_config('info',foreground='#33CC33')
        self.textarea.tag_config('cmd',foreground='#0099CC')




        self.action = StringVar()
        self.action.set('显示信息')
        self.state = StringVar()
        self.status = Label(self.win, textvariable=self.state)
        self.state.set('当前操作：显示信息')
        self.status.grid(row=5,columnspan=4,sticky=W)


        self.menubar = Menu(self.win)
        #创建下拉菜单File，然后将其加入到顶级的菜单栏中
        self.filemenu = Menu(self.menubar,tearoff=0)
        self.filemenu.add_command(label="选择Java项目目录", command=self.SelectProjectDir)
        self.filemenu.add_command(label="保存日志到文件", command=self.Savelog)
        self.filemenu.add_command(label="清空日志", command=self.ClearLog)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.win.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        #创建另一个下拉菜单Edit
        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="删除连通图", command=lambda: self.toggle_action('删除连通图'))
        self.editmenu.add_command(label="显示节点信息", command=lambda: self.toggle_action('显示信息'))
        self.editmenu.add_command(label="显示定义代码", command=lambda: self.toggle_action('显示定义'))
        self.editmenu.add_command(label="保存该子连通图", command=lambda: self.toggle_action('保存连通图'))
        self.menubar.add_cascade(label="回调操作",menu=self.editmenu)
        #创建下拉菜单Help
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.about)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        #显示菜单
        self.win.config(menu=self.menubar)
        self.win.after(1000,self.UpdateTime)
        self.gtime=0


    def toggle_action(self,act='显示信息'):
        self.action.set(act)
        self.state.set('当前回调操作：'+act)

    def SelectProjectDir(self):
        global PROJECT_DIR
        dirname=GetCmdOutput('zenity --title="选择Java软件项目源代码目录" --file-selection --directory',msg=False)[2]
        if dirname:
            self.entry.delete(0,END) #清空entry里面的内容
            self.entry.insert(0,dirname) #将选择好的路径加入到entry里面
            PROJECT_DIR=dirname
            self.Msgln('选择了Java项目文件夹'+PROJECT_DIR,'info')

    def Savelog(self):
        filename=GetCmdOutput('zenity --title="保存日志" --file-selection --filename="Java软件复杂网络生成与分析日志.log" --save --confirm-overwrite',msg=False)[2].replace('\n','')
        if filename=='':return
        data=self.textarea.get('1.0',END)
        f=file(filename,'w')
        f.write(data)
        f.close
        self.Msgln('以上日志已保存为'+filename)

    def ClearLog(self):
        data = GetCmdOutput('zenity --question --text="您确定要清空当前日志吗？"',msg=False)[0]
        if data==0:
            self.textarea.delete("1.0",END)


    def UpdateTime(self):
        self.txtVar.set(Now())
        self.win.after(1000,self.UpdateTime)


    def Msg(self,string,t=None):
        self.gtime=time.time()
        if t==None:
            self.textarea.insert(END,Now()+' '+string+'......')
        else:
            self.textarea.insert(END,Now()+' '+string+'......',t)
        self.textarea.see(END)

    def Msgln(self,string,t=None):
        if t==None:
            self.textarea.insert(END,Now()+' '+string+'\n')
        else:
            self.textarea.insert(END,Now()+' '+string+'\n',t)
        self.textarea.see(END)

    def MsgRaw(self,string,t=None):
        if t==None:
            self.textarea.insert(END,string)
        else:
            self.textarea.insert(END,string,t)
        self.textarea.see(END)

    def MsgDone(self):
        self.textarea.insert(END,'完成!(耗时 %.3f 秒)\n' % float(time.time()-self.gtime))
        self.textarea.see(END)
        self.gtime=0

    def FileSelect(self):
        global PROJECT_DIR
        filepath = filedialog.askdirectory()     #调用filedialog模块的askdirectory()函数去打开文件夹
        if filepath:
            self.entry.delete(0,END) #清空entry里面的内容
            self.entry.insert(0,filepath) #将选择好的路径加入到entry里面
            PROJECT_DIR=filepath.encode('utf-8')
            # print(PROJECT_DIR)
            self.Msgln('选择了Java项目文件夹'+PROJECT_DIR,'info')

    def Begin(self):
        mainloop()

    def Go(self):
        global PROJECT_DIR
        if self.entry.get()=='':pass
        else:
            PROJECT_DIR=self.entry.get()
            self.Msgln('选择了Java项目文件夹'+PROJECT_DIR,'info')
        if PROJECT_DIR=='':
            RunSubProcess('zenity --warning --text="请您先选择Java项目所在路径！"')
        else:
            RunAsync(Run,None)


    def about(self):
        RunSubProcess('zenity --title="关于" --text-info --filename=README --width=600 --height=400')

if __name__=="__main__":
    app=App()
    app.Begin()
