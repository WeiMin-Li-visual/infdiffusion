#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2020/10/30 14:27
# @Author  : 邓志斌
# @Email   : 1830601430@qq.com
# @File    : gameTheory.py
# @Software: PyCharm


import numpy as np
import networkx as nx
import random
import math
import json


# 初始化网络
# input: data_path
# output: network, node_num, graph_data
def init_network(data_path):
    network_file = open(data_path)
    network = []
    for each_line in network_file:
        line_split = each_line.split()
        network.append([int(line_split[0]), int(line_split[1])])
    network_file.close()

    G = nx.Graph(network)

    nodes = list(G.nodes)
    node_num = len(nodes)

    # # 让节点名称和索引相对应
    # nodes_list = list(nx.nodes(G))
    # nodes_list.sort()
    # node_dict = dict()
    # for i in range(node_num):
    #     node_dict[nodes_list[i]] = i

    # 记录每个节点的位置信息
    pos = nx.drawing.spring_layout(G)

    # 记录节点的坐标
    node_coordinate = []
    for i in range(node_num):
        node_coordinate.append([])
    for i, j in pos.items():
        # node_coordinate[node_dict[i]].append(float(j[0]))
        # node_coordinate[node_dict[i]].append(float(j[1]))
        node_coordinate[i - 1].append(float(j[0]))
        node_coordinate[i - 1].append(float(j[1]))

    # 设置传给前端的节点数据边数据的json串
    graph_data_json = {}
    nodes_data_json = []
    # for node in nodes_list:
    #     nodes_data_json.append({
    #         'attributes': {'modularity_class': 0},
    #         'id': str(node),
    #         'category': 0,
    #         'itemStyle': '',
    #         'label': {'normal': {'show': 'false'}},
    #         'name': str(node),
    #         'symbolSize': 35,
    #         'value': 111,
    #         'x': node_coordinate[node_dict[node]][0],
    #         'y': node_coordinate[node_dict[node]][1]
    #     })
    for node in range(node_num):
        nodes_data_json.append({
            'attributes': {'modularity_class': 0},  # 给定节点的属性
            'id': str(node),  # 节点的ID
            'category': 0,
            'itemStyle': '',
            'label': {'normal': {'show': 'false'}},
            'name': str(node),
            'symbolSize': 35,
            'value': 111,
            'x': node_coordinate[node][0],
            'y': node_coordinate[node][1]
        })
    links_data_json = []
    cur_edges = []
    for link in network:
        edge = [link[1], link[0]]
        if edge not in cur_edges:
            link_id = len(links_data_json)
            links_data_json.append({
                'id': str(link_id),
                'lineStyle': {'normal': {}},
                'name': 'null',
                'source': str(link[0] - 1),
                'target': str(link[1] - 1)
            })
            cur_edges.append(link)
    graph_data_json['nodes'] = nodes_data_json
    graph_data_json['links'] = links_data_json
    graph_data = json.dumps(graph_data_json)
    return network, node_num, graph_data, G


# 设置初始激活节点
def active_node(node_num, proportion, nodes):

    # 初始随机设置1%的节点为激活节点
    count = int(node_num * proportion)
    if count == 0:
        count = 1
    now_active_nodes = set()
    while (count > 0):
        nd = random.randint(0, node_num-1)
        node = nodes[nd]
        if node not in now_active_nodes:
            now_active_nodes.add(node)
            count -= 1

    return now_active_nodes


# 存储每条边在网络中的序号
def init_edgeNum(network,number_of_nodes):
    edgeNum = []  # 存储每条边在networkTemp中的序号
    for i in range(number_of_nodes):
        edgeNum.append([])
        for j in range(number_of_nodes):
            edgeNum[i].append(0)
    count = 0
    for linePiece in network:
        edgeNum[linePiece[0] - 1][linePiece[1] - 1] = count
        count += 1
    return edgeNum


# 计算行为概率
def probab(u1, u0, demd=1):
    try:
        p = 1 / (1 + math.exp(((-1) * (u1 - u0)) / demd))
    except OverflowError:
        p = 0
    return p


def diffuse_one_round(G, active_nodes, demd,edgeNum):
    dmax = 200
    # 协调博弈的收益矩阵
    a = 1
    c = 1

    payoff = [[a, 0], [0, c]]
    activated_nodes_of_this_round = set()

    edge_location = [] # 记录激活边的序号

    for node in active_nodes:
        u1 = 0
        u0 = 0
        nbs = G.neighbors(node)
        for nb in nbs:
            if nb in active_nodes:
                continue
            for n in G.neighbors(nb):
                if n in active_nodes:
                    u1 += payoff[0][0]
                    u0 += payoff[1][0]
                else:
                    u1 += payoff[0][1]
                    u0 += payoff[1][1]
            u1 /= (dmax * payoff[0][0])
            u0 /= (dmax * payoff[0][0])

            p = probab(u1, u0, demd)
            rp = np.random.rand(1)

            if p >= rp:
                edge_location.append(edgeNum[node-1][nb-1])
                activated_nodes_of_this_round.add(nb)

    return activated_nodes_of_this_round,edge_location
