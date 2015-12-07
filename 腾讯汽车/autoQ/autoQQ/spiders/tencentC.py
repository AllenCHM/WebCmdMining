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


class tencentCSpider(Spider):
    name = "tencentC" #腾讯汽车_论坛
    # allowed_domains = [u".auto.qq.com",
    #                    ]
    start_urls = [
        u'http://club.auto.qq.com/f-441-1.htm',  #修改此处即可修改车型
    ]

    def __init__(self):
        self.host = u'http://club.auto.qq.com/'

    def parse(self, response):
        hxs = Selector(response)
        divs = hxs.xpath(u'//div[@class="bm_c"]//table/tbody[starts-with(@id, "normalthread")]')
        for div in divs:
            item = {}
            item[u'source'] = u'腾讯汽车'
            item[u'author'] = div.xpath('.//td[@class="by"]/cite/a/text()').extract()[0]
            item[u'recordDate'] = div.xpath('.//td[@class="by"]/em/span/text()').extract()[0]
            item[u'link'] = self.host + div.xpath('.//th[@class="new"]/a/@href').extract()[0]
            item[u'clicknum'] = div.xpath('.//td[@class="num"]/em/text()').extract()[0]
            item[u'title'] = div.xpath('.//th[@class="new"]/a/text()').extract()[0]
            # item[u'replynum'] = div.xpath('.//td[@class="num"]/a/text()').extract()
            item[u'lastReDate'] = div.xpath('.//td[@class="by"]/em/a/text()').extract()[0]
            item[u'datatype'] = u'论坛'
            yield Request(item[u'link'], meta={u'item': item}, callback=self.parseReply)

        nextPage = hxs.xpath('//a[@class="nxt"]/@href').extract() #获取评论下一页
        if nextPage and u'javascript:void(0);' not in nextPage[0]:
            nextPage = self.host + nextPage[0]
            yield Request(nextPage, callback=self.parse)


    def parseReply(self, response):
        hxs = Selector(response)
        item = AutoqqItem()
        for i in response.meta[u'item'].keys():
            item[i] = response.meta[u'item'][i]
        if not response.meta[u'item'].has_key('reContent'):
            item[u'content'] = hxs.xpath('//table[starts-with(@id, "pid")]//div[@class="pcb"]//td[1]').xpath('string(.)').extract()[0].strip()
            tables = hxs.xpath('//table[starts-with(@id, "pid")]')[1:]
            item[u'reContent'] = []
        else:
            tables = hxs.xpath('//table[starts-with(@id, "pid")]')
        for table in tables:
            try:
                tmp = {}
                tmp[u'author'] = table.xpath('.//td[@class="pls"]//div[@class="authi"]/a/text()').extract()[0]
                tmp[u'recordDate'] = table.xpath('.//td[@class="plc"]//div[@class="authi"]/em/text()').extract()[0][4:]
                tmp[u'floor'] = table.xpath('.//td[@class="plc"]/div/strong/a/em/text()').extract()[0]
                tmp[u'content'] = table.xpath('.//td[@class="t_f"]').xpath('string(.)').extract()[0].strip()
                item[u'reContent'].append(tmp)
            except:
                pass
        nextPage = hxs.xpath('//a[@class="nxt"]/@href').extract() #获取评论下一页
        if nextPage and u'javascript:void(0);' not in nextPage[0]:
            nextPage = self.host + nextPage[0]
            print len(item[u'reContent'])
            yield Request(nextPage, meta={u'item': dict(item)}, callback=self.parseReply)
        else:
            item[u'replynum'] = len(item[u'reContent'])
            yield item
