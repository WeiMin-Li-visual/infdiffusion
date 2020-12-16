#!/usr/bin/python3.6

'''
    Implements the Louvain method.
    Input: a weighted undirected graph
    Ouput: a (partition, modularity) pair where modularity is maximum
'''


class PyLouvain:
    '''
        Builds a graph from _path.
        _path: a path to a file containing "node_from node_to" edges (one per line)
    '''

    @classmethod
    def from_file(cls, path):
        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        nodes = {}
        edges = []
        for line in lines:
            n = line.split()
            if not n:
                break
            nodes[n[0]] = 1
            nodes[n[1]] = 1
            w = 1
            if len(n) == 3:
                w = int(n[2])
            edges.append(((n[0], n[1]), w))
        # rebuild graph with successive identifiers
        nodes_, edges_ = in_order(nodes, edges)
        #print("%d nodes, %d edges" % (len(nodes_), len(edges_)))
        return cls(nodes_, edges_)

    '''
        Builds a graph from _path.
        _path: a path to a file following the Graph Modeling Language specification
    '''

    @classmethod
    def from_gml_file(cls, path):
        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        nodes = {}
        edges = []
        current_edge = (-1, -1, 1)
        in_edge = 0
        for line in lines:
            words = line.split()
            if not words:
                break
            if words[0] == 'id':
                nodes[int(words[1])] = 1
            elif words[0] == 'source':
                in_edge = 1
                current_edge = (int(words[1]), current_edge[1], current_edge[2])
            elif words[0] == 'target' and in_edge:
                current_edge = (current_edge[0], int(words[1]), current_edge[2])
            elif words[0] == 'value' and in_edge:
                current_edge = (current_edge[0], current_edge[1], int(words[1]))
            elif words[0] == ']' and in_edge:
                edges.append(((current_edge[0], current_edge[1]), 1))
                current_edge = (-1, -1, 1)
                in_edge = 0
        nodes, edges = in_order(nodes, edges)
        #print("%d nodes, %d edges" % (len(nodes), len(edges)))
        return cls(nodes, edges)

    '''
        Initializes the method.
        _nodes: a list of ints
        _edges: a list of ((int, int), weight) pairs
    '''

    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        # precompute m (sum of the weights of all links in network)
        #            k_i (sum of the weights of the links incident to node i)
        self.m = 0
        self.k_i = [0 for n in nodes]
        self.edges_of_node = {}
        self.w = [0 for n in nodes]
        for e in edges:
            self.m += e[1]
            self.k_i[e[0][0]] += e[1]
            self.k_i[e[0][1]] += e[1]  # there's no self-loop initially
            # save edges by node
            if e[0][0] not in self.edges_of_node:
                self.edges_of_node[e[0][0]] = [e]
            else:
                self.edges_of_node[e[0][0]].append(e)
            if e[0][1] not in self.edges_of_node:
                self.edges_of_node[e[0][1]] = [e]
            elif e[0][0] != e[0][1]:
                self.edges_of_node[e[0][1]].append(e)
        # access community of a node in O(1) time
        self.communities = [n for n in nodes]
        self.actual_partition = []

    '''
        Applies the Louvain method.
    '''

    def apply_method(self):
        network = (self.nodes, self.edges)
        best_partition = [[node] for node in network[0]]
        best_q = -1
        i = 1
        while 1:
            # print("pass #%d" % i)
            i += 1
            partition = self.first_phase(network)
            q = self.compute_modularity(partition)
            partition = [c for c in partition if c]
            # print("%s (%.8f)" % (partition, q))
            # clustering initial nodes with partition
            if self.actual_partition:
                actual = []
                for p in partition:
                    part = []
                    for n in p:
                        part.extend(self.actual_partition[n])
                    actual.append(part)
                self.actual_partition = actual
            else:
                self.actual_partition = partition
            if q == best_q:
                break
            network = self.second_phase(network, partition)
            best_partition = partition
            best_q = q

        return (self.actual_partition, best_q)

    '''
        Computes the modularity of the current network.
        _partition: a list of lists of nodes
    '''

    def compute_modularity(self, partition):
        q = 0
        m2 = self.m * 2
        for i in range(len(partition)):
            q += self.s_in[i] / m2 - (self.s_tot[i] / m2) ** 2
        return q

    '''
        Computes the modularity gain of having node in community _c.
        _node: an int
        _c: an int
        _k_i_in: the sum of the weights of the links from _node to nodes in _c
    '''

    def compute_modularity_gain(self, node, c, k_i_in):
        return 2 * k_i_in - self.s_tot[c] * self.k_i[node] / self.m

    '''
        Performs the first phase of the method.
        _network: a (nodes, edges) pair
    '''

    def first_phase(self, network):
        # make initial partition
        best_partition = self.make_initial_partition(network)
        while 1:
            improvement = 0
            for node in network[0]:
                node_community = self.communities[node]
                # default best community is its own
                best_community = node_community
                best_gain = 0
                # remove _node from its community
                best_partition[node_community].remove(node)
                best_shared_links = 0
                for e in self.edges_of_node[node]:
                    if e[0][0] == e[0][1]:
                        continue
                    if e[0][0] == node and self.communities[e[0][1]] == node_community or e[0][1] == node and \
                            self.communities[e[0][0]] == node_community:
                        best_shared_links += e[1]
                self.s_in[node_community] -= 2 * (best_shared_links + self.w[node])
                self.s_tot[node_community] -= self.k_i[node]
                self.communities[node] = -1
                communities = {}  # only consider neighbors of different communities
                for neighbor in self.get_neighbors(node):
                    community = self.communities[neighbor]
                    if community in communities:
                        continue
                    communities[community] = 1
                    shared_links = 0
                    for e in self.edges_of_node[node]:
                        if e[0][0] == e[0][1]:
                            continue
                        if e[0][0] == node and self.communities[e[0][1]] == community or e[0][1] == node and \
                                self.communities[e[0][0]] == community:
                            shared_links += e[1]
                    # compute modularity gain obtained by moving _node to the community of _neighbor
                    gain = self.compute_modularity_gain(node, community, shared_links)
                    if gain > best_gain:
                        best_community = community
                        best_gain = gain
                        best_shared_links = shared_links
                # insert _node into the community maximizing the modularity gain
                best_partition[best_community].append(node)
                self.communities[node] = best_community
                self.s_in[best_community] += 2 * (best_shared_links + self.w[node])
                self.s_tot[best_community] += self.k_i[node]
                if node_community != best_community:
                    improvement = 1
            if not improvement:
                break
        return best_partition

    '''
        Yields the nodes adjacent to _node.
        _node: an int
    '''

    def get_neighbors(self, node):
        for e in self.edges_of_node[node]:
            if e[0][0] == e[0][1]:  # a node is not neighbor with itself
                continue
            if e[0][0] == node:
                yield e[0][1]
            if e[0][1] == node:
                yield e[0][0]

    '''
        Builds the initial partition from _network.
        _network: a (nodes, edges) pair
    '''

    def make_initial_partition(self, network):
        partition = [[node] for node in network[0]]
        self.s_in = [0 for node in network[0]]
        self.s_tot = [self.k_i[node] for node in network[0]]
        for e in network[1]:
            if e[0][0] == e[0][1]:  # only self-loops
                self.s_in[e[0][0]] += e[1]
                self.s_in[e[0][1]] += e[1]
        return partition

    '''
        Performs the second phase of the method.
        _network: a (nodes, edges) pair
        _partition: a list of lists of nodes
    '''

    def second_phase(self, network, partition):
        nodes_ = [i for i in range(len(partition))]
        # relabelling communities
        communities_ = []
        d = {}
        i = 0
        for community in self.communities:
            if community in d:
                communities_.append(d[community])
            else:
                d[community] = i
                communities_.append(i)
                i += 1
        self.communities = communities_
        # building relabelled edges
        edges_ = {}
        for e in network[1]:
            ci = self.communities[e[0][0]]
            cj = self.communities[e[0][1]]
            try:
                edges_[(ci, cj)] += e[1]
            except KeyError:
                edges_[(ci, cj)] = e[1]
        edges_ = [(k, v) for k, v in edges_.items()]
        # recomputing k_i vector and storing edges by node
        self.k_i = [0 for n in nodes_]
        self.edges_of_node = {}
        self.w = [0 for n in nodes_]
        for e in edges_:
            self.k_i[e[0][0]] += e[1]
            self.k_i[e[0][1]] += e[1]
            if e[0][0] == e[0][1]:
                self.w[e[0][0]] += e[1]
            if e[0][0] not in self.edges_of_node:
                self.edges_of_node[e[0][0]] = [e]
            else:
                self.edges_of_node[e[0][0]].append(e)
            if e[0][1] not in self.edges_of_node:
                self.edges_of_node[e[0][1]] = [e]
            elif e[0][0] != e[0][1]:
                self.edges_of_node[e[0][1]].append(e)
        # resetting communities
        self.communities = [n for n in nodes_]
        return (nodes_, edges_)


