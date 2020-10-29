# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, flash
import json
import random
import copy
from flask_socketio import SocketIO
from threading import Lock
import networkx as nx
from flask_socketio import SocketIO
from threading import Lock
import re
import sourceDetection as sd
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
@app.route('/SI')
def SI():
    '''
    TODO
    :return:
    '''
    return render_template('SI.html')


# 介绍SIR
@app.route('/introduceSIR')
def introduceSIR():
    '''
    TODO
    :return:
    '''
    return render_template('introduceSIR.html')


# SIR模型扩散
@app.route('/SIR')
def SIR():
    '''
    TODO
    :return:
    '''
    return render_template('SIR.html')

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
@app.route('/GameTheory')
def GameTheory():
    '''
    TODO
    :return:
    '''
    return render_template('GameTheory.html')


# 前后端通信（参见：https://blog.csdn.net/weixin_36380516/article/details/80418354）
@socketio.on('connect', namespace='/SI')
def test_connect():
    thread = socketio.start_background_task(target=SI)


if __name__ == '__main__':
    socketio.run(app, debug=True)
