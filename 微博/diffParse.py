#coding=utf-8
__author__ = 'AllenCHM'

import pymongo

conn = pymongo.MongoClient('192.168.2.165')
db = conn['wss']
doc = db['friends']

count = 0

for i in doc.find():
    attentions = []
    follows = []
    for k in i[u'attentions']:
        attentions.append(k[u'uid'])

    for k in i[u'follows']:
        follows.append(k[u'uid'])

    for k in attentions:
        if k in follows:
            print i[u'uid'], k
            count += 1

    if count > 100:
        print u'++++++++++++++++++++++++'