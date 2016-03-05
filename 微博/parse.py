#coding=utf-8
__author__ = 'AllenCHM'

import codecs
from lxml import etree

with codecs.open('test.html', u'r', 'utf-8') as f:
    t = f.read()
    hxs = etree.HTML(t)
