# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'
#####################################
#
#  未完成
#
############################################

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import json
import pymongo
from scrapy import Request
import time
import re
from bili.settings import MONGOHOST



class GetFeedBackByAidScrapy(BaseSpider):
    name = u'getFeedBackByAid'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]

    def start_requests(self):
        count = self.doc.count()
        for k in xrange(0,count, 10000):
            tmp = self.doc.find({}, {u'aid': 1}).skip(k).limit(10000)
            for i in tmp:
                url = u'http://api.bilibili.com/feedback?type=jsonp&ver=3&callback=jQuery17202343479166738689_' + str(int(time.time()*1000)) + u'&mode=arc&aid=' + str(i[u'aid']) + u'&pagesize=200&page=1&_=' + str(int(time.time()*1000))
                yield Request(url, callback=self.parse)

    def parse(self, response):
        pass


    def spider_close(self):
        self.connectionMongoDB.close()