#coding=utf-8
__author__ = 'AllenCHM'

from selenium import webdriver
from selenium.webdriver.common.proxy import *
import time
import codecs
import re
import random
import pymongo
from lxml import etree
import hashlib
import urlparse
import pymongo

import redis

client = pymongo.MongoClient('mongodb://192.168.2.165,192.168.3.132,192.168.4.129/?replicaSet=mongo')
db = client[u'wss']
doc = db[u'friends']
docB = db[u'docB']
redisKeysSet = redis.Redis(u'192.168.3.133', port=6379, db=10)

def checkOut(doc):
    count = doc.count()
    if count > 100:
        return True
    else:
        return False

def parsePageInfo(doc, html, current_url):
    print current_url
    try:
        soup = etree.HTML(html)
        divs = soup.xpath('//div[@node-type="feed_list"]//div[contains(@class, "WB_cardwrap")]')
        lists = []
        for num, div in enumerate(divs):
            item = {}
            #微博ID, 微博正文， 链接地址， 发布时间， 微博来源， 转发量， 评论数， 评论内容， 点赞数，微博类型
            try:
                item[u'微博ID'] = div.xpath('.//div[@class="feed_content wbcon"]/a[1]/text()')[0].strip()
            except:
                continue
            item[u'IDurl'] = div.xpath('.//div[@class="feed_content wbcon"]/a[1]/@href')[0]
            item[u'微博正文'] = div.xpath('.//div[@class="feed_content wbcon"]/p[@class="comment_txt"]')[0].xpath('string(.)')
            item[u'链接地址'] = div.xpath('.//div[@class="feed_from W_textb"]/a[1]/@href')[-1]
            item[u'发布时间'] = div.xpath('.//div[@class="feed_from W_textb"]/a[1]/@title')[0].strip()
            try:
                item[u'微博来源'] = div.xpath('.//div[@node-type="like"]/div[@class="feed_from W_textb"]/a[@rel="nofollow"]/text()')[0]
            except:
                item[u'微博来源'] = u''
            item[u'转发量'] = div.xpath('.//div[@class="feed_action clearfix"]/ul/li[2]')[0].xpath('string(.)')[2:]
            item[u'评论数'] = div.xpath('.//div[@class="feed_action clearfix"]/ul/li[3]')[0].xpath('string(.)')[2:]
            # item[u'评论内容']
            item[u'点赞数'] = div.xpath('.//div[@class="feed_action clearfix"]/ul/li[4]')[0].xpath('string(.)')
            item[u'微博类型'] = div.xpath('.//div[@class="feed_content wbcon"]/div[@class="comment"]')
            if item[u'微博类型']:
                item[u'微博类型'] = u'转发'
            else:
                item[u'微博类型'] = u'原创'
            doc.update({u'链接地址':item[u'链接地址']},item, True)
        return True
    except Exception, e:
        return False

