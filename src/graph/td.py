# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/20"

import matplotlib.pyplot as plt
import datetime

def trans(s):
    y, m, d = map(int, (s[:4], s[4:6], s[6:]))
    return datetime.datetime(y, m, d)

if __name__ == '__main__':
    lt = map(str.strip, open("06.gb"))
    lt = filter(len, lt)
    lt = map(lambda x: x.split(","), lt)
    lt = zip(*lt)
    ds = map(trans, lt[0])
    
    for i in range(1, len(lt)):
        lt[i] = map(float, lt[i])
    t0 = lt[1][0]
    lt[1] = map(lambda x: x / t0, lt[1])
    t0 = lt[2][0]
    lt[2] = map(lambda x: x / t0, lt[2])
    
    plt.plot_date(ds, lt[1], "-r")
    # plt.plot_date(ds, lt[14], "-b")
    # plt.plot_date(ds, lt[-1], "-g")
    plt.show()
