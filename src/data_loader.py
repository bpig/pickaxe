# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *

Aux = collections.namedtuple('Aux', ['ds', 'workDay'])

def getLine(fin):
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        yield l

def getFtKv(fin):
    for l in getLine(fin):
        pos = l.find(",")
        key = l[:pos]
        items = l[pos + 1:].split(",")
        items = map(lambda x: x.split("_"), items)
        yield key, items

def getAux(fin):
    kv = {}
    for k, v in getFtKv(fin):
        kv[k] = Aux(v[0], v[1])
    return kv

if __name__ == '__main__':
    aux = getAux("data/2010/2016.ft.aux")
    print aux.ds
    print aux.workDay
