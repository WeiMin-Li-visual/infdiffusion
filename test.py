#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2020/10/30 14:26
# @Author  : 邓志斌
# @Email   : 1830601430@qq.com
# @File    : test.py
# @Software: PyCharm
import json

a=[]

a.append([1,2,3,34])
a.append([3,4,5])
a=json.dumps(a)
print(a)