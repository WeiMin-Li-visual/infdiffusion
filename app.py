# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, flash
import json
import random
import copy
from flask_socketio import SocketIO
from threading import Lock

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
