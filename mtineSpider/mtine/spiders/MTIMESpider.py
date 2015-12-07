# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'


from  scrapy.spider import BaseSpider
from  scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from mtine.items import MtineItem
import requests
from urllib import quote
from time import time
import re
import pymysql
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class MtimeSpider(BaseSpider):
    name = 'mtimeSpider'
    allowed_domains = ['mtime.com']

    def __init__(self):
        self.connection = pymysql.connect(host='192.168.1.165',
                                 port= 3306,
                                 user='root',
                                 passwd='yourpass',
                                 charset='utf8mb4',
                                 db='mtime')
        self.cursor = self.connection.cursor()

# http://movie.mtime.com/movie/search/section/#pageIndex=1&initialcn=1_B
    def start_requests(self):
        return [Request("http://movie.mtime.com",
                               callback=self.parseUrls)]

    def parseUrls(self, response):
        # for i in xrange(10000,250000):
        for i in xrange(10000,10001):
            if self.cursor.execute(''' SELECT name FROM movie WHERE id = (%s)''', (i)) != 0:
                continue
            # yield Request('http://service.channel.mtime.com/service/search.mcs?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Pages.SearchService&Ajax_CallBackMethod=SearchMovieByCategory&Ajax_CrossDomain=2&Ajax_RequestUrl=http%3A%2F%2Fmovie.mtime.com%2Fmovie%2Fsearch%2Fsection%2F%23&' + \
            #             'Ajax_CallBackArgument13=1&Ajax_CallBackArgument14=' +param + '&Ajax_CallBackArgument16=1&Ajax_CallBackArgument17=4&Ajax_CallBackArgument18=1', callback=self.parseUrl)
            yield Request('http://movie.mtime.com/' + str(i), callback=self.parseUrl)

    def parseUrl(self, response):
        hxs = HtmlXPathSelector(response)
        title = hxs.select('//title/text()').extract()[0]
        if u'很抱歉，你要访问的页面不存在' == title:
            return
        id = response.url.split('/')[3]
        title = title.replace('\'', ' ')
        item = MtineItem()
        item["name"] = title
        item["id"] = id
        yield item