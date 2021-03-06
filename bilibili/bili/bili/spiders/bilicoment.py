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

class BilibiCommScrapy(BaseSpider):
    name = u'bilibiComm'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.doc = self.db["avIndex"]
        self.userInfo = self.db["userInfo"]
        self.comment = self.db["comment"]
        self.userInfoUrl = u'http://space.bilibili.com/ajax/member/GetInfo?mid='

    def start_requests(self):
        count = self.doc.count()
        for k in xrange(0,count, 10000):
            tmp = self.doc.find({}, {u'aid': 1}).skip(k).limit(10000)
            for i in tmp:
                url = u'http://api.bilibili.com/feedback?type=jsonp&ver=3&callback=jQuery17202343479166738689_' + str(int(time.time()*1000)) + u'&mode=arc&aid=' + str(i[u'aid']) + u'&pagesize=20&page=1&_=' + str(int(time.time()*1000))
                yield Request(url, callback=self.parse)

    def parse(self, response):
        tmp = re.findall('\((.*)\)', response.body, re.S)
        page = re.findall('page=(.*?)&', response.url)[0]
        tmp = json.loads(tmp[0])
        if tmp.has_key(u'list'):
            if tmp[u'list']:
                for i in tmp[u'list']:
                    self.comment.update_one({u'aid': int(re.findall('aid=(.*?)&', response.url)[0])},
                                            {u"$addToSet": {u"feedback": i}}, True)
                    if not self.userInfo.find_one({u'mid':str(i[u'mid'])}, {u'_id':1}):
                        yield Request(self.userInfoUrl + str(i[u'mid']), callback=self.parseUserInfoJson)
                if int(page)*20 < tmp[u'results']:
                    for i in xrange(int(page)+1, (tmp[u'pages']+20-1)/20):
                        url = response.url.split(u'&')
                        url[-2] = u'page=' + str(i)
                        url = u'&'.join(url)
                        yield Request(url, callback=self.parse)

    def parseUserInfoJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                    self.userInfo.update_one({u'mid': tmp[u'data'][u'mid']}, {u'$set':tmp[u'data']}, True)
        except:
            pass

    def closed(self, reason):
        self.connectionMongoDB.close()