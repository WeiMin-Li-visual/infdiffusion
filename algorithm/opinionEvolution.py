#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 23:39
# @Author  : 王婕、刘芳宇
# @Email   : 523566462@qq.com、905805357@qq.com
# @File    : opinionEvolution.py
# @Software: PyCharm
# !/usr/bin/env python3
import pandas as pd
import datetime
import time
import json
# 标题字典表(静态)
MicroBlogTitleTable = {'1': '万众一心抗击疫情微博评论', '2': '嫦娥五号探月任务微博评论',
                       '3': '直击2020美国大选微博评论', '4': '丁真直播带你游理塘微博评论',
                       '5': '科比与女儿GiGi直升机坠机微博评论', '6': '罗志祥与周扬清分手事件微博评论'}
# 微博评论文件路径表(静态)
MicroBlogFilePathTable = {'1': 'static/data/MicroBlogComments/MicroBlogComments1.csv',
                          '2': 'static/data/MicroBlogComments/MicroBlogComments2.csv',
                          '3': 'static/data/MicroBlogComments/MicroBlogComments3.csv',
                          '4': 'static/data/MicroBlogComments/MicroBlogComments4.csv',
                          '5': 'static/data/MicroBlogComments/MicroBlogComments5.csv',
                          '6': 'static/data/MicroBlogComments/MicroBlogComments6.csv'}
#计算两个时间点相隔几周
def getweeks(date_str1, date_str2):
    compare_time1 = time.strptime(date_str1, "%Y-%m-%d")
    compare_time2 = time.strptime(date_str2, "%Y-%m-%d")
    # 比较日期
    date1 = datetime.datetime(compare_time1[0], compare_time1[1], compare_time1[2])
    date2 = datetime.datetime(compare_time2[0], compare_time2[1], compare_time2[2])
    diff_days = (date2 - date1).days
    return diff_days//7

#日期格式：2020-04-23 13:46:00
#根据时和日统计展示信息
#时间（年月日时和年月日）：评论量
#文件路径例子：data_path='static/data/MicroBlogComments/MicroBlogComments1.csv'
def countCommentVolume(data_path):
    # 时间（年月日时）：评论量
    commentsVolumeByHour = {}
    #时间（年月日）：评论量
    commentsVolumeByDay = {}
    # 时间（年月日时）：评论量
    sortCommentsVolumeByHour = {}
    # 时间（年月日）：评论量
    sortCommentsVolumeByDay = {}
    # 时间（周）：评论量
    sortCommentsVolumeByWeek = {}
    # 读取csv文件至列表
    comments_data=pd.read_csv(data_path).values
    #评论数组的维度
    [rows, cols] = comments_data.shape
    #遍历评论数组的行，即遍历评论
    for i in range(rows):
        # 获取时间（年月日时），通过切割日期字符串
        hour = comments_data[i][1][0:-6]
        #获取时间（年月日），通过切割日期字符串
        day = comments_data[i][1][0:-9]
        # 判断统计字典里面是否添加过该时间（年月日时），若不在添加该时间
        if (hour not in commentsVolumeByHour.keys()):
            commentsVolumeByHour[hour] = 0
        #判断统计字典里面是否添加过该时间（年月日），若不在添加该时间
        if(day not in commentsVolumeByDay.keys()):
            commentsVolumeByDay[day] = 0
        #统计量加一
        commentsVolumeByHour[hour] += 1
        #统计量加一
        commentsVolumeByDay[day] += 1
    # 给得到的评论统计量按时间（年月日时）排个序
    new_commentsVolume = sorted(commentsVolumeByHour.items(), key=lambda commentsVolume: commentsVolume[0])
    for i in range(len(new_commentsVolume)):
        sortCommentsVolumeByHour[new_commentsVolume[i][0]] = str(new_commentsVolume[i][1])
    # 给得到的评论统计量按时间（年月日）排个序
    new_commentsVolume=sorted(commentsVolumeByDay.items(), key=lambda commentsVolume:commentsVolume[0])
    for i in range(len(new_commentsVolume)):
        sortCommentsVolumeByDay[new_commentsVolume[i][0]] = str(new_commentsVolume[i][1])

    #下面开始计算评论周统计量
    #获取起始天例如：2020-04-23
    startDay=list(sortCommentsVolumeByDay.keys())[0]
    #startDay = min(sortCommentsVolumeByDay.keys(), key=(lambda x: x))
    # 遍历日评论量的统计字典（day:count)
    for key in sortCommentsVolumeByDay.keys():
        # 获取时间（周），通过计算第几天对应开始第几周，从1周开始计数
        weekNum=getweeks(startDay, key)+1
        week = '第' + str(weekNum) + '周'
        # 判断统计字典里面是否添加过该时间（第x周），若不在添加该时间
        if (week not in sortCommentsVolumeByWeek.keys()):
            sortCommentsVolumeByWeek[week] = '0'
        # 该周统计量=累和近7天的评论量
        sortCommentsVolumeByWeek[week] = str(int(sortCommentsVolumeByWeek[week]) + int(sortCommentsVolumeByDay[key]))
    return sortCommentsVolumeByHour, sortCommentsVolumeByDay, sortCommentsVolumeByWeek

