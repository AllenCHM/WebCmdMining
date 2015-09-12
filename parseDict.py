# -*- coding: utf-8 -*-
__author__ = 'AllenCHM'

def loadTextDict(fileName):
    f = open(fileName)
    wordsTuple = []
    for i in f.readlines():
        i = i.strip()
        if i:
            wordsTuple.append(i)
    f.close()
    return wordsTuple
