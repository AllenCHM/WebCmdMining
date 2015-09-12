# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'
import requests
from os.path import getsize
from datetime import  datetime
import sys
import json
from parseDict import loadTextDict
try:
    import cPickle as pickle
except:
    pickle

reload(sys)
sys.setdefaultencoding('utf-8')

def ruleOneTest(a, i):
    target = [] #评价对象
    sentiment = [] #情感用词
    if a["relate"] in ['HED', 'COO'] and  a["pos"] in [u'a', u'b']:
        sentiment.append(a["cont"])
        for j in range(int(a['id']), 0, -1): #向HED左逐个遍历
            if i[j]['relate'] == 'SBV':
                target.append(i[j]['cont'])
        if len(target): #target不为空
            print u'规则一处理'
            print u' 评价对象词为：',
            # for k in target:
            #     print k,
            print target[0]
            print  u' 情感评价词为：',
            # for k in sentiment:
            #     print k,
            print sentiment[0]
            return target[0], sentiment[0]
    return False

def ruleTwoTest(a, i):
    target = [] #评价对象
    sentiment = [] #情感用词
    dd = False
    dd1 = False
    if a["relate"] in ['HED', 'COO'] and a["pos"] not in [u'a', u'b']:
        for j in range(int(a['id']), 0, -1): #向HED左逐个遍历
            if i[j]['relate'] == 'SBV':
                dd = True
                target.append(i[j]['cont'])
        for j in range(int(a['id'])+1, len(i)): #向HED右逐个遍历
            if i[j]['pos'] in ['a', 'b', 'v']:
                sentiment.append(i[j]["cont"])
                dd1 = True
        if dd and dd1: #确保target和sentiment都有值
            print u'规则二处理'
            print u'评价对象词：',
            print target[0]
            print  u'情感评价词为：',
            # for k in sentiment:
            #     print k,
            print sentiment[0]
            return target[0], sentiment[0]
    return False


def ruleThrTest(a, i):
    target = [] #评价对象
    sentiment = [] #情感用词
    if  a['pos'] in [u'a', u'b', u'd', u'v', u'i'] and a['relate'] in ['HED', 'COO']:
        sentiment.append(a['cont'])
        for j in range(int(a['id'])): #向HED左逐个遍历
            if  i[j]['relate'] in [u'ATT', u'ADV', u'SBV'] and i[j]['pos'] in [u'n', u'nd', u'ws', u'k']: #查找符合要求的字
                target.append(i[j]['cont'])
            if len(target):
                print u'规则三处理'
                print u' 评价对象词为：',
                print target[-1]
                print u' 情感评价词为：',
                print sentiment[-1]
                return target[-1], sentiment[-1]
    return False


def ruleFourTest(a, i):
    target = [] #评价对象
    sentiment = [] #情感用词
    if  a['pos'] in [u'a', u'b', u'd', u'v', u'i'] and a['relate'] in ['HED', 'COO']:
        sentiment.append(a['cont'])
        for j in range(int(a['id'])): #向HED左逐个遍历
            if  i[j]['relate'] in [u'ATT', u'ADV', u'SBV'] and i[j]['pos'] in [u'n', u'nd', u'ws', u'k']: #查找符合要求的字
                target.append(i[j]['cont'])
        if not len(target):
            for j in range(int(a['id'])+1, len(i)): #向HED右逐个遍历
                if  i[j]['relate'] in [u'ATT', u'SBV', u'COO', u'VOB', u'CMP'] and i[j]['pos'] in [u'n', u'nd', u'ws', u'k']: #查找符合要求的字
                    target.append(i[j]['cont'])
                if len(target):
                    print u'规则四处理'
                    print u'评价对象词：',
                    print target[0]
                    # for k in target:
                    #     print k
                    print  u'情感评价词为：',
                    print sentiment[0]
                    return target[0], sentiment[0]
    return False

def ruleParse(a, i, targetDict):
    count = 0
    try:
        target, sentiment = ruleOneTest(a, i)
        if targetDict.has_key(target):
            targetDict[target].append(sentiment)
        else:
            targetDict.setdefault(target, [sentiment])
        count += 1
    except:
        pass

    try:
        target, sentiment = ruleTwoTest(a, i)
        if targetDict.has_key(target):
            targetDict[target].append(sentiment)
        else:
            targetDict.setdefault(target, [sentiment])
        count += 1
    except:
        pass

    try:
        target, sentiment = ruleThrTest(a, i)
        if targetDict.has_key(target):
            targetDict[target].append(sentiment)
        else:
            targetDict.setdefault(target, [sentiment])
        count += 1
    except:
        pass

    try:
        target, sentiment = ruleFourTest(a, i)
        if targetDict.has_key(target):
            targetDict[target].append(sentiment)
        else:
            targetDict.setdefault(target, [sentiment])
        count += 1
    except:
        pass
    return count, targetDict

