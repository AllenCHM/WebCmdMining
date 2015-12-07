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


class pcautoPSpider(Spider):
    name = u"pcautoP"  #评论数据源同车主点评
    allowed_domains = [u"pcauto.com.cn",
                       ]
    start_urls = [
        u'http://www.pcauto.com.cn/pingce/tiyan/',  #新车试驾
        u'http://www.pcauto.com.cn/pingce/yc/',      #专业评测
        u'http://www.pcauto.com.cn/pingce/dbpc/',  #对比评测
        u'http://www.pcauto.com.cn/pingce/cqcs/',  #长期测试
    ]

    def __init__(self):
        self.host = u'http://price.pcauto.com.cn/comment/sg164/p'

    def parse(self, response):
        hxs = Selector(response)
        divs = hxs.xpath('//div[@class="pic-txt clearfix"]')
        print len(divs)
        for div in divs:
            detail = {}
            detail[u'title'] = div.xpath('.//div[@class="txt"]/p[1]/a/text()').extract()[0]
            tmp = div.xpath('.//div[@class="txt"]/p[1]/a/@href').extract()[0]
            page = tmp.split('/')
            allContent = page[-1].split('.')
            id = allContent[0]
            allContent[0] += u'_all'
            allContent = '.'.join(allContent)
            page[-1] = allContent
            pageUrl = '/'.join(page)
            detail[u'link'] = pageUrl
            detail[u'href'] = tmp
            detail[u'id'] = id
            detail[u'time'] = div.xpath('.//div[@class="txt"]/p[2]/span[1]').xpath('string(.)').extract()[0]
            detail[u'user'] = div.xpath('.//div[@class="txt"]/p[2]/span[2]').xpath('string(.)').extract()[0].strip()
            tmp = div.xpath('.//div[@class="txt"]/p[2]/span[3]').xpath('string(.)').extract()[0]
            try:
                detail[u'replynum'] = re.findall('>(.*?)</a>', tmp)[0]
            except:
                detail[u'replynum'] = 0
            yield Request(detail[u'link'], meta={'detail': detail}, callback=self.parseInfo)
        nextPage = hxs.xpath('//a[@class="next"]/@href').extract()
        if nextPage:
            yield Request(nextPage[0], callback=self.parse)


    def parseInfo(self, response):
        hxs = Selector(response)
        item = PcautoItem()
        item[u"source"] = u'太平洋汽车网'
        item[u"author"] = response.meta[u'detail'][u'user']
        item[u"recordDate"] = response.meta[u'detail'][u'time']
        item[u"content"] = hxs.xpath('.//div[@class="artText clearfix"]').xpath('string(.)').extract()[0].strip()
        item[u"link"] = response.meta[u'detail'][u'link']
        item[u"title"] = response.meta[u'detail'][u'title']
        # item[u"sourceEquipment"] = ''
        item[u"reContent"] = self.reViewParse(response.meta[u'detail'][u'href'])
        item[u"datatype"] = u'评测'
        item[u"replynum"] = response.meta[u'detail'][u'replynum']
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


    def reViewParse(self, link, urlHandle=1, pageSize=40):
        params = {
                    u'urlHandle': urlHandle,
                    u'url': link,
                    u'pageSize': pageSize,
                    u'callback': u'jsonpqjtk9io',
                }
        url = u'http://cmt.pcauto.com.cn/action/comment/list_new_json.jsp'
        r = requests.get(url, params=params)
        tmp = re.findall(u'\((.*)\)', r.content)[0]
        tmp = json.loads(tmp)
        t = []
        for i in tmp[u'data']:
            data = {}
            data[u'content'] = i[u'content']
            data[u'recordDate'] = i[u'createTime']
            data[u'author'] = i[u'nickName']
            data[u'floor'] = i[u'floor']
            data[u'ip'] = i[u'ip']
            data[u'sourceEquipment'] = i[u'client']
            data[u'support'] = i[u'support']
            if i.has_key(u'replyRef'):
                data[u'reContent'] = {}
                data[u'reContent'][u'content'] = i[u'replyRef'][u'content']
                data[u'reContent'][u'author'] = i[u'replyRef'][u'nickName']
                data[u'reContent'][u'ip'] = i[u'replyRef'][u'ip']
                data[u'reContent'][u'recordDate'] = i[u'replyRef'][u'createTime']
                data[u'reContent'][u'support'] = i[u'replyRef'][u'support']
                data[u'reContent'][u'sourceEquipment'] = i[u'replyRef'][u'client']
            t.append(data)
        if urlHandle < tmp[u'pageCount']:
            urlHandle += 1
            if urlHandle == tmp[u'pageCount']:
                pageSize = tmp[u'total'] - (urlHandle-1)*30
            else:
                pageSize = 30
            t.extend(self.reViewParse(link, urlHandle+1, pageSize))
        return t


