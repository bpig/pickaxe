# -*- coding:utf-8 -*-
from collections import Counter

from common import *
from data_loader import getFt, getAns

def gain(predict, stock, numStock, ds):
    money = [0.5, 0.5]
    
    for i, d in enumerate(ds):
        buy = StringIO()
        increase, count = 0, 0
        ii = i % 2
        high, low, stop = 0, 0, 0
        for rec in predict[d]:
            # if len(predict[d]) < 1000:
            #     break
            if count == numStock:
                break
            key = rec.code
            assert key in stock.keys(), "ft keys error, %s not exist" % key
            
            info = stock[key]
            assert d in info.ds, "%s not exist" % d
            
            index = info.ds.index(d) - 1  # tomorrow
            if index == 0:
                continue
            # stop or +10 high
            if info.status[index] == '1':
                stop += 1
                continue
            if info.s_status[index] == '1':
                high += 1
                continue
            inPrice = float(info.s[index])
            index -= 1  # the day after tomorrow
            # stop or -10 low
            mark = False
            while index >= 0 and (info.status[index] == '1' or info.e_status[index] == '2'):
                index -= 1
                mark = True
            if mark:
                if info.status[index + 1] == '1':
                    stop += 1
                else:
                    low += 1
            
            if index < 0:
                print "warning, %s low everyday" % key
                index = 0
            outPrice = float(info.e[index])
            # buy.write(key + "_" + rec.tgt + ",")
            buy.write(key + ",")
            increase += outPrice / inPrice
            count += 1
        
        bg = money[ii]
        if count != 0:
            money[ii] *= (increase / count - 0.0015)
        ed = money[ii]
        lack = ""
        if count < numStock:
            lack = "lack(%d)" % count
        
        total = sum(money)
        print d, "%.8f" % total, "%.8f" % bg, "->", "%.8f" % ed, \
            "%.8f" % (ed / bg), high, low, stop, len(predict[d]), lack  # , buy.getvalue()[:-1]
    
    return sum(money)

def process(predictFile, numStock, start, period):
    stock = getFt("data/2010/2016.ft")
    predict = dict(getAns(predictFile))
    
    ds = sorted(predict.keys())
    idx = ds.index(start)
    ds = ds[idx:idx + period]
    
    money = gain(predict, stock, numStock, ds)
    print "after %d days:" % len(ds)
    print "final: " + `money`

if __name__ == "__main__":
    tgt = "ans/" + sys.argv[1]
    
    args = [50, "20160104", 230]
    la = len(sys.argv) - 2
    args[:la] = sys.argv[2:]
    numStock, start, period = args
    
    process(tgt, int(numStock), start, int(period))
