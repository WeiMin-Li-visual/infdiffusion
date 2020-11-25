# -*- coding:utf-8 -*-
from flask import Flask, render_template,request
from flask_socketio import SocketIO
from threading import Lock
from algorithm import gameTheory
from algorithm import sourceDetection as sd
from algorithm import SIModel as si
from algorithm import SIRModel as sir


import json
import random
import copy

import pandas as pd

import networkx as nx
from flask_socketio import SocketIO
from threading import Lock
import re
thread_lock = Lock()

async_mode = None
thread = None
app = Flask(__name__)
app.secret_key = 'dzb'
socketio = SocketIO(app, async_mode=async_mode)


# 主界面
@app.route('/')
def index():
    return render_template('index.html')


# 使用说明
@app.route('/introduce')
def introduce():
    '''
    TODO
    :return:
    '''

    test = "使用说明界面"
    # 把需要的数据给对应的页面
    return render_template('introduce.html', test=test)


# 关于我们
@app.route('/aboutUs')
def aboutUs():
    '''
    TODO
    :return:
    '''
    return render_template('aboutUs.html')


# 加入我们
@app.route('/joinIn')
def joinIn():
    '''
    TODO
    :return:
    '''
    return render_template('joinIn.html')


# 用户可以自己添加网络
@app.route('/addNetwork')
def addNetwork():
    '''
    TODO
    :return:
    '''
    return render_template('addNetwork.html')


# 舆情演化
@app.route('/poEvolution')
def poEvolution():
    '''
    TODO
    :return:
    '''
    return render_template('poEvolution.html')


# 介绍SI
@app.route('/introduceSI')
def introduceSI():
    '''
    TODO
    :return:
    '''
    return render_template('introduceSI.html')


