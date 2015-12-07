# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

import requests
import re
import json
from lxml import etree
import pymongo
import time

connectionMongoDB = pymongo.MongoClient(host='192.168.2.165', port=27017)
db =  connectionMongoDB['bilibili']
doc =  db["avIndex"]

url = u'http://www.bilibili.com/'

ranking3DayUrl = u'http://www.bilibili.com/index/ranking-3day.json'
dayUrl = u'http://www.bilibili.com/index/catalogy/1-3day.json'
promoteUrl = u'http://www.bilibili.com/index/promote.json'
recomUrl = u'http://live.bilibili.com/bili/recom?callback=liveXhrDone'
dingUrl = u'http://www.bilibili.com/index/ding.json'
dingUrlIndex = u'http://www.bilibili.com/index/ding/'             #(0-156  返回json索引)



#视频地址
avUrl = u'http://www.bilibili.com/video/av2844582/'
# 视频集
# option标签的value值

#对应弹幕地址
dangUrl = u'http://comment.bilibili.com/2806340.xml'
#对应推荐
tuijianUrl = u'http://comment.bilibili.com/recommend,1825349'
#对应标签
biaoqianUrl = u'http://www.bilibili.com/api_proxy?app=tag&action=/tags/archive_list&aid=2844582&nomid=1'

avUrl = u'http://www.bilibili.com/video/av2844582/'

#评论地址


response = requests.get(avUrl)
tmp = re.findall('cid=(.*?)&', response.content)
print tmp[0]



        #4443708

connectionMongoDB.close()

    # tmp = re.findall('\((.*)\)', response.content, re.S)
    # tmp = response.json()

    # hxs = etree.HTML(response.content)
    #
    # href = hxs.xpath('//a/@href')
    #
    # for a in href:
    #     print(a)

