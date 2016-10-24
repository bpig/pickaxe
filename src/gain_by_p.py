# -*- coding:utf-8 -*-
from collections import Counter

from common import *

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

def gain(predict, stock, numStock, period, start):
    ds = sorted(predict.keys(), key=lambda x: x)
    totalMoney = [0.5, 0.5]
    updateMoney = [0.5, 0.5]
    if start not in ds:
        print ds
        print "start date is too late"
        return -1, totalMoney
    ss = ds.index(start)
    ds = ds[ss:]
    for i in range(period):
        if i >= len(ds):
            return i - 1, totalMoney
        d = ds[i]
        buy = ["", ""]
        increase = [0, 0]
        count = [0, 0]
        ii = i % 2;
        for rec in predict[d]:
            if count[ii] == numStock:
                break
            key = rec[0]
            if key not in stock.keys():
                continue
            items = stock[key]
            if d not in items[0]:
                continue
            index = items[0].index(d) - 1
            if index < 1:
                continue
            # 停盘 or 开盘涨停
            if items[15][index] == 1 or items[16][index] == 1:
                continue
            inPrice = float(items[5][index])
            nextDayIndex = index - 1
            # 停盘 or 收盘跌停
            while nextDayIndex >= 0 and (items[15][nextDayIndex] == 1 or items[18][nextDayIndex] == 2):
                nextDayIndex -= 1
            if nextDayIndex < 0:
                continue
            outPrice = float(items[8][nextDayIndex])
            buy[ii] += str(key) + "_" + rec[1] + "_" + rec[2] + ","
            increase[ii] += outPrice / inPrice
            count[ii] += 1
        # print d, len(predict[d]), totalMoney[ii], count[ii], increase[ii]
        # if count[ii] == 0:
        #     continue
        updateMoney[ii] = (increase[ii] / count[ii] - 0.0015) * totalMoney[ii]
        # print d, "start: " + str(totalMoney[ii]), "end: " + str(updateMoney[ii]),
        #  "buy " + str(count[ii]) + " stocks: " +buy[ii]
        
        lt = buy[ii].split(",")[-2]
        bg = sum(totalMoney)
        ed = sum(updateMoney)
        print d, "%.8f" % bg, "->", "%.8f" % ed, "%.8f" % (ed / bg)
        if count[ii] < numStock:
            print "no enough number of stocks to buy in"
        totalMoney[ii] = updateMoney[ii]
    
    return i, totalMoney

def process(predictFile, stockFile, numStock, period, start):
    stock = loadFile(stockFile)
    predict = {}
    for k, v in loadFile(predictFile).items():
        v = sorted(v, key=lambda x: float(x[1]), reverse=True)
        predict[k] = v
    i, money = gain(predict, stock, numStock, period, start)
    print "after " + str(i + 1) + " days:"
    print "final: " + str(sum(money))

if __name__ == "__main__":
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]

    pfile = "ans/" + cfg["pout"]

    stockFile = "data/2016.ft.2"
    try:
        numStock = 50
        numStock = int(sys.argv[2])
    except:
        pass
    try:
        period = 230
        period = int(sys.argv[3])
    except:
        pass
    try:
        start = "20160104"
        #start = "20161010"
        start = sys.argv[4]
    except:
        pass
    
    process(pfile, stockFile, numStock, period, start)

    # process("../data/2016.ans", "../data/2016.ft", 100, 180, "20160104")

