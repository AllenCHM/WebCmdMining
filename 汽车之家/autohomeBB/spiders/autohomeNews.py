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
from autohomeBB.items import AutohomeItem

reload(sys)
sys.setdefaultencoding('utf-8')


class AutohomeNewsSpider(Spider):
    name = "autohomeNews" #该爬虫针对评测文章
    allowed_domains = ["autohome.com.cn",
                       ]
    start_urls = [
        'http://www.autohome.com.cn/153/3/0-0-1-0/',  #修改此处即可修改车型
    ]

    def __init__(self):
        self.host = u'http://k.autohome.com.cn'

    def parse(self, response):
        hxs = Selector(response)
        lis = hxs.xpath('//div[@class="cont-info"]//li')
        for li in lis:
            h3 = li.xpath('.//h3/a/@href').extract()[0]
            page = h3.split('/')
            allContent = page[-1].split('.')
            id = allContent[0]
            allContent[0] += u'-all'
            allContent = '.'.join(allContent)
            page[-1] = allContent
            pageUrl = '/'.join(page)
            num = li.xpath('.//p[@class="name-tx"]/span[3]').xpath('string(.)').extract()[0]
            #直接阅读全文
            yield Request(pageUrl, meta={u'num': num, 'id':id}, callback=self.pageParse)
        #获取下一页的链接
        nextPage = hxs.xpath('//a[@class="page-item-next"]/@href').extract()
        if nextPage:
            yield Request(nextPage[0], callback=self.parse)

    def pageParse(self,response):
        hxs = Selector(response)
        item = AutohomeItem()
        item[u"source"] = u'汽车之家'
        try:
            #发帖人
            item[u"author"] = hxs.xpath('//div[@class="article-info"]/span[4]/a/text()').extract()[0].strip()
        except:
            #发帖人
            item[u"author"] = hxs.xpath('//div[@class="article-info"]/span[4]/text()').extract()[0].split(u'：')[-1].strip()
         #发帖时间
        tmp = hxs.xpath('//div[@class="article-info"]/span[1]/text()').extract()[0].strip()
        tmp = re.findall(u'(.*?)年(.*?)月(.*?)日(.*)', tmp)
        item[u"recordDate"] = tmp[0][0] + u'-' + tmp[0][1] + u'-' + tmp[0][2] + tmp[0][3]
        #评测内容
        item[u"content"] = hxs.xpath('//div[@class="article-content"]').xpath('string(.)').extract()[0].strip()
        #帖子链接地址
        item[u'link'] = response.url
        #帖子点击数量
        item[u'clicknum'] = response.meta[u'num']
        #帖子主题
        item[u'title'] = hxs.xpath('//h1').xpath('string(.)').extract()[0].strip()
        #发帖的设备
        item[u'sourceEquipment'] = ''
        #帖子回复的内容
        item[u'reContent'] = []
        tmp = self.ReplyJsonredis(response, response.meta['id'])
        if tmp:
            for reContent in tmp:
                tmpDict = {}
                #回复内容
                tmpDict[u'content'] = reContent[u'RContent'].strip()
                #回复楼层
                tmpDict[u'RFloor'] = reContent[u'RFloor']
                #回复人
                tmpDict[u'author'] = reContent[u'RMemberName']
                #回复时间
                tmp = reContent[u'RReplyDate']
                t = tmp.split('(')[-1].split('-')[0]
                t = time.localtime(float(t)/1000.0)
                tmpDict[u'recordDate']  = time.strftime('%Y-%m-%d %H:%M:%S', t)
                #使用设备
                tmpDict[u'sourceEquipment'] = reContent[u'SpType']
                if reContent.has_key(u'Quote'):
                    tmpDict[u'reContent'] = {}
                    #该回复针对楼层回复内容
                    tmpDict[u'reContent'][u'content'] = reContent[u'Quote'][u'RContent']
                    #该回复针对楼层号
                    tmpDict[u'reContent'][u'RFloor'] = reContent[u'Quote'][u'RFloor']
                    #该回复针对楼层回复人
                    tmpDict[u'reContent'][u'author'] = reContent[u'Quote'][u'RMemberName']
                    #该回复针对楼层回复时间
                    tmp = reContent[u'Quote'][u'RReplyDate']
                    t = tmp.split('(')[-1].split('-')[0]
                    t = time.localtime(float(t)/1000.0)
                    tmpDict[u'reContent'][u'recordDate'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
                    #该回复针对楼层回复使用设备
                    tmpDict[u'reContent'][u'sourceEquipment'] = reContent[u'Quote'][u'SpType']
                item[u'reContent'].append(tmpDict)
        #数据类型
        item[u'datatype'] = u'评测'
        #帖子回复数
        item[u'replynum'] = len(item[u'reContent'])
        if item[u"reContent"]:
            #最后回帖时间或者点击时间
            item[u'lastReDate'] = item[u"reContent"][0][u'recordDate']
        else:
            #最后回帖时间或者点击时间
            item[u'lastReDate'] = ''
        yield item

    def ReplyJsonredis(self, response, objectId,  page=1):
        params = {
            u'count': u'10',
            u'page': page,
            u'id': objectId,
            u'datatype': u'jsonp',
            u'appid': '1',
            u'callback': u'jQuery172016438238229602575_'+str(int(time.time()*1000)),
            u'_': str(int(time.time()*1000)),
        }
        headers = {
            u'User-Agent':u'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',
        }
        r = requests.get(u'http://reply.autohome.com.cn/ShowReply/ReplyJsonredis.ashx', params=params, headers=headers)
        r = r.content.decode('gb2312').encode('utf-8')
        r = re.findall('\((.*)\)', r, re.S)
        r = json.loads(r[0])
        commentlist = r[u'commentlist']
        if page*10 < r[u'commentcount']:
            tmp = self.ReplyJsonredis(response, objectId, page+1)
            commentlist.extend(tmp)
        return commentlist