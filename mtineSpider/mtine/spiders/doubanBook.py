# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'


from  scrapy.spider import BaseSpider
from  scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import requests
from urllib import quote
from time import time
import re
import pymysql
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class DoubanBookSpider(BaseSpider):
    name = 'doubanBook'
    allowed_domains = ['douban.com']
    start_urls = [
        u'http://book.douban.com/'
    ]

    def parse(self, response):
        hxs = Selector(response)
        lists = hxs.select('//a/@href').extract()
        for a in lists:
            if u'ebook' in a:
                yield Request(a, callback=self.parseEbook)

            elif u'subject' in a:
                yield Request(a, callback=self.parseSubject)

    def parseEbook(self, response):
        hxs = Selector(response)
        info = hxs.xpath('//div[@class="article-profile-bd"]')
        tmp = info.extract()
        print(tmp)
        item = {}
        item[u'name'] = info.xpath('./h1/text()').extract()[0]
        item[u'href'] = response.url
        divs = info.xpath('./div/p')
        for i in divs:
            a = i.xpath('.//span[1]').xpath('string(.)').extract()
            b = i.xpath('.//span[2]').xpath('string(.)').extract()
            if a and b:
                item[a[0].strip()] = b[0].strip()
        lists = hxs.select('//a/@href').extract()
        for a in lists:
            if u'ebook' in a:
                yield Request(a, callback=self.parseEbook)

            elif u'subject' in a:
                yield Request(a, callback=self.parseSubject)

    def parseSubject(self, response):
        hxs = Selector(response)
        item = {}
        item[u'name'] = hxs.xpath('//div[@id="wrapper"]/h1').xpath('string(.)').extract()[0].strip()
        item[u'href'] = response.url
        div = hxs.xpath('//div[@id="info"]')
        tmp = div.extract()
        k = div.xpath('string(.)').extract()[0].strip()
        k = k.split('\n')
        tmp = []
        for i in k:
            if i.strip():
                tmp.append(i.strip())
        k = []
        for num, i in enumerate(tmp):
            if u':' in i and u':' != i[-1]:
                k.append(i)
            elif u':' == i[-1]:
                k.append(i)
            else:
                k[-1] += i
        for i in k:
            try:
                a, b = i.split(':')
                item[a.strip()] = b.strip()
            except:
                pass

        lists = hxs.select('//a/@href').extract()
        for a in lists:
            if u'ebook' in a:
                yield Request(a, callback=self.parseEbook)

            elif u'subject' in a:
                yield Request(a, callback=self.parseSubject)