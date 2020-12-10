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
MicroBlogTitleTable = {'1': '“万众一心抗击疫情”话题舆情演化分析', '2': '“嫦娥五号探月任务”话题舆情演化分析',
                       '3': '“直击2020美国大选”话题舆情演化分析', '4': '”丁真直播带你游理塘“话题舆情演化分析',
                       '5': '“科比与女儿GiGi直升机坠机”话题舆情演化分析', '6': '“罗志祥与周扬清分手事件”话题舆情演化分析'}
# 微博评论文件路径表(静态)
MicroBlogFilePathTable = {'1': 'static/data/MicroBlogComments/MicroBlogComments1.csv',
                          '2': 'static/data/MicroBlogComments/MicroBlogComments2.csv',
                          '3': 'static/data/MicroBlogComments/MicroBlogComments3.csv',
                          '4': 'static/data/MicroBlogComments/MicroBlogComments4.csv',
                          '5': 'static/data/MicroBlogComments/MicroBlogComments5.csv',
                          '6': 'static/data/MicroBlogComments/MicroBlogComments6.csv'}
#微博话题介绍
MicroBlogIntroductionTable = {'1': '2019年12月以来，湖北省武汉市持续开展流感及相关疾病监测，发现多起病毒性肺炎病例，均诊断为病毒性肺炎/肺部感染。2020年1月20日，习近平对新型冠状病毒感染的肺炎疫情作出重要指示，强调要把人民群众生命安全和身体健康放在第一位，坚决遏制疫情蔓延势头。2020年1月30日晚，世界卫生组织（WHO）宣布，将新型冠状病毒疫情列为国际关注的突发公共卫生事件（PHEIC）。',
                              '2': '2020年7月，中国将实施的嫦娥五号任务，则是围绕月球采样返回的主要目标打造的无人探测任务，嫦娥五号探测器的着陆地点为月球正面西北部的吕姆克山脉。2020年11月24日4时30分，中国在中国文昌航天发射场，用长征五号遥五运载火箭成功发射探月工程嫦娥五号探测器，火箭飞行约2200秒后，顺利将探测器送入预定轨道，开启中国首次地外天体采样返回之旅。2020年12月1日，嫦娥五号探测器成功在月球正面预选着陆区着陆。',
                              '3': '美国时间2020年8月18日，约瑟夫·拜登正式成为2020年美国民主党总统候选人。8月24日下午，唐纳德·特朗普正式被提名为2020年美国共和党总统候选人。北京时间11月3日13点左右（美国东部时间3日凌晨），2020年美国大选选举日投票正式开始。北京时间11月8日凌晨（美国时间11月7日），据美国媒体测算，民主党总统候选人约瑟夫·拜登已获得超过270张选举人票。',
                              '4': '《丁真的世界》，以康巴少年丁真为第一主角，拍摄的四川甘孜州文旅宣传片，视频中，丁真走在雪山脚下，奔跑在高原草地，还牵着第一次“出镜”的白马悠闲徜徉在纯净的理塘美景中。',
                              '5': '2020年1月26日，美职篮退役球星科比·布莱恩特在美国加利福尼亚州南部卡拉巴萨斯市发生的直升机坠毁事故中丧生，享年41岁。从此，世间再无黑曼巴。“你看过凌晨四点的洛杉矶吗”这句话一直不能忘掉，他的努力，他的坚强，他的天赋，为他换来的，是5夺NBA总冠军，1次常规赛MVP，2次总决赛MVP，4次全明星赛MVP！对于科比，对于湖人的24号，我们永远不能忘记。科比·布莱恩特，一路走好！',
                              '6': '周扬青—篇堪称典范的“分手长文”将罗志祥的人生“捶”地稀碎!周扬青娓娓道来，把她与罗志祥9年来的感情进行了“总结”∶罗志祥有一部专门用来和女生聊天的手机;周扬青不在的几乎每一天，罗志祥都会约不同女生来家里;罗志祥去每一个城市，都有可以约到酒店的女生;罗志祥和旗下的女艺人，都有亲密关系，而她们也曾被介绍给周扬青认识;罗志祥和兄弟们对于那些被叫出来玩的女生，非常的不尊重，还会经常多人一起“运动”。'}
