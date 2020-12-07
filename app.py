# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from threading import Lock
from algorithm import gameTheory
from algorithm import sourceDetection as sd
from algorithm import SIModel as si
from algorithm import SIRModel as sir
import pandas as pd
import json
import random
import copy
import networkx as nx
from flask_socketio import SocketIO
from threading import Lock
from flask_mail import Mail, Message
import pymysql
import requests
import os
import io
import datetime
import re

thread_lock = Lock()

async_mode = None
thread = None
app = Flask(__name__)
app.secret_key = 'dzb'
socketio = SocketIO(app, async_mode=async_mode)
# 连接数据库
connection = pymysql.connect(host='localhost', user='root', password='root', db='po_evolution_platform')

# 得到一个可以执行SQL语句的光标对象
cur = connection.cursor()  # 执行完毕返回的结果集默认以元组显示
cur.execute('use po_evolution_platform')  # 执行SQL语句

# 配置Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.qq.com'  # 邮箱服务器
app.config['MAIL_PORT'] = 587  # 端口
app.config['MAIL_USE_TLS'] = True  # 是否使用TLS
app.config['MAIL_USERNAME'] = '1830601430@qq.com'  # 邮箱
app.config['MAIL_PASSWORD'] = 'xxnglsfenzxsehgi'  # 授权码
mail = Mail(app)


# 检测用户名是否存在
@app.route('/checkUser', methods=["POST"])
def checkUser():
    if request.method == 'POST':
        cur.execute('use po_evolution_platform')
        requestArgs = request.values
        user = requestArgs.get('user')
        cur.execute("select * from users where user = " + "'" + user + "'")
        result = cur.fetchone()  # 获取查询结果
        if result is None:
            return jsonify({'isExist': False})
        elif result is not None:
            return jsonify({'isExist': True})


# 检测邮箱是否和账号相对应
@app.route('/checkMail', methods=["POST"])
def checkMail():
    if request.method == 'POST':
        cur.execute('use po_evolution_platform')
        requestArgs = request.values
        user = requestArgs.get('user')
        mail = requestArgs.get('mail')
        cur.execute("select mail from users where user = " + "'" + user + "'")
        result = cur.fetchone()  # 获取查询结果
        if result is not None and mail == result[0]:
            return jsonify({'isExist': True})
        return jsonify({'isExist': False})


# 修改密码
@app.route('/forget', methods=["GET", "POST"])
def forget():
    if request.method == 'GET':
        return render_template('forget.html')
    elif request.method == 'POST':
        requestArgs = request.values
        new = requestArgs.get('password')
        user = requestArgs.get('user')
        cur.execute("update users set password=MD5('" + new + "') where user='" + user + "'")
        connection.commit()
        return jsonify({'isSuccess': 1})


# 注册账号
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        requestArgs = request.values
        user = requestArgs.get('user')
        password = requestArgs.get('password')
        number = requestArgs.get('number')
        unit = requestArgs.get('unit')
        mail = requestArgs.get('mail')
        role = '1'  # 默认普通用户
        str1 = "'" + user + "'" + ",'" + number + "'," + "'" + mail + "'" + "," \
               + "'" + unit + "'" + "," + "MD5('" + password + "')" + ",1"
        cur.execute('insert into users (user,number,mail,unit,password,role_id) values (' + str1 + ")")
        connection.commit()
        return jsonify({'isSuccess': 1})


# 通过邮件发送验证码
@app.route('/send', methods=["POST"])
def send():
    requestArgs = request.form
    user = requestArgs.get('user')
    dirMail = requestArgs.get('mail')
    verificationList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                        'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 's', 't', 'x', 'y', 'z', 'A', 'B', 'C', 'D',
                        'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'S', 'T', 'X', 'Y', 'Z']

    veriCode = ''
    for i in range(4):
        veriCode += verificationList[random.randint(0, len(verificationList) - 1)]
    msg = Message(subject="舆情演化平台验证码", sender="1830601430@qq.com", recipients=[dirMail])
    msg.body = "你好，" + user + ":\n" + "感谢你使用我们的社交网络舆情演化与分析平台" + "\n" + "你的验证码是：\n" + veriCode  # 验证码主体
    mail.send(msg)  # 发送邮件
    return jsonify({'code': veriCode, 'ischecked': 1})