'''
    Rebuilds a graph with successive nodes' ids.
    _nodes: a dict of int
    _edges: a list of ((int, int), weight) pairs
'''


def in_order(nodes, edges):
    # rebuild graph with successive identifiers
    nodes = list(nodes.keys())
    nodes.sort()
    i = 0
    nodes_ = []
    d = {}
    for n in nodes:
        nodes_.append(i)
        d[n] = i
        i += 1
    edges_ = []
    for e in edges:
        edges_.append(((d[e[0][0]], d[e[0][1]]), e[1]))
    return (nodes_, edges_)


# -*- coding:utf-8 -*-
import numpy as np
import networkx as nx
import json
import random
from itertools import chain
from ast import literal_eval
import copy
# author: 刘艳霞

data_path = 'static/data/synfix/z_3/synfix_3.t01.edges'
pyl = PyLouvain.from_file(data_path)
Communitys, q = pyl.apply_method()  # 对网络划分分区
Num = len(list(chain.from_iterable(Communitys)))
node_in_Community = [0 for i in range(Num)]  # 每个节点所在的分区
for i in range(len(Communitys)):
    for j in Communitys[i]:
        node_in_Community[j] = i + 4



# 初始化网络
def init_network(data_path):
    # 读入数据
    network_file = open(data_path)
    edges = []  # 边列表
    # edges1 = []  # 用来寻找最短路径遍历
    for each_line in network_file:
        line_split = each_line.split()
        # edges1.append([int(line_split[0])-1, int(line_split[1])-1])
        if (int(line_split[0]) - 1) < (int(line_split[1]) - 1):
            t = [int(line_split[0]) - 1, int(line_split[1]) - 1]
        else:
            t = [int(line_split[1]) - 1, int(line_split[0]) - 1]
        if (t not in edges):
            edges.append(t)

    network_file.close()
    nodes = set({})  # 节点集合
    for each_link in edges:
        nodes.add(each_link[0])
        nodes.add(each_link[1])
    node_num = len(nodes)  # 节点数量

    G = nx.Graph(edges)
    # 记录每个节点的位置信息
    pos = nx.drawing.spring_layout(G)
    node_coordinate = []
    for i in range(node_num):
        node_coordinate.append([])
    for i, j in pos.items():
        node_coordinate[i].extend([float(j[0]), float(j[1])])
    # 设置传给前端的节点和边数据的json串
    graph_data_json = {}
    nodes_data_json = []
    for node in range(node_num):
        nodes_data_json.append({
            'attributes': {'modularity_class': 0},
            'id': str(node),
            'category': node_in_Community[node],
            'itemStyle': '',
            'label': {'normal': {'show': 'false'}},
            'name': str(node),
            'symbolSize': 35,
            'value': 111,
            'x': node_coordinate[node][0],
            'y': node_coordinate[node][1]
        })
    edges_data_json = []
    cur_edges = []
    for link in edges:
        edge = [link[1], link[0]]
        if edge not in cur_edges:
            link_id = len(edges_data_json)
            edges_data_json.append({
                'id': str(link_id),
                'lineStyle': {'normal': {}},
                'name': 'null',
                'source': str(link[0]),
                'target': str(link[1])
            })
            cur_edges.append(link)
    graph_data_json['nodes'] = nodes_data_json
    graph_data_json['links'] = edges_data_json
    graph_data = json.dumps(graph_data_json)  # 将字典形式的数据结构转换为JSON
    return edges, node_num, graph_data, G  # 边列表，节点的数量，图数据


