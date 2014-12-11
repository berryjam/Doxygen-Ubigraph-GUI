# coding= utf-8
import xmlrpclib, time, random,os
import networkx
import SimpleXMLRPCServer
import code_parser as CP
import threading
view = 'no server created'
view_server_high_light_style=0
member_id={}               # 函数的hash=>id，hash是一个字符串，id是一数字
member_hash={}             # 把上面的反过来

CallbackFunction=None
callback_server=None
callback_server_port=None

# show functions ##############################
# 

def Show(G,callback_function=None,uri='http://127.0.0.1:20738/RPC2'):
    global view
    global member_id            # 函数的hash=>id，hash是一个字符串，id是一数字
    global member_hash          # 把上面的反过来
    global view_server_high_light_style
    global CallbackFunction
    global callback_server
    global callback_server_port

    CallbackFunction=callback_function
    G_reversed = G.reverse()
    view_server = xmlrpclib.Server(uri)
    view = view_server.ubigraph
    view.clear()

    # edgeStyle = view.new_edge_style(0)
    edgeStyle = 0               # 0为默认全部的
    # view.set_edge_style_attribute(edgeStyle, "color", "#ffffff")
    # view.set_edge_style_attribute(edgeStyle, "showstrain", "true")
    # view.set_edge_style_attribute(edgeStyle, "arrow", "true")
    # view.set_edge_style_attribute(edgeStyle, "spline", "true")

    member_id={}            # 函数的hash=>id，hash是一个字符串，id是一数字
    member_hash={}          # 把上面的反过来
    callback_server_port = random.randint(20739,20999)

    degree_max = max(G.degree().values())
    indegree_max = max(G.in_degree().values())
    outdegree_max = max(G.out_degree().values())

    id=0
    for node in G.nodes_iter():
        hash = node
        if member_id.has_key(hash):continue # 会有重复情况。
        else:
            member_id[hash]=id
            view.new_vertex_w_id(id)
        id+=1

    for edge in G.edges_iter():
        view.new_edge( member_id[edge[0]], member_id[edge[1]])

    member_hash = dict(zip(member_id.values(),member_id))

    for id in member_hash:
        node = member_hash[id]
        indegree = G.in_degree(node)
        outdegree = G.out_degree(node)
        degree = G.degree(node)
        size = str((float(degree)/degree_max+0.1)*8)
        inColor = hex(int((float(indegree)/indegree_max+1)*127))[2:]
        if len(inColor)==1: inColor='0'+inColor
        outColor = hex(int((float(outdegree)/outdegree_max+1)*127))[2:]
        if len(outColor)==1: outColor='0'+outColor
        color = '#'+inColor+'0f'+outColor
        # print degree_max,degree,  indegree_max,indegree,  outdegree_max,outdegree, size
        # view.set_vertex_attribute(id, "color", color)
        # view.set_vertex_attribute(id, "size", size)
        # time.sleep(0.1)
        # view.set_vertex_attribute(id, "shape", "sphere")



    if callback_function==None:pass
    else:
        name=callback_function.func_name
        name='gnu'
        view.set_vertex_style_attribute(0, "callback_left_doubleclick", "http://127.0.0.1:" + str(callback_server_port) + "/"+name)

def RunCallBackServer():
    global CallbackFunction
    global callback_server
    global callback_server_port
    if CallbackFunction==None:pass # 如果存在回调函数则运行回调服务器
    else:
        callback_server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", callback_server_port),logRequests=False)
        callback_server.register_introspection_functions()
        callback_server.register_function(CallbackFunction,'gnu')
        print ("Listening for callbacks from ubigraph_server on port " + str(callback_server_port))
        # while self.serve:
        #     callback_server.handle_request()
        callback_server.serve_forever()
        print 'call back server stoped'


def ChangeNodeStyle(id):          # 改变节点状态
    global view
    global view_server_high_light_style
    view.change_vertex_style(id, view_server_high_light_style)
    return 0

def DeleteNode(id):          # 改变节点状态
    global view
    view.remove_vertex(id);
    return 0

def GetNode(id):
    global member_hash
    return member_hash[id]

def GetID(name):
    global member_id
    return member_id[name]

def ParseCode(*params):
    parser_type = params[0]
    file = params[1]
    network_type = params[2]
    p=CP.Code2Network_doxygen(file)
    if network_type=='function':
        graph = p.FunctionCallGraph()
        return graph
    graph = p.ClassGraph()
    return graph


def CallBack(node_id): return 0

class RunAsync(threading.Thread):
    def __init__(self,function=None,arg=None,CallBackFunction=None,callBackArg=None,count=True,DoneFunction=None,msg=''):
        threading.Thread.__init__(self)
        self.f = function
        self.f_arg = arg
        self.f_callback = CallBackFunction
        self.f_callback_arg = callBackArg
        self.f_done=DoneFunction
        self.msg=msg
        # self.daemon=True
        self.start()

    def run(self):
        if (self.f_arg==None):self.f()
        else:  self.f(self.f_arg)




if __name__=="__main__":
    print( 'this is code_analysis.py' )
    G = ParseCode('doxygen','all.xml','function')
    # networkx.write_gml(G,'a.gml.gz')
    # newViewServer()
    Show(G,CallBack)
    # CallbackFunction=CallBack
    a=RunCallBackServer()
    RunAsync(a.Run)
    time.sleep(5)
    a.Quit()
    # time.sleep(5)