# 登录界面，最后发布将其调整为主界面
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        cur.execute('use po_evolution_platform')
        return render_template('login.html')
    elif request.method == 'POST':
        requestArgs = request.values
        user = requestArgs.get('user')
        password = requestArgs.get('password')

        # if user==None and password==None:
        #     check['usps'] = -1
        #     return jsonify({'check': check})
        cur.execute("select * from users where user = " + "'" + user + "'")
        result = cur.fetchone()  # 没找到为None, 否则返回对应的元组
        cur.execute("select md5('" + password + "')")
        p = cur.fetchone()  # 返回的是三元组，p[0]是需要的值
        check = {'userInfo': -1, 'passwordInfo': -1}
        if result is None:
            check['userInfo'] = -1
        elif result is not None:
            check['userInfo'] = 0
            if p[0] == result[1]:
                check['passwordInfo'] = 1
            elif p[0] != result[1]:
                check['passwordInfo'] = 0
        check = json.dumps(check)
        return jsonify({'check': check})


@app.route('/fun', methods=["POST"])
def fun():
    requestArgs = request.values
    user = requestArgs.get('user')
    cur.execute("select * from users where user = " + "'" + user + "'")
    result = cur.fetchone()
    return jsonify({'user': result})


# 注销账号
@app.route('/deleteUserInfo', methods=["GET", "POST"])
def deleteUserInfo():
    if request.method == 'GET':
        return render_template('deleteUserInfo.html')
    elif request.method == 'POST':
        requestArgs = request.values
        user = requestArgs.get('user')
        cur.execute("select user from users where user = " + "'" + user + "'")
        result = cur.fetchone()
        print(result)
        if result is not None:
            cur.execute("delete from users where user = " + "'" + user + "'")
            connection.commit()
            return jsonify({'isSuccess': 1})
        return jsonify({'isSuccess': 0})


# 获得session
@app.route('/getSessionUser', methods=["GET", "POST"])
def getSessionUser():
    user = request.cookies['user']
    cur.execute("select * from users where user = " + "'" + user + "'")
    result = cur.fetchone()

    number = "xxx"
    mail = "xxx"
    unit = "xxx"

    if result[2] != '':
        number = result[2]
    if result[3] != '':
        mail = result[3]
    if result[4] != '':
        unit = result[4]

    if result is not None:
        return jsonify({'user': user, 'number': number, 'mail': mail, 'unit': unit, 'isSuccess': 1})
    return jsonify({'isSuccess': 0})


# 主界面
@app.route('/index')
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


# 检测网络结构名是否存在
@app.route('/checkNetworkName', methods=["POST"])
def checkNetworkName():
    if request.method == 'POST':
        cur.execute('use po_evolution_platform')
        requestArgs = request.values
        dataname = requestArgs.get('textfield')
        user = request.cookies['user']
        cur.execute("select dataname from datas where user = " + "'" + user + "'")
        result = cur.fetchone()  # 获取查询结果
        if result is not None and dataname in result:
            return jsonify({'isExist': True})

        cur.execute("select dataname from datas where role_id = 2")
        result = cur.fetchone()
        if result is not None and dataname in result:
            return jsonify({'isExist': True})
        return jsonify({'isExist': False})