mean = 2  # 高斯分布的均值
variance = 0.5  # 方差

# data_path="static/data/karate.dat"
edges, node_num, graph_data, G = init_network(data_path)
edges_num = len(edges)


# 计算邻接矩阵，矩阵的元素表示两个节点的时延
def adjacency_matrix():
    node_neigbors_dic = {}  # 使用字典的形式存放节点及其节点的邻居，key:节点 values:邻居列表
    edgeNum = np.zeros([node_num, node_num])  # 存储每条边在edges中的序号,是个二维矩阵，每个元素表示两节点连边在边列表edges中的位置
    A = np.zeros([node_num, node_num])  # 网络的邻接矩阵
    for i in range(len(edges)):
        index1 = int(edges[i][1])
        index2 = int(edges[i][0])
        A[index1][index2] = A[index2][index1] = round(
            random.gauss(mean, variance), 2)  # 数据中的节点是从1开始的，而矩阵是从0开始的
        edgeNum[index2][index1] = edgeNum[index1][index2] = i
        if index1 not in node_neigbors_dic.keys():
            node_neigbors_dic[index1] = [index2]
        else:
            node_neigbors_dic[index1].append(index2)

        if index2 not in node_neigbors_dic.keys():
            node_neigbors_dic[index2] = [index1]
        else:
            node_neigbors_dic[index2].append(index1)
    # for j in range(len(edges1)):
    # edgeNum[int(edges1[j][0])][int(edges1[j][1])] = j
    return A, edgeNum,node_neigbors_dic


