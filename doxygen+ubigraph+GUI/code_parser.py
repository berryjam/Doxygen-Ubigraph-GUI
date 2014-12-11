# coding= utf-8
import xmlrpclib
import xml.etree.cElementTree
#import xml.etree.ElementTree
import networkx
import HTMLParser
import subprocess

def GetCmdOutput(commandString,onError='throw',msg=True):
    try:
        proc = subprocess.Popen([commandString], stdin=subprocess.PIPE, stdout=subprocess.PIPE,shell=True )
        data = proc.communicate()
        outputString = data[0]
        errorString = data[1]
        if errorString==None:pass
        
        # if proc.returncode == 0:
        #     return (0, commandString, outputString)
        # else:
        return (proc.returncode, commandString, outputString)

    except subprocess.CalledProcessError,e:
        MsgRaw(e.output,'error')
        if onError=='throw':
            pass
        # raise MyError,'内部命令执行错误'
        else:pass
        return (e.returncode, e.cmd, e.output)

class Code2Network_doxygen:
    def __init__(self,xmlfile='all.xml',debug=False):
        self.tree = xml.etree.cElementTree.ElementTree(file=xmlfile)
        self.debug = debug
        self.htmlparser= HTMLParser.HTMLParser()

    def ClassGraph(self):
        co_graph=networkx.DiGraph()
        graph = self.tree.findall('.//collaborationgraph')+self.tree.findall('.//inheritancegraph')
        
        fo = open("/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/类信息.txt","w+")
        fhasho = open("/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/类信息散列表.txt","w+")
        
        for item in graph:
            # xml.etree.ElementTree.dump(item)
            # print dir(item)
            # exit()
            for node in item:
#                link = node.find('.//link')
                name = (node.find('.//label')).text
#                name = link.attrib['refid']
                id = int(node.attrib['id'])
                
                fhasho.write(str(id) + ";" + name + "\n")
                related_id = ""
                
                co_graph.add_node(id,name=name)
                children = node.findall('childnode')
                for child in children:
                    id0 = int(child.attrib['refid'])
                    if id==id0: pass
                    else:
                        related_id += str(id0) + "#"
                        
                        # print id,id0
                        relation = child.attrib['relation']
                        co_graph.add_edge(id,id0,relation=relation)
                fo.write(str(id) + ";" + "(" + related_id + ")" + "\n")
        return co_graph



    def FunctionCallGraph(self):
        global app
        call_graph= networkx.DiGraph() # networkx有向图对象
        function_count = 0      # 函数总数
        reference_count=0       # 调用其他函数的次数
        referencedby_count=0    # 统计被调用的次数
        
        function_reference_count = 0 # 记录当前函数调用了其他函数的数量
        function_referencedby_count = 0 # 记录当前函数被调用的次数
        
        fo = open("/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/函数信息.txt","w+")
        fhasho = open("/Users/berryjam/Tsinghua/软件体系结构/大作业相关/doxygen+ubigraph+GUI/函数信息散列表.txt","w+")

        functions = self.tree.findall('.//memberdef[@kind="function"]') # 所有函数的列表
        for item in functions:  # item为一个函数，这里先把所有函数都塞到网络里
            function_count += 1
            location = item.findall('.//location')[0]
            fileStr = self.htmlparser.unescape(location.attrib['file']).encode('utf-8')
            lineStr = location.attrib['line']
            columnStr = location.attrib['column']
            call_graph.add_node(item.attrib['id'],file=fileStr,line=lineStr,column=columnStr)

        for item in functions:  # item为一个函数
            
            function_name = (item.find('.//definition')).text
            function_id = item.attrib['id']
            function_reference_count = 0
            function_referencedby_count = 0
            function_referencedby_id = ""
            function_reference_id = ""

            referencedby_funcs = item.findall('.//referencedby') # item函数被哪些函数调用了，返回列表
            for another_item in referencedby_funcs:              # item函数被another_item函数调用
                function_referencedby_id +=  another_item.attrib['refid'] + "#"
                function_referencedby_count += 1    # 函数的被调用次数加1
                
                be_called_id = item.attrib['id']
                caller_id = another_item.attrib['refid']
                if call_graph.has_node(caller_id) and call_graph.has_node(be_called_id): # 表明这两者都是函数，因为还可能有函数到变量的引用
                    referencedby_count += 1 # 统计被调用的次数
                    call_graph.add_edge( caller_id, be_called_id ) # 添加一条边,
                    # 注意这样最后的网络是依赖网，函数A调用了B，则最后在networkx里G[A]能找到B，但G[B]无法找到A。

            reference_funcs = item.findall('.//references') # item函数调用了哪些函数，返回列表
            for another_item in reference_funcs:            # item函数调用了another_item函数
                function_reference_id += another_item.attrib['refid'] + "#"
                
                fhasho.write(another_item.attrib['refid'] + ";" + another_item.text + "\n")
                
                function_reference_count += 1   # 函数的调用其他函数数量加1
                
                caller_id = item.attrib['id']
                be_called_id = another_item.attrib['refid']
                if call_graph.has_node(caller_id) and call_graph.has_node(be_called_id): # 表明这两者都是函数，因为还可能有函数到变量的引用
                    reference_count += 1       # 调用其他函数的次数
                    call_graph.add_edge( caller_id, be_called_id ) # 添加一条边,networkx里重复添加边算做一条
            
            fo.write(function_id + ";" + "(" + function_referencedby_id + ")" + ";" + "(" + function_reference_id + ")" + ";" + str(function_reference_count) + ";" + str(function_referencedby_count) +"\n")
            fhasho.write(function_id + ";" + function_name + "\n")

        if self.debug==True:
            print('debug mode enable')
        return call_graph