# 用户可以自己添加网络
@app.route('/addNetwork', methods=["GET", "POST"])
def addNetwork():
    err = "false"
    if request.method == 'GET':
        err = "true"
        cur.execute('use po_evolution_platform')
        return render_template('addNetwork.html', err=err)
    elif request.method == 'POST':
        base_path = os.path.dirname(os.path.realpath(__file__)) + "\static\data"
        upload_path = os.path.join(base_path, 'upload')  # 上传文件目录
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        """处理上传文件"""
        filedata = request.files.get('fileField')
        filename = request.values.get('textfield')

        if filename == '':
            err = "请选择文件!"
        elif filename[-4:] != '.txt':
            err = "文件不符合格式！"
        else:
            file_path = None

            flag=0
            cur.execute('use po_evolution_platform')
            dataname = filename.split("\\")[-1].split(".")[0]
            user = request.cookies['user']
            cur.execute("select dataname from datas where user = " + "'" + user + "'")
            result = cur.fetchone()
            if result is not None and dataname in result:
                flag=1
                err = "网络结构已存在"

            cur.execute("select dataname from datas where role_id = 2")
            result = cur.fetchone()
            if result is not None and dataname in result:
                flag=1
                err = "网络结构已存在"

            if flag==0:
                try:
                    time = str(datetime.datetime.now())
                    time = time.replace(' ', '_').replace('-', '_').replace(':', '_').replace('.', '_') + '.txt'
                    file_path = os.path.join(upload_path, time)
                    filedata = str(filedata.read())
                    print(filedata)
                    file = filedata[2:-2].replace("\\t", ",").replace("\\r", "").split("\\n")
                    with open(file_path, 'w') as writef:
                        for row in file:
                            row = row.strip("'").split(",")
                            temp = []

                            # \d+ 匹配字符串中的数字部分，返回列表
                            num1 = re.findall('\d+', row[0])
                            num2 = re.findall('\d+', row[0])
                            if (len(num1) != 1 or len(num2) != 1):
                                err = "文件不符合格式！"
                                break
                            temp.append(num1[0])
                            temp.append(num2[0])
                            writef.write("\t".join(temp))
                            writef.write("\n")

                    if (err == "文件不符合格式！"):
                        os.remove(file_path)
                except IOError:
                    err = "上传失败！"
                err = "上传成功！"

            if err == "上传成功！":
                dataname = filename.split("\\")[-1].split(".")[0]
                user = request.cookies['user']
                cur.execute("select role_id from users where user = " + "'" + user + "'")
                result = cur.fetchone()
                str1 = "'" + dataname + "'" + ",'" + user + "'," + "'" + file_path + "'" + "," \
                       + "'" + str(result[0]) + "'"
                cur.execute('insert into datas (dataname,user,data_path,role_id) values (' + str1 + ")")
                connection.commit()

    return render_template('addNetwork.html', err=err)


# 舆情演化
@app.route('/poEvolution')
def poEvolution():
    '''
    TODO
    :return:
    '''
    data = [1, 2, 3, 4, 5]
    return render_template('poEvolution.html', data=data)


# 介绍SI
@app.route('/introduceSI')
def introduceSI():
    '''
    TODO
    :return:
    '''
    return render_template('introduceSI.html')


