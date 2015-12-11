# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
import json
import pymongo
from scrapy import Request
import time
import re
import requests
import base64

class GifZOLScrapy(BaseSpider):
    name = u'gifZOL'
    # allowed_domains = [u'bilibili.com', ]
    start_urls = [
        u'http://xiaohua.zol.com.cn/qutu/'
    ]
    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host='192.168.2.165', port=27017)
        self.db = self.connectionMongoDB['AllenTest']
        self.doc = self.db["AllenTestGif"]
    #     self.avChartDoc = self.db["avChart"]
    #     self.avUrlDoc = self.db["avUrl"]


    def parse(self, response):
        hxs = Selector(response)
        imgs = hxs.xpath('//ul[@class="article-list"]//img')
        for img in imgs:
            tmp = img.extract()
            href = img.xpath('./@src').extract()[0]
            r = requests.get(href)
            item = {}
            item[u'name'] = href.split('/')[-1]
            item[u'body'] = base64.b64encode(r.content)
            self.doc.update({u'name':item[u'name']}, item, True)
            yield Request(href, callback=self.parseInfo)


    def spider_close(self):
        self.connectionMongoDB.close()