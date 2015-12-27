# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import json
import pymongo
from scrapy import Request
import time
import re

class BilibiCommScrapy(BaseSpider):
    name = u'bilibiComm'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host='192.168.0.8', port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]
        self.avCommentDoc = self.db["avComment"]

    def start_requests(self):
        count = self.doc.count()
        for k in xrange(0,count, 10000):
            tmp = self.doc.find({}, {u'aid': 1}).skip(k).limit(10000)
            for i in tmp:
                url = u'http://api.bilibili.com/feedback?type=jsonp&ver=3&callback=jQuery17202343479166738689_' + str(int(time.time()*1000)) + u'&mode=arc&aid=' + str(i[u'aid']) + u'&pagesize=200&page=1&_=' + str(int(time.time()*1000))
                yield Request(url, callback=self.parse)

    def parse(self, response):
        tmp = re.findall('\((.*)\)', response.body, re.S)
        page = re.findall('page=(.*?)&', response.url)[0]
        aid = re.findall('aid=(.*?)&', response.url)[0]
        tmp = json.loads(tmp[0])
        if tmp[u'list']:
            tmp.update({u'aid':aid, u'page':page, u'downloadTime':time.time()})
            self.avCommentDoc.save(tmp)
            #总评论数算法
            if tmp[u'pages'] > int(page):
                url = response.url.split(u'&')
                url[-2] = u'page=' + str(int(page)+1)
                url = u'&'.join(url)
                yield Request(url, callback=self.parse)



    def spider_close(self):
        self.connectionMongoDB.close()