#汇总统计展示信息(参数为微博类型序号，例：'1')
def calculateCommentVolume(categoryStr):
    #根据类型序号查最上面的表获取文件路径
    MicroBlogFilePath=MicroBlogFilePathTable[categoryStr]
    #根据类型序号查最上面的表获取微博标题
    title = {'MicroBlogTitle': '1'}#默认选中项
    title['MicroBlogTitle'] = MicroBlogTitleTable[categoryStr]#查表获取微博主题名
    MicroBlogTitle = json.dumps(title)#json.dumps封装
    #设置回传的微博类别，方便前端下拉框归档到上一次的选中
    #下拉框选择后用document.getElementById()将option.selected定为选中的值，要回传选中的下拉框value值opinionCategory
    category = {'MicroBlogCategory': '1'}  # 默认选中项
    category['MicroBlogCategory'] = categoryStr  # 回传上次选中的类别
    MicroBlogCategory = json.dumps(category)  # json.dumps封装
    #按时、日、周统计评论量
    sortCommentsVolumeByHour, sortCommentsVolumeByDay, sortCommentsVolumeByWeek = countCommentVolume(MicroBlogFilePath)
    #封装统计量
    commentsVolumeByHour = json.dumps(sortCommentsVolumeByHour)
    commentsVolumeByDay = json.dumps(sortCommentsVolumeByDay)
    commentsVolumeByWeek = json.dumps(sortCommentsVolumeByWeek, ensure_ascii=False)
    return MicroBlogTitle, MicroBlogCategory, commentsVolumeByHour, commentsVolumeByDay, commentsVolumeByWeek

# #根据小时统计展示信息
# #时间（年月日时）：评论量
# sortCommentsVolumeByHour={}
# def calculateCommentVolumeByHour(data_path):
#     #时间（年月日时）：评论量
#     commentsVolume = {}
#     # 时间（年月日时）：评论量
#     sortCommentsVolume = {}
#     comments_data=pd.read_csv(data_path).values#读取csv文件至列表
#     #评论数组的维度
#     [rows, cols] = comments_data.shape
#     #遍历评论数组的行，即遍历评论
#     for i in range(rows):
#         #获取时间（年月日时），通过切割日期字符串
#         hour=comments_data[i][1][0:-6]
#         #判断统计字典里面是否添加过该时间（年月日时），若不在添加该时间
#         if(hour not in commentsVolume.keys()):
#             commentsVolume[hour]=0
#         #统计量加一
#         commentsVolume[hour]+=1
#     # 给得到的评论统计量按时间（年月日时）排个序
#     new_commentsVolume=sorted(commentsVolume.items(),key=lambda commentsVolume:commentsVolume[0])
#     for i in range(len(new_commentsVolume)):
#         sortCommentsVolume[new_commentsVolume[i][0]]=str(new_commentsVolume[i][1])
#     #print(sortCommentsVolume.keys())#时间（年月日时）列表
#     #print(sortCommentsVolume.values())#评论量列表
#     return sortCommentsVolume
#
# #根据周统计展示信息
# #时间（周）：评论量
# def calculateCommentVolumeByWeek(sortCommentsVolumeByDay):
#     #时间（周）：评论量
#     commentsVolume = {}
#     i=0
#     #遍历日评论量的统计字典（day:count)
#     for key in sortCommentsVolumeByDay.keys():
#         # 获取时间（周），通过计算第几天对应开始第几周
#         week="第"+str(int((i/7)+1))+"周"
#         # 判断统计字典里面是否添加过该时间（第x周），若不在添加该时间
#         if (week not in commentsVolume.keys()):
#             commentsVolume[week]='0'
#         #该周累和近7天的评论量
#         commentsVolume[week]=str(int(commentsVolume[week])+int(sortCommentsVolumeByDay[key]))
#         i+=1
#     return commentsVolume

# #调用函数求日评论量统计
# sortCommentsVolumeByDay=calculateCommentVolumeByDay(data_path)
# #封装成json数据进行前后端传输
# commentsVolumeByDay = json.dumps(sortCommentsVolumeByDay)
# #调用函数求时评论量统计
# sortCommentsVolumeByHour=calculateCommentVolumeByHour(data_path)
# #封装成json数据进行前后端传输
# commentsVolumeByHour = json.dumps(sortCommentsVolumeByHour)
# #利用日评论统计量 求周评论量统计
# sortCommentsVolumeByWeek=calculateCommentVolumeByWeek(sortCommentsVolumeByDay)
# #封装成json数据进行前后端传输
# commentsVolumeByWeek = json.dumps(sortCommentsVolumeByWeek)
#给评论按时间排个序
#comments_sortdata=comments_data.sort_values(by=['时间'],na_position='first').values

#词云图片生成
# from wordcloud import WordCloud
# import jieba
# import pandas as pd
# #1.将字符串切分
# def chinese_jieba(text):
#     wordlist_jieba=jieba.cut(text)
#     space_wordlist=" ".join(wordlist_jieba)
#     return space_wordlist
#
# def worldCould(data_path):
#     comments_data=pd.read_csv(data_path).values[:, 2]
#     comments=' '.join(map(str, comments_data))
#     text=chinese_jieba(comments)
#     #2.图片遮罩层
#     #mask_pic=numpy.array(Image.open("china.jpg"))
#     #3.将参数mask设值为：mask_pic
#     wordcloud = WordCloud(font_path="STXINWEI.TTF", background_color="white", width=910, height=400,
#                           max_words=50, min_font_size=8).generate(text)
#     wordcloud.to_file('static/data/MicroBlogCommentsWordCloud/MicroBlogCommentsWordCloud.png')
#     image=wordcloud.to_image()
#     image.show()
#     return 0
#
# worldCould('static/data/MicroBlogComments/MicroBlogComments.csv')