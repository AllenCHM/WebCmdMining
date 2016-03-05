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
doc = db[u'friends_bj']
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
    browser.find_element_by_xpath(u'//div[@node-type="username_box"]//input[@class="W_input"]').send_keys('18750426694')
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

urls = [
"http://weibo.com/1797799703", "http://weibo.com/5533169510", "http://weibo.com/2734206734", "http://weibo.com/2342743601", "http://weibo.com/2312192367", "http://weibo.com/1798291911", "http://weibo.com/1915181085", "http://weibo.com/2931962630", "http://weibo.com/1423906831", "http://weibo.com/3968488198", "http://weibo.com/1878536337", "http://weibo.com/3114217141", "http://weibo.com/3963865365", "http://weibo.com/3963351016", "http://weibo.com/1691628713", "http://weibo.com/1654881272", "http://weibo.com/1751113165", "http://weibo.com/5652201232", "http://weibo.com/2128267493", "http://weibo.com/3988930308", "http://weibo.com/2527322652", "http://weibo.com/1989076102", "http://weibo.com/3968491980", "http://weibo.com/3968488204", "http://weibo.com/3963843375", "http://weibo.com/3961196946", "http://weibo.com/1662255995", "http://weibo.com/5769696321", "http://weibo.com/1243793012", "http://weibo.com/1341125831", "http://weibo.com/2361262805", "http://weibo.com/1762957477", "http://weibo.com/3969420453", "http://weibo.com/1838619383", "http://weibo.com/3985983207", "http://weibo.com/3225864882", "http://weibo.com/1713501330", "http://weibo.com/2268275743", "http://weibo.com/3968488189", "http://weibo.com/1906046247", "http://weibo.com/5092297878", "http://weibo.com/5072560749", "http://weibo.com/3966644362", "http://weibo.com/1991550691", "http://weibo.com/1724447020", "http://weibo.com/1422022897", "http://weibo.com/3835595866", "http://weibo.com/2006389055", "http://weibo.com/2740790974", "http://weibo.com/2235580975", "http://weibo.com/2692595975", "http://weibo.com/5064606862", "http://weibo.com/1720525933", "http://weibo.com/2410563195", "http://weibo.com/3055014330", "http://weibo.com/5122936014", "http://weibo.com/1999007095", "http://weibo.com/2163565084", "http://weibo.com/1790923493", "http://weibo.com/5162937601", "http://weibo.com/1792485791", "http://weibo.com/1791665943", "http://weibo.com/1822726104", "http://weibo.com/3541890751", "http://weibo.com/1729162790", "http://weibo.com/1687429197", "http://weibo.com/1197244213", "http://weibo.com/5537859169", "http://weibo.com/1787556490", "http://weibo.com/1809540321", "http://weibo.com/2001666941", "http://weibo.com/3137117785", "http://weibo.com/1778953751", "http://weibo.com/3268871244", "http://weibo.com/1903264735", "http://weibo.com/2269078921", "http://weibo.com/1786280233", "http://weibo.com/2635639830", "http://weibo.com/3148649650", "http://weibo.com/5750112399", "http://weibo.com/1034470890", "http://weibo.com/1791660463", "http://weibo.com/3888309658", "http://weibo.com/1984089984", "http://weibo.com/1756383827", "http://weibo.com/2005423851", "http://weibo.com/3105218461", "http://weibo.com/3616839457", "http://weibo.com/1823794923", "http://weibo.com/3968488190", "http://weibo.com/5054596212", "http://weibo.com/3968488181", "http://weibo.com/1404479685", "http://weibo.com/2914554593", "http://weibo.com/1908705761", "http://weibo.com/1668684331", "http://weibo.com/2050260973", "http://weibo.com/1823979293", "http://weibo.com/1761056553", "http://weibo.com/5644684807", "http://weibo.com/1242665563", "http://weibo.com/2664690563", "http://weibo.com/3169944732", "http://weibo.com/3617552662", "http://weibo.com/1274521265", "http://weibo.com/5216037788", "http://weibo.com/3428968152", "http://weibo.com/1771318995", "http://weibo.com/1824842215", "http://weibo.com/1059248074", "http://weibo.com/1941803115", "http://weibo.com/1880288131", "http://weibo.com/1316844285", "http://weibo.com/1973581661", "http://weibo.com/2102970692", "http://weibo.com/2857806483", "http://weibo.com/3765691592", "http://weibo.com/2475523237", "http://weibo.com/2159376824", "http://weibo.com/2299261537", "http://weibo.com/2438728894", "http://weibo.com/1229219243", "http://weibo.com/1734467303", "http://weibo.com/3962214853", "http://weibo.com/1363165087", "http://weibo.com/2025430347", "http://weibo.com/1781075451", "http://weibo.com/3968241340", "http://weibo.com/1898448903", "http://weibo.com/1980408873", "http://weibo.com/1854236163", "http://weibo.com/3645499217", "http://weibo.com/2720757791", "http://weibo.com/5144505584", "http://weibo.com/5042581580", "http://weibo.com/1266607724", "http://weibo.com/2551574072", "http://weibo.com/1753154305", "http://weibo.com/1744947102", "http://weibo.com/1349450775", "http://weibo.com/1845392212", "http://weibo.com/1450296277", "http://weibo.com/1960163705", "http://weibo.com/1962727405", "http://weibo.com/1167002485", "http://weibo.com/5045446317", "http://weibo.com/1883204831", "http://weibo.com/2377335887", "http://weibo.com/3308998643", "http://weibo.com/2672665935", "http://weibo.com/1791102475", "http://weibo.com/2301760324", "http://weibo.com/2486817984", "http://weibo.com/1420779805", "http://weibo.com/2169867245", "http://weibo.com/3162581327", "http://weibo.com/1656860115", "http://weibo.com/1032239177", "http://weibo.com/2259484741", "http://weibo.com/2154959042", "http://weibo.com/2608689545", "http://weibo.com/3967083647", "http://weibo.com/2830476334", "http://weibo.com/1245152922", "http://weibo.com/2163573294", "http://weibo.com/1627598833", "http://weibo.com/2017415525", "http://weibo.com/1883112467", "http://weibo.com/1771572367", "http://weibo.com/1346534320", "http://weibo.com/3006587265", "http://weibo.com/3445915604", "http://weibo.com/1571483910", "http://weibo.com/2173080265", "http://weibo.com/1833599723", "http://weibo.com/1854081251", "http://weibo.com/2135777823", "http://weibo.com/1941710194", "http://weibo.com/2230189937", "http://weibo.com/1051297793", "http://weibo.com/1833054350", "http://weibo.com/2433540797", "http://weibo.com/2095874897", "http://weibo.com/1936898517", "http://weibo.com/1958445221", "http://weibo.com/3003100917", "http://weibo.com/3614572132", "http://weibo.com/3493618704", "http://weibo.com/1107344172", "http://weibo.com/1939977747", "http://weibo.com/1580455052", "http://weibo.com/3989882567", "http://weibo.com/1191531243", "http://weibo.com/1978495547", "http://weibo.com/2783011915", "http://weibo.com/2728277134", "http://weibo.com/1952021033", "http://weibo.com/1688096280", "http://weibo.com/1945618165", "http://weibo.com/2383101957", "http://weibo.com/1959402553", "http://weibo.com/5045763164", "http://weibo.com/2612247160", "http://weibo.com/2526174661", "http://weibo.com/3297563001", "http://weibo.com/2803885070", "http://weibo.com/1780094170", "http://weibo.com/2177925505", "http://weibo.com/2113602565", "http://weibo.com/1095025490", "http://weibo.com/1672043751", "http://weibo.com/1948500185", "http://weibo.com/1704865683", "http://weibo.com/2114150201", "http://weibo.com/1291761345", "http://weibo.com/1955138173", "http://weibo.com/1762552153", "http://weibo.com/2192498977", "http://weibo.com/1752149147", "http://weibo.com/1803815591", "http://weibo.com/2090190895", "http://weibo.com/2188794765", "http://weibo.com/2693748333", "http://weibo.com/1769946917", "http://weibo.com/1678962435", "http://weibo.com/1558064697", "http://weibo.com/1795114534", "http://weibo.com/1502294800", "http://weibo.com/1810991965", "http://weibo.com/2485131580", "http://weibo.com/2030053571", "http://weibo.com/1034938472", "http://weibo.com/1270622602", "http://weibo.com/1820313881", "http://weibo.com/1737846875", "http://weibo.com/5127324344", "http://weibo.com/1461323480", "http://weibo.com/1742902041", "http://weibo.com/2543117341", "http://weibo.com/1655062563", "http://weibo.com/1977061781", "http://weibo.com/2121418047", "http://weibo.com/1594396184", "http://weibo.com/2093016854", "http://weibo.com/2282096741", "http://weibo.com/2028305941", "http://weibo.com/5668037757", "http://weibo.com/3478819115", "http://weibo.com/1790288231", "http://weibo.com/3190562390", "http://weibo.com/1869779105", "http://weibo.com/1989471131", "http://weibo.com/5093903150", "http://weibo.com/1790076067", "http://weibo.com/1745736392", "http://weibo.com/2672780283", "http://weibo.com/2413809017", "http://weibo.com/1626740162", "http://weibo.com/5045759230", "http://weibo.com/1666357137", "http://weibo.com/2047470494", "http://weibo.com/1427142004", "http://weibo.com/1676693401", "http://weibo.com/5328925901", "http://weibo.com/1850458053", "http://weibo.com/1079025660", "http://weibo.com/1429200580", "http://weibo.com/3923985760", "http://weibo.com/1888695233", "http://weibo.com/1682329234", "http://weibo.com/1676255841", "http://weibo.com/2205407270", "http://weibo.com/3511238985", "http://weibo.com/5776481062", "http://weibo.com/3886385007", "http://weibo.com/3573653367", "http://weibo.com/2330218117", "http://weibo.com/1402341707", "http://weibo.com/2301186705", "http://weibo.com/1830236570", "http://weibo.com/1868277863", "http://weibo.com/1942136003", "http://weibo.com/3988236770", "http://weibo.com/1872127503", "http://weibo.com/1881571383", "http://weibo.com/1794680183", "http://weibo.com/1975040987", "http://weibo.com/1889043422", "http://weibo.com/1757631893", "http://weibo.com/1685803485", "http://weibo.com/2722080571", "http://weibo.com/2481151193", "http://weibo.com/2483662593", "http://weibo.com/1679552440", "http://weibo.com/2139408855", "http://weibo.com/1396589321", "http://weibo.com/2456080521", "http://weibo.com/1909815847", "http://weibo.com/1750180715", "http://weibo.com/1860745947", "http://weibo.com/2447105971", "http://weibo.com/1168820311", "http://weibo.com/3994631948", "http://weibo.com/2394719875", "http://weibo.com/1801264033", "http://weibo.com/2127166987", "http://weibo.com/2620526431", "http://weibo.com/1721692663", "http://weibo.com/2768209961", "http://weibo.com/2959019513", "http://weibo.com/3626709204", "http://weibo.com/2506675147", "http://weibo.com/1584300794", "http://weibo.com/1850861517", "http://weibo.com/1788319985", "http://weibo.com/2806603243", "http://weibo.com/3169570103", "http://weibo.com/1084307914", "http://weibo.com/1747719453", "http://weibo.com/1648955774", "http://weibo.com/1954475963", "http://weibo.com/1744815953", "http://weibo.com/1199238303", "http://weibo.com/2302025355", "http://weibo.com/3777575603", "http://weibo.com/1844875765", "http://weibo.com/1271834500", "http://weibo.com/1866534780", "http://weibo.com/3982882255", "http://weibo.com/3655008273", "http://weibo.com/5321251739", "http://weibo.com/2966024617", "http://weibo.com/1650116370", "http://weibo.com/1878576585", "http://weibo.com/2606455717", "http://weibo.com/2500511277", "http://weibo.com/1228960972", "http://weibo.com/3179766922", "http://weibo.com/1798938397", "http://weibo.com/1155153832", "http://weibo.com/1253209584", "http://weibo.com/1775005473", "http://weibo.com/3911653688", "http://weibo.com/1076563927", "http://weibo.com/2367578440", "http://weibo.com/1026031500", "http://weibo.com/1482186125", "http://weibo.com/1420148432", "http://weibo.com/1657944993", "http://weibo.com/1532459795", "http://weibo.com/1294894814", "http://weibo.com/1775306727", "http://weibo.com/2036593015", "http://weibo.com/1017228380", "http://weibo.com/3220889304", "http://weibo.com/1737061673", "http://weibo.com/2418839864", "http://weibo.com/2128628052", "http://weibo.com/1957749031", "http://weibo.com/5283619952", "http://weibo.com/1793028393", "http://weibo.com/1415899604", "http://weibo.com/1881599737", "http://weibo.com/2812652242", "http://weibo.com/2719898831", "http://weibo.com/2715595284", "http://weibo.com/1809140662", "http://weibo.com/2667802891", "http://weibo.com/2732117903", "http://weibo.com/1904832300", "http://weibo.com/1304729682", "http://weibo.com/1740138072", "http://weibo.com/1585179632", "http://weibo.com/5536402352", "http://weibo.com/1724809172", "http://weibo.com/5762808769", "http://weibo.com/1944546987", "http://weibo.com/1782938405", "http://weibo.com/1769944677", "http://weibo.com/5578130104", "http://weibo.com/1273000415", "http://weibo.com/2610597177", "http://weibo.com/2931962050", "http://weibo.com/1397415561", "http://weibo.com/1595924212", "http://weibo.com/2760663205", "http://weibo.com/2397356981", "http://weibo.com/1757263343", "http://weibo.com/2269554105", "http://weibo.com/1066040913", "http://weibo.com/5397422660", "http://weibo.com/1985674023", "http://weibo.com/2128744570", "http://weibo.com/1764602585", "http://weibo.com/1934746154", "http://weibo.com/3306884973", "http://weibo.com/2577070731", "http://weibo.com/1402746861", "http://weibo.com/2398296223", "http://weibo.com/2578947207", "http://weibo.com/2352556201", "http://weibo.com/3170261587", "http://weibo.com/2312928145", "http://weibo.com/1744846463", "http://weibo.com/2380011427", "http://weibo.com/2547418685", "http://weibo.com/1565540261", "http://weibo.com/1758136335", "http://weibo.com/5288723959", "http://weibo.com/1802621792", "http://weibo.com/2851802783", "http://weibo.com/2062784083", "http://weibo.com/1807868727", "http://weibo.com/1775892925", "http://weibo.com/2656465513", "http://weibo.com/1760244835", "http://weibo.com/2393697595", "http://weibo.com/3089983251", "http://weibo.com/3220813631", "http://weibo.com/2855839524", "http://weibo.com/2181815845", "http://weibo.com/2818228045", "http://weibo.com/3910537199", "http://weibo.com/1993943270", "http://weibo.com/2743636645", "http://weibo.com/1064393461", "http://weibo.com/1219298213", "http://weibo.com/2485627254", "http://weibo.com/5656821116", "http://weibo.com/2260225877", "http://weibo.com/5047248514", "http://weibo.com/1842986603", "http://weibo.com/2991607847", "http://weibo.com/2161690653", "http://weibo.com/1760698354", "http://weibo.com/2609410473", "http://weibo.com/1747255690", "http://weibo.com/2252514951", "http://weibo.com/2531464421", "http://weibo.com/2808314123", "http://weibo.com/1414858335", "http://weibo.com/1940802822", "http://weibo.com/1277499947", "http://weibo.com/5045654075", "http://weibo.com/2712685007", "http://weibo.com/2095132197", "http://weibo.com/2038232585", "http://weibo.com/1739576207", "http://weibo.com/2834583284", "http://weibo.com/2259979935", "http://weibo.com/5597706272", "http://weibo.com/5134505444", "http://weibo.com/5252716841", "http://weibo.com/1864843141", "http://weibo.com/2113377732", "http://weibo.com/1686849900", "http://weibo.com/2313023795", "http://weibo.com/2603997295", "http://weibo.com/3552342827", "http://weibo.com/1936999414", "http://weibo.com/1278829304", "http://weibo.com/5596836083", "http://weibo.com/2739466037", "http://weibo.com/1728745380", "http://weibo.com/1477000800", "http://weibo.com/1194546910", "http://weibo.com/1693877241", "http://weibo.com/5307591364", "http://weibo.com/2679883803", "http://weibo.com/1896436013", "http://weibo.com/1803471211", "http://weibo.com/1501694923", "http://weibo.com/1961816103", "http://weibo.com/2407152163", "http://weibo.com/1951911205", "http://weibo.com/1422254915", "http://weibo.com/1749595273", "http://weibo.com/1821165181", "http://weibo.com/1848312681", "http://weibo.com/1767668535", "http://weibo.com/2128859037", "http://weibo.com/3956028361", "http://weibo.com/1438906770", "http://weibo.com/2623043251", "http://weibo.com/1826182440", "http://weibo.com/5212475421",


]