# SI模型扩散
@app.route('/SI',methods=["GET", "POST"])
def SI():
    '''
    TODO
    :return:
    '''
    # path = 'static/data/Wiki.txt'
    # networkTemp, number_of_nodes, graph_data = si.init_network(path)
    # network_synfix, num_nodes_synfix, graph_data_synfix = si.init_network(path)
    # data = pd.read_table(path, header=None)

    graph_data1 = json.loads(si.graph_data)  # 将json数据转化为字典的形式
    nodeset, num_node = si.CalculateNodesnum()
    Susceptible = nodeset       # 易感者集合
    Infected = []               # 感染者集合
    edge = []                   # 边
    times = []                  # 保存经历了多少时间步

    sus_node = []               # 保存每一时间步易感者节点集合
    inf_node = []               # 保存每一时间步感染者节点集合
    edges_record = []           # 保存边
    sus_node_num = []           # 保存每一时间步易感节点数量
    inf_node_num =[]            #保存每一时间步感染节点数量

    # 随机生成一个感染源节点，并从易感节点移除加入感染节点集

    inf = random.randint(1, num_node)
    Infected.append(inf)
    Susceptible.remove(inf)
    # 打印
    # print("Inf_node:", inf)
    # print("Inf_Susceptible:", Susceptible, len(Susceptible))
    # print("Inf_Infected:", Infected, len(Infected))
    t = 0
    err = "false"
    # SI模拟
    if request.method == "GET":
        sus_node = json.dumps([])
        inf_node = json.dumps([])
        edges_record = json.dumps([])
        err = "true"
        rateSI = 0
        return render_template('SI.html', graph_data=si.graph_data, susceptible_nodes=sus_node,sus_node_num = sus_node_num,
                               infected_nodes=inf_node, edges_record=edges_record, inf_node_num=inf_node_num,
                               times=times,err = err,rateSI = rateSI,method_type=1)
    if request.method == "POST":
        rateSI = request.form.get('rateSI')
        if rateSI != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(rateSI):
                err = "输入不合法，请输入0-1区间的值"
            elif float(rateSI)<0 or float(rateSI)>1:
                err="输入错误，请输入0-1区间的值"
        elif rateSI=="":
            err = "请输入感染率"
    if err!="false":
        return render_template('SI.html', graph_data=si.graph_data, susceptible_nodes=json.dumps([]),
                               infected_nodes=json.dumps([]),  edges_record=json.dumps([]),
                               sus_node_num=sus_node_num, inf_node_num=inf_node_num,
                               times=times, err=err,rateSI = 0,method_type=1)

    while len(Susceptible) != 0:
        sus_node.append(copy.deepcopy(Susceptible))
        inf_node.append(copy.deepcopy(Infected))
        edges_record.append(copy.deepcopy(edge))

        sus_node_num.append(len(Susceptible))
        inf_node_num.append(len(Infected) )
        t = t + 1
        # print(type(rateSI))
        Susceptible, Infected, edge = si.SIsimulation(float(rateSI),Susceptible, Infected)
        # print(t, ":Susceptible:", Susceptible, len(Susceptible))
        # print(t, ":Infected:", Infected, len(Infected))
        # print(t, "edge", edge, len(edge))
    sus_node.append(copy.deepcopy(Susceptible))
    inf_node.append(copy.deepcopy(Infected))
    edges_record.append(copy.deepcopy(edge))

    sus_node_num.append(len(Susceptible))
    inf_node_num.append(len(Infected))

    for i in range(1,t+2):
        times.append(i)
    # print("times:",times)
    # print("edge:", edges_record)
    sus_node1 = []
    sus_node1.append(sus_node[0])
    for i in range(1, len(sus_node)):
        sus_node1.append([])
        for j in range(len(sus_node[i])):
            if (sus_node[i][j] not in sus_node[i - 1]):
                sus_node1[i].append(sus_node[i][j])
    # print(sus_node1, len(sus_node1))

    inf_node1 = []
    inf_node1.append(inf_node[0])
    for i in range(1, len(inf_node)):
        inf_node1.append([])
        for j in range(len(inf_node[i])):
            if (inf_node[i][j] not in inf_node[i - 1]):
                inf_node1[i].append(inf_node[i][j])
    # print(inf_node1, len(inf_node1))

    sus_node = json.dumps(sus_node1)
    inf_node = json.dumps(inf_node1)
    edges_record = json.dumps(edges_record)

    # print("inf_node_num", inf_node_num)

    graph_data1 = json.dumps(graph_data1)  # 将数据转化为json格式
    return render_template('SI.html', graph_data=graph_data1, susceptible_nodes=sus_node,infected_nodes=inf_node,
                           edges_record=edges_record, sus_node_num = sus_node_num,inf_node_num=inf_node_num,
                           times=times,err = err,rateSI = rateSI,method_type=1)



# 介绍SIR
@app.route('/introduceSIR')
def introduceSIR():
    '''
    TODO
    :return:
    '''
    return render_template('introduceSIR.html')


