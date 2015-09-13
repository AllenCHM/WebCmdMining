# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class MtinePipeline(object):
    def __init__(self):
        self.connection = pymysql.connect(host='192.168.1.165',
                                 port= 3306,
                                 user='root',
                                 passwd='yourpass',
                                 charset='utf8mb4',
                                 db='mtime')
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        if item:
            try:
                if self.cursor.execute(''' SELECT name FROM movie WHERE id = (%s)''', (item['id'])) == 0:
                    query = ('INSERT INTO movie(id, name)  VALUES (%s, \'%s\')' % (item['id'], item['name']))
                    self.cursor.execute(query)
                    self.connection.commit()
                else:
                    pass
            except Exception, e:
                print(e)
                print(u'更新失败',item)
        return item

    def spider_closed(self):
        spider_opened(self)
