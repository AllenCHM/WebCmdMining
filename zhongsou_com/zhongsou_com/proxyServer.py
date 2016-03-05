#coding=utf-8
__author__ = 'AllenCHM'

from time import time
from scrapy import Request
import pymongo
import redis


class ProxyServerBase():
    def __init__(self, redisHost="localhost", redisPort=6379):
        #redis
        self.redisDB = redis.Redis(host=redisHost, port=redisPort, db=2)

    def put(self, keyName, ip):
        self.redisDB.lpush(keyName, ip)

    def delete(self, keyName, ip):
        self.redisDB.lrem(keyName, ip)

    def get(self, keyName):
        return self.redisDB.rpoplpush(keyName,keyName)

    def lrange(self, key, start, stop):
        return self.redisDB.lrange(key,start, stop)

    def exists(self, name):
        return self.redisDB.exists(name)

    def push(self, name, *values):
        return self.redisDB.lpush(name, *values)

class ProxyServerMongo(ProxyServerBase):
    def __init__(self, mongoHost="localhost", mongoPort=27017, redisHost="localhost", redisPort=6379):
        ProxyServerBase.__init__(self,redisHost, redisPort)
        #mongoDB
        self.connection = pymongo.MongoClient(host=mongoHost, port=mongoPort)
        self.db = self.connection[u'ProxyServer']
        self.doc = self.db[u'proxyServerIpStatus']

    def success(self, proxies):
        ip = proxies.values()[0]
        self.doc.insert({
            u'ip': ip,
            u'timestamp': time(),
            u'status': 1
        })

    def bad(self, keyName, ip, url, spiderName):
        self.doc.insert({
            u'ip': ip,
            u'timestamp': time(),
            u'status': 0,
            u'url': url,
            u'spider': spiderName
        })

    #针对redis服务第一次启动，初始化redis list
    def init(self, keyName):
        tmp = self.doc.find({u'status': 1}, {u'ip': 1})
        for i in tmp:
            self.put(keyName, i[u'ip'])

    def getProxies(self, keyName):
        proxyIP = self.get(keyName)
        return {proxyIP.split(u':')[0]: proxyIP}

    def close(self):
        self.connection.close()

class ProxyMiddleware(ProxyServerMongo):
    def __init__(self,MONGOHOST, REDISHOST, spiderName):
        ProxyServerMongo.__init__(self,mongoHost=MONGOHOST, redisHost=REDISHOST)
        if not self.exists(u'serverName_'+spiderName):
            self.push(u'serverName_' +spiderName, *self.lrange(u'serverName', 0, -1))

    @classmethod
    def from_crawler(cls, crawler):
        MONGOHOST = crawler.settings.get('MONGOHOST')
        REDISHOST = crawler.settings.get('REDISHOST')
        spiderName = crawler.spider.name
        return cls(MONGOHOST,REDISHOST, spiderName)

    def process_request(self, request, spider):
        request.meta['proxy'] = self.get('serverName_'+spider.name)

    def process_exception(self, request, exception, spider):
        self.bad(keyName='serverName_'+spider.name, ip=request.meta['proxy'], url=request.url, spiderName=spider.name)
        return Request(url=request.url, meta=request.meta, callback=request.callback, dont_filter=True)