# SIR模型扩散
@app.route('/SIR',methods=["GET", "POST"])
def SIR():
    '''
    TODO
    :return:
    '''

    graph_data1 = json.loads(sir.graph_data)  # 将json数据转化为字典的形式
    nodeset, num_node = sir.CalculateNodesnum()
    Susceptible = nodeset       # 易感者集合
    Infected = []               # 感染者集合
    Resistant = []              # 恢复者集合
    edge = []                   # 边
    times = []                  # 保存经历了多少时间步

    sus_node = []               # 保存每一时间步易感节点集合
    inf_node = []               # 保存每一时间步感染节点集合
    res_node = []               # 保存每一时间步恢复节点集合
    edges_record = []           # 保存边

    sus_node_num = []           # 保存每一时间步易感节点数量
    inf_node_num = []           # 保存每一时间步感染节点数量
    res_node_num = []           # 保存每一时间步恢复节点的数量

    # 随机生成一个感染源节点，并从易感节点移除加入感染节点集
    inf = random.randint(1, num_node)
    Infected.append(inf)
    Susceptible.remove(inf)

    # print("Inf_node:", inf)
    # print("Inf_Susceptible:", Susceptible, len(Susceptible))
    # print("Inf_Infected:", Infected, len(Infected))
    # print("Inf_Resistant:", Resistant, len(Resistant))

    t = 0
    err = "false"  # 返回错误信息
    # SIR模拟
    if request.method == "GET":
        sus_node = json.dumps([])
        inf_node = json.dumps([])
        res_node = json.dumps([])
        edges_record = json.dumps([])
        err = "true"
        rateSI = 0
        rateIR = 0

        return render_template('SIR.html', graph_data=sir.graph_data, susceptible_nodes=sus_node,
                               infected_nodes=inf_node, resistant_nodes=res_node, edges_record=edges_record,
                               sus_node_num = sus_node_num,inf_node_num=inf_node_num, res_node_num=res_node_num,
                               times=times,err=err,rateIR = rateIR,rateSI = rateSI,method_type=1)
    if request.method == "POST":
        rateSI = request.form.get('rateSI')
        rateIR = request.form.get('rateIR')
        if rateSI != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(rateSI):
                err = "输入不合法，请输入0-1区间的值"
            elif float(rateSI)<0 or float(rateSI)>1:
                err="输入错误，请输入0-1区间的值"
        elif rateSI=="":
            err = "请输入感染率"
        if rateIR != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(rateIR):
                err = "输入不合法，请输入0-1区间的值"
            elif float(rateIR) < 0.05 or float(rateIR) > 0.9:
                err = "输入错误，请输入0-1区间的值"
        elif rateIR == "":
            err = "请输入恢复率"

        if (rateIR=="" and rateSI ==""):
            err = "请输入感染率和恢复率"
    if err!="false":
        return render_template('SIR.html', graph_data=sir.graph_data, susceptible_nodes=json.dumps([]),
                               infected_nodes=json.dumps([]), resistant_nodes=json.dumps([]), edges_record=json.dumps([]),
                               sus_node_num=sus_node_num, inf_node_num=inf_node_num, res_node_num=res_node_num,
                               times=times, err=err, rateIR = 0,rateSI = 0,method_type=1)

    while len(Infected) != 0:
        sus_node.append(copy.deepcopy(Susceptible))
        inf_node.append(copy.deepcopy(Infected))
        res_node.append(copy.deepcopy(Resistant))
        edges_record.append(copy.deepcopy(edge))

        sus_node_num.append(len(Susceptible))
        inf_node_num.append(len(Infected))
        res_node_num.append(len(Resistant))
        t = t + 1
        # print(type(rateSI))
        # print(type(rateIR))
        Susceptible, Infected, Resistant,edge = sir.SIRsimulation(float(rateSI),float(rateIR),Susceptible, Infected,Resistant)
        # print(t, ":Susceptible:", Susceptible, len(Susceptible))
        # print(t, ":Infected:", Infected, len(Infected))
        # print(t, ":Resistant:", Resistant, len(Resistant))
        # print(t, "edge", edge, len(edge))

    sus_node.append(copy.deepcopy(Susceptible))
    inf_node.append(copy.deepcopy(Infected))
    res_node.append(copy.deepcopy(Resistant))
    edges_record.append(copy.deepcopy(edge))

    sus_node_num.append(len(Susceptible))
    inf_node_num.append(len(Infected))
    res_node_num.append(len(Resistant))

    for i in range(1,t+2):
        times.append(i)
    # print("times:",times)
    #
    # print("edge:", edges_record)
    sus_node1 = []
    sus_node1.append(sus_node[0])
    for i in range(1, len(sus_node)):
        sus_node1.append([])
        for j in range(len(sus_node[i])):
            if (sus_node[i][j] not in sus_node[i - 1]):
                sus_node1[i].append(sus_node[i][j])
    # print(sus_node1, len(sus_node1))

    inf_node1 = []
    inf_node1.append(inf_node[0])
    for i in range(1, len(inf_node)):
        inf_node1.append([])
        for j in range(len(inf_node[i])):
            if (inf_node[i][j] not in inf_node[i - 1]):
                inf_node1[i].append(inf_node[i][j])
    # print(inf_node1, len(inf_node1))

    res_node1 = []
    res_node1.append(res_node[0])
    for i in range(1, len(res_node)):
        res_node1.append([])
        for j in range(len(res_node[i])):
            if (res_node[i][j] not in res_node[i - 1]):
                res_node1[i].append(res_node[i][j])
    # print(res_node1, len(res_node1))

    sus_node = json.dumps(sus_node1)
    inf_node = json.dumps(inf_node1)
    res_node = json.dumps(res_node1)
    edges_record = json.dumps(edges_record)

    # print("inf_node_num", inf_node_num)
    # print("res_node_num",res_node_num)

    graph_data1 = json.dumps(graph_data1)  # 将数据转化为json格式
    return render_template('SIR.html', graph_data=graph_data1, susceptible_nodes=sus_node,
                           infected_nodes=inf_node, resistant_nodes=res_node, edges_record=edges_record,
                           sus_node_num = sus_node_num,inf_node_num=inf_node_num, res_node_num=res_node_num,
                           times=times, err=err,rateIR = rateIR,rateSI = rateSI,method_type=1)


