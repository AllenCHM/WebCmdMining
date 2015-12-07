# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'


from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from datetime import datetime
import json
from urllib import urlencode
import urlparse
from scrapy.http import Request
import sys
import random
import time
import datetime
import pymongo
import re
import requests
from autoQQ.items import AutoqqItem

reload(sys)
sys.setdefaultencoding('utf-8')


class tencentKSpider(Spider):
    name = "tencentK" #腾讯汽车_点评
    # allowed_domains = [u".auto.qq.com",
    #                    ]
    start_urls = [
        u'http://cgi.data.auto.qq.com/php/index.php?mod=wom&serial=225&class=0&list=1',  #修改此处即可修改车型
    ]

    def __init__(self):
        self.host = u'http://cgi.data.auto.qq.com'
        self.hostW = u'http://cgi.data.auto.qq.com/php/'

    def parse(self, response):
        yield Request(url=u'http://cgi.data.auto.qq.com/php/index.php?mod=wom&serial=225&list=1&pos=top&class=0', callback=self.parseAll)
        yield Request(url=u'http://cgi.data.auto.qq.com/php/index.php?mod=wom&serial=225&list=1&pos=top&class=4', callback=self.parseW)

    def parseW(self, response):
        hxs = Selector(response)
        lists = hxs.xpath('//div[@class="list"]')
        for list in lists:
            item = AutoqqItem()
            item[u'source'] = u'腾讯汽车'
            item[u'datatype'] = u'微评'
            try:
                item[u'author'] = list.xpath('.//span[contains(@class, "name")]/text()').extract()[0]
                item[u'content'] = list.xpath('./p').xpath('string(.)').extract()[0]
                item[u'recordDate'] = list.xpath('.//span[@class="date"]/text()').extract()[0]
                yield item
            except:
                t = list.extract()
                pass
        nextPage = hxs.xpath('//a[@id="g_auto_next_page"]/@href').extract()
        if nextPage:
            nextPage = self.hostW + nextPage[0]
            yield Request(nextPage, callback=self.parseW)

    def parseAll(self, response):
        hxs = Selector(response)
        divs = hxs.xpath(u'//div[@class="bd"]/div[@class="pt-list cl"]')
        for div in divs:
            item = AutoqqItem()
            try:
                item[u'source'] = u'腾讯汽车'
                item[u'author'] = div.xpath('./div[@class="pic"]/p[contains(@class,"name")]/@title').extract()[0]
                item[u'recordDate'] = div.xpath('./div[@class="txtarea"]/p/span/text()').extract()[0]
                item[u'content'] =div.xpath('.//dl[@class="yqlist cl"]').xpath('string(.)').extract()[0]
                item[u'link'] = self.host + div.xpath('./div[@class="txtarea"]/h3/a/@href').extract()[0]
                tmp = div.xpath('.//span[@class="support"]/span/text()').extract()
                if tmp:
                    item[u'clicknum'] = tmp[0]
                item[u'title'] = div.xpath('.//div[@class="txtarea"]/h3/a/text()').extract()[0]
                tmp = div.xpath('.//span[@class="repley"]/text()').extract()
                if tmp:
                    item[u'replynum'] = tmp[0]
                else:
                    item[u'replynum'] = 0
                item[u'datatype'] = u'点评'
                if item[u'replynum']:
                    url = self.host + div.xpath('.//span[@class="repley"]/a/@href').extract()[0]
                    yield Request(url, meta={u'item': dict(item)}, callback=self.parseReply)
                else:
                    item[u'reContent'] = []
                    item[u'lastReDate'] = item[u'recordDate']
                    yield item
            except:
                pass #该错误为最后评论栏引起

        nextPage = hxs.xpath('//a[@id="g_auto_next_page"]/@href').extract() #获取评论下一页
        if nextPage and u'javascript:void(0);' not in nextPage[0]:
            nextPage = self.host + nextPage[0]
            yield Request(nextPage, callback=self.parse)


    def parseReply(self, response):
        hxs = Selector(response)
        item = AutoqqItem()
        for i in response.meta[u'item'].keys():
            item[i] = response.meta[u'item'][i]
        if not response.meta[u'item'].has_key('reContent'):
            item[u'reContent'] = []
        divs = hxs.xpath('//div[@class="pt2-list cl"]')
        for div in divs:
            try:
                tmp = {}
                tmp[u'author'] = div.xpath('.//p[contains(@class, "name")]/@title').extract()[0]
                tmp[u'recordDate'] = div.xpath('.//span[@class="date"]/text()').extract()[0]
                tmp[u'floor'] = div.xpath('.//span[@class="num"]/text()').extract()[0]
                tmp[u'content'] = div.xpath('.//div[@class="txt"]').xpath('string(.)').extract()[0]
                item[u'reContent'].append(tmp)
            except:
                pass
        nextPage = hxs.xpath('//a[@id="g_auto_next_page"]/@href').extract() #获取评论下一页
        if nextPage and u'javascript:void(0);' not in nextPage[0]:
            nextPage = self.host + nextPage[0]
            yield Request(nextPage, meta={u'item': dict(item)}, callback=self.parseReply)
        else:
            item[u'lastReDate'] = item[u"reContent"][-1][u'recordDate']
            yield item
