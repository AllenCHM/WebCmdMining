# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
import json
import pymongo
from scrapy import Request
import time
import re
from dy2018_com.settings import MONGOHOST

class DytTScrapy(BaseSpider):
    name = u'dytt'
    allowed_domains = [u'dy2018.com', ]
    start_urls = [
        u'http://www.dy2018.com/'
    ]


    def __init__(self):
        self.connectionMongoDB = pymongo.MongoClient(host=MONGOHOST, port=27017)
        self.db = self.connectionMongoDB['AllenTest']
        self.doc = self.db["dytt"]
        self.host = u'http://www.dy2018.com'

    def parse(self, response):
        hxs = Selector(response)
        a = hxs.xpath('//div[@class="contain"]/ul//a/@href').extract()
        for i in a:
            yield Request(self.host+i, callback=self.parseList)

    def parseList(self, response):
        hxs = Selector(response)
        a = hxs.xpath('//div[@class="co_content8"]/ul//a/@href').extract()
        for i in a:
            yield Request(self.host+i, callback=self.parseInfo)
        nextPage = hxs.xpath(u'//div[@class="x"]//a/@href').extract()
        for page in nextPage:
            yield Request(self.host+page, callback=self.parseList)

    def parseInfo(self, response):
        hxs = Selector(response)
        ps = hxs.xpath('//div[@id="Zoom"]//p')
        item = {}
        tmp = ''
        for p in ps:
            t = p.xpath('string(.)').extract()[0].strip()
            if t.strip():
                for i in [u' ', u'\r', u'\t', u'\n', u'　', u'】', u']:']:
                    t = t.replace(i, u'')
                if u'译名' in t:
                    item[u'译名'] = t.split(u'译名')[-1]
                elif u'片名' in t:
                    item[u'片名'] = t.split(u'片名')[-1]
                elif u'剧名' in t:
                    item[u'剧名'] = t.split(u'剧名')[-1]
                elif u'主演' in t:
                    item[u'主演'] = t.split(u'主演')[-1]
                elif u'年代' in t:
                    item[u'年代'] = t.split(u'年代')[-1]
                elif u'地区' in t:
                    item[u'地区'] = t.split(u'地区')[-1]
                elif u'类别' in t:
                    item[u'类别'] = t.split(u'类别')[-1]
                elif u'语言' in t:
                    item[u'语言'] = t.split(u'语言')[-1]
                elif u'类型' in t:
                    item[u'类型'] = t.split(u'类型')[-1]
                elif u'字幕' in t:
                    item[u'字幕'] = t.split(u'字幕')[-2]
                    if not item[u'字幕']:
                        pass
                elif u'上映时间' in t:
                    item[u'上映时间'] = t.split(u'上映时间')[-1]
                elif u'评分' in t:
                    item[u'评分'] = t.split(u'评分')[-1]
                elif u'片长' in t:
                    item[u'片长'] = t.split(u'片长')[-1]
                elif u'播送' in t:
                    item[u'播送'] = t.split(u'播送')[-1]
                elif u'导演' in t:
                    item[u'导演'] = t.split(u'导演')[-1]

        if item:
            a = hxs.xpath('//tbody//a/text()').extract()
            item[u'link'] = response.url
            item[u'downloadLink'] = []
            for i in a:
                if u'ftp' in i:
                    item[u'downloadLink'].append(i)
            self.doc.update({u'link':item[u'link']}, item, True)

    def spider_close(self):
        self.connectionMongoDB.close()