# SI模型扩散
@app.route('/SI', methods=["GET", "POST"])
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
    Susceptible = nodeset  # 易感者集合
    Infected = []  # 感染者集合
    edge = []  # 边
    times = []  # 保存经历了多少时间步

    sus_node = []  # 保存每一时间步易感者节点集合
    inf_node = []  # 保存每一时间步感染者节点集合
    edges_record = []  # 保存边
    sus_node_num = []  # 保存每一时间步易感节点数量
    inf_node_num = []  # 保存每一时间步感染节点数量

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
        return render_template('SI.html', graph_data=si.graph_data, susceptible_nodes=sus_node,
                               sus_node_num=sus_node_num,
                               infected_nodes=inf_node, edges_record=edges_record, inf_node_num=inf_node_num,
                               times=times, err=err, rateSI=rateSI, method_type=1)
    if request.method == "POST":
        rateSI = request.form.get('rateSI')
        if rateSI != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(rateSI):
                err = "输入不合法，请输入0-1区间的值"
            elif float(rateSI) < 0 or float(rateSI) > 1:
                err = "输入错误，请输入0-1区间的值"
        elif rateSI == "":
            err = "请输入感染率"
    if err != "false":
        return render_template('SI.html', graph_data=si.graph_data, susceptible_nodes=json.dumps([]),
                               infected_nodes=json.dumps([]), edges_record=json.dumps([]),
                               sus_node_num=sus_node_num, inf_node_num=inf_node_num,
                               times=times, err=err, rateSI=0, method_type=1)

    while len(Susceptible) != 0:
        sus_node.append(copy.deepcopy(Susceptible))
        inf_node.append(copy.deepcopy(Infected))
        edges_record.append(copy.deepcopy(edge))

        sus_node_num.append(len(Susceptible))
        inf_node_num.append(len(Infected))
        t = t + 1
        # print(type(rateSI))
        Susceptible, Infected, edge = si.SIsimulation(float(rateSI), Susceptible, Infected)
        # print(t, ":Susceptible:", Susceptible, len(Susceptible))
        # print(t, ":Infected:", Infected, len(Infected))
        # print(t, "edge", edge, len(edge))
    sus_node.append(copy.deepcopy(Susceptible))
    inf_node.append(copy.deepcopy(Infected))
    edges_record.append(copy.deepcopy(edge))

    sus_node_num.append(len(Susceptible))
    inf_node_num.append(len(Infected))

    for i in range(1, t + 2):
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
    return render_template('SI.html', graph_data=graph_data1, susceptible_nodes=sus_node, infected_nodes=inf_node,
                           edges_record=edges_record, sus_node_num=sus_node_num, inf_node_num=inf_node_num,
                           times=times, err=err, rateSI=rateSI, method_type=1)


# 介绍SIR
@app.route('/introduceSIR')
def introduceSIR():
    '''
    TODO
    :return:
    '''
    return render_template('introduceSIR.html')


# SIR模型扩散
@app.route('/SIR', methods=["GET", "POST"])
def SIR():
    '''
    TODO
    :return:
    '''

    graph_data1 = json.loads(sir.graph_data)  # 将json数据转化为字典的形式
    nodeset, num_node = sir.CalculateNodesnum()
    Susceptible = nodeset  # 易感者集合
    Infected = []  # 感染者集合
    Resistant = []  # 恢复者集合
    edge = []  # 边
    times = []  # 保存经历了多少时间步

    sus_node = []  # 保存每一时间步易感节点集合
    inf_node = []  # 保存每一时间步感染节点集合
    res_node = []  # 保存每一时间步恢复节点集合
    edges_record = []  # 保存边

    sus_node_num = []  # 保存每一时间步易感节点数量
    inf_node_num = []  # 保存每一时间步感染节点数量
    res_node_num = []  # 保存每一时间步恢复节点的数量

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
                               sus_node_num=sus_node_num, inf_node_num=inf_node_num, res_node_num=res_node_num,
                               times=times, err=err, rateIR=rateIR, rateSI=rateSI, method_type=1)
    if request.method == "POST":
        rateSI = request.form.get('rateSI')
        rateIR = request.form.get('rateIR')
        if rateSI != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(rateSI):
                err = "输入不合法，请输入0-1区间的值"
            elif float(rateSI) < 0 or float(rateSI) > 1:
                err = "输入错误，请输入0-1区间的值"
        elif rateSI == "":
            err = "请输入感染率"
        if rateIR != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(rateIR):
                err = "输入不合法，请输入0-1区间的值"
            elif float(rateIR) < 0.05 or float(rateIR) > 0.9:
                err = "输入错误，请输入0-1区间的值"
        elif rateIR == "":
            err = "请输入恢复率"

        if (rateIR == "" and rateSI == ""):
            err = "请输入感染率和恢复率"
    if err != "false":
        return render_template('SIR.html', graph_data=sir.graph_data, susceptible_nodes=json.dumps([]),
                               infected_nodes=json.dumps([]), resistant_nodes=json.dumps([]),
                               edges_record=json.dumps([]),
                               sus_node_num=sus_node_num, inf_node_num=inf_node_num, res_node_num=res_node_num,
                               times=times, err=err, rateIR=0, rateSI=0, method_type=1)

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
        Susceptible, Infected, Resistant, edge = sir.SIRsimulation(float(rateSI), float(rateIR), Susceptible, Infected,
                                                                   Resistant)
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

    for i in range(1, t + 2):
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
                           sus_node_num=sus_node_num, inf_node_num=inf_node_num, res_node_num=res_node_num,
                           times=times, err=err, rateIR=rateIR, rateSI=rateSI, method_type=1)


