#coding=utf-8
__author__ = 'AllenCHM'
#
#
#

import requests
import gzip
import json
import pymongo
import os
import chardet
connectionMongoDB = pymongo.MongoClient(host='192.168.0.29', port=27017)
db = connectionMongoDB['AllenTest']
doc = db["usaGov"]
lists =  os.listdir('./log/')
os.chdir(u'./log')
print(os.getcwdu())
for i in lists:
    tmps = []
    with gzip.GzipFile(filename=i, mode='r') as f:
        for k in f:
            if k.strip():
                try:
                    tmps.append(json.loads(k.strip(), encoding='windows-1252'))
                except Exception,e:
                    pass
    if tmps:
            doc.insert_many(tmps)
            os.remove(i)
    else:
        print u'nothing'


