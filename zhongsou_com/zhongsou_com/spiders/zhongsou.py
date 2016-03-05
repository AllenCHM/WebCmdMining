#coding=utf-8
__author__ = 'AllenCHM'
#
#      楚金所--新手项目
#
import pymongo
from scrapy.http import Request
from  scrapy.spiders import Spider
from scrapy.selector import Selector
import redis
import time
import re
import subprocess

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class ZhongSouSpider(Spider):
    name = 'Zhongsou'
    start_urls = [
        u'http://t.zhongsou.com/people.html',
        u'http://t.zhongsou.com/people/YL/YL.html',
        u'http://t.zhongsou.com/people/TY/TY.html',
        u'http://t.zhongsou.com/people/QC/QC.html',
        u'http://t.zhongsou.com/people/LY/LY.html',
        u'http://t.zhongsou.com/people/CY/CY.html',
        u'http://t.zhongsou.com/people/YX/YX.html',
        u'http://t.zhongsou.com/people/FC/FC.html',
        u'http://t.zhongsou.com/people/CJ/CJ.html',
        u'http://t.zhongsou.com/people/DZSW/DZSW.html',
        u'http://t.zhongsou.com/people/HLW/HLW.html',
        u'http://t.zhongsou.com/people/YS/YS.html',
        u'http://t.zhongsou.com/people/WH/WH.html',
        u'http://t.zhongsou.com/people/KJ/KJ.html',
        u'http://t.zhongsou.com/people/ZZ/ZZ.html',
        u'http://t.zhongsou.com/people/SH/SH.html',
        u'http://t.zhongsou.com/people/JS/JS.html',
        u'http://t.zhongsou.com/people/SP/SP.html',
        u'http://t.zhongsou.com/people/JK/JK.html',
        u'http://t.zhongsou.com/people/JY/JY.html',
        u'http://t.zhongsou.com/people/ZR/ZR.html',
        u'http://t.zhongsou.com/people/LS/LS.html',
    ]

    def __init__(self, **kwargs):
        self.connection=pymongo.MongoClient(host='192.168.2.165', port=27017)
        self.db = self.connection['wss']
        self.zhongsou = self.db['zhongsou']
        self.redisConnHash = redis.Redis(u'192.168.3.133', port=6379, db=3)
        self.count = 0

    def parse(self, response):
        hxs = Selector(response)
        tuij_list_lis = hxs.xpath('//div[contains(@class, "main_scenery")]//li')
        for li in tuij_list_lis:
            name = li.xpath('.//a/@title').extract()[0]
            url = li.xpath('.//a/@href').extract()[0]
            yield Request(url, meta={u'name':name}, callback=self.parsePerson)

        ysmx_more = hxs.xpath('//div[@class="ysmx_more"]/a/@href').extract()
        for url in ysmx_more:
            yield Request(url, callback=self.parse)

        nextPage = hxs.xpath('//a[@class="com_page"]/@href').extract()
        if nextPage:
            for i in nextPage:
                yield Request(i, callback=self.parse)


    def parsePerson(self, response):
        hxs = Selector(response)
        url = hxs.xpath('//div[contains(@class, "blogger_add")]/a/@href').extract()[0]
        if u'weibo.com' not in url:
            return
        item = {}
        item[u'name'] = response.meta[u'name']
        item[u'url'] = url
        bloggertj = hxs.xpath('//div[contains(@class, "bloggertj")]/div')
        item[u'关注数'] = bloggertj[0].xpath('string(.)').extract()[0]
        item[u'粉丝数'] = bloggertj[1].xpath('string(.)').extract()[0]
        item[u'微博'] = bloggertj[2].xpath('string(.)').extract()[0]
        self.zhongsou.update({u'url':item[u'url']}, item, True)


    def closed(self, reason):
        self.connection.close()