#!/bin/bash
export PATH=$PATH:/usr/bin
cd /root/bili
kill -9 `ps -ef |grep bilibiComm|awk '{print $2}' `
nohup scrapy crawl bilibiComm >> ./log/bilibiComm.log 2>&1 &
