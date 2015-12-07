#!/bin/bash
export PATH=$PATH:/usr/bin
cd /root/bili
kill -9 `ps -ef |grep AvIndex|awk '{print $2}' `
nohup scrapy crawl AvIndex >> ./log/AvIndex.log 2>&1 &