# 谣言溯源： 刘艳霞
@app.route('/sourceDetection', methods=["GET", "POST"])
def SourceDetection():
    node_in_Community = sd.node_in_Community  # 每个节点所在的分区
    err = "false"  # 返回错误信息
    if request.method == "GET":
        # 初始化权重矩阵
        err = "true"
        active_records = json.dumps([])
        ObserverNodeList = []
        edge_records = json.dumps([])
        return render_template('sourceDetection.html', graph_data=sd.graph_data,
                               ObserverNodeList=ObserverNodeList, active_records=active_records,
                               edge_records=edge_records,
                               shortestPath=[], err=err, node_in_Community=node_in_Community)
    else:  # request：请求对象，获取请求方式数据
        percentage = request.form.get('percentage')  # 观测点数量
        iteration = request.form.get('iteration')  # 迭代次数
        method = request.form.get('method')  # 选择观测点方法
        # mean=request.form.get('mean')#时延均值
        # variance=request.form.get('variance')#时延方差
        if percentage != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(percentage):
                err = "输入不合法，请输入0.05-0.9之间的数字"
            elif float(percentage) < 0.05 or float(percentage) > 0.9:
                err = "输入错误，请输入0.05-0.9之间的数字"
        elif percentage == "":
            err = "输入为空，请输入观测比例"
        if iteration == "":
            err = "输入为空，请输入迭代次数"
        else:
            if iteration.isdigit() == False:
                err = "输入不合法，请输入一个整数"
            elif int(iteration) < 1 or int(iteration) > 10000:
                err = "迭代次数最少为1，请输入大于1的整数"
    if err != "false":
        return render_template('sourceDetection.html', graph_data=sd.graph_data,
                               ObserverNodeList=[], active_records=json.dumps([]), edge_records=json.dumps([]),
                               shortestPath=[], err=err, node_in_Community=node_in_Community)
    count = 0  # 准确定位到源的次数
    errorDistance = [0 for index in range(5)]  # 存放每一跳的误差比例
    all_iteration_dis = []  # [[真实的源，预测的源，第一次迭代误差距离]，第二次迭代预测源与真实源的误差距离，.....,误差列表，所有迭代中的准确率]
    distance = 0
    mean_error_distance = 0  # 平均误差距离
    shortestPath = []  # [[[6(reverse_source), 35(reverse_target), 98.0(边编号）]], [[2, 5, 33.0], [5, 6, 75.0], [6, 35, 98.0]], 记录每个最短路径
    shortestPath1 = []  # 最短路径列表[[a,b,c],[c,f,g,e]....]
    active_records1 = []
    edge_records1 = []
    ObserverNodeList1 = []
    for i in range(int(iteration)):
        candidateCommunity, candidateCommunityObserveInfectedNode, ALLCandidatSourceNode, AllCandidateObserveNode, relSource, CommunitiesList, \
        SourceNodeInCom, ObserverNodeList, active_records, edge_records = sd.SI_diffusion(float(percentage),
                                                                                          int(method))
        preSource, maxValue = sd.GM(ALLCandidatSourceNode, AllCandidateObserveNode)
        if (preSource == relSource):
            count += 1
            errorDistance[0] += 1
            distance = 0
        else:
            distance = nx.shortest_path_length(sd.G, preSource, relSource)
            errorDistance[distance] += 1
        all_iteration_dis.append([relSource, preSource, distance])
        if i == 0:
            ObserverNodeList1 = ObserverNodeList
            print("edge_records", edge_records)
            active_records1 = json.dumps(active_records)
            edge_records1 = json.dumps(edge_records)
            for i in ObserverNodeList1:
                shortestPath1.append(nx.shortest_path(sd.G, i, relSource))
            for paths in shortestPath1:
                shortestPath.append([])
                for i in range(len(paths) - 1):
                    shortestPath[len(shortestPath) - 1].append(
                        [paths[i], paths[i + 1], sd.edgeNum[paths[i]][paths[i + 1]]])
    for j in range(len(errorDistance)):
        mean_error_distance += errorDistance[j] * j
        errorDistance[j] = round(errorDistance[j] / int(iteration), 2)  # 误差在各跳数的比例
    mean_error_distance = round(mean_error_distance / int(iteration), 2)  # 平均误差距离
    errorDistance = [e for e in errorDistance if e > 0]
    all_iteration_dis.extend(
        [errorDistance, round(count / int(iteration), 2), mean_error_distance])  # 误差列表，定位准确率，平均误差距离
    return render_template('sourceDetection.html', graph_data=sd.graph_data,
                           ObserverNodeList=ObserverNodeList1,
                           active_records=active_records1, edge_records=edge_records1,
                           shortestPath=shortestPath, err=err, all_iteration_dis=all_iteration_dis,
                           node_in_Community=node_in_Community)


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
@app.route('/GameTheory', methods=["GET", "POST"])
def gametheory():
    steps = 10
    graph_data = None
    uncertainty = None
    proportion = None
    node_num = 0
    G = None
    edgeNum = None
    nodes = None
    network_path = None
    method = None
    index = 0

    err = "false"
    if request.method == "GET":
        err = "true"

    else:  # request：请求对象，获取请求方式数据
        proportion = request.form.get('proportion')
        uncertainty = request.form.get('uncertainty')  # 不确定性因子的大小
        network_path = request.form.get("network")
        method = request.form.get("method")

        path = None
        if network_path == "wiki":
            path = "static/data/Wiki.txt"
        elif network_path == "synfix":
            path = "static/data/synfix_3.t01.edges"
        elif network_path == "BA无标度":
            path = "static/data/BA.txt"
        elif network_path == "ER":
            path = "static/data/ER.txt"

        ways = 0  # 默认协调博弈
        if method == "协调博弈":
            ways = 0

        if proportion != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(proportion):
                err = "输入不合法，请输入0-1之间的数字"
            elif float(proportion) <= 0:
                err = "输入错误，请输入大于0的数字"
            elif float(proportion) > 1:
                err = "输入错误，请输入0-1之间的数字"
        elif proportion == "":
            err = "输入为空，请输入活跃用户比例"

        if uncertainty != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(uncertainty):
                err = "输入不合法，请输入大于0的数字"
            elif float(uncertainty) < 0:
                err = "输入错误，请输入大于0的数字"
        elif uncertainty == "":
            err = "输入为空，请输入不确定因子的大小"

        proportion = float(proportion)
        uncertainty = float(uncertainty)
        gt = gameTheory.GameTheory(path, steps, proportion, uncertainty)
        gt.init_network()
        gt.active_node()
        gt.diffuse()
        index = min(gt.nodes)

        return render_template('GameTheory.html', graph_data=gt.graph_data, step_active_node=gt.step_active_node,
                               step_active_node_sum=gt.step_active_node_sum, err=err, proportion=proportion,
                               uncertainty=uncertainty, network_path=network_path, method=method, index=index)

    if err != "false":
        step_active_node = [[]]
        step_active_node_sum = []
        return render_template('GameTheory.html', graph_data=graph_data, step_active_node=step_active_node,
                               step_active_node_sum=step_active_node_sum, err=err, proportion=proportion,
                               uncertainty=uncertainty, network_path=network_path, method=method, index=index)


