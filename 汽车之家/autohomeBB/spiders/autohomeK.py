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


class AutohomeKSpider(Spider):
    name = "AutohomeK" #汽车之家_口碑
    allowed_domains = [u"autohome.com.cn",
                       ]
    start_urls = [
        u'http://k.autohome.com.cn/153',  #修改此处即可修改车型
    ]

    def __init__(self):
        self.host = u'http://k.autohome.com.cn'

    def parse(self, response):
        hxs = Selector(response)
        commentUrls = hxs.xpath('//div[@class="mouthcon js-koubeidataitembox"]//a[@class="orange"]/@href').extract() #获取评论主页
        for commentUrl in commentUrls:
            yield Request(commentUrl, callback=self.commentParse)
        nextPage = hxs.xpath('//a[@class="page-item-next"]/@href').extract() #获取评论下一页
        if nextPage and u'###' not in nextPage[0]:
            nextPage = self.host + nextPage[0]
            yield Request(nextPage, callback=self.parse)

    def commentParse(self, response):
        hxs = Selector(response)
        item = AutohomeItem()
        item[u"source"] = u'汽车之家'
        #发帖人账号
        item[u"author"] = hxs.xpath('//div[@class="mouth"]//div[@class="user-name"]/a/text()').extract()[0]
        #发帖人买车时间
        # tmp = hxs.xpath('//div[@class="choose-con"]//dd[@class="font-arial bg-blue"]/text()').extract()
        # if tmp:
        #     item[u'registerDate'] =tmp[0]
        # else:
        #     item[u'registerDate'] = None
        #购买车型
        tmp = hxs.xpath('//div[@class="choose-con"]/dl[1]//dd')[0].xpath('string(.)').extract()[0].strip().replace('\r\n', '')
        item[u'attention'] = tmp
        #购买地点
        tmp = hxs.xpath('//div[@class="choose-con"]/dl[2]//dd')[0].xpath('string(.)').extract()[0].strip().replace('\r\n', '')
        item[u'addr'] = tmp
        mouthItems = hxs.xpath('//div[@class="mouth-item"]')
        item[u"contentList"] = []
        for mouthItem in  mouthItems:
            content = {}
            #追加or口碑or质量
            kOd = mouthItem.xpath('.//div[@class="cont-title fn-clear"]//i[@class="icon icon-zj"]/text()').extract()
            #发帖时间
            tmp = mouthItem.xpath('./div/div/b/text()').extract()[0]
            tmp = re.findall(u'(.*?)年(.*?)月(.*?)日', tmp)
            content[u'recordDate'] = tmp[0][0] + u'-' + tmp[0][1] + u'-' + tmp[0][2]
            #发帖的内容
            if u'口碑' in kOd:
                tmp = mouthItem.xpath('./div[last()]').xpath('string(.)').extract()
                content[u'content'] = tmp[0].strip()
            elif u'质量' in kOd:
                tmp = mouthItem.xpath('.//div[@class="text-con qua-con"]').xpath('string(.)').extract()
                content[u'content'] = tmp[0].strip()
            else:
                tmp = mouthItem.xpath('.//dd[@class="add-dl-text"]').xpath('string(.)').extract()
                content[u'content'] = tmp[0].strip()
            item[u"contentList"].append(content)
        #帖子链接地址
        item[u'link'] = response.url
        #帖子点击数量
        tmp = hxs.xpath('//div[@class="help"]//span[@class="orange"]/text()').extract()
        item[u'clicknum'] = tmp[0]
        #帖子主题
        tmp = hxs.xpath('//div[@class="mouth-title-end over-hid"]//h1').xpath('string(.)').extract()
        item[u'title'] = tmp[0]
        #发帖的设备
        item[u'sourceEquipment'] = ''
        #帖子回复的内容
        objectId = re.findall('"objectId":"(.*?)",', response.body)[0]
        item[u'reContent'] = []
        tmp = self.ReplyJsonredis(response, objectId)
        if tmp:
            for reContent in tmp:
                tmpDict = {}
                tmpDict[u'content'] = reContent[u'RContent']
                tmpDict[u'RFloor'] = reContent[u'RFloor']
                tmpDict[u'author'] = reContent[u'RMemberName']
                t = reContent[u'RReplyDate']
                t = t.split('(')[-1].split('-')[0]
                t = time.localtime(float(t)/1000.0)
                tmpDict[u'recordDate'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
                tmpDict[u'sourceEquipment'] = reContent[u'SpType']
                if reContent.has_key(u'Quote'):
                    tmpDict[u'reContent'] = {}
                    tmpDict[u'reContent'][u'content'] = reContent[u'Quote'][u'RContent']
                    tmpDict[u'reContent'][u'RFloor'] = reContent[u'Quote'][u'RFloor']
                    tmpDict[u'reContent'][u'author'] = reContent[u'Quote'][u'RMemberName']
                    t = reContent[u'Quote'][u'RReplyDate']
                    t = t.split('(')[-1].split('-')[0]
                    t = time.localtime(float(t)/1000.0)
                    tmpDict[u'reContent'][u'recordDate'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
                    tmpDict[u'reContent'][u'sourceEquipment'] = reContent[u'Quote'][u'SpType']
                item[u'reContent'].append(tmpDict)
        #数据类型
        item[u'datatype'] = u'车主点评'
        #帖子回复数
        item[u'replynum'] = len(item[u'reContent'])
        #最后回帖时间或者点击时间
        if item[u"reContent"]:
            item[u'lastReDate'] = item[u"reContent"][0][u'recordDate']
        else:
            item[u'lastReDate'] = ''
        yield item

    def ReplyJsonredis(self, response, objectId,  page=1):
        params = {
            u'count': u'10',
            u'page': page,
            u'id': objectId,
            u'datatype': u'jsonp',
            u'appid': u'5',
            u'callback': u'jQuery17205774591560475528_'+str(int(time.time()*1000)),
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

