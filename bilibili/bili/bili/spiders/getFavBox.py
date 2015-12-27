# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
import json
import pymongo
from scrapy import Request
from datetime import datetime

class GetFavBoxScrapy(BaseSpider):
    name = u'getFavBox'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host='192.168.0.8', port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.userInfo = self.db["userInfo"]

    def start_requests(self):
        count = self.userInfo.count()
        for k in xrange(0, count, 10000):
            tmp = self.userInfo.find({}, {u'mid': 1}).skip(k).limit(10000)
            for i in tmp:
                yield Request(u'http://space.bilibili.com/ajax/fav/getBoxList?mid=%s' %(str(i[u'mid'])),meta={u'mid': i[u'mid']} ,callback=self.parseJson)


    def parseJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                for i in tmp[u'data'][u'list']:
                    self.userInfo.update({u'mid': str(response.meta[u'mid'])}, {'$addSet':{u'favBox': i}}, True)
        except:
            pass

    def spider_close(self):
        self.connectionMongoDB.close()