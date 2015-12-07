# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

import json
import sys
import time
import re

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import requests

from autohomeBB.items import AutohomeItem

reload(sys)
sys.setdefaultencoding('utf-8')


class AutohomeClubSpider(Spider):
    name = u"autohomeClub"
    allowed_domains = [u"autohome.com.cn",
                       ]
    start_urls = [
        u'http://club.autohome.com.cn/bbs/forum-c-153-1.html?orderby=dateline&qaType=-1',  #修改此处即可修改车型
    ]

    def __init__(self):
        self.host = u'http://club.autohome.com.cn'

    def parse(self, response):
        hxs = Selector(response)
        postUrls = hxs.xpath('//dl[@class="list_dl bluebg"][2]/following-sibling::*') #获取评论主页
        ids = ''
        postDetails = {}
        for postUrl in postUrls:
            postDetail = {}
            try:
                postDetail[u'link'] = self.host + postUrl.xpath('./dt/a/@href').extract()[0]
                postDetail[u'title'] = postUrl.xpath('./dt/a/text()').extract()[0].strip()
                postDetail[u'author'] = postUrl.xpath('./dd/a/text()').extract()[0].strip()
                postDetail[u'pubDate'] = postUrl.xpath('./dd[1]/span/text()').extract()[0].strip()
                postDetail[u'id'] = postUrl.xpath('./dd[2]/@lang').extract()[0].strip()
                ids += postDetail[u'id'] + u'%2C'
                postDetail[u'clicknum'] = ''
                postDetail[u'lastReDate'] = postUrl.xpath('./dd[3]/span/text()').extract()[0].strip()
                postDetails[postDetail[u'id']] = postDetail
            except Exception, e:
                pass
        headers = {'User-Agent':'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',}
        url = u'http://club.ajax.autohome.com.cn/topic/rv?fun=jsonprv&callback=jsonprv&ids=' + ids + u'&callback=jsonprv&_=' + str(int(time.time()*1000))
        r = requests.get(url, headers=headers)
        r = r.content.decode(u'gb2312').encode(u'utf-8')
        rv = re.findall('\((.*)\)', r, re.S)[0]
        rv = json.loads(rv)
        for k in rv:
            postDetails[str(k[u"topicid"])][u'clicknum'] = k[u'views']
            postDetails[str(k[u"topicid"])][u'replynum'] = k[u'replys']
            tmp = postDetails[str(k[u"topicid"])]
            yield Request(url=tmp[u'link'], meta={u'detail':tmp}, callback=self.pageParse)

        nextPage = hxs.xpath('//a[@class="afpage"]/@href').extract() #获取评论下一页
        if nextPage:
            nextPage = self.host + nextPage[0]
            yield Request(nextPage, callback=self.parse)

    def pageParse(self, response):
        hxs = Selector(response)
        item = AutohomeItem()
        contstxts = hxs.xpath('//div[@class="clearfix contstxt outer-section"]')
        tmp = contstxts[0].extract()
        tmp = re.findall(u'注册：(.*?)<', tmp, re.S)
        tmp = re.findall(u'(.*?)年(.*?)月(.*?)日', tmp[0])
        item[u"registerDate"] = tmp[0][0] + u'-' + tmp[0][1] + u'-' + tmp[0][2]
        item[u"source"] = u'汽车之家'
        #数据类型
        item[u'datatype'] = u'论坛'
        item[u"author"] = response.meta[u"detail"][u'author'] #发帖人账号
        #购买车型
        try:
            tmp = contstxts[0].xpath('//ul[@class="leftlist"]/li[7]/a[2]/@title').extract()
            item[u'attention'] = tmp[0]
        except:
            tmp = contstxts[0].xpath('//ul[@class="leftlist"]/li[7]/a/@title').extract()
            item[u'attention'] = tmp[0]
        #购买地点
        tmp = contstxts[0].xpath('//ul[@class="leftlist"]/li[6]/a[1]/text()').extract()
        try:
            item[u'attention'] = tmp[0]
        except:
            print()
        #发帖的设备
        try:
            tmp = contstxts[0].xpath('.//div[@class="plr26 rtopcon"]/span[3]/a/text()').extract()
            item[u'sourceEquipment'] = tmp[0]
        except:
            pass
        #发帖时间
        item[u'recordDate'] = response.meta[u'detail'][u'pubDate']
        #帖子主题
        item[u'title'] = response.meta[u'detail'][u'title']
        #帖子链接地址
        item[u'link'] = response.meta[u'detail'][u'link']
        #帖子回复数
        item[u'replynum'] = response.meta[u'detail'][u'replynum']
        #帖子点击数量
        item[u'clicknum'] = response.meta[u'detail'][u'clicknum']
        #最后回帖时间或者点击时间
        item[u'lastReDate'] = response.meta[u'detail'][u'lastReDate']
        #发帖的内容
        tmp = contstxts[0].xpath('.//div[@class="conttxt"]').xpath('string(.)').extract()
        item[u'content'] = tmp[0].strip()
        #帖子回复的内容
        item[u'reContent'] = []
        divs = hxs.xpath('//div[@id="maxwrap-reply"]//div[@class="clearfix contstxt outer-section"]')
        for div in divs:
            tmpDict = {}
            tmpDict[u"author"] =div.xpath('.//li[@class="txtcenter fw"]/a/text()').extract()[0]
            try:
                tmpDict[u'content'] = div.xpath('.//div[@xname="content"]/div/div[last()]').xpath('string(.)').extract()[0]
                if not tmpDict[u'content']:
                    raise
            except:
                try:
                    tmpDict[u'content'] = div.xpath('.//div[@class="rconten"]/div[last()]/div/div[last()]/text()').extract()[0]
                    if not tmpDict[u'content']:
                        raise
                except:
                    try:
                        tmpDict[u'content'] = div.xpath('.//div[@class="w740"]').xpath('string(.)').extract()[0]
                        if not tmpDict[u'content']:
                            raise
                    except:
                        try:
                            tmpDict[u'content'] = div.xpath('.//div[@class="promptcons"]/text()').extract()[0]
                            if not tmpDict[u'content']:
                                raise
                        except:
                            pass
            tmpDict[u'RFloor'] = div.xpath('.//div[@class="fr"]/a/@rel').extract()[0]
            try:
                tmpDict[u'sourceEquipment'] = div.xpath('.//div[@class="plr26 rtopconnext"]/span[3]/a/text()').extract()[0]
            except:
                pass
            tmpDict[u'recordDate'] = div.xpath('.//div[@class="plr26 rtopconnext"]/span[2]/text()').extract()[0]
            try:
                relyhf = div.xpath('.//div[@class="relyhf"]')
                if relyhf:
                    tmpDict[u'reContent'] = {}
                    tmpDict[u'reContent'][u'content'] = relyhf.xpath('./div[@class="relyhfcon"]/p[2]').xpath('string(.)').extract()[0]
                    tmpDict[u'reContent'][u'RFloor'] = relyhf.xpath('./div[@class="relyhfcon"]/p[1]/a[2]/text()').extract()[0]
                    tmpDict[u'reContent'][u'author'] = relyhf.xpath('./div[@class="relyhfcon"]/p[1]/a[1]/text()').extract()[0]
                    tmpDict[u'reContent'][u'recordDate'] = relyhf.xpath('./div[@class="relyhfcon"]/p[1]/text()').extract()[0].replace(u' 发表在 ', '')
            except:
                pass
            item[u'reContent'].append(tmpDict)
        yield item


