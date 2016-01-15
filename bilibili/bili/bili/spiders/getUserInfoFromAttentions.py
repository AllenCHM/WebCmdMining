# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
import json
import pymongo
from scrapy import Request
from datetime import datetime
from bili.settings import MONGOHOST

class GetUserInfoFromAttentionsScrapy(BaseSpider):
    name = u'getUserInfoFromAttentions'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]
        self.userInfo = self.db["userInfo"]

    def start_requests(self):
        userInfoUrl = u'http://space.bilibili.com/ajax/member/GetInfo?mid='
        total = self.userInfo.find({u'attentionList':{u'$exists':1}}, {u'attentionList':1}).count()
        for m in xrange(0, total, 100):
            tmp = self.userInfo.find({u'attentionList':{u'$exists':1}}, {u'attentionList':1}).skip(m).limit(100)
            for k in tmp:
                for i in k[u'attentionList']:
                    if not self.userInfo.find({u'mid':str(i[u'mid'])}).count():
                        yield Request(userInfoUrl + str(i[u'mid']), callback=self.parseJson)

    def parseJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                self.userInfo.update({u'mid': tmp[u'data'][u'mid']}, tmp[u'data'], True)
        except:
            pass

    def spider_close(self):
        self.connectionMongoDB.close()