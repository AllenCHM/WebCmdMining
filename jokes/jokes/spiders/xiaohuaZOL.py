# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
import json
import pymongo
from scrapy import Request
import time
import re

class XiaohuaZOLScrapy(BaseSpider):
    name = u'xiaohuaZOL'
    # allowed_domains = [u'bilibili.com', ]
    start_urls = [
        u'http://xiaohua.zol.com.cn/'
    ]
    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host='192.168.2.165', port=27017)
        self.db = self.connectionMongoDB['AllenTest']
        self.doc = self.db["AllenTest"]
    #     self.avChartDoc = self.db["avChart"]
    #     self.avUrlDoc = self.db["avUrl"]


    def parse(self, response):
        hxs = Selector(response)
        lis = hxs.xpath('//ul[contains(@class, "news-list classification-nav")]/li')
        for li in lis:
            classfical = li.xpath('./a/text()').extract()[0]
            href = u'http://xiaohua.zol.com.cn' + li.xpath('./a/@href').extract()[0]
            yield Request(href, meta={"classfical":classfical}, callback=self.parseInfo)

    def parseInfo(self, response):
        hxs = Selector(response)
        allList = hxs.xpath('//a[@class="all-read"]')
        for a in allList:
            href = u'http://xiaohua.zol.com.cn' + a.xpath('./@href').extract()[0]
            yield Request(href, meta={"classfical": response.meta["classfical"]}, callback = self.parsePage)
        nextPage = hxs.xpath('//a[@class="page-next"]/@href').extract()
        if nextPage:
            nextPage = u'http://xiaohua.zol.com.cn' + nextPage[0]
            yield Request(nextPage, meta={"classfical": response.meta["classfical"]}, callback = self.parseInfo)

    def parsePage(self, response):
        hxs = Selector(response)
        item = {}
        item[u'classfical'] = response.meta[u'classfical']
        item[u'content'] = hxs.xpath('//div[@class="article-text"]').xpath('string(.)').extract()[0].strip()
        self.doc.insert(item)

    def spider_close(self):
        self.connectionMongoDB.close()