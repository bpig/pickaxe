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

def gain(predict, stock, numStock, period):
    ds = sorted(predict.keys(), key=lambda x: x[0])
    totalMoney = [0.5, 0.5]
    updateMoney = [0, 0]
    for i in range(period):
        if i >= len(ds):
            return i-1, totalMoney
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
            index = items[0].index(d)
            # 停盘 or 开盘涨停
            if items[11][index] == 1 or items[12][index] == 2:
                continue
            inPrice = float(items[5][index])
            nextDayIndex = index - 1
            # 停盘 or 收盘跌停
            while nextDayIndex >= 0 and (items[11][nextDayIndex] == 1 or items[11][nextDayIndex] == 3):
                nextDayIndex -= 1
            if nextDayIndex < 0:
                return i, totalMoney
            outPrice = float(items[8][nextDayIndex])
            buy[ii] += str(key) + "_" + rec[1] + ","
            increase[ii] += outPrice / inPrice
            count[ii] += 1
        updateMoney[ii] = (increase[ii] / count[ii] - 0.0015) * totalMoney[ii]
        print d, "start: " + str(totalMoney[ii]), "end: " + str(updateMoney[ii]), "buy " + str(count[ii]) + " stocks: " +buy[ii]
        if count[ii] < numStock:
            print "no enough number of stocks to buy in"
        totalMoney[ii] = updateMoney[ii]

    return i, totalMoney

def process(predictFile, stockFile, numStock, period):
    stock = loadFile(stockFile)
    predict = {}
    for k, v in loadFile(predictFile).items():
        v = sorted(v, key=lambda x: float(x[1]), reverse=True)
        predict[k] = v
    i, money = gain(predict, stock, numStock, period)
    print "after " + str(i+1) + " days:"
    print "final: " + str(sum(money))

if __name__ == "__main__":
    predictFile = sys.argv[1]
    stockFile = sys.argv[2]
    numStock = int(sys.argv[3])
    period = int(sys.argv[4])
    process(predictFile, stockFile, numStock, period)