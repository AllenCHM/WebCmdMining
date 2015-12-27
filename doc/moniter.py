import pymongo
import time
from datetime import datetime

connectionMongoDB = pymongo.MongoClient(host='localhost', port=27017)
db = connectionMongoDB['bilibili']
userInfo = db["userInfo"]
avIndex = db["avIndex"]

while True:
    print str(datetime.now()), u'userInfo Total Number:', userInfo.count(), u'avIndex Total Number:', avIndex.count()
    time.sleep(10)