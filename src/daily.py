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

def getArgs():
    parser = ArgumentParser(description="Gain")
    parser.add_argument("-t", dest="tgt", required=True,
                        help="target")
    parser.add_argument("-ds", dest="ds", required=True,
                        help="date")
    parser.add_argument("-f", dest="f", action="store_true", default=False,
                        help="filter")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    fin = "ans/" + args.tgt
    
    filter_by_rule.process(fin, output=False)
    
    for l in open(fin + ".filter"):
        key, pairs = parseLine(l)
        if key == args.ds:
            break

    if key != args.ds:
        print "not %s" % args.ds
    
    ct = 100
    items = map(lambda (item, weight): item, pairs)[:ct]
    
    assert len(items) == ct
    weight = map(lambda _: random.random(), items)
    weight = sorted(weight, reverse=True)
    
    print ",".join(["", "code", "weight"])
    for i in range(ct):
        print ",".join(map(str, (i + 1, items[i], weight[i])))
