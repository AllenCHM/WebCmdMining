#coding:utf-8
from collections import Counter
import re
from chardet import detect
c = Counter()
import codecs
with codecs.open(u'gaojihanyudacidian.idx', u'r', u'utf-8', u'ignore') as f:
    i = f.read()
    t = re.findall(u'([\u4e00-\u9fa5])', i)
    c = Counter(t)
    for i in c.keys():
        print i,
    print