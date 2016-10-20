# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/20/16"

import matplotlib.pyplot as plt
import datetime
import numpy as np

def getData():
    ls = map(str.strip, open("rate"))
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

if __name__ == '__main__':
    k, v = getData()
    vv = []
    kk = []
    dt = getSS()
    for i in range(len(k)):
        if k[i] in dt:
            vv += [v[i]]
            kk += [k[i]]
    s = [float(dt[_]) for _ in kk]
    s0 = s[0]
    s = map(lambda x: x / s0, s)
    print s0, s[-1]
    kk = map(trans2date, kk)
    print len(s), len(kk)
    plt.plot_date(kk, vv, "m-")
    plt.plot_date(kk, s, "-")
    plt.show()
    # axes.plot_date(dates, yList, 'm-', marker='.', linewidth=1)
    # axes.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    # axes.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
    # figure.autofmt_xdate()  # print k, v
    # plt.plot(k, v, "r")
    # plt.show()
