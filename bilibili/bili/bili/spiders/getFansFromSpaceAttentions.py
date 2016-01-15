# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
import json
import pymongo
from scrapy import Request
from datetime import datetime
import re
from bili.settings import MONGOHOST

class GetFansFromSpaceAttentionsScrapy(BaseSpider):
    name = u'getFansFromSpaceAttentions'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.userInfo = self.db["userInfo"]

    def start_requests(self):
        userInfoUrl = u'http://space.bilibili.com/ajax/friend/GetAttentionList?mid={}&page=1'
        count = self.userInfo.find({}, {u'_id':1}).count()
        for k in xrange(0, count, 1000):
            for i in self.userInfo.find({}, {u'mid':1}).skip(k).limit(1000):
                yield Request(userInfoUrl.format(str(i[u'mid'])), meta={u'mid': i[u'mid']}, callback=self.parseUserAttentionJson)

    def parseUserAttentionJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                for i in tmp[u'data'][u'list']:
                    data = {
                        u'mid':i[u'fid'],
                        u'addtime':i[u'addtime'],
                        u'uname':i[u'uname'],
                            }
                    self.userInfo.update({u'mid': str(response.meta[u'mid'])}, {u'$addToSet':{u'attentionList':data}})
                    t = self.userInfo.find({u'mid':str(i[u'fid'])})
                    # if not t.count():
                    #     userInfoUrl = u'http://space.bilibili.com/ajax/member/GetInfo?mid='
                    #     yield Request(userInfoUrl + str(i[u'fid']), callback=self.parseUserInfoJson)
                if tmp[u'data'][u'pages'] > 5:
                    num = 5
                else:
                    num = tmp[u'data'][u'pages']
                for k in xrange(2, num+1):
                # 系统限制只能看前5页
                # for k in xrange(tmp[u'data'][u'pages']):
                    url = response.url.replace(re.findall(u'page=.*', response.url)[0], u'page='+str(k))
                    yield Request(url, meta={u'mid': response.meta[u'mid']}, callback=self.parseUserAttentionJson)
        except:
            pass

    def parseUserInfoJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                    self.userInfo.update({u'mid': tmp[u'data'][u'mid']}, tmp[u'data'], True)
        except:
            pass

    def spider_close(self):
        self.connectionMongoDB.close()