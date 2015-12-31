# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
import json
import pymongo
from scrapy import Request
from datetime import datetime
import re
from bili.settings import MONGOHOST


class GetFansFromSpaceFansScrapy(BaseSpider):
    name = u'getFansFromSpaceFans'
    allowed_domains = [u'bilibili.com', ]

    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['bilibili']
        self.userInfo = self.db["userInfo"]

    def start_requests(self):
        userInfoUrl = u'http://space.bilibili.com/ajax/friend/GetFansList?mid={}&page=1'
        tmp = self.userInfo.find({}, {u'mid':1})  #mid 为用户id
        for i in tmp:
            yield Request(userInfoUrl.format(str(i[u'mid'])), meta={u'mid': i[u'mid']}, callback=self.parseUserFansJson)

    def parseUserFansJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                for i in tmp[u'data'][u'list']:
                    data = {
                        u'mid':i[u'fid'],
                        u'addtime':i[u'addtime'],
                        u'uname':i[u'uname'],
                            }
                    self.userInfo.update({u'mid': str(response.meta[u'mid'])}, {u'$addToSet':{u'fansList':data}})
                    t = self.userInfo.find({u'mid':str(i[u'fid'])})
                    if not t.count():
                        userInfoUrl = u'http://space.bilibili.com/ajax/member/GetInfo?mid='
                        yield Request(userInfoUrl + str(i[u'fid']), callback=self.parseUserInfoJson)
                # for k in xrange(tmp[u'data'][u'pages']):
                #系统限制只能看前5页
                for k in xrange(6):
                    url = response.url.replace(re.findall(u'page=.*', response.url)[0], u'page='+str(k))
                    yield Request(url, meta={u'mid': response.meta[u'mid']}, callback=self.parseUserFansJson)
        except:
            pass

    def parseUserInfoJson(self, response):
        try:
            tmp = json.loads(response.body)
            if tmp[u'status']:
                    self.userInfo.update({u'mid': tmp[u'data'][u'mid']}, tmp[u'data'], True)
        except:
            pass

    def spider_close(self):
        self.connectionMongoDB.close()