def getAttention(doc, html):
    user = re.findall('\$CONFIG\[\'onick\'\]=\'(.*?)\';', html)[0]
    uid = re.findall('\$CONFIG\[\'oid\'\]=\'(.*?)\';', html)[0]
    item = {}
    item[u'user'] = user
    item[u'uid'] = uid
    item[u'attentions'] = []
    if not doc.find_one({u'uid':item[u'uid']}):
        doc.insert(item)

    hxs = etree.HTML(html)
    lis = hxs.xpath('//ul[@class="follow_list"]/li')
    for li in lis:
        t = {}
        name = li.xpath('.//dt[@class="mod_pic"]/a/@title')[0]
        userHref = urlparse.urlsplit(li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@href')[0]).path
        try:
            addr = li.xpath('.//div[@class="info_add"]/span/text()')[0]
            id = li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@usercard')[0].split('&')[0][3:]
        except:
            continue
        t[u'user'] = name
        t[u'uid'] = id
        t[u'userHref'] = userHref
        t[u'addr'] = addr
        doc.update({u'uid':item[u'uid']}, {'$addToSet':{u'attentions':t}})

def getFollow(doc, html):
    user = re.findall('\$CONFIG\[\'onick\'\]=\'(.*?)\';', html)[0]
    uid = re.findall('\$CONFIG\[\'oid\'\]=\'(.*?)\';', html)[0]
    item = {}
    item[u'user'] = user
    item[u'uid'] = uid
    item[u'follows'] = []
    if not doc.find_one({u'uid':item[u'uid']}):
        doc.insert(item)
    hxs = etree.HTML(html)
    lis = hxs.xpath('//ul[@node-type="userListBox"]/li')
    for li in lis:
        t = {}
        name = li.xpath('.//dt[@class="mod_pic"]/a/@title')[0]
        userHref = urlparse.urlsplit(li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@href')[0]).path
        try:
            addr = li.xpath('.//div[@class="info_add"]/span/text()')[0]
            id = li.xpath('.//dd[contains(@class,"mod_info")]/div[contains(@class,"info_name")]/a[@class="S_txt1"]/@usercard')[0].split('&')[0][3:]
        except:
            continue
        t[u'user'] = name
        t[u'uid'] = id
        t[u'userHref'] = userHref
        t[u'addr'] = addr
        doc.update({u'uid':item[u'uid']}, {'$addToSet':{u'follows':t}})

def loginWeibo():
    browser = webdriver.Firefox()
    browser.get(u'http://s.weibo.com/weibo/%25E8%25BD%25AC%25E5%259F%25BA%25E5%259B%25A0%25E9%25A3%259F%25E5%2593%2581&nodup=1')
    time.sleep(10)
    browser.find_element_by_xpath(u'//p[@class="tips_co"]//a[@action-type="login"]').click()
    time.sleep(10)
    browser.find_element_by_xpath(u'//div[@class="tab_bar"]//a[@node-type="login_tab"]').click()
    time.sleep(5)
    browser.find_element_by_xpath(u'//div[@node-type="username_box"]//input[@class="W_input"]').send_keys('15733285247')
    browser.find_element_by_xpath(u'//div[@node-type="password_box"]//input[@class="W_input"]').send_keys('a123456')
    raw_input('ok')
    # browser.find_element_by_xpath(u'//div[@class="item_btn"]//a[@action-type="btn_submit"]').click()
    return browser

def getPage(browser, url):
    print url
    browser.get(url)
    time.sleep(random.uniform(8, 15))
    return browser

def savePage(count, resource):
    fileName = str(count) + u'.html'
    with codecs.open(fileName, u'w', u'utf-8') as f:
        f.write(resource)

def saveUserPage(url, resource):
    fileName = u'./userInfo/' + hashlib.md5(url).hexdigest() + u'.html'
    with codecs.open(fileName, u'w', u'utf-8') as f:
        f.write(resource)

def genUrl(url):
    a, b = re.findall('custom:(.*?):(.*?)&', url)[0]
    t = list(re.findall('(.*?)-(.*?)-(.*?)-(.*?)$', b)[0])
    if t[3] == '23':
        t[2] = str(int(t[2])+1)
        t[3] = '0'
    else:
        t[3] = str(int(t[3])+1)
    t = '-'.join(t)
    if u'category=4' in url:
        template = u'http://s.weibo.com/weibo/%25E5%25A4%25A9%25E6%25B4%25A5%25E7%2588%2586%25E7%2582%25B8&vip=1=1&suball=1&timescope=custom:{d}:{c}&Refer=g'.format(d=a, c=b)
    elif u'category=5' in url:
        template = u'http://s.weibo.com/weibo/%25E5%25A4%25A9%25E6%25B4%25A5%25E7%2588%2586%25E7%2582%25B8&category=4&suball=1&timescope=custom:{d}:{c}&Refer=g'.format(d=a, c=b)
    elif u'vip=1' in url:
        template = u'http://s.weibo.com/weibo/%25E5%25A4%25A9%25E6%25B4%25A5%25E7%2588%2586%25E7%2582%25B8&atten=1&suball=1&timescope=custom:{d}:{c}&Refer=g'.format(d=a, c=b)
    elif u'atten=1' in url:
        template = u'http://s.weibo.com/weibo/%25E5%25A4%25A9%25E6%25B4%25A5%25E7%2588%2586%25E7%2582%25B8&scope=ori&suball=1&timescope=custom:{d}:{c}&Refer=g'.format(d=a, c=b)
    elif u'scope=ori' in url:
        template = u'http://s.weibo.com/weibo/%25E5%25A4%25A9%25E6%25B4%25A5%25E7%2588%2586%25E7%2582%25B8&xsort=hot&suball=1&timescope=custom:{d}:{c}&Refer=g'.format(d=a, c=b)
    elif u'xsort=hot' in url:
        template = u'http://s.weibo.com/weibo/%25E5%25A4%25A9%25E6%25B4%25A5%25E7%2588%2586%25E7%2582%25B8&category=5&suball=1&timescope=custom:{d}:{c}&Refer=g'.format(d=t, c=a)
    else:
        template = url
    if u'2015-08-26' in template:
        return ''
    return template


browser = loginWeibo()


while True:
    tt = docB.find({}, {u'user_uid':1, u'url':1}).sort(u'user_uid',1)
    for uid in tt:
        url= uid[u'url'].split(uid[u'user_uid'])[0] + uid[u'user_uid']
        if redisKeysSet.sismember(u'friends', url):
            continue
        try:
            browser = getPage(browser, url)
            time.sleep(random.uniform(7,10))
            # browser.find_element_by_xpath('//td/a[@bpfilter="page_frame"]//span[contains(text(), "关注")]').click()
            browser.find_element_by_xpath('//td/a[@bpfilter="page_frame"]//span[contains(text(), "粉丝")]').click()
            time.sleep(random.uniform(7,10))
            tmpHtml = browser.page_source
            getFollow(doc,tmpHtml)
            for i in xrange(4):
                print i
                browser.find_element_by_xpath('//a[contains(@class, "page next")]/span[contains(text(), "下一页")]').click()
                time.sleep(random.uniform(7,10))
                tmpHtml = browser.page_source
                getFollow(doc,tmpHtml)

            # browser.find_element_by_xpath('//li/a[@bpfilter="page"]//span[contains(text(), "的粉丝")]').click()
            # time.sleep(random.uniform(7,10))
            # tmpHtml = browser.page_source
            # getFollow(doc,tmpHtml)
            # for i in xrange(4):
            #     print i
            #     browser.find_element_by_xpath('//a[contains(@class, "page next")]/span[contains(text(), "下一页")]').click()
            #     time.sleep(random.uniform(7,10))
            #     tmpHtml = browser.page_source
            #     getFollow(doc,tmpHtml)

            redisKeysSet.sadd(u'friends', url)
            if not random.randint(2, 15) % 2:
                browser.get(u'http://weibo.com')
                time.sleep(random.uniform(7,10))
        except Exception, e:
            continue

browser.quit()



