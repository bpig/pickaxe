# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *
from data_loader import getAns, getFt, Aux, formatAns

def filterByStop(ds, stock):
    def _inter(_):
        ft = stock[_.code]
        idx = ft.ds.index(ds)
        return ft.status[idx] == '0'
    
    return _inter

def filterByHighLine(ds, stock):
    def _inter(_):
        ft = stock[_.code]
        idx = ft.ds.index(ds)
        return not(ft.high[idx] == ft.low[idx] \
                               and float(ft.e[idx]) > float(ft.pe[idx]))
    
    return _inter

def filterByNew(ds, aux):
    def _inter(_):
        ft = aux[_.code]
        idx = ft.ds.index(ds)
        return int(ft.work_day[idx]) > 120
    
    return _inter

if __name__ == "__main__":
    if len(sys.argv) == 3:
        ct = int(sys.argv[2])
    else:
        ct = 50
    
    fin = "ans/" + sys.argv[1]
    fout = open(fin + ".filter", "w")
    
    stock = getFt("data/2010/2016.ft")
    aux = getFt("data/2010/2016.ft.aux", Aux)
    st2016 = set(map(str.strip, open("data/2016.st")))
    
    for ds, ans in sorted(getAns(fin)):
        ct = [len(ans)]
        ans = filter(lambda _: _.code not in st2016, ans)
        ct += [len(ans)]
        ans = filter(filterByStop(ds, stock), ans)
        ct += [len(ans)]
        ans = filter(filterByHighLine(ds, stock), ans)
        ct += [len(ans)]
        ans = filter(filterByNew(ds, aux), ans)
        ct += [len(ans)]
        print ds, ct
        
        ans = map(formatAns, ans)
        fout.write(ds + "," + ",".join(ans) + "\n")
