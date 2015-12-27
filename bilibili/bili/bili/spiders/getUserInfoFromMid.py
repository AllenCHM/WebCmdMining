# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
import json
import pymongo
from scrapy import Request
from datetime import datetime

class GetUserInfoFromMidScrapy(BaseSpider):
    name = u'getUserInfoFromMid'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host='192.168.0.8', port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]
        self.userInfo = self.db["userInfo"]

    def start_requests(self):
        userInfoUrl = u'http://space.bilibili.com/ajax/member/GetInfo?mid='
        tmp = self.doc.find({}, {u'mid':1})  #mid 为用户id
        for i in tmp:
            t = self.userInfo.find({u'mid':str(i[u'mid'])})
            if not t.count():
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