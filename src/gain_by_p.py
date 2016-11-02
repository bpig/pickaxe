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
    st2016 = set(map(str.strip, open("data/2016.st")))
    ds = sorted(predict.keys())
    totalMoney = [0.5, 0.5]
    updateMoney = [0.5, 0.5]
    if start not in ds:
        print ds
        print "start date is too late"
        return -1, totalMoney
    ss = ds.index(start)
    ds = ds[ss:ss+period]
    for i, d in enumerate(ds):
        stCt = 0
        buy = ["", ""]
        increase = [0, 0]
        count = [0, 0]
        ii = i % 2;
        nobuy = 0
        nosell = 0
        stop = 0
        for rec in predict[d]:
            if len(predict[d]) < 1000:
                break
            if count[ii] == numStock:
                break
            key = rec[0]
            if key not in stock.keys():
                continue
            if key in st2016:
                stCt += 1
                continue
            items = stock[key]
            if d not in items[0]:
                continue
            index = items[0].index(d) - 1
            if index < 1:
                continue
            # stop or +10 high
            if items[15][index] == '1' or items[16][index] == '1':
                if items[15][index] == '1':
                    stop += 1
                else:
                    nobuy += 1
                continue
            inPrice = float(items[5][index])
            nextDayIndex = index - 1
            # stop or -10 low
            while nextDayIndex >= 0 and \
                  (items[15][nextDayIndex] == '1' or items[18][nextDayIndex] == '2'):
                nextDayIndex -= 1
                if items[15][nextDayIndex] == '1':
                    stop += 1
                else:
                    nosell += 1
            if nextDayIndex < 0:
                continue
            outPrice = float(items[8][nextDayIndex])
            #buy[ii] += str(key) + "_" + rec[1] + "_" + rec[2] + ","
            buy[ii] += str(key) + "_" + rec[2] + ","
            increase[ii] += outPrice / inPrice
            count[ii] += 1
        # print d, len(predict[d]), totalMoney[ii], count[ii], increase[ii]
        if count[ii] != 0:
            updateMoney[ii] = (increase[ii] / count[ii] - 0.0015) * totalMoney[ii]
        # print d, "start: " + str(totalMoney[ii]), "end: " + str(updateMoney[ii]),
        #  "buy " + str(count[ii]) + " stocks: " +buy[ii]
        
            lt = buy[ii].split(",")[-2]
        bg = totalMoney[ii]
        ed = updateMoney[ii]
        lack = ""
        if count[ii] < numStock:
            # print "no enough number of stocks to buy in"
            lack = "lack(%d)" % count[ii]

        totalMoney[ii] = updateMoney[ii]
        total = sum(totalMoney)
        print d, "%.8f" % total, "%.8f" % bg, "->", "%.8f" % ed, "%.8f" % (ed / bg), nobuy, nosell, stCt, stop, len(predict[d]), lack #, buy[ii]
    
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
    pfile = "ans/" + sys.argv[1]

    stockFile = "data/2010/2016.ft"
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
        #start = "20161020"
        start = sys.argv[4]
    except:
        pass

    process(pfile, stockFile, numStock, period, start)

    # process("../data/2016.ans", "../data/2016.ft", 100, 180, "20160104")

