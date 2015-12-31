# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import json
import pymongo
from scrapy import Request
import time
import re
from bili.settings import MONGOHOST

class GetSubmitVideosByMidScrapy(BaseSpider):
    name = u'getSubmitVideosByMid'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]
        self.userInfo = self.db["userInfo"]

    def start_requests(self):
        count = self.userInfo.count()

        for k in xrange(0, count, 10000):
            tmp = self.userInfo.find({}, {u'mid': 1}).skip(k).limit(10000)
            for i in tmp:
                yield Request(u'http://space.bilibili.com/ajax/member/getSubmitVideos?mid=%s&pagesize=30&tid=0&keyword=&page=1' %(i[u'mid']), callback=self.parse)
# chartid 4443709
# 与url对应

    def parse(self, response):
        data = json.loads(response.body)
        if data[u'status']:
            if data[u'data'].has_key(u'vlist'):
                for i in data[u'data'][u'vlist']:
                    self.doc.update({u'aid':str(i[u'aid'])}, i, True)
            if data[u'data'][u'pages'] > 1:
                for p in xrange(2, data[u'data'][u'pages']):
                    url = response.url.replace(re.findall('(page=\d.*?)', response.url)[0], u'page='+str(p))
                    yield Request(url, callback=self.parse)
                    pass
        else:
            print u'network error'


    def spider_close(self):
        self.connectionMongoDB.close()