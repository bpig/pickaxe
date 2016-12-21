#!/bin/env python
# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *
from data_loader import getAns, getFt, Aux, formatAns

def filterByMa(ds, aux, exKv):
    def _inter(_):
        ft = aux[_.code]
        ex = exKv[_.code]
        idx = ft.ds.index(ds)
        return float(ft.e[idx]) > ex[1][idx] > ex[2][idx] > ex[3][idx] > ex[4][idx]
    return _inter

def filterByStop(ds, aux):
    def _inter(_):
        ft = aux[_.code]
        idx = ft.ds.index(ds)
        return ft.status[idx] == '0'
    
    return _inter

def filterByJump(ds, aux):
    def _inter(_):
        ft = aux[_.code]
        st = ft.ds.index(ds)
        ed = st + 15
        es = sorted(map(float, ft.e[st:ed]))
        return es[-1] / es[0] > 1.1
    
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

def process(fin, newSt=False, high=False, st=False, jump=False, output=False):
    fout = open(fin + ".filter", "w")
    aux = getFt(AUX_FILE, Aux)
    
    #    ft = aux['600380.SH']
    #    ft2 = stock['600380.SH']
    #    idx = ft.ds.index("20161111")
    #    print idx, ft2.ds[:idx+1], ft2.status[:idx+1]#, ft2.pe[-1], ft2.e[-1], ft2.ds[-1], ft2.rate[-1]
    #    sys.exit(1)
    st2016 = set(map(str.strip, open("data/2016.st")))

    exKv = {}
    for f in os.listdir("raw/f13e"):
        if "dumper" in f:
            continue
        ex = np.load("raw/f13e/" + f)
        exKv[f] = ex
    
    for ds, ans in sorted(getAns(fin)):
        ct = [len(ans)]
        
        ans = filter(filterByStop(ds, aux), ans)
        ct += [len(ans)]

        # ans = filter(filterByMa(ds, aux, exKv), ans)
        # ct += [len(ans)]
        
        if not st:
            ans = filter(lambda _: _.code not in st2016, ans)
            ct += [len(ans)]
        
        if not high:
            ans = filter(filterByHighLine(ds, aux), ans)
            ct += [len(ans)]

        # if not jump:
        #     ans = filter(filterByJump(ds, aux), ans)
        #     ct += [len(ans)]
        
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
