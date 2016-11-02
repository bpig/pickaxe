# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *

Aux = collections.namedtuple('Aux', ['ds', 'work_day'])
Ft = collections.namedtuple(
    'Ft', 
    ['ds', 'rate', 'volumn', 'amount', 'pe', 's', 'high', 'low', 'e', 'turnover',
      'shares', 's_rate', 'h_rate', 'l_rate', 'e_rate', 
      'status', 's_status', 'wav_status', 'e_status', 'target'])

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

def getFt(fin, dtype=Ft):
    kv = {}
    for k, v in getFtKv(fin):
        kv[k] = dtype(*v)
    return kv

if __name__ == '__main__':
    aux = getFt("data/2010/2016.ft.aux", Aux)
    keys = aux.keys()
    key = keys[0]
    print len(aux[key].ds), len(aux[key].work_day)

    ft = getFt("data/2010/2016.ft")
    print len(ft[key].ds), len(ft[key].target)