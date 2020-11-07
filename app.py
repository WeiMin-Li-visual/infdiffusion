# -*- coding:utf-8 -*-
from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Lock
from algorithm import gameTheory
import json

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


# 谣言溯源
@app.route('/rumorDetection')
def rumorDetection():
    '''
    TODO
    :return:
    '''
    return render_template('rumorDetection.html')


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
    print("第%s轮" % 0)
    print(step_active_node_sum)
    active_nodes = set()
    active_nodes = active_nodes.union(now_active_nodes)

    edge_records = []

    for i in range(steps):
        now_active_nodes, edge_records = gameTheory.diffuse_one_round(G, active_nodes, demd, edgeNum)
        step_active_node.append(list(now_active_nodes))
        active_nodes = active_nodes.union(now_active_nodes)
        step_active_node_sum.append(len(active_nodes) / node_num)
        print("第%s轮" % (i + 1))
        print(step_active_node_sum)

    # print(step_active_node)
    # print(len(step_active_node))
    # step_active_node = json.dumps(step_active_node)
    # print(step_active_node)
    # step_active_node_sum = json.dumps(step_active_node_sum)
    return render_template('GameTheory.html', graph_data=graph_data, step_active_node=step_active_node,
                           step_active_node_sum=step_active_node_sum)


# 基于博弈论的行为扩散
def GameTheory_thread():
    steps = 10
    demd = 10
    proportion = 0.01
    path = "static/data/synfix/z_3/synfix_3.t01.edges"
    network, node_num, graph_data, G = gameTheory.init_network(path)
    edgeNum = gameTheory.init_edgeNum(network, node_num)
    nodes = list(G.nodes)

    count = 0
    socketio.emit('server_response',
                  {'data': [count, graph_data, 0]},
                  namespace='/GameTheory')

    # 初始随机设置1%的节点为激活节点
    now_active_nodes = gameTheory.active_node(node_num, proportion, nodes)

    step_active_node_sum = []  # 每一步的激活结点数量
    active_nodes = set()
    edge_records = []

    while steps > 0:
        count += 1
        now_active_nodes_json = list(now_active_nodes)
        edge_records_json = list(edge_records)

        socketio.emit('server_response',
                      {'data': [count, now_active_nodes_json, edge_records_json]},
                      namespace='/GameTheory')

        active_nodes = active_nodes.union(now_active_nodes)
        step_active_node_sum.append(len(active_nodes) / node_num)
        print("第%s轮" % steps)
        print(step_active_node_sum)
        now_active_nodes, edge_records = gameTheory.diffuse_one_round(G, active_nodes, demd, edgeNum)
        steps -= 1

    # 传输最后的扩散结果
    count += 1
    print(count)
    socketio.sleep(1)  # 休眠1秒
    socketio.emit('server_response',
                  {'data': [count, step_active_node_sum, 0]},
                  namespace='/GameTheory')


# 前后端通信（参见：https://blog.csdn.net/weixin_36380516/article/details/80418354）
@socketio.on('connect', namespace='/GameTheory')
def GameTheory_connect():
    thread = socketio.start_background_task(target=GameTheory_thread)


if __name__ == '__main__':
    socketio.run(app, debug=True)