if __name__=="__main__":
    print('this is code_parser.py')
    cn = Code2Network_doxygen()
    G = cn.ClassGraph()
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,8))
    pos=networkx.spring_layout(G)
    networkx.draw_networkx_edges(G,pos,alpha=0.4)
    networkx.draw_networkx_nodes(
        G,pos,
        node_size=15,
        node_color="red",
        linewidths=0.4
        )
    plt.axis('off')
    plt.show()
    G = cn.FunctionCallGraph()
    if member_id.has_key(item.attrib['id']) and member_id.has_key(another_item.attrib['refid']):
                     id  = int(member_id[item.attrib['id']])
                     rid = int(member_id[another_item.attrib['refid']])
                     if id==rid: print( 'node edges to itself:',id)
                     else:
                         # direct edges
                         key = str(rid)+'->'+str(id)
                         if direct_edges.has_key(key):
                             # print( 'direct edges douplicate:',key)
                             pass
                         else:
                             direct_edges[key]=(rid,id)
                         # undirect edges
                         biger_id=max(id,rid)
                         small_id=min(id,rid)
                         key = str(small_id)+'>'+str(biger_id)
                         if non_direct_edges.has_key(key):
                             # print( 'non-direct edges douplicate:',key)
                             pass
                         else:
                             non_direct_edges[key]=(biger_id,small_id)
                             referencedby_count+=1
                             # self.view.new_edge(biger_id,small_id)


    if member_id.has_key(item.attrib['id']) and member_id.has_key(another_item.attrib['refid']):
                     id  = int(member_id[item.attrib['id']])
                     rid = int(member_id[another_item.attrib['refid']])
                     if id==rid: print 'node edges to itself:',id
                     else:
                         # direct edges
                         key = str(id)+'->'+str(rid)
                         if direct_edges.has_key(key):
                             # print( 'direct edges douplicate:',key)
                             pass
                         else:
                             direct_edges[key]=(id,rid)
                         # undirect edges
                         biger_id=max(id,rid)
                         small_id=min(id,rid)
                         key = str(small_id)+'>'+str(biger_id)
                         if non_direct_edges.has_key(key):
                             # print( 'non-direct edges douplicate:',key )
                             pass
                         else:
                             non_direct_edges[key]=(biger_id,small_id)
                             reference_count+=1
                             # self.view.new_edge(biger_id,small_id)





    print ('count of nodes:',count)
    print( 'referencedby=',referencedby_count)
    print( 'references=',reference_count)
    print( 'count of node:',member_count)
    G=networkx.Graph()
    G.add_edges_from(direct_edges.values())
#    return G

    import matplotlib.pyplot as plt
    networkx.draw(G,with_labels=False,node_size=1,pos = networkx.circular_layout(G))
         # networkx.draw(G,with_labels=False,node_size=1,pos = networkx.random_layout(G))
         # networkx.draw(G,with_labels=False,node_size=1,pos = networkx.shell_layout(G))
         # networkx.draw(G,with_labels=False,node_size=4,pos = networkx.spring_layout(G))
         # networkx.draw(G,with_labels=False,node_size=1,pos = networkx.spectral_layout(G))
    plt.figure(figsize=(12,10))
    pos=networkx.spring_layout(G)
    networkx.draw_networkx_edges(G,pos,alpha=0.4)
    networkx.draw_networkx_nodes(
             G,pos,
             node_size=15,
             node_color="red",
             linewidths=0.4
             )
    plt.axis('off')
    plt.show()



        # self.view_server = xmlrpclib.Server('http://127.0.0.1:20738/RPC2')
        # self.view = self.view_server.ubigraph
        # self.view.clear()


        # non_direct_edges={}     # 无向边的map，用于查重
        # direct_edges={}         # 有向边的map，用于查重
        # direct_edges_array=[]   # 有向边列表(A,B)表示从A到B的一条有向边，实际上是用来一次性导入networkx用的。
