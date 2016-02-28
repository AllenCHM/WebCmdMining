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

import pymongo

# client = pymongo.MongoClient('mongodb://192.168.2.165,192.168.3.132,192.168.4.129/?replicaSet=mongo')
client = pymongo.MongoClient('localhost')
db = client[u'wss']
doc = db[u'es']


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
    time.sleep(10)
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
    t = list(re.findall('(.*?)-(.*?)-(.*?)-(.*?)$', a)[0])
    if t[3] == '0':
        t[2] = str(int(t[2])-1)
        t[3] = '23'
    else:
        t[3] = str(int(t[3])-1)
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
    if u'2015-08-11' in template:
        return ''
    return template


browser = loginWeibo()
browser = getPage(browser, u'http://s.weibo.com/weibo/%25E5%25A4%25A9%25E6%25B4%25A5%25E7%2588%2586%25E7%2582%25B8&category=5&suball=1&timescope=custom:2015-08-27-23:2015-08-28-0&Refer=g')
time.sleep(random.uniform(20,30))
count = 0
while True:

    current_url = browser.current_url
    try:
        tmpHtml = browser.page_source
        parsePageInfo(doc,tmpHtml, current_url)
        # js="var q=document.documentElement.scrollTop=10000"
        # browser.execute_script(js)
        # time.sleep(random.uniform(1,5))
        # tmpHtml = browser.page_source
        # parsePageInfo(doc,tmpHtml)

        browser.find_element_by_xpath('//a[contains(@class, "page next")]').click()
        time.sleep(random.uniform(15,40))
    except Exception, e:
        time.sleep(random.uniform(5,30))
        nextPage = re.findall('下一页', tmpHtml, re.S)
        if nextPage:
            browser = getPage(browser, current_url)
        else:
            url = genUrl(current_url)
            if url:
                browser = getPage(browser, url)
            else:
                break
        time.sleep(random.uniform(20,26))

browser.quit()



