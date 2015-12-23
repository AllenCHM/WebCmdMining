#encoding=utf-8

import jieba

#功能1： 结巴分词用法
def test1():
    #全模式
    seg_list = jieba.cut(u'我来到北京清华大学', cut_all=True)
    print('  /'.join(seg_list))

    #精确模式
    seg_list = jieba.cut(u'我来到北京清华大学', cut_all=False)
    print('  /'.join(seg_list))

    #默认为精确模式
    seg_list = jieba.cut(u'我来到北京清华大学')
    print('  /'.join(seg_list))

    #搜索引擎模式
    seg_list = jieba.cut_for_search(u'小明硕士毕业于中科院计算所，后在日本京都大学深造')
    print('  /'.join(seg_list))

#功能2： 添加自定义字典
#用法：iieba.load_userdict(file_name)  #file_name为自定义字典的路径
#字典格式和dict.txt一样，一个词占一行，每一行分三部分，一部分为词语，另一部分为词频，最后为词性（可省略）， 用空格隔开
#示例
# https://github.com/fxsjy/jieba/blob/master/test/test_userdict.py


# 功能3： 关键字提取
def test3():
    import jieba.analyse
    sentence = u' 开发者可以指定自己自定义的词典，以便包含jieba词库里没有的词。虽然jieba有新词识别能力，但是自行添加新词可以保证更高的正确率. 开发者可以指定自己自定义的词典，以便包含jieba词库里没有的词。虽然jieba有新词识别能力，但是自行添加新词可以保证更高的正确率 . 开发者可以指定自己自定义的词典，以便包含jieba词库里没有的词。虽然jieba有新词识别能力，但是自行添加新词可以保证更高的正确率 . 开发者可以指定自己自定义的词典，以便包含jieba词库里没有的词。虽然jieba有新词识别能力，但是自行添加新词可以保证更高的正确率 '
    tmp = jieba.analyse.extract_tags(sentence, topK=2)  #topK为返回几个TF/IDF权重最大的关键词，默认值为20
    print(u','.join(tmp))

#功能4： 词性标注
def test4():
    #标注句子分词后每个词的词性，采用和ictclas兼容的标记法
    import jieba.posseg as pseg
    words = pseg.cut(u'我是臭傻逼')
    for w in words:
        print(w.word, w.flag)

#功能5：并行分词
# 原理：将目标文本按行分隔后，把各行文本分配到多个python进程进行分词，然后归并结果，从而获得分词速度的可观提升
# 基于python自带的multiprocessing模块，目前不支持windows
# 用法：jieba.enable_parallel(4) 开启并行分词模式，参数为并行进程数
#         jieba.disable_parallel() 关闭并行分词模式


#功能6 Tokenize: 返回词语在原文的起始位置，注意参数只接受unicode
def test5():
    #默认模式
    result = jieba.tokenize(u'永和服装饰品有限公司')
    for tk in result:
        print('word %s\t\t start:%d \t\t end:%d' %(tk[0], tk[1], tk[2]))
    print
    print
    #搜索模式
    result = jieba.tokenize(u'永和服装饰品有限公司', mode='search')
    for tk in result:
        print('word %s\t\t start:%d \t\t end:%d' %(tk[0], tk[1], tk[2]))

#功能7： chineseAnalyzer for whoosh搜索引擎
# https://github.com/fxsjy/jieba/blob/master/test/test_whoosh.py

# 其他词典
# 占用内存较小的词典文件 https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.small
# 支持繁体分词更好的词典文件 https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.big
# jieba.set_dictionary('data/dict.txt.big')