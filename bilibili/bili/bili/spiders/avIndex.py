# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import json
import pymongo
from scrapy import Request
import time

class AvIndexWebScrapy(BaseSpider):
    name = u'AvIndex'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host='192.168.0.8', port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]

    def start_requests(self):
        dingUrlIndex = u'http://www.bilibili.com/index/ding/'
        # requestList = []
        for i in xrange(0, 160):
            yield Request(dingUrlIndex + str(i) + u'.json', callback=self.parseJson)
            # requestList.append(Request(dingUrlIndex + str(i) + u'.json', callback=self.parseJson))
        # return requestList

    def parseJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'list']:
                for k in tmp[u'list']:
                    k.update({u'downloadTime': time.time()})
                    self.doc.update({u'aid': k[u'aid']}, k, True)
        except:
            pass

    def spider_close(self):
        self.connectionMongoDB.close()