# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *
from data_loader import getAns, getFt, Aux, formatAns

def filterByStop(ds, stock):
    def _inter(_):
        ft = stock[_.code]
        idx = ft.ds.index(ds)
        return ft.status[idx] == 0
    
    return _inter

def filterByHighLine(ds, stock):
    def _inter(_):
        ft = stock[_.code]
        idx = ft.ds.index(ds)
        return ft.high[idx] == ft.low[idx]
    
    return _inter

if __name__ == "__main__":
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    if len(sys.argv) == 3:
        ct = int(sys.argv[2])
    else:
        ct = 50
    
    fin = "ans/" + cfg["tout"]
    fout = open(fin + ".filter", "w")
    
    stock = getFt("data/2010/2016.ft")
    aux = getFt("data/2010/2016.ft.aux", Aux)
    st2016 = set(map(str.strip, open("data/2016.st")))
    
    for ds, ans in getAns(fin):
        bg = len(ans)
        ans = filter(lambda _: _.code not in st2016, ans)
        ans = filter(filterByStop, ans)
        ans = filter(filterByHighLine, ans)
        print ds, bg, "->", len(ans)
        
        ans = map(formatAns, ans)
        fout.write(ds + "," + ",".join(ans) + "\n")

