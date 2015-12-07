# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs


class AutohomePipeline(object):
    def __init__(self, crawler):
        self.file = codecs.open(u'%s.json' % crawler.spider.name, 'w', encoding='utf-8')

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler)
        return pipeline

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()
