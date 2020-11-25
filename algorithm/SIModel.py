
import json
import random
import numpy as np
import pandas as pd

#初始化网络
def init_network(data_path):
    import networkx as nx

    # 读入数据
    network_file = open(data_path)
    network = []
    for each_line in network_file:
        line_split = each_line.split()
        network.append([int(line_split[0]), int(line_split[1])])
    network_file.close()

    # 计算节点个数
    nodes = set({})
    for each_link in network:
        nodes.add(each_link[0])
        nodes.add(each_link[1])
    node_num = len(nodes)

    G = nx.Graph(network)

    # # 让节点名称和索引相对应
    # nodes_list = list(nx.nodes(G))
    # nodes_list.sort()
    # node_dict = dict()
    # for i in range(node_num):
    #     node_dict[nodes_list[i]] = i

    # 记录每个节点的位置信息
    pos = nx.drawing.spring_layout(G)
    node_coordinate = []
    for i in range(node_num):
        node_coordinate.append([])
    for i, j in pos.items():
        # node_coordinate[node_dict[i]].append(float(j[0]))
        # node_coordinate[node_dict[i]].append(float(j[1]))
        node_coordinate[i-1].append(float(j[0]))
        node_coordinate[i-1].append(float(j[1]))

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
            'attributes': {'modularity_class': 0},
            'id': str(node),
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
                'source': str(link[0]-1),
                'target': str(link[1]-1)
            })
            cur_edges.append(link)
    graph_data_json['nodes'] = nodes_data_json
    graph_data_json['links'] = links_data_json
    graph_data = json.dumps(graph_data_json)
    return network, node_num, graph_data

path='static/data/Wiki.txt'
networkTemp, number_of_nodes, graph_data = init_network(path)
network_synfix, num_nodes_synfix, graph_data_synfix = init_network(path)
data = pd.read_table(path,header=None)


# 计算节点数
def CalculateNodesnum():
    node = []
    for i in range(len(data)):
        n1 = int(data[0][i])
        n2 = int(data[1][i])
        if n1 not in node:
            node.append(n1)
        if n2 not in node:
            node.append(n2)
    num_node = len(node)
    return node, num_node

# 计算边数
def CalculateEdgesnum():
    edges = []
    for j in range(len(data)):
        e = [data[0][j], data[1][j]]
        edges.append(e)
    num_edges = len(edges)
    return num_edges, edges

# 计算邻接矩阵
def AdjacencyMatrix():
    num_edges,edges = CalculateEdgesnum()
    Adj = np.zeros([number_of_nodes, number_of_nodes], dtype=int)
    for i in range(num_edges):
        Adj[int(edges[i][0] - 1)][int(edges[i][1] - 1)] = 1
        Adj[int(edges[i][1] - 1)][int(edges[i][0] - 1)] = 1
    return Adj

#边的序号
def EdgeNumber():
    num_edges,edges = CalculateEdgesnum()
    nodeset, num_node = CalculateNodesnum()
    edgeNum = np.zeros([num_node, num_node])
    for i in range(num_edges):
        edgeNum[int(edges[i][0]) - 1][int(edges[i][1]) - 1] = edgeNum[int(edges[i][1]) - 1][
            int(edges[i][0]) - 1] = i
    # print("edgeNum:", edgeNum)
    return edgeNum

# 计算度集
def NodeDegreeSet():
    A = AdjacencyMatrix()
    DegreeSet = np.zeros([number_of_nodes], dtype=int)
    for i in range(number_of_nodes):
        Degree = 0
        for j in range(number_of_nodes):
            if (A[i][j] == 1):
                Degree += 1
        DegreeSet[i] = Degree
    return DegreeSet

# 计算邻居节点集
def NeighborNodeSet():
    A = AdjacencyMatrix()
    NeighborNode = []
    for i in range(number_of_nodes):
        neinode = []

        for j in range(number_of_nodes):
            if (A[i][j] == 1):
                neinode.append(j+1)  # 矩阵是从0开始的，节点是从1开始的
        NeighborNode.append(neinode)
    return NeighborNode

# SI模拟传播
def SIsimulation(rateSI,Sus, Inf ):
    edges_set = []
    edgenum = EdgeNumber()  # 边的序号
    N = NeighborNodeSet()  # 邻居节点集合
    # 对感染节点的邻居，以一定的概率被感染
    for i in range(len(Inf)):
        s = int(Inf[i])
        for j in N[s-1]:
            if (j in Sus):
                if random.random() <= rateSI:
                    Inf.append(j)
                    Sus.remove(j)
                    edges_set.append(edgenum[s-1][j-1])
    return Sus, Inf, edges_set


