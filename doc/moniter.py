import pymongo
import time
from datetime import datetime

connectionMongoDB = pymongo.MongoClient(host='localhost', port=27017)
db = connectionMongoDB['bilibili']
userInfo = db["userInfo"]
avIndex = db["avIndex"]
old = 0
while True:
    new = userInfo.count()
    # print str(datetime.now()), u'userInfo Total Number:', userInfo.count(), u'avIndex Total Number:', avIndex.count()
    print str(datetime.now()), u'userInfo Total Number:', new, u'  Add:', (new-old)
    old = new
    time.sleep(10)