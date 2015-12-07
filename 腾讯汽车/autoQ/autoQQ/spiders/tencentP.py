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
from urllib import urlencode


reload(sys)
sys.setdefaultencoding('utf-8')
sys.setrecursionlimit(1000000)


class tencentPSpider(Spider):
    name = "tencentP" #腾讯汽车_评测
    # allowed_domains = [u".auto.qq.com",
    #                    ]
    start_urls = [
        u'http://auto.qq.com/evaluat.htm',  #修改此处即可修改车型
    ]

    def __init__(self):
        self.host = u'http://auto.qq.com'

    def parse(self, response):
        hxs = Selector(response)
        lis = hxs.xpath('//div[@class="newsList"]//ul[@id="LIST_LM"]/li')
        for div in lis:
            item = {}
            try:
                item[u'source'] = u'腾讯汽车'
                item[u'link'] = self.host + div.xpath('.//h3/a/@href').extract()[0]
                item[u'title'] = div.xpath('.//h3/a/text()').extract()[0]
                item[u'datatype'] = u'评测'
                yield Request(item[u'link'], meta={u'item': dict(item)}, callback=self.parseReferer)
            except:
                pass #该错误为最后评论栏引起

    def parseReferer(self, response):
        t = response.url.split('/')
        tmp = t[-1].split('.')
        tmp[0] += u'_all'
        t[-1] = u'.'.join(tmp)
        yield Request(u'/'.join(t), meta=response.meta, callback=self.parseReply)

    def parseReply(self, response):
        hxs = Selector(response)
        item = AutoqqItem()
        for i in response.meta[u'item'].keys():
            item[i] = response.meta[u'item'][i]

        item[u'reContent'] = []
        try:
            print response.url
            try:
                item[u'author'] = hxs.xpath('//span[@class="color-a-3"]/text()').extract()[0]
            except:
                pass
            item[u'recordDate'] = hxs.xpath('//span[@class="article-time"]/text()').extract()[0]
            item[u'content'] = hxs.xpath('//div[@bosszone="content"]').xpath('string(.)').extract()[0]
            id = re.findall('cmt_id = (.*?);', response.body)[0]
        except:
            try:
                try:
                    item[u'author'] = hxs.xpath('//span[@class="a_author"]/text()').extract()[0]
                except:
                    pass
                item[u'recordDate'] = hxs.xpath('//span[@class="a_time"]/text()').extract()[0]
                item[u'content'] = hxs.xpath('//div[@class="bd"]').xpath('string(.)').extract()[0]
                id = re.findall('cmt_id = (.*?);', response.body)[0]
            except:
                return
        url = u'http://coral.qq.com/article/' + id + u'/comment?'
        params = {
            u'commentid': 0,
            u'reqnum': 20,
            u'callback': u'mainComment',
            u'_': str(int(time.time()*1000)),
        }
        item["replynum"] = 0
        yield  Request(url+urlencode(params), meta={'item':dict(item)}, callback=self.parseComment)

    def parseComment(self, response):
        item = AutoqqItem()
        for i in response.meta[u'item'].keys():
            item[i] = response.meta[u'item'][i]
        if not response.meta[u'item'].has_key('reContent'):
            item[u'reContent'] = []
        r = re.findall('\((.*)\)', response.body, re.S)
        r = json.loads(r[0])
        if r[u'data'][u'reqnum']:
            for i in r[u'data'][u'commentid']:
                tmp = {}
                tmp[u'author'] = i[u'userinfo'][u'nick']
                tmp[u'content'] = i[u'content']
                tmp[u'sport'] = i[u'up']
                tmp[u'recordDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i[u'time']))
                tmp[u'addr'] = i[u'userinfo'][u'region']
                item[u'reContent'].append(tmp)
        num = len(item[u'reContent'])
        if num < r[u'data'][u'total'] and r[u'data'][u'hasnext']:
            t = r[u'data'][u'total'] - num
            if t >= 20:
                reqnum = 20
            else:
                reqnum = t
            params = {
                    u'commentid': r[u'data'][u'last'],
                    u'reqnum': reqnum,
                    # u'tag':0,
                    u'callback': u'mainComment',
                    u'_': str(int(time.time()*1000)),
                }
            url = response.url.split(u'?')[0] + u'?'
            yield Request(url+urlencode(params), meta={'item':dict(item)}, callback=self.parseComment)
        else:
            item[u'replynum'] = len(item[u'reContent'])
            # 最后回帖时间或者点击时间
            if item[u"reContent"]:
                item[u'lastReDate'] = item[u"reContent"][0][u'recordDate']
            else:
                item[u'lastReDate'] = ''
            yield item