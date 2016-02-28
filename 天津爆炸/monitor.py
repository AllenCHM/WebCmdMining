#coding:utf-8

import pymongo
import time
import datetime


conn = pymongo.MongoClient(u'localhost')
db = conn[u'wss']
doc = db[u'es']
old = 0


while True:
    new = doc.count()
    print datetime.datetime.now(), new, new-old
    old = new
    time.sleep(20)