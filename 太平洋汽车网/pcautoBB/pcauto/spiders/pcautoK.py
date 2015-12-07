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

from pcauto.items import PcautoItem

reload(sys)
sys.setdefaultencoding('utf-8')


class pcautoKSpider(Spider):
    name = u"pcautoK"
    allowed_domains = [u"pcauto.com.cn",
                       ]
    start_urls = [
        u'http://price.pcauto.com.cn/comment/sg164/',  #修改此处即可修改车型
    ]

    def __init__(self):
        self.host = u'http://price.pcauto.com.cn/comment/sg164/p'

    def parse(self, response):
        hxs = Selector(response)
        mainBodys = hxs.xpath('//div[@class="main_table clearfix"]')
        if mainBodys:
            for mainBody in mainBodys:
                item = PcautoItem()
                item[u"source"] = u'太平洋汽车网'
                item[u"author"] = mainBody.xpath('.//div[@class="info"]/a/text()').extract()[0].strip()
                tmp = mainBody.xpath('.//div[@class="car"]/div[2]/span[2]/text()').extract()[0].strip()
                tmp = re.findall(u'(.*?)年(.*?)月', tmp)
                item[u"registerDate"] = tmp[0][0] + u'-' + tmp[0][1]
                item[u"recordDate"] = mainBody.xpath('.//div[@class="info"]/p/a/text()').extract()[0].strip()[:-2]
                item[u"attention"] = mainBody.xpath('.//div[@class="car"]/div[1]/span[2]/a/text()').extract()[0].strip()
                item[u"addr"] = mainBody.xpath('.//div[@class="car"]/div[3]/span[2]/text()').extract()[0].strip()
                item[u"content"] = mainBody.xpath('.//div[@class="table_text clearfix"]').xpath('string(.)').extract()[0].strip()
                item[u"link"] = mainBody.xpath('.//a[@data-event="toggleComment"]/@data-url').extract()[0]
                tmp = mainBody.xpath('.//div[@class="corners"]/a[contains(@class,"good")]/em/text()').extract()
                if tmp:
                    item[u"clicknum"] = re.findall('\((.*)\)', tmp[0])[0]
                else:
                    item[u"clicknum"] = 0
                # item[u"title"] = ''
                # item[u"sourceEquipment"] = ''
                item[u"reContent"] = self.reViewParse(item[u'link'])
                item[u"datatype"] = u'车主点评'
                item[u"replynum"] = len(item[u'reContent'])
                if item[u'reContent']:
                    item[u"lastReDate"] = item[u'reContent'][0][u'recordDate']
                else:
                    item[u"lastReDate"] = item[u"recordDate"]
                yield item

        nextPage = hxs.xpath('//div[@class="pcauto_page"]/a[@class="next"]') #下一页
        if nextPage:
            nextPage = nextPage.extract()[0]
            pageNum = re.findall('goCommentPage\((.*?)\)', nextPage)[0]
            nextPage = self.host + str(pageNum) + u'.html'
            yield Request(nextPage, callback=self.parse)


    def reViewParse(self, link):
        params = {
                    u'urlHandle': u'1',
                    u'url': link,
                    u'pageSize': u'5',
                    u'callback': u'jsonpdplg3qg',
                }
        url = u'http://cmt.pcauto.com.cn/action/comment/list_new_json.jsp'
        r = requests.get(url, params=params)
        try:
            tmp = re.findall(u'\((.*)\)', r.content)[0]
            tmp = json.loads(tmp)
            t = []
            for i in tmp[u'data']:
                data = {}
                data[u'content'] = i[u'content']
                data[u'recordDate'] = i[u'createTime']
                data[u'author'] = i[u'nickName']
                t.append(data)
            return t
        except:
            return []