for url in urls:
    if redisKeysSet.sismember(u'friends', url):
        continue
    try:
        browser = getPage(browser, url)
        time.sleep(random.uniform(7,10))
        browser.find_element_by_xpath('//td/a[@bpfilter="page_frame"]//span[contains(text(), "关注")]').click()
        time.sleep(random.uniform(7,10))
        tmpHtml = browser.page_source
        getAttention(doc,tmpHtml)
        for i in xrange(4):
            print i
            browser.find_element_by_xpath('//a[contains(@class, "page next")]/span[contains(text(), "下一页")]').click()
            time.sleep(random.uniform(7,10))
            tmpHtml = browser.page_source
            getAttention(doc,tmpHtml)

        browser.find_element_by_xpath('//li/a[@bpfilter="page"]//span[contains(text(), "的粉丝")]').click()
        time.sleep(random.uniform(7,10))
        tmpHtml = browser.page_source
        getFollow(doc,tmpHtml)
        for i in xrange(4):
            print i
            browser.find_element_by_xpath('//a[contains(@class, "page next")]/span[contains(text(), "下一页")]').click()
            time.sleep(random.uniform(7,10))
            tmpHtml = browser.page_source
            getFollow(doc,tmpHtml)

        redisKeysSet.sadd(u'friends', url)
        if checkOut(doc):
            break
    except Exception, e:
        continue

browser.quit()



