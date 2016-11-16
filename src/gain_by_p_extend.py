# -*- coding:utf-8 -*-
from collections import Counter

from common import *
from data_loader import getFt, getAns
import filter_by_rule

def gain(predict, stock, numStock, ds, output, x):
    money = [1.0 / x] * x
    month = ["init"]
    rate = [1.0]
    
    for i, d in enumerate(ds):
        buy = StringIO()
        increase, count = 0, 0
        ii = i % x
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
            #index -= 1  # the day after tomorrow
            index -= x - 1  # the day after tomorrow
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
            #buy.write(key + "_" + rec.tgt + ",")
            #buy.write(key + ",")
            increase += outPrice / inPrice
            buy.write("%s_%.3f," % (key, outPrice / inPrice))
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
            print ("{ds} {total:>7.3f} {rate:>5.3f} " +
                   "{bg:>7.3f} -> {ed:>7.3f} {hi} {lo} {stop} {ct} {lack}").format(
                       ds=d, total=total, rate=ed / bg, 
                       bg=bg, ed=ed, hi=high, lo=low, stop=stop, 
                       ct=len(predict[d]), lack=lack) #, buy.getvalue()[:-1]

        key = d[:-2]
        if key not in month:
            month += [key]
            rate += [total]
        else:
            rate[-1] = total
    if output:
        print "month rate"
        for m, r1, r2 in zip(month[1:], rate[:-1], rate[1:]):
            print "%s %.3f" % (m, r2 / r1)
    return sum(money)

def process(predictFile, numStock, start=None, period=200, output=True, x=4):
    stock = getFt("data/2010/2016.ft")
    predict = dict(getAns(predictFile))
    
    ds = sorted(predict.keys())
    if not start or start not in ds:
        idx = 0
    else:
        idx = ds.index(start)
    ds = ds[idx:idx + period]
    
    money = gain(predict, stock, numStock, ds, output, x)
    if output:
        print "after %d days:" % len(ds)
        print "final: %.3f" % money
    return money


def getArgs():
    parser = ArgumentParser(description="Gain")
    parser.add_argument("-t", dest="tgt", required=True,
                        help="target")
    parser.add_argument("-fn", dest="fn", action="store_true", default=False,
                        help="filter new")
    parser.add_argument("-c", dest="c", default=50, type=int, 
                        help="cal count")
    parser.add_argument("-x", dest="x", default=2, type=int, 
                        help="day")
    parser.add_argument("-d", dest="d", action="store_true", default=False,
                        help="direct, no filter")
    parser.add_argument("-hi", dest="h", action="store_true", default=False,
                        help="high line ok")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    tgt = "ans/" + args.tgt

    if not args.d and not "filter" in tgt:
        filter_by_rule.process(tgt, args.fn, nohigh=not args.h)
        tgt += ".filter"
    
    process(tgt, args.c, x=args.x)