A, edgeNum ,node_neigbors_dic= adjacency_matrix()
DegreeMatrix = []  # 度矩阵
for i in A:
    degreeList = [1 for j in i if j > 0]
    DegreeMatrix.append(sum(degreeList))

#改变邻接矩阵，除了感染end的节点start外其他节点的邻接矩阵值都设置为0
def change_matrix(new_node_neigbors_dic,end,start):
    end_neighbors=new_node_neigbors_dic[end]
    if start in end_neighbors:
        end_neighbors.remove(start)
    for neighbor in end_neighbors:
        if end in new_node_neigbors_dic[neighbor]:
            new_node_neigbors_dic[neighbor].remove(end)
    return new_node_neigbors_dic

# 选择度数较高的观测节点
def chooseHighDegreeObserves(com, observeNum):
    degreeDic = {}
    for node in com:
        degreeDic[node] = DegreeMatrix[node]
    sortedObsercesDegree = sorted(degreeDic.items(), key=lambda x: x[1], reverse=True)
    observes = [i[0] for i in sortedObsercesDegree]
    return observes[:observeNum]


# 选择度数较小的观测节点
def chooseLowDegreeObserves(com, observeNum):
    degreeDic = {}
    for node in com:
        degreeDic[node] = DegreeMatrix[node]
    sortedObsercesDegree = sorted(degreeDic.items(), key=lambda x: x[1])
    observes = [i[0] for i in sortedObsercesDegree]
    return observes[:observeNum]


