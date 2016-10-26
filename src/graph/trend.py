# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/20/16"

import matplotlib.pyplot as plt
import datetime
import numpy as np

def getData(filename):
    ls = map(str.strip, open(filename))
    ls = filter(lambda x: x, ls)
    kv = map(lambda x: x.split()[:2], ls)[:-27]
    return zip(*kv)

def getSS():
    ls = map(str.strip, open("000001.ss"))[1:]
    ls = filter(lambda x: x, ls)
    kv = map(lambda x: x.split(",")[:2], ls)
    k, v = zip(*kv)
    k = map(lambda x: "".join(x.split("-")), k)
    return dict(zip(k, v))

def trans2date(s):
    y = int(s[:4])
    m = int(s[4:6])
    d = int(s[6:])
    return datetime.datetime(y, m, d)

def filterByYahoo(k, v, dt):
    vv = []
    kk = []
    for i in range(len(k)):
        if k[i] in dt:
            vv += [v[i]]
            kk += [k[i]]
    
    return kk, vv

def getYahoo(dt, k):
    s = [float(dt[_]) for _ in k]
    s0 = s[0]
    s = map(lambda x: x / s0, s)
    return s

if __name__ == '__main__':
    k, v = getData("rate")
    k1, v1 = getData("rate.v2601")
    k2, v2 = getData("rate.c24")
    k3, v3 = getData("rate.v41200")
    
    dt = getSS()
    k, v = filterByYahoo(k, v, dt)
    k1, v1 = filterByYahoo(k1, v1, dt)
    k2, v2 = filterByYahoo(k2, v2, dt)
    k3, v3 = filterByYahoo(k3, v3, dt)
    assert len(k) == len(k1)
    s = getYahoo(dt, k)
    
    k = map(trans2date, k)
    
    plt.plot_date(k, v3, "r-")
    plt.plot_date(k, v2, "-")
    plt.plot_date(k, v1, "-")
    plt.plot_date(k, v, "-")
    plt.plot_date(k, s, "-")
    plt.show()
    # axes.plot_date(dates, yList, 'm-', marker='.', linewidth=1)
    # axes.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    # axes.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
    # figure.autofmt_xdate()  # print k, v
    # plt.plot(k, v, "r")
    # plt.show()
