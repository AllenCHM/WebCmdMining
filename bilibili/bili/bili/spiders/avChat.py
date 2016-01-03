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

class AvChatScrapy(BaseSpider):
    name = u'avChat'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]
        self.avChartDoc = self.db["avChart"]
        self.avUrlDoc = self.db["avUrl"]

    def start_requests(self):
        count = self.doc.count()
        for k in xrange(0, count, 1000):
            for i in self.doc.find({}, {u'aid':1}).skip(k).limit(1000):
                yield Request(u'http://www.bilibili.com/video/av' + str(i[u'aid']) + u'/', callback=self.parse)

    def parse(self, response):
        self.avUrlDoc.update({u'url': response.url}, {u'url': response.url, u'downloadTime': time.time()}, True)
        hxs = HtmlXPathSelector(response)
        cid = re.findall('cid=(.*?)&', response.body)
        if cid:
            self.avChartDoc.update({'url': response.url}, {'url': response.url, 'cid': cid[0]}, True)
            yield Request(u'http://comment.bilibili.com/' + cid[0] + u'.xml', callback=self.parseXml)
        try:
            options = hxs.xpath('//option/@value')
            for option in options:
                tmp = option.extract()
                if tmp:
                    yield Request(u'http://comment.bilibili.com' + tmp[0], callback=self.parse)
        except:
            pass

    def parseXml(self, response):
        hxs = HtmlXPathSelector(response)
        chatid = hxs.xpath('//chatid/text()').extract()[0]
        ds = hxs.xpath('//d')
        chatList = self.avChartDoc.find_one({u'cid': chatid}, {u'chatList': 1})
        try:
            chatList = dict(chatList)
        except:
            pass
        if not chatList.has_key(u'chatList'):
            chatList.update({u'chatList': []})
        tmp = chatList[u'chatList']
        for d in ds:
            try:
                p = d.xpath('./@p').extract()[0]
                v = d.xpath('./text()').extract()[0]
                if {u'p': p, u'v': v} not in tmp:
                    tmp.append({u'p': p, u'v': v})
            except Exception, e:
                pass
        self.avChartDoc.update({u'_id': chatList[u'_id']}, {'$set': {u'chatList': tmp, u'downloadTime': time.time()}}, True)


    def spider_close(self):
        self.connectionMongoDB.close()