# 基于博弈论的行为扩散对比
@app.route('/gametheory_comparison', methods=["GET", "POST"])
def gametheory_comparison():
    steps = 10
    uncertainty1 = None
    proportion1 = None
    uncertainty2 = None
    proportion2 = None

    path = "static/data/Wiki.txt"
    gt = gameTheory.GameTheory(path, steps)
    gt.init_network()
    index = min(gt.nodes)

    err1 = "false"
    err2 = "false"
    if request.method == "GET":
        err1 = "true"
        err2 = "true"

        step_active_node1 = [[]]
        step_active_node_sum1 = []
        step_active_node2 = [[]]
        step_active_node_sum2 = []
        return render_template('gametheory_comparison.html', graph_data=gt.graph_data,
                               step_active_node1=step_active_node1, step_active_node2=step_active_node2,
                               step_active_node_sum1=step_active_node_sum1, step_active_node_sum2=step_active_node_sum2,
                               err1=err1, err2=err2, proportion1=proportion1, proportion2=proportion2,
                               uncertainty1=uncertainty1, uncertainty2=uncertainty2, index=index)

    else:
        proportion1 = request.form.get('proportion1')
        uncertainty1 = request.form.get('uncertainty1')
        proportion2 = request.form.get('proportion2')
        uncertainty2 = request.form.get('uncertainty2')

        if proportion1 != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(proportion1):
                err1 = "输入不合法，请输入0-1之间的数字"
            elif float(proportion1) <= 0:
                err1 = "输入错误，请输入大于0的数字"
            elif float(proportion1) > 1:
                err1 = "输入错误，请输入0-1之间的数字"
        elif proportion1 == "":
            err1 = "输入为空，请输入活跃用户比例"

        if uncertainty1 != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(uncertainty1):
                err1 = "输入不合法，请输入大于0的数字"
            elif float(uncertainty1) < 0:
                err1 = "输入错误，请输入大于0的数字"
        elif uncertainty1 == "":
            err1 = "输入为空，请输入不确定因子的大小"

        if proportion2 != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(proportion2):
                err2 = "输入不合法，请输入0-1之间的数字"
            elif float(proportion2) <= 0:
                err2 = "输入错误，请输入大于0的数字"
            elif float(proportion2) > 1:
                err2 = "输入错误，请输入0-1之间的数字"
        elif proportion2 == "":
            err2 = "输入为空，请输入活跃用户比例"

        if uncertainty2 != "":
            if not re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(uncertainty2):
                err2 = "输入不合法，请输入大于0的数字"
            elif float(uncertainty2) < 0:
                err2 = "输入错误，请输入大于0的数字"
        elif uncertainty2 == "":
            err2 = "输入为空，请输入不确定因子的大小"

        uncertainty1 = float(uncertainty1)
        proportion1 = float(proportion1)
        uncertainty2 = float(uncertainty2)
        proportion2 = float(proportion2)

        # step_active_node1 = []
        # step_active_node_sum1 = []
        # step_active_node2 = []
        # step_active_node_sum2 = []

        gt1 = gameTheory.GameTheory(path, steps, proportion1, uncertainty1)
        gt1.init_network()
        gt1.active_node()
        gt1.diffuse()

        gt2 = gameTheory.GameTheory(path, steps, proportion2, uncertainty2)
        gt2.init_network()
        gt2.active_node()
        gt2.diffuse()

        return render_template('gametheory_comparison.html', graph_data=gt.graph_data,
                               step_active_node1=gt1.step_active_node, step_active_node2=gt2.step_active_node,
                               step_active_node_sum1=gt1.step_active_node_sum,
                               step_active_node_sum2=gt2.step_active_node_sum,
                               err1=err1, err2=err2, proportion1=proportion1, proportion2=proportion2,
                               uncertainty1=uncertainty1, uncertainty2=uncertainty2, index=index)


# # 前后端通信（参见：https://blog.csdn.net/weixin_36380516/article/details/80418354）
# class GameTheory_thread(object):
#     pass
#
#
# @socketio.on('connect', namespace='/GameTheory')
# def GameTheory_connect():
#     thread = socketio.start_background_task(target=gametheory)

if __name__ == '__main__':
    socketio.run(app, debug=True)
