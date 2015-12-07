#coding=utf-8
__author__ = 'AllenCHM'

import json
import codecs
fileName = u'AutohomeK.json'
f = open(fileName, 'r')
itemList = []
for num, i in enumerate(f):
    tmp = json.loads(i)
    itemList.append(itemList)
    print(num)
f.close()
print()