def loadList():
    posChList =  loadTextDict(u'正面评价词语（中文）.txt')
    negChList =  loadTextDict(u'负面评价词语（中文）.txt')
    posSentimentChList =  loadTextDict(u'正面情感词语（中文）.txt')
    negSentimentChList =  loadTextDict(u'负面情感词语（中文）.txt')
    mostChList =  loadTextDict(u'mostChList.txt')
    veryChList =  loadTextDict(u'veryChList.txt')
    moreChList =  loadTextDict(u'moreChList.txt')
    ishChList =  loadTextDict(u'ishChList.txt')
    insufficientChList =  loadTextDict(u'insufficientChList.txt')
    inverseChList =  loadTextDict(u'inverseChList.txt')
    return posChList, negChList, posSentimentChList, negSentimentChList, mostChList, veryChList, moreChList, ishChList, insufficientChList, inverseChList
# posChList, negChList, posSentimentChList, negSentimentChList, mostChList, veryChList, moreChList, ishChList, insufficientChList, inverseChList = loadList()


def sentiment_score_list(dataset, posChList, posSentimentChList, negChList, negSentimentChList):
    for i in dataset:
        poscount = 0 #积极词的第一次分值
        if i == "id":
            continue
        for word in dataset[i]:
            if word in posChList or word in posSentimentChList: #判断词语是否是情感词
                poscount += 1
            if word in negChList or word in negSentimentChList:
                poscount -= 1
        if poscount > 0:
            dataset[i] = 1
        else:
            dataset[i] = -1
    return dataset

def main():

    #加载语料库
    posChList, negChList, posSentimentChList, negSentimentChList, mostChList, veryChList, moreChList, ishChList, insufficientChList, inverseChList = loadList()

    filename = (u'flower.txt') #测试文件名称， 后面被测试句子代替（缩短测试时间）
    oldfile = open(filename,'r') #打开文件
    size = getsize(filename)  #获取文件大小
    totalCount = size/(1024*20) + 1 #按照20k大小分块，可分块数
    startTime = datetime.now() #记录程序开始时间
    filecount = 0  #处理分块时，记录当前分块位置
    print u'文件名称：%s' % filename
    print u'文件大小：%s B' % size
    targetList =[] #存放最后处理的结果
    count = 0 #记录情感用词个数
    while True:
        startTimeNow = datetime.now() #记录开始时间
        print
        print u'正在处理第%s个分块, 共计%s个分块'% (filecount+1, totalCount)
        s = oldfile.read(1024*20) #读取20k大小文件
        if not s:
            break #没有文件了则跳出死循环
        # s = u'是她爱不爱我这种？' #使用特定句子测试
        s = s.replace('\n', '').replace('\r', '').replace('\xe3\x80\x80', '').replace(' ','').strip() #处理20k数据中的回车，空格，制表符等
        url = 'http://ltpapi.voicecloud.cn/analysis/'
        data ={'api_key': '54S5f2S3kuyMEmvGUgIqRbFJxv0zQnVcbtmb0Ixq',
               'text': s,
               'pattern': 'all',
               'format': 'json'}
        startTimeParse = datetime.now() #记录时间
        response = requests.post(url, data=data) #访问ltp API， 获取数据
        responseTime = datetime.now()  #记录时间
        c = {}
        c = json.loads(response.text) #处理获取到的json文件为dict
        c = c[0]
        for d in xrange(len(c)):  #遍历所有的句子
            i = c[d]
            targetDict = {}
            wordsDict ={}
            for a in i:  #遍历句子中所有的字
                k, targetDict = ruleParse(a, i, targetDict)
                count += k
            wordsDict.setdefault('id', d)
            for k in targetDict:
                wordsDict.setdefault(k, list(set(targetDict[k])))
            targetList.append(sentiment_score_list(wordsDict, posChList, posSentimentChList, negChList, negSentimentChList))

        tagTime = datetime.now()
        filecount += 1
        print u'文本处理花费时间： %s' % str(startTimeParse-startTimeNow)
        print u'网络花费时间： %s' % str(responseTime- startTimeParse)
        print u'标签抽取花费时间： %s' % str(tagTime - responseTime)
        blockParseTime = datetime.now()
        print u'本分块处理花费时间： %s' % (blockParseTime - startTimeNow)
        print u'第%s个分块已经处理完， %s个分块未处理'% (filecount,totalCount-filecount)
        if filecount == totalCount:
        # if filecount == 1:
            break

    targetNum = 0
    for i in targetList:
        targetNum += len(i)

    print
    print u'评价对象总数： %s' % str(targetNum)
    print u'情感描述总数： %s' % count
    print u'共计耗时： ' + str(datetime.now()- startTime)
    f = open('log.txt', 'w')
    for i in targetList:
        s = str(u'id') + u' : ' + str(i['id']) + '\n'
        f.write(s)
        for k in i:
            if k == 'id':
                continue
            s = str(k) + u' : ' + str(i[k]) + '\n'
            f.write(s)
        f.write('\n')
    f.close()
    print u'''处理结果见log.txt
            id: 句子序号
            1: 表正面
            -1： 表负面
    '''
    oldfile.close()

if __name__ == "__main__":
    main()