def SI_diffusion(percentage, choose_observer_method):
    sourceNode = random.randrange(0, node_num)  # 随机生成一个源节点
    infected_arr = [sourceNode]  # 感染节点集合，初始的感染节点只有一个源节点处于感染状态，其他节点都是处于易感染状态
    ObserverNodeList = []  # 观测节点列表
    data = [data for data in Communitys if sourceNode in data]  # 计算源节点所在的分区，方便后面与估计出的分区做比较
    SourceNodeInCom = Communitys.index(data[0])  # 源节点所在的分区
    for com in Communitys:
        countObserver = int(len(com) * percentage)
        if countObserver < 1:
            countObserver = 2
        if choose_observer_method == 1:
            ObserverNodeList.append(random.sample(com, countObserver))
        elif choose_observer_method == 2:
            ObserverNodeList.append(chooseHighDegreeObserves(com, countObserver))
        elif choose_observer_method == 3:
            ObserverNodeList.append(chooseLowDegreeObserves(com, countObserver))
        else:
            ObserverNodeList.append(random.sample(com, countObserver))
    ObserveNodeDic = {}  # 观测节点字典列表  key:观测节点 value:对应的分区
    for i in range(len(ObserverNodeList)):
        for j in ObserverNodeList[i]:
            if (j != sourceNode):  # 假设选择的所有观测节点不是源节点
                ObserveNodeDic[j] = [i]
    infectTime = np.zeros(node_num)  # 网络中每个节点被感染的时间，为了方便计算观测节点的感染时间
    ObserverNum = len(ObserveNodeDic.keys())  # 观测节点的数量
    keys = list(ObserveNodeDic.keys())  # 所有的观测节点
    relObserveList = list(keys)
    count = 0
    active_records = []  # 记录每次迭代激活的节点及其感染时间[[[去感染的节点1，感染节点1，感染时间1],[去感染的节点2，感染节点2，感染时间2],[]],[第二次迭代],[]...]
    edge_records = []  # 记录激活边在edges1中的序号
    while (count < ObserverNum):  # 直到所有的观测节点都被感染停止信息扩散
        active_records.append([])
        edge_records.append([])
        for i in range(len(infected_arr)):
            for j in range(node_num):
                if count == ObserverNum:  # 如果所有的观测节点都感染了，此时停止信息扩散，因为我们只需要知道观测节点的信息就可以了
                    break
                if (A[infected_arr[i]][
                    j] > 0 and j not in infected_arr):  # 如果infected_arr[i]和j两个节点有边连接，并且infected_arr[i]的邻居j不在已感染列表中,邻接矩阵中的值表示时延
                    infectTime[j] = infectTime[infected_arr[i]] + A[infected_arr[i]][
                        j]  # 节点j的感染时间等于节点infected_arr[i]的感染时间加上路径ij的时延值
                    infected_arr.append(j)  # 将这个节点加入到感染节点集合中，下一个时刻可以传染为未感染的邻居节点
                    active_records[len(active_records) - 1].append(
                        [infected_arr[i], j, round(infectTime[j], 2)])  # 将感染的节点信息加入该次迭代的列表中
                    edge_records[len(edge_records) - 1].append(edgeNum[infected_arr[i]][j])  # 刚感染的边信息加入该次迭代的边列表中
                    if j in keys:  # 用来记录观测节点的感染信息
                        count += 1
                        ObserveNodeDic[j].extend([infected_arr[i], infectTime[j]])
                        keys.remove(j)  # 为了下次循环判断一个感染节点是否是观测节点的时候减少计算
    communityObservesInfectedTime = {}  # 每个社区观测节点的感染时间{社区id:[观测节点a感染时间，观测节点b感染时间...],社区id2：[]}
    comObserveNodeAndTime = {}
    for key, values in ObserveNodeDic.items():
        if (values[0] in communityObservesInfectedTime):
            communityObservesInfectedTime[values[0]].append(values[2])
            comObserveNodeAndTime[values[0]].append([key, values[2]])
        else:
            communityObservesInfectedTime[values[0]] = [values[2]]
            comObserveNodeAndTime[values[0]] = [[key, values[2]]]
    communityAvgInfectedTime = {}  # 每个社区的平均感染时间列表
    for key, values in communityObservesInfectedTime.items():  # 计算前一半节点观测感染时间的最小值
        communityAvgInfectedTime[key] = round(sum(values) / len(values), 2)  # 取平均
    sortedComInfectedTime = sorted(communityAvgInfectedTime.items(),
                                   key=lambda item: item[1])  # 对每个社区的平均感染时间进行升序排序[(0, 3.04), (5, 3.53)...]
    candidateCommunity = []  # 候选源节点所在的分区
    candidateCommunityObserveInfectedNode = []  # 候选分区内观测节点及其感染时间列表
    AllCandidateObserveNode = []
    ALLCandidatSourceNode = []
    CommunitiesList = []  # 候选社区[社区1，社区2，社区3，社区4]
    for i in range(len(Communitys)):
        canCom = sortedComInfectedTime[i][0]  # 每一个候选分区
        CommunitiesList.append(canCom)
        candidateCommunity.append(Communitys[canCom])
        candidateCommunityObserveInfectedNode.append(comObserveNodeAndTime[canCom])
        AllCandidateObserveNode.extend(comObserveNodeAndTime[canCom])
        # 对于前四个分区，每个分区选择感染时间较早的一半的观测节点
        ALLCandidatSourceNode.extend(Communitys[canCom])
    return candidateCommunity, candidateCommunityObserveInfectedNode, ALLCandidatSourceNode, AllCandidateObserveNode, sourceNode, \
           CommunitiesList, SourceNodeInCom, relObserveList, active_records, edge_records


