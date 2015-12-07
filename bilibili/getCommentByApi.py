# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

import requests
import re
import json

url = u'http://www.bilibili.com/video/av3193967'

apiUrl = u'http://api.bilibili.com/feedback?type=jsonp&ver=3&callback=jQuery17202343479166738689_1447891693154&mode=arc&aid=3193967&pagesize=200&page=1&_=1447891705491'
#参数解释：
# ?type=jsonp
# &ver=3
# callback=jQuery17202343479166738689_1447891693154
# &mode=arc
# &aid=3193967  视频id
# &pagesize=200  pagesize，可以对比results查看是否到达最后一页
# &page=1
# &_=1447891705491'


response = requests.get(apiUrl)
tmp = re.findall('\((.*)\)', response.content, re.S)
# tmp = response.json()
tmp = json.loads(tmp[0])
for i in tmp:
    print(i)

