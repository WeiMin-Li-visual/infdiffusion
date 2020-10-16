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

@app.route('/')
def hello_world():
    return render_template('index.html')


# SI模型
@app.route('/SI')
def SI():
    '''
    TODO
    :return:
    '''
    return render_template('SI.html')

# SIC模型
@app.route('/SIR')
def SIR():
    '''
    TODO
    :return:
    '''
    return render_template('SIR.html')

# 舆情演化分析
@app.route('/yuqing')
def yuqing():
    '''
    TODO
    :return:
    '''
    return render_template('yuqing.html')

# 前后端通信
@socketio.on('connect', namespace='/SI')
def test_connect():
    thread = socketio.start_background_task(target=SI)

if __name__ == '__main__':
    socketio.run(app, debug=True)

