#!/bin/env python
# -*- coding:utf-8 -*-
from collections import Counter

from common import *
from data_loader import getFt, getAns, Aux
import filter_by_rule

def gain(predict, stock, numStock, ds, detail):
    count = 0
    increase = 0
    for key in predict:
        if count >= numStock:
            break
        assert key in stock.keys(), "ft keys error, %s not exist" % key

        info = stock[key]
        assert ds in info.ds, "%s not exist" % ds

        index = info.ds.index(ds)
        assert index > 0, "%s is to ealy" % ds

        if info.status[index] == '1':
            continue
        if info.s_status[index] == '1':
            continue
        inPrice = float(info.s[index])
        index -= 1
        while index >= 0 and (info.status[index] == '1' or info.e_status[index] == '2'):
            index -= 1
        if index < 0:
            if detail:
                print "warning: %s stop， 无法卖出" % key
            index = 0
        outPrice = float(info.e[index])
        increase += outPrice / inPrice
        if detail:
            print "%s_%.3f" % (key, outPrice / inPrice)
        count += 1
    res = increase / count - 0.0015
    return res


def loadPredictFile(predictFile):
    predict = []
    for l in open(predictFile):
        l = l.strip()
        if "code" in l or not l:
            continue
        key = l.split(",")[1]
        if key[:4] == '"=""':
            key = key[4:-3]
        if key:
            predict += [key]
    return predict

def getDs(predictFile):
    filename = os.path.basename(predictFile)
    return filename.split(".")[0][:8]

def getArgs():
    parser = ArgumentParser(description="Gain")
    parser.add_argument("-t", dest="tgt", required=True,
                        help="target")
    parser.add_argument("-c", dest="c", default=50, type=int, 
                        help="cal count")
    parser.add_argument("-v", dest="v", action="store_true", default=False,
                        help="verbose")
    return parser.parse_args()    


def process(predictFile, numStock,  stock, detail=False):
    ds = getDs(predictFile)
    predict = loadPredictFile(predictFile)

    try:
        inc = gain(predict, stock, numStock, ds, detail)
    except:
        sys.exit(0)

    #print os.path.basename(predictFile), "%.6f" % inc
    print ds, "%.6f" % inc

if __name__ == "__main__":
    args = getArgs()
    stock = getFt(AUX_FILE, Aux)
    stock2 = dict([(x[:6],y) for (x, y) in stock.iteritems()])

    if os.path.isfile(args.tgt):
        st = stock2 if "model" in args.tgt else stock
        process(args.tgt, args.c, st)
    else:
        for f in sorted(os.listdir(args.tgt)):
            if not f.startswith("2") or not f.endswith("csv"):
                continue
            f = os.path.join(args.tgt, f)
            st = stock2 if "model" in f else stock
            process(f, args.c, st, detail=args.v)
    
    