#BFS 广度优先搜索   层序遍历
def BFS(s):#graph图  s指的是开始结点
    #需要一个队列
    queue=[]
    queue.append(s)
    seen=set()#看是否访问过该结点
    seen.add(s)
    BFSTree={}
    index=0
    t=1
    while (len(queue)>0):
        size=len(queue)
        for i in range(size):
            vertex=queue.pop(0)#保存第一结点，并弹出，方便把他下面的子节点接入
            BFSTree[vertex] = index
            #nodes=graph[vertex]#子节点的数组
            nodes=node_neigbors_dic[vertex]
            for w in nodes:
                if w not in seen:#判断是否访问过，使用一个数组
                    t+=1
                    queue.append(w)
                    seen.add(w)
        index+=1
    return BFSTree

def GM(Community,ObserverInfectedList):
    Observes=[a[0] for a in ObserverInfectedList]# 所有的观测节点按照时间升序排列
    Community=list(set(Community).difference(set(Observes)))
    ReferenceNodeInfor = ObserverInfectedList[0]
    d = []  # [[节点id,相对于第一个观测节点的时延],[],[],....] 观测节点对应时延列表
    observeInfTimeDelayList = []  # 所有感染的观测节点（除了第一个参考节点）相对于第一个参考节点的时延
    for observeIndex in range(1, len(ObserverInfectedList)):
        d.append([])
        timeDelay = ObserverInfectedList[observeIndex][1] - ReferenceNodeInfor[1]
        d[len(d) - 1].extend([ObserverInfectedList[observeIndex][0], timeDelay])
        observeInfTimeDelayList.append(timeDelay)
    maxValue = -100
    PreSource = 0
    varianceMatrix = CalvarianceMatrix(ReferenceNodeInfor[0], d)  # 方差矩阵
    for AssumedSource in Community:#候选源节点集合中每个节点为源时计算最大似然函数
        BFSTree = BFS(AssumedSource)
        u=ShortestPathLength(AssumedSource,ReferenceNodeInfor[0],d,BFSTree)#假设的源节点，参考的源节点，真实的时延向量（目前是为了计算观测节点） 得到理论的时间延迟
        if type(u)!=list:
            continue
        bb = list(map(lambda x, y: x - y, observeInfTimeDelayList, 0.5*np.array(u)))
        ans = np.dot(np.dot(u, np.linalg.inv(np.array(varianceMatrix))), np.transpose([bb]))
        if(ans>maxValue):
            maxValue=ans
            PreSource=AssumedSource
    return PreSource,maxValue

