#coding=utf-8
__author__ = 'AllenCHM'
#
#      查询公司外网ip地址，并邮件发送。
#

from scrapy import cmdline

cmdline.execute('scrapy crawl gifZOL'.split())