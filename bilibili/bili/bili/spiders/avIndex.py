# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'
#获取首页视频

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import json
import pymongo
from scrapy import Request
import time
from datetime import datetime
from bili.settings import MONGOHOST

class AvIndexWebScrapy(BaseSpider):
    name = u'AvIndex'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]

    def start_requests(self):
        dingUrlIndex = u'http://www.bilibili.com/index/ding/'
        for i in xrange(0, 160):
            yield Request(dingUrlIndex + str(i) + u'.json', callback=self.parseJson)

    def parseJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'list']:
                for k in tmp[u'list']:
                    self.doc.update_one({u'aid':k[u'aid']}, {'$set': k}, True)
        except:
            pass

    def spider_close(self):
        self.connectionMongoDB.close()