#!/bin/env python
# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *
from data_loader import getAns, getFt, Aux, formatAns

def filterByStop(ds, aux):
    def _inter(_):
        ft = aux[_.code]
        idx = ft.ds.index(ds)
        return ft.status[idx] == '0'
    
    return _inter

def filterByHighLine(ds, aux):
    def _inter(_):
        ft = aux[_.code]
        idx = ft.ds.index(ds)
        return not (ft.high[idx] == ft.low[idx] \
                    and float(ft.e[idx]) > float(ft.pe[idx]))
    
    return _inter

def filterByNew(ds, aux):
    def _inter(_):
        ft = aux[_.code]
        idx = ft.ds.index(ds)
        return int(ft.work_day[idx]) > 100
    
    return _inter

def process(fin, newSt=False, high=False, st=False, output=False):
    fout = open(fin + ".filter", "w")
    aux = getFt(AUX_FILE, Aux)
    
    #    ft = aux['600380.SH']
    #    ft2 = stock['600380.SH']
    #    idx = ft.ds.index("20161111")
    #    print idx, ft2.ds[:idx+1], ft2.status[:idx+1]#, ft2.pe[-1], ft2.e[-1], ft2.ds[-1], ft2.rate[-1]
    #    sys.exit(1)
    st2016 = set(map(str.strip, open("data/2016.st")))
    
    for ds, ans in sorted(getAns(fin)):
        ct = [len(ans)]
        
        ans = filter(filterByStop(ds, aux), ans)
        ct += [len(ans)]
        
        if not st:
            ans = filter(lambda _: _.code not in st2016, ans)
            ct += [len(ans)]
        
        if not high:
            ans = filter(filterByHighLine(ds, aux), ans)
            ct += [len(ans)]
        
        if not newSt:
            ans = filter(filterByNew(ds, aux), ans)
            ct += [len(ans)]
        
        if output:
            print ds, ct
        
        ans = map(formatAns, ans)
        if ans:
            fout.write(ds + "," + ",".join(ans) + "\n")

def getArgs():
    parser = ArgumentParser(description="Filter")
    parser.add_argument("-t", dest="tgt", required=True,
                        help="target")
    parser.add_argument("-n", dest="new", action="store_true", default=False,
                        help="st new")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    tgt = "ans/" + args.tgt
    process(tgt, args.n)
