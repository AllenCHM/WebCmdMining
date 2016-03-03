#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pymongo
import csv

conn = pymongo.MongoClient(u'localhost')
db = conn[u'wss']
doc = db[u'es']


# db1 = conn[u'wsss']
# doc1 = db1[u'es']
# for i in doc1.find({}, {u'_id':0}):
#     doc.update({u'链接地址':i[u'链接地址']}, i, True)
import codecs



def task2():
    f= codecs.open('wbTask2.csv', 'wb', u'utf-8')
    fieldName = [u'转发量', u'微博ID', u'发布时间', u'微博正文']
    dict_writer = csv.DictWriter(f, fieldnames=fieldName)
    dict_writer.writerow(dict(zip(fieldName, fieldName)))
    c = []
    for i in doc.find({}, {u'转发量':1, u'微博正文':1, u'微博ID':1, u'发布时间':1, u'_id':0}):
        if i[u'转发量']:
            if int(i[u'转发量']) >1000 and u'2016' not in i[u'发布时间'] and u'天津' in i[u'微博正文'] and u'爆炸' in i[u'微博正文']:
                c.append(i)
    for i in c:
        dict_writer.writerow(i)
    f.close()


def task1():
    f= codecs.open('wbTask1.csv', 'wb', u'utf-8')
    fieldName = [u'转发量', u'微博ID', u'发布时间', u'微博正文']
    dict_writer = csv.DictWriter(f, fieldnames=fieldName)
    dict_writer.writerow(dict(zip(fieldName, fieldName)))
    c = []
    for i in doc.find({}, {u'转发量':1, u'微博正文':1, u'微博ID':1, u'发布时间':1, u'_id':0}):
        if i[u'转发量']:
            if int(i[u'转发量']) >500 and u'2016' not in i[u'发布时间'] and u'天津' in i[u'微博正文'] and u'爆炸' in i[u'微博正文']:
                c.append(i)

    c.sort(lambda x,y: cmp(int(x[u'转发量']), int(y[u'转发量'])))
    print len(c)
    for i in c[-500:]:
        dict_writer.writerow(i)
    f.close()

task1()
task2()
conn.close()