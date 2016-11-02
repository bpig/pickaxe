# -*- coding:utf-8 -*-
from collections import Counter

from common import *
from data_loader import getFt, getAns

def gain(predict, stock, numStock, ds):
    totalMoney = [0.5, 0.5]
    updateMoney = [0.5, 0.5]
    
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
        
        if count != 0:
            updateMoney[ii] = (increase / count - 0.0015) * totalMoney[ii]
        
        bg = totalMoney[ii]
        ed = updateMoney[ii]
        lack = ""
        if count < numStock:
            lack = "lack(%d)" % count
        
        totalMoney[ii] = updateMoney[ii]
        total = sum(totalMoney)
        print d, "%.8f" % total, "%.8f" % bg, "->", "%.8f" % ed, \
            "%.8f" % (ed / bg), high, low, stop, len(predict[d]), lack #, buy.getvalue()[:-1]
    
    return i, sum(totalMoney)

def process(predictFile, numStock, period, start):
    stock = getFt("data/2010/2016.ft")
    predict = dict(getAns(predictFile))
    
    ds = sorted(predict.keys())
    idx = ds.index(start)
    ds = ds[idx:idx + period]
    
    i, money = gain(predict, stock, numStock, ds)
    print "after " + str(i + 1) + " days:"
    print "final: " + `money`

if __name__ == "__main__":
    pfile = "ans/" + sys.argv[1]
    
    try:
        numStock = 50
        numStock = int(sys.argv[2])
    except:
        pass
    try:
        start = "20160104"
        # start = "20161020"
        start = sys.argv[3]
    except:
        pass
    try:
        period = 230
        period = int(sys.argv[4])
    except:
        pass
    
    process(pfile, numStock, period, start)

