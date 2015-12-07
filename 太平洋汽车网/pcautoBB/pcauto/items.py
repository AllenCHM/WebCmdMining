# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PcautoItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field()
    author = scrapy.Field()
    registerDate = scrapy.Field()
    recordDate = scrapy.Field()
    attention = scrapy.Field()
    addr = scrapy.Field()
    content = scrapy.Field()
    link = scrapy.Field()
    clicknum = scrapy.Field()
    title = scrapy.Field()
    sourceEquipment = scrapy.Field()
    reContent = scrapy.Field()
    datatype = scrapy.Field()
    replynum = scrapy.Field()
    lastReDate = scrapy.Field()