# 谣言溯源： 刘艳霞
@app.route('/sourceDetection',methods=["GET", "POST"])
def SourceDetection():
    node_in_Community=sd.node_in_Community#每个节点所在的分区
    err="false" # 返回错误信息
    if request.method == "GET":
        # 初始化权重矩阵
        err = "true"
        active_records = json.dumps([])
        ObserverNodeList=[]
        edge_records=json.dumps([])
        return render_template('sourceDetection.html', graph_data=sd.graph_data,
                               ObserverNodeList=ObserverNodeList,active_records=active_records, edge_records=edge_records,
                               shortestPath=[],err=err,node_in_Community=node_in_Community)
    else:#request：请求对象，获取请求方式数据
        percentage=request.form.get('percentage')#观测点数量
        iteration=request.form.get('iteration')#迭代次数
        method=request.form.get('method')#选择观测点方法
        #mean=request.form.get('mean')#时延均值
        #variance=request.form.get('variance')#时延方差
        if percentage != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(percentage):
                err="输入不合法，请输入0.05-0.9之间的数字"
            elif float(percentage)<0.05 or float(percentage)>0.9:
                err="输入错误，请输入0.05-0.9之间的数字"
        elif percentage=="":
            err = "输入为空，请输入观测比例"
        if iteration=="":
            err="输入为空，请输入迭代次数"
        else:
            if iteration.isdigit()==False:
                err="输入不合法，请输入一个整数"
            elif int(iteration)<1 or int(iteration)>10000:
                err="迭代次数最少为1，请输入大于1的整数"
    if err!="false":
        return render_template('sourceDetection.html', graph_data=sd.graph_data,
                               ObserverNodeList=[],active_records=json.dumps([]), edge_records=json.dumps([]),
                              shortestPath=[], err=err,node_in_Community=node_in_Community)
    count = 0#准确定位到源的次数
    errorDistance = [0 for index in range(5)]#存放每一跳的误差比例
    all_iteration_dis=[]#[[真实的源，预测的源，第一次迭代误差距离]，第二次迭代预测源与真实源的误差距离，.....,误差列表，所有迭代中的准确率]
    distance=0
    mean_error_distance = 0  # 平均误差距离
    shortestPath = []  # [[[6(reverse_source), 35(reverse_target), 98.0(边编号）]], [[2, 5, 33.0], [5, 6, 75.0], [6, 35, 98.0]], 记录每个最短路径
    shortestPath1 = []  # 最短路径列表[[a,b,c],[c,f,g,e]....]
    active_records1=[]
    edge_records1=[]
    ObserverNodeList1=[]
    for i in range(int(iteration)):
        candidateCommunity, candidateCommunityObserveInfectedNode, ALLCandidatSourceNode, AllCandidateObserveNode, relSource, CommunitiesList,\
        SourceNodeInCom, ObserverNodeList, active_records, edge_records = sd.SI_diffusion(float(percentage),int(method))
        preSource, maxValue = sd.GM(ALLCandidatSourceNode, AllCandidateObserveNode)
        if (preSource == relSource):
            count+=1
            errorDistance[0] += 1
            distance=0
        else:
            distance=nx.shortest_path_length(sd.G,preSource,relSource)
            errorDistance[distance]+=1
        all_iteration_dis.append([relSource,preSource,distance])
        if i==0:
            ObserverNodeList1=ObserverNodeList
            print("edge_records",edge_records)
            active_records1 = json.dumps(active_records)
            edge_records1 = json.dumps(edge_records)
            for i in ObserverNodeList1:
                shortestPath1.append(nx.shortest_path(sd.G, i,relSource))
            for paths in shortestPath1:
                shortestPath.append([])
                for i in range(len(paths) - 1):
                    shortestPath[len(shortestPath) - 1].append([paths[i],paths[i + 1],sd.edgeNum[paths[i]][paths[i + 1]]])
    for j in range(len(errorDistance)):
        mean_error_distance += errorDistance[j] * j
        errorDistance[j] = round(errorDistance[j] / int(iteration), 2)  # 误差在各跳数的比例
    mean_error_distance = round(mean_error_distance / int(iteration), 2)  # 平均误差距离
    errorDistance=[e for e in errorDistance if e>0]
    all_iteration_dis.extend([errorDistance,round(count/int(iteration),2),mean_error_distance])#误差列表，定位准确率，平均误差距离
    return render_template('sourceDetection.html', graph_data=sd.graph_data,
                               ObserverNodeList=ObserverNodeList1,
                               active_records=active_records1, edge_records=edge_records1,
                               shortestPath=shortestPath, err=err,all_iteration_dis=all_iteration_dis,node_in_Community=node_in_Community)


