#!/bin/env python
# -*- coding:utf-8 -*-
from collections import Counter

from common import *
from data_loader import getFt, getAns, Aux
import filter_by_rule

def gain(predict, stock, numStock, ds, output, detail):
    count = 0
    stop = 0
    high = 0
    stop = 0
    low = 0
    increase = 0
    for key in predict:
        if count < numStock:
            break
        assert key in stock.keys(), "ft keys error, %s not exist" % key

        info = stock[key]
        assert ds in info.ds, "%s not exist" % ds

        index = info.ds.index(ds)
        assert index > 0, "%s is to ealy" % ds

        if info.status[index] == '1':
            stop += 1
            continue
        if info.s_status[index] == '1':
            high += 1
            continue
        inPrice = float(info.s[index])
        index -= 1
        while index >= 0 and (info.status[index] == '1' or info.e_status[index] == '2'):
            index -= 1
            mark = True
        if mark:
            if info.status[index + 1] == '1':
                stop += 1
            else:
                low += 1
        if index < 0:
            print "warning: %s 跌停， 无法卖出"
            index = 0
        outPrice = float(info.e[index])
        increase += outPrice / inPrice
        print "%s_%.3f" % (key, outPrice / inPrice)
        count += 1
    res = 100 * (increase / count - 0.0015) - 100
    print res


def loadPredictFile(predictFile):
    predict = []
    for l in open(predictFile):
        l = l.strip()
        if "code" in l or not l:
            continue
        key = l.split(",")[1]
        predict += key
    return predict

def process(predictFile, numStock, output=True, detail=False):
    stock = getFt(AUX_FILE, Aux)
    ds = predictFile.split(".")[0]
    print ds
    predict = loadPredictFile(predictFile)
    print predict
    gain(predict, stock, numStock, ds, output, detail)

if __name__ == "__main__":
    # args = getArgs()
    # tgt = "ans/" + args.tgt
    #
    # if args.d or "filter" in tgt:
    #     process(tgt, args.c, start=args.ds, detail=args.v)
    # else:
    #     filter_by_rule.process(tgt, args.n, args.h, args.st)
    #     tgt += ".filter"
    #     process(tgt, args.c, start=args.ds, detail=args.v)
    process()
    
    


