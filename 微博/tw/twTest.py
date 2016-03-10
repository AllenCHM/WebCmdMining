#coding=utf-8
__author__ = 'AllenCHM'

from selenium import webdriver
import time
from lxml import etree
import random
count = 0

def parseHtml(html):
    hxs = etree.HTML(html)
    item = {}
    item[u'uid'] = hxs.xpath('//div[@id="mHead"]/@uid')[0]
    if not doc.find_one({'uid':item[u'uid']}):
        doc.insert(item)
    divs = hxs.xpath('//div[@id="followCont"]/div[@title]')
    for div in divs:
        t = {}
        t[u'uid'] = div.xpath('./@id')[0]
        t[u'href'] = div.xpath('./@href')[0]
        t[u'name'] = div.xpath('./@title')[0].split(' ')[1]
        tt = div.xpath('.//div[@class="location"]')
        t[u'gender'] = tt[0].xpath('./span[1]/@title')[0]
        t[u'addr'] = tt[0].xpath('./span[2]/@title')[0]
        doc.update({u'uid':item[u'uid']}, {'$addToSet':{'follows':t}}, True)

import pymongo
import redis

redisKeysSet = redis.Redis(u'139.129.6.66', port=16379, db=10, password='xnccm316461465')
# client = pymongo.MongoClient('mongodb://192.168.2.165,192.168.3.132,192.168.4.129/?replicaSet=mongo')
client = pymongo.MongoClient('localhost')
db = client[u'wss']
doc = db[u'friends']
docB = db[u'docB']

browser = webdriver.Firefox()


urls = []
for i in docB.find({}, {u'url':1, u'user_uid':1}):
    url = i[u'url'].split(i[u'user_uid'])[0].replace('weibo', 'tw.weibo')+ i[u'user_uid']+ u'/follow'
    urls.append(url)

count = 0
while True:
    url = random.choice(urls)
    if redisKeysSet.sismember(u'friends', url) or redisKeysSet.sismember(u'friendsLock', url):
        continue
    try:
        redisKeysSet.sadd(u'friendsLock', url)
        browser.get(url)
        time.sleep(random.uniform(7,25))
        parseHtml(browser.page_source)
        js="var q=document.documentElement.scrollTop=10000"
        browser.execute_script(js)
        time.sleep(random.uniform(15,35))
        parseHtml(browser.page_source)
        count = 0
        while True:
            count += 1
            print count


            if u"下一頁" not in browser.page_source:
                break
            try:
                browser.find_element_by_xpath('//div[@id="cboxClose"]').click()
                browser.find_element_by_xpath('//div[@class="pageBar"]//a[contains(text(), "下一頁")]').click()
            except:
                browser.find_element_by_xpath('//div[@class="pageBar"]//a[contains(text(), "下一頁")]').click()

            time.sleep(random.uniform(15,35))
            if u'Error 423 Unknown Error'  in browser.page_source:
                time.sleep(random.uniform(17,65))
                browser.get(browser.current_url)
                time.sleep(random.uniform(7,15))
            parseHtml(browser.page_source)
            js="var q=document.documentElement.scrollTop=10000"
            browser.execute_script(js)
            time.sleep(random.uniform(16,35))
            parseHtml(browser.page_source)
        redisKeysSet.sadd(u'friends', url)
        redisKeysSet.srem(u'friendsLock', url)

    except Exception, e:
        browser.get(url)
        time.sleep(random.uniform(10,25))
        redisKeysSet.srem(u'friendsLock', url)


print()