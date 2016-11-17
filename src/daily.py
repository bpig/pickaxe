#!/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/26"
from common import *
import filter_by_rule

def loadFile(fin):
    kv = {}
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        pos = l.find(",")
        key = l[:pos]
        items = l[pos + 1:].split(",")
        items = map(lambda x: x.split("_"), items)
        kv[key] = items
    return kv

def parseLine(l):
    l = l.strip()
    pos = l.find(",")
    key = l[:pos]
    items = [_.split("_")[0] for _ in l[pos + 1:].split(",")]
    weight = [float(_.split("_")[1]) for _ in l[pos + 1:].split(",")]
    return key, zip(items, weight)

if __name__ == "__main__":
    fin = "ans/" + sys.argv[1]
    
    filter_by_rule.process(fin, filterNew=True, output=False)
    
    l = next(open(fin + ".filter"))
    key, pairs = parseLine(l)
    top = filter(lambda (item, weight):weight == 1.0, pairs)
    tail = filter(lambda (item, weight):weight != 1.0, pairs)

    print key, len(top), len(tail)
    top = map(lambda (item, weight): item, top)
    tail = map(lambda (item, weight): item, tail)
    random.shuffle(top)
    random.shuffle(tail)
    
    ct = 100
    items = top[:60] + tail[:40]
    assert len(items) == 100
    weight = map(lambda _:random.random(), items)
    weight = sorted(weight, reverse=True)
    
    print ",".join(["", "code", "weight"])
    for i in range(ct):
        print ",".join(map(str, (i + 1, items[i], weight[i])))

