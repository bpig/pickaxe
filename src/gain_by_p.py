# -*- coding:utf-8 -*-
from collections import Counter

from common import *
from data_loader import getFt, getAns
import filter_by_rule

def gain(predict, stock, numStock, ds, output):
    money = [0.5, 0.5]
    month = ["init"]
    rate = [1.0]
    
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
            if index < 1:
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
        if output:
            print d, "%.5f" % total, "%.5f" % bg, "->", "%.5f" % ed, \
                "%.5f" % (ed / bg), high, low, stop, len(predict[d]), lack  # , buy.getvalue()[:-1]
        key = d[:-2]
        if key not in month:
            month += [key]
            rate += [total]
        else:
            rate[-1] = total
    if output:
        print "month rate"
        for m, r1, r2 in zip(month[1:], rate[:-1], rate[1:]):
            print "%s %.5f" % (m, r2 / r1)
    return sum(money)

def process(predictFile, numStock, start, period, output=True):
    stock = getFt("data/2010/2016.ft")
    predict = dict(getAns(predictFile))
    
    ds = sorted(predict.keys())
    if start not in ds:
        idx = 0
    else:
        idx = ds.index(start)
    ds = ds[idx:idx + period]
    
    money = gain(predict, stock, numStock, ds, output)
    if output:
        print "after %d days:" % len(ds)
        print "final: " + `money`
    return money

if __name__ == "__main__":
    tgt = "ans/" + sys.argv[1]
    # first do filter
    filter_by_rule.process(tgt)
    
    args = [50, "20160104", 230]
    la = len(sys.argv) - 2
    args[:la] = sys.argv[2:]
    numStock, start, period = args
    
    process(tgt + ".filter", int(numStock), start, int(period))