#微博话题热度评分，打星号
MicroBlogPopularityScoreTable = {'1': '4.5', '2': '3.5', '3': '4', '4': '3.5', '5': '4', '6': '4.5'}
#微博话题阅读次数
MicroBlogReadingTimesTable = {'1': '11414000000', '2': '330000000', '3': '1380000000', '4': '1090000000', '5': '740000000', '6': '2090000000'}
#微博话题讨论次数
MicroBlogDiscussionTimesTable = {'1': '6289700', '2': '119000', '3': '54000', '4': '141135', '5': '312000', '6': '189000'}
#微博话题原创人数
MicroBlogOriginalNumberTable = {'1': '41000', '2': '4072', '3': '11000', '4': '1435', '5': '23000', '6': '42000'}
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
    category = {'MicroBlogCategory': '1'}#默认选中项
    category['MicroBlogCategory'] = categoryStr#回传上次选中的类别
    MicroBlogCategory = json.dumps(category)#json.dumps封装
    #按时、日、周统计评论量
    sortCommentsVolumeByHour, sortCommentsVolumeByDay, sortCommentsVolumeByWeek = countCommentVolume(MicroBlogFilePath)
    #封装统计量
    commentsVolumeByHour = json.dumps(sortCommentsVolumeByHour)
    commentsVolumeByDay = json.dumps(sortCommentsVolumeByDay)
    commentsVolumeByWeek = json.dumps(sortCommentsVolumeByWeek, ensure_ascii=False)
    #根据类型序号查最上面的表获取微博话题介绍
    introduction = {'MicroBlogIntroduction': '1'}#默认选中项
    introduction['MicroBlogIntroduction'] = MicroBlogIntroductionTable[categoryStr]#查表获取微博话题介绍
    MicroBlogIntroduction = json.dumps(introduction)  # json.dumps封装
    # 根据类型序号查最上面的表获取微博话题热度评分
    popularityScore = {'MicroBlogPopularityScore': '1'}  # 默认选中项
    popularityScore['MicroBlogPopularityScore'] = MicroBlogPopularityScoreTable[categoryStr]  # 查表获取微博话题热度评分
    MicroBlogPopularityScore = json.dumps(popularityScore)  # json.dumps封装
    # 根据类型序号查最上面的表获取微博话题阅读次数
    readingTimes = {'MicroBlogReadingTimes': '1'}  # 默认选中项
    readingTimes['MicroBlogReadingTimes'] = MicroBlogReadingTimesTable[categoryStr]  # 查表获取微博话题阅读次数
    MicroBlogReadingTimes = json.dumps(readingTimes)  # json.dumps封装
    # 根据类型序号查最上面的表获取微博话题讨论次数
    discussionTimes = {'MicroBlogDiscussionTimes': '1'}  # 默认选中项
    discussionTimes['MicroBlogDiscussionTimes'] = MicroBlogDiscussionTimesTable[categoryStr]  # 查表获取微博话题讨论次数
    MicroBlogDiscussionTimes = json.dumps(discussionTimes)  # json.dumps封装
    # 根据类型序号查最上面的表获取微博话题原创人数
    originalNumber = {'MicroBlogOriginalNumber': '1'}  # 默认选中项
    originalNumber['MicroBlogOriginalNumber'] = MicroBlogOriginalNumberTable[categoryStr]  # 查表获取微博话题原创人数
    MicroBlogOriginalNumber = json.dumps(originalNumber)  # json.dumps封装
    return MicroBlogTitle, MicroBlogCategory, commentsVolumeByHour, commentsVolumeByDay, commentsVolumeByWeek, MicroBlogIntroduction, MicroBlogPopularityScore, MicroBlogReadingTimes, MicroBlogDiscussionTimes, MicroBlogOriginalNumber

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