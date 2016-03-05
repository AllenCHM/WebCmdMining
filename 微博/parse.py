#coding=utf-8
__author__ = 'AllenCHM'

import codecs
from lxml import etree
import urlparse
import re
import pymongo

c = []

def getAttention():
    with codecs.open('3.html', u'r', 'utf-8') as f:
        t = f.read()
        # $CONFIG['onick']='凯德印象';
        user = re.findall('\$CONFIG\[\'onick\'\]=\'(.*?)\';', t)[0]
        uid = re.findall('\$CONFIG\[\'oid\'\]=\'(.*?)\';', t)[0]
        item = {}
        item[u'user'] = user
        item[u'uid'] = uid
        item[u'attentions'] = []
        hxs = etree.HTML(t)
        lis = hxs.xpath('//ul[@class="follow_list"]/li')
        for li in lis:
            t = {}
            name = li.xpath('.//dt[@class="mod_pic"]/a/@title')[0]
            userHref = urlparse.urlsplit(li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@href')[0]).path
            try:
                addr = li.xpath('.//div[@class="info_add"]/span/text()')[0]
                id = li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@usercard')[0].split('&')[0][3:]
            except:
                continue
            t[u'user'] = name
            t[u'uid'] = id
            t[u'userHref'] = userHref
            t[u'addr'] = addr
            item[u'attentions'].append(t)
    return item

def getFollow():
    with codecs.open('3.html', u'r', 'utf-8') as f:
        t = f.read()
        user = re.findall('\$CONFIG\[\'onick\'\] = \'(.*?)\';', t)[0]
        uid = re.findall('\$CONFIG\[\'uid\'\] = \'(.*?)\';', t)[0]
        item = {}
        item[u'user'] = user
        item[u'uid'] = uid
        item[u'follows'] = []
        hxs = etree.HTML(t)
        lis = hxs.xpath('//ul[@node-type="userListBox"]/li')
        for li in lis:
            t = {}
            name = li.xpath('.//dt[@class="mod_pic"]/a/@title')[0]
            userHref = urlparse.urlsplit(li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@href')[0]).path
            try:
                addr = li.xpath('.//div[@class="info_add"]/span/text()')[0]
                id = li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@usercard')[0].split('&')[0][3:]
            except:
                continue
            t[u'user'] = name
            t[u'uid'] = id
            t[u'userHref'] = userHref
            t[u'addr'] = addr
            item[u'follows'].append(t)
    return item

i = getAttention()
print()
