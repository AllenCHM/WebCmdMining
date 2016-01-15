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
        self.timestamp = str(int(time.time()*1000))
        self.userInfoUrl = u'http://space.bilibili.com/ajax/member/GetInfo?mid='

    def start_requests(self):
        count = self.userInfo.count()
        for k in xrange(0, count, 10000):
            tmp = self.userInfo.find({}, {u'mid': 1}).skip(k).limit(10000)
            for i in tmp:
                yield Request(u'http://space.bilibili.com/ajax/member/getSubmitVideos?mid=%s&pagesize=30&tid=0&keyword=&page=1' %(i[u'mid']), callback=self.parse)

    def parse(self, response):
        try:
            data = json.loads(response.body)
            if data[u'status']:
                data = data[u'data']
        except:
            tmp = re.findall('\((.*)\)', response.body, re.S)
            data = json.loads(tmp[0])
        if data.has_key(u'vlist'):
            for i in data[u'vlist']:
                self.doc.update({u'aid':str(i[u'aid'])}, i, True)
                url = u'http://api.bilibili.com/feedback?type=jsonp&ver=3&callback=jQuery17202343479166738689_' + self.timestamp + u'&mode=arc&aid=' + str(i[u'aid']) + u'&pagesize=20&page=1&_=' + self.timestamp
                yield Request(url, callback=self.parseComm)

        if data.has_key(u'pages'):
            if data[u'pages'] > 1:
                for p in xrange(2, data[u'pages']):
                    url = response.url.replace(re.findall('(page=\d.*?)', response.url)[0], u'page='+str(p))
                    yield Request(url, callback=self.parse)

    def parseComm(self, response):
        tmp = re.findall('\((.*)\)', response.body, re.S)
        page = re.findall('page=(.*?)&', response.url)[0]
        aid = re.findall('aid=(.*?)&', response.url)[0]
        tmp = json.loads(tmp[0])
        if tmp[u'list']:
            for i in tmp[u'list']:
                self.doc.update({u'aid':int(aid)}, {u"$addToSet":{u"feedback":i}}, True)
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
                    self.userInfo.update({u'mid': tmp[u'data'][u'mid']}, tmp[u'data'], True)
        except:
            del response


    def spider_close(self):
        self.connectionMongoDB.close()