# 介绍霍克斯过程
@app.route('/introduceHawks')
def introduceHawks():
    '''
    TODO
    :return:
    '''
    return render_template('introduceHawks.html')


# 基于霍克斯过程的行为扩散
@app.route('/Hawks')
def Hawks():
    '''
    TODO
    :return:
    '''
    return render_template('Hawks.html')


# 介绍博弈论
@app.route('/introduceGameTheory')
def introduceGameTheory():
    '''
    TODO
    :return:
    '''
    return render_template('introduceGameTheory.html')


# 基于博弈论的行为扩散
@app.route('/GameTheory',methods=["GET", "POST"])
def GameTheory():
    steps = 10
    demd = 10
    proportion = 0.01
    path = "static/data/synfix/z_3/synfix_3.t01.edges"
    network, node_num, graph_data, G = gameTheory.init_network(path)
    edgeNum = gameTheory.init_edgeNum(network, node_num)
    nodes = list(G.nodes)

    # 初始随机设置1%的节点为激活节点
    now_active_nodes = gameTheory.active_node(node_num, proportion, nodes)
    step_active_node = []
    step_active_node.append(list(now_active_nodes))
    step_active_node_sum = []  # 每一步的激活结点数量
    step_active_node_sum.append(len(now_active_nodes) / node_num)
    # print("第%s轮" % 0)
    # print(step_active_node_sum)
    active_nodes = set()
    active_nodes = active_nodes.union(now_active_nodes)

    edge_records = []

    for i in range(steps):
        now_active_nodes, edge_records = gameTheory.diffuse_one_round(G, active_nodes, demd, edgeNum)
        step_active_node.append(list(now_active_nodes))
        active_nodes = active_nodes.union(now_active_nodes)
        step_active_node_sum.append(len(active_nodes) / node_num)
        # print("第%s轮" % (i + 1))
    print(step_active_node_sum)
    return render_template('GameTheory.html', graph_data=graph_data, step_active_node=step_active_node,
                           step_active_node_sum=step_active_node_sum)

# 前后端通信（参见：https://blog.csdn.net/weixin_36380516/article/details/80418354）
class GameTheory_thread(object):
    pass


@socketio.on('connect', namespace='/GameTheory')
def GameTheory_connect():
    thread = socketio.start_background_task(target=GameTheory_thread)


if __name__ == '__main__':
    socketio.run(app, debug=True)
