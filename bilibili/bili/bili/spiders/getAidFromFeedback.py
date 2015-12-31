# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
import json
import pymongo
from scrapy import Request
from datetime import datetime
import re
from bili.settings import MONGOHOST


class GetAidFromFeedbackScrapy(BaseSpider):
    name = u'getAidFromFeedback'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.userInfo = self.db["userInfo"]
        self.doc = self.db["avIndex"]
        self.userInfoUrl = u'http://space.bilibili.com/ajax/member/GetInfo?mid='

    def start_requests(self):
        count = self.doc.find({u'feedback':{u"$exists":1}}, {u'_id':1}).count()
        for k in xrange(0, count, 1000):
            for i in self.doc.find({u'feedback':{u"$exists":1}}, {u'feedback':1}).skip(k).limit(1000):
                for feedback in i[u'feedback']:
                    if not self.userInfo.find({u'mid':str(feedback[u'mid'])}).count():
                        yield Request(self.userInfoUrl + str(feedback[u'mid']), callback=self.parseUserInfoJson)

    def parseUserInfoJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                    self.userInfo.update({u'mid': str(tmp[u'data'][u'mid'])}, tmp[u'data'], True)
        except:
            pass

    def spider_close(self):
        self.connectionMongoDB.close()