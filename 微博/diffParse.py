#coding=utf-8
__author__ = 'AllenCHM'

import pymongo

conn = pymongo.MongoClient('192.168.2.165')
db = conn['wss']
doc = db['friends']

count = 0
d = {}
for i in doc.find():
    attentions = []
    follows = []
    try:
        for k in i[u'attentions']:
            attentions.append(k[u'uid'])
            d.setdefault(k[u'uid'], k)

        for k in i[u'follows']:
            follows.append(k[u'uid'])

        for k in attentions:
            if k in follows:
                print i[u'uid'], u',',k, u',', d[k][u'addr']
                count += 1
    except:
        continue


print count