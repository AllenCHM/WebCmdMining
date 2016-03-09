#coding=utf-8
__author__ = 'AllenCHM'

import codecs
from lxml import etree

with codecs.open('tmp.html', 'r') as f:
    tmpHtml = f.read()

hxs = etree.HTML(tmpHtml)
divs = hxs.xpath('//div[@id="followCont"]/div[@title]')
for div in divs:
    id = div.xpath('./@id')[0]
    href = div.xpath('./@href')[0]
    name = div.xpath('./@title')[0].split(' ')[1]
    tt = div.xpath('.//div[@class="location"]')
    gender = tt[0].xpath('./span[1]/@title')[0]
    location = tt[0].xpath('./span[2]/@title')[0]

    print id
    print href
    print name
    print gender
    print location
    print