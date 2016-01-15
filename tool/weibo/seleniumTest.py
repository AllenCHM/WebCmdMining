#coding=utf-8
__author__ = 'AllenCHM'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from lxml import html
import requests


def parsePage(doc, orderList):
    soup = html.fromstring(orderList)
    for k in soup.xpath('//tbody[@id]'):
        try:
            item = {}
            item[u'dealtime'] = k.xpath('.//span[@class="dealtime"]/text()')[0]
            item[u'dealID'] = k.xpath('.//a[@name="orderIdLinks"]/text()')[0]
            item[u'dealUrl'] = k.xpath('.//a[@name="orderIdLinks"]/@href')[0].replace(u'//', u'http://')
            item[u'dealInfo'] = []
            for i in k.xpath('./tr[@oty]'):
                t = {}
                t[u'goodID'] = i.xpath('.//div[@class="p-extra"]/ul/li/span/@data-sku')[0]
                t[u'goodNum'] = i.xpath('.//div[@class="goods-number"]/text()')[0].strip()[1:]
                item[u'dealInfo'].append(t)
            item[u'amount'], item[u'payment']= k.xpath('.//div[@class="amount"]/span/text()')
            item[u'orderStatus'] = k.xpath('.//span[@class="order-status"]/text()')[0].strip()
        except Exception, e:
            continue
        print()
    nextPage = soup.xpath('//a[@class="next"]/@href')
    if nextPage:
        return nextPage[0]
    else:
        return ''


def getJdDealList(cookies, doc):
    orderList2015Url = u'http://order.jd.com/center/list.action?search=0&d=2015&s=1024'  #2015年的订单
    urls =[
        orderList2015Url,
    ]

    for url in urls:
        headers = {
            u'Host':u'order.jd.com',
            u'Pragma':u'no-cache',
            u'User-Agent':u'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            u'Upgrade-Insecure-Requests':u'1',
        }
        r = requests.get(url, headers=headers, cookies=cookies)
        orderList = r.content.decode('gb2312')
        nextPage = parsePage(doc, orderList)
        if nextPage:
            urls.append(u'http:' + nextPage)


# browser = webdriver.Ie(U'C:\\Users\\cheng\\Downloads\\IEDriverServer.exe')
browser = webdriver.Firefox()
# browser.get(u'https://ebsnew.boc.cn/boc15/login.html')
browser.get(u'https://passport.jd.com/new/login.aspx?ReturnUrl=http%3A%2F%2Fwww.jd.com%2F')
# browser.find_element_by_id('rdboc20').click()
browser.find_element_by_id('loginname').send_keys('chinaxnccm')
browser.find_element_by_id('nloginpwd').send_keys('xnccm316461465')
browser.find_element_by_id('loginsubmit').click()
c = browser.get_cookies()
cookies = {}
for i in c:
    cookies[i[u'name']] = i[u'value']
doc = ''
getJdDealList(cookies, doc)



browser.quit()