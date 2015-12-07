# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

import json
import sys
import time
import re

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, Response, TextResponse
import requests

from pcauto.items import PcautoItem

reload(sys)
sys.setdefaultencoding('utf-8')


class pcautoCSpider(Spider):
    name = u"pcautoC"  #评论数据源同车主点评
    allowed_domains = [u"pcauto.com.cn",
                       ]
    start_urls = [
        u'http://bbs.pcauto.com.cn/forum-17468.html/',
    ]

    def __init__(self):
        self.host = u'http://price.pcauto.com.cn/comment/sg164/p'

    def parse(self, response):
        hxs = Selector(response)
        tbodys = hxs.xpath('//table[@class="data_table"]//tbody')
        detail = {}
        ids = ''
        fid = response.url.split('-')[-1].split('.')[0]
        url = u'http://bbs.pcauto.com.cn/forum/loadStaticInfos.ajax'
        id = hxs.xpath('//td[@class="nums"]/em/@class').extract()[0]
        id = re.findall('(\d*) ', id)
        ids = ','.join(id)
        params = {
            'isBrandForum': 'true',
            'tids': ids,
            'fid': fid
        }
        r = requests.get(url=url, params=params)
        tmp = r.json()
        viewInfo ={}
        for i in tmp[u"topicViews"]:
            viewInfo[u'tid'] = i[u'view']
        for tbody in tbodys:
            try:
                tmp = tbody.extract()
                id = tbody.xpath('.//td[@class="nums"]/em/@class').extract()[0]
                id = re.findall('(\d*) ', id)[0]
                t = str(id)
                detail[t] = {}
                detail[t][u'title'] = tbody.xpath('.//th[@class="title"]//a[contains(@class, "topicurl")]/text()').extract()[0]
                detail[t][u'link'] = tbody.xpath('.//th[@class="title"]//a[contains(@class, "topicurl")]/@href').extract()[0]
                detail[t][u'user'] = tbody.xpath('.//td[@class="author"]/cite/a/text()').extract()[0]
                detail[t][u'recordDate'] = tbody.xpath('.//td[@class="author"]/em/text()').extract()[0]
                detail[t][u'replynum'] = tbody.xpath('.//td[@class="nums"]/cite/text()').extract()[0].strip()
                detail[t][u'view'] = viewInfo[u'tid']
                detail[t][u'lastReDate'] = tbody.xpath('.//td[@class="lastpost"]/em/text()').extract()[0].strip()
            except:
                pass
        for i in detail.keys():
            yield Request(detail[i][u'link'], meta={u'detail': detail[i]}, callback=self.parseInfo)
        nextPage = hxs.xpath('//a[@class="next"]/@href').extract()
        if nextPage:
            yield Request(nextPage[0], callback=self.parse)

    def parseInfo(self, response):
        hxs = Selector(response)
        item = PcautoItem()
        item[u"source"] = u'太平洋汽车网'
        item[u"author"] = response.meta[u'detail'][u'user']
        item[u"recordDate"] = response.meta[u'detail'][u'recordDate']
        item[u"content"] = hxs.xpath(u'//div[@class="post_msg replyBody"][1]/text()').extract()[0].strip()
        item[u"link"] = response.meta[u'detail'][u'link']
        item[u"title"] = response.meta[u'detail'][u'title']
        # item[u"sourceEquipment"] = ''
        item[u"reContent"] = self.reViewParse(response)
        item[u"datatype"] = u'论坛'
        item[u"replynum"] = response.meta[u'detail'][u'replynum']
        if item[u"reContent"]:
            item[u'lastReDate'] = item[u"reContent"][-1][u'recordDate']
        else:
            item[u'lastReDate'] = ''
        yield item
        nextPage = hxs.xpath('//div[@class="pcauto_page"]/a[@class="next"]') #下一页
        if nextPage:
            nextPage = nextPage.extract()[0]
            pageNum = re.findall('goCommentPage\((.*?)\)', nextPage)[0]
            nextPage = self.host + str(pageNum) + u'.html'
            yield Request(nextPage, callback=self.parse)



    def reViewParse(self, response):
        try:
            hxs = Selector(response)
        except:
            hxs = Selector(text=response.text)
        reViews = hxs.xpath('//div[contains(@class, "post_wrap")]')
        reContent = []
        ids = hxs.xpath('//div[contains(@class, "user_info")]/@authorid').extract()
        ids = u','.join(ids)
        try:
            fid = re.findall('fid=(\d.*?)\'', response.body)[0]
        except:
            try:
                fid = re.findall('fid=(\d.*?)\'', response.text)[0]
            except:
                return reContent
        tid = response.url.split('.')[-2].split('-')[1]
        params = {
            'isBrandForum': 'true',
            'vids': ids,
            'fid': fid,
            'tid': tid,
        }
        url = u'http://bbs.pcauto.com.cn/topic/loadStaticInfos.ajax'
        r = requests.get(url, params=params)
        vipInfo = {}
        for i in r.json()[u"vipInfo"]:
            vipInfo[str(i[u'vipid'])] = i[u'serialname'] + u' ' + i[u'modelname']
        if reViews:
            for reView in reViews:
                item = {}
                #帖子被删或被屏蔽了 , 处理为抛弃
                try:
                    item[u"author"] = reView.xpath('.//p[contains(@class, "uName")]/a[1]/text()').extract()[0]
                    item[u"content"] = reView.xpath('.//div[contains(@class, "post_msg replyBody")]').xpath('string(.)').extract()[0].strip()
                    item[u"recordDate"] = reView.xpath('.//div[contains(@class, "post_time")]/text()').extract()[0].strip()[4:]
                    item[u"floor"] = reView.xpath('.//div[contains(@class, "post_floor")]').xpath('string(.)').extract()[0].strip()
                    lis = reView.xpath('.//div[contains(@class, "user_info")]/ul/li')
                    for li in lis:
                        tmp = li.xpath('string(.)').extract()[0].strip()
                        try:
                            a, b = tmp.split(u'：')
                            if a == u'用户':
                                pass
                            elif a == u'地区':
                                item['addr'] = b.strip()
                            elif a == u'爱车':
                                tmp = reView.xpath('.//div[contains(@class, "user_info")]/@authorid').extract()[0]
                                item['attention'] = vipInfo[str(tmp)]
                        except:
                            pass
                    try:
                        item[u"sourceEquipment"] = reView.xpath('.//div[contains(@class, "post_edition")]/a').xpath('string(.)').extract()[0].strip()
                    except:
                        pass
                    reContent.append(item)
                except:
                    pass

        nextPage = hxs.xpath('//a[@class="next"]/@href').extract()
        if nextPage:
            header = {
                'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
                'Referer':response.url
            }
            time.sleep(10)
            r = requests.get(nextPage[0], headers=header)
            reContent.extend(self.reViewParse(r))
        return reContent
