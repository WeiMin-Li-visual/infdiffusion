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


class GameTheory():
    def __init__(self, data_path,steps, proportion=0.1, uncertainty=0.1):
        self.data_path = data_path
        self.proportion = proportion
        self.uncertainty = uncertainty
        self.steps=steps
        self.G = None
        self.nodes = None
        self.node_num = None
        self.graph_data = None
        self.network = None
        self.step_active_node = []
        self.step_active_node_sum = []
        self.now_active_nodes = set()
        self.active_nodes = set()

    # 初始化网络
    # input: data_path
    # output: network, node_num, graph_data
    def init_network(self):
        network_file = open(self.data_path)
        self.network = []
        for each_line in network_file:
            line_split = each_line.split()
            self.network.append([int(line_split[0]), int(line_split[1])])
        network_file.close()
        self.G = nx.Graph(self.network)
        self.nodes = list(self.G.nodes)
        self.node_num = len(self.nodes)

        # 记录每个节点的位置信息
        pos = nx.drawing.spring_layout(self.G)

        # 记录节点的坐标
        node_coordinate = []
        for i in range(self.node_num):
            node_coordinate.append([])
        for i, j in pos.items():
            node_coordinate[i - 1].append(float(j[0]))
            node_coordinate[i - 1].append(float(j[1]))

        # 设置传给前端的节点数据边数据的json串
        graph_data_json = {}
        nodes_data_json = []

        for node in range(self.node_num):
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
        for link in self.network:
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
        self.graph_data = json.dumps(graph_data_json)

    # 设置初始激活节点
    def active_node(self):
        count = int(self.node_num * self.proportion)
        if count == 0:
            count = 1
        while (count > 0):
            nd = random.randint(0, self.node_num - 1)
            node = self.nodes[nd]
            if node not in self.now_active_nodes:
                self.now_active_nodes.add(node)
                count -= 1

    # 存储每条边在网络中的序号
    def __init_edgeNum(self):
        edgeNum = []
        for i in range(self.node_num):
            edgeNum.append([])
            for j in range(self.node_num):
                edgeNum[i].append(0)
        count = 0
        for linePiece in self.network:
            edgeNum[linePiece[0] - 1][linePiece[1] - 1] = count
            count += 1
        return edgeNum

    def diffuse_one_round(self):
        dmax = 200
        # 协调博弈的收益矩阵
        a = 1
        c = 1

        payoff = [[a, 0], [0, c]]
        self.now_active_nodes=set()
        for node in self.active_nodes:
            u1 = 0
            u0 = 0
            nbs = self.G.neighbors(node)
            for nb in nbs:
                if nb in self.active_nodes:
                    continue
                for n in self.G.neighbors(nb):
                    if n in self.active_nodes:
                        u1 += payoff[0][0]
                        u0 += payoff[1][0]
                    else:
                        u1 += payoff[0][1]
                        u0 += payoff[1][1]
                u1 /= (dmax * payoff[0][0])
                u0 /= (dmax * payoff[0][0])

                p = self.__probab(u1, u0, self.uncertainty)
                rp = np.random.rand(1)

                if p >= rp:
                    # edge_location.append(edgeNum[node - 1][nb - 1])
                    self.now_active_nodes.add(nb)


    def diffuse(self):
        self.step_active_node.append(list(self.now_active_nodes))
        self.step_active_node_sum.append(len(self.now_active_nodes) / self.node_num)
        self.active_nodes = self.active_nodes.union(self.now_active_nodes)

        for i in range(self.steps):
            self.diffuse_one_round()
            self.step_active_node.append(list(self.now_active_nodes))
            self.active_nodes = self.active_nodes.union(self.now_active_nodes)
            self.step_active_node_sum.append(len(self.active_nodes) / self.node_num)

    # 计算行为概率
    def __probab(self, u1, u0, demd=1.0):
        try:
            p = 1 / (1 + math.exp(((-1) * (u1 - u0)) / demd))
        except OverflowError:
            p = 0
        return p
