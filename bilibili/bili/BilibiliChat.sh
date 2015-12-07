#!/bin/bash
export PATH=$PATH:/usr/bin
cd /root/bili
kill -9 `ps -ef |grep avChat|awk '{print $2}' `
nohup scrapy crawl avChat >> ./log/avChat.log 2>&1 &