def calShortestPath(ALLCandidatSourceNode, AllCandidateObserveNode):
    Observes = [a[0] for a in AllCandidateObserveNode]  # 所有的观测节点按照时间升序排列
    ALLCandidatSourceNode = list(set(ALLCandidatSourceNode).difference(set(Observes)))
    Paths={}
    for candidateSource in ALLCandidatSourceNode:
        Paths[candidateSource]={}
        for observe in AllCandidateObserveNode:
            Paths[candidateSource][observe[0]]=nx.shortest_path_length(G,candidateSource,observe[0])
    return Paths





#计算观测节点集合和源节点的最短路径长度[长度1，长度2....]
def cal_shortest_path_length_list(source,Observes,BFSTree):
    shortest_path_length_list=[]
    for observe in Observes:
        if nx.has_path(G,source,observe):
            #shortest_path_length_list.append(nx.shortest_path_length(G,source,observe))
            #shortest_path_length_list.append(Paths[source][observe])
            shortest_path_length_list.append(abs(BFSTree[source]-BFSTree[observe]))
        else:
            print("99999")
            return 999
    return shortest_path_length_list

def ShortestPathLength(Source, ReferenceNode, d,BFSTree):
    ObserveList=[]
    ObserveList.append(ReferenceNode)
    for i in d:
        ObserveList.append(i[0])
    ObserversPathLength=cal_shortest_path_length_list(Source,ObserveList,BFSTree)
    if type(ObserversPathLength)==list:
        ObserveNodeShortestPathLengthList = []# 除了参考节点以外的节点到源节点的最短路径列表
        for i in range(1,len(ObserveList)):
            ObserveNodeShortestPathLengthList.append(mean * (ObserversPathLength[i] - ObserversPathLength[0]))
        return ObserveNodeShortestPathLengthList  # 返回其他观测节点相对于第一个观测节点的理论时延列表[[观测节点1，理论时延],[]...]
    else:
        return ObserversPathLength

# 计算两个路径相交的边的个数
def calIntersectEdge1(edgeList1, edgeList2):
    edges1 = []
    edges2 = []
    for i in range(len(edgeList1) - 1):
        if edgeList1[i] < edgeList1[i + 1]:
            edges1.append([edgeList1[i], edgeList1[i + 1]])
        else:
            edges1.append([edgeList1[i + 1], edgeList1[i]])
    for j in range(len(edgeList2) - 1):
        if edgeList2[j] < edgeList2[j + 1]:
            edges2.append([edgeList2[j], edgeList2[j + 1]])
        else:
            edges2.append([edgeList2[j + 1], edgeList2[j]])
    count = 0
    for edge in edges1:
        if edge in edges2:
            count += 1
    return count*variance

# 方差矩阵
def CalvarianceMatrix(ObserveOne, d):
    # 最短的路径[0,10,2]表示路径长度为2，包括0-10 10-2这两条边，字典的key表示节点id，value表示边的集合
    observe_num = len(d)  # 观测节点的数量
    varianceMatrix = np.zeros([observe_num, observe_num])  # 方差矩阵
    # 判断是否有交边
    for i in range(observe_num):
        for j in range(observe_num):
            if i >= j:  # 矩阵是对角矩阵，只需要计算一半就可以了
                shortestPathList1 = nx.shortest_path(G,ObserveOne,d[i][0])
                shortestPathList2 = nx.shortest_path(G,ObserveOne,d[j][0])
                varianceMatrix[i][j] = varianceMatrix[j][i] = calIntersectEdge1(shortestPathList1, shortestPathList2)
    return varianceMatrix



# 输入candidateCommunity 候选分区，candidateCommunityObserveInfectedNode：候选分区的节点感染时间
def sourceDetection(candidateCommunity, candidateCommunityObserveInfectedNode):
    preScore = -100
    preSource = -1
    candidateSourceList = []  # 四个社区的候选源节点
    for i in range(len(candidateCommunity)):
        candidateSource, maxValue = GM(candidateCommunity[i], candidateCommunityObserveInfectedNode[i])  # 计算每个社区最可能的源
        candidateSourceList.append(candidateSource)
        if maxValue > preScore:
            preScore = maxValue
            preSource = candidateSource
    return preSource, candidateSourceList
