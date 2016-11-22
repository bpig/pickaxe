# -*- coding:utf-8 -*-
from common import *
from data_loader import Ft, getFt, getFtEx

kernels = {}

def register_kernel(func):
    kernels[func.__name__] = func
    return func

def rateCount(rates):
    def trans(x):
        x = 10 * x
        x = min(10.0, x)
        x = max(-10.0, x)
        x += 10
        return int(x)
    rates = map(trans, rates)
    ans = [0] * 21
    for r in rates:
        ans[r] += 1
    return ans

def genStatus(status):
    ct0 = Counter(map(int, status[0]))
    ct1 = Counter(map(int, status[1]))
    ct2 = Counter(map(int, status[2]))
    ct3 = Counter(map(int, status[3]))
    return [ct0[0], ct0[1],
            ct1[0], ct1[1], ct1[2],
            ct2[0], ct2[1] + ct2[3], ct2[2] + ct2[3], ct2[3],
            ct3[0], ct3[1], ct3[2]]

@register_kernel
def f1(key, info, ex):
    omit = 30
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    win = 15
    for idx in select:
        feas = []
        # assert len(info) == 20, len(info)
        for i in range(win):
            n = idx + i
            feas += [info[row][n]
                     for row in [1, 2, 3, 9, 10, 11, 12, 13, 14, 19, 20]]
            feas += oneHotStatus(info.status[n], info.s_status[n],
                                 info.wav_status[n], info.e_status[n])
        feas += [ex[row][idx] for row in range(1, len(ex))]
        ds = info.ds[idx]
        tgt = info.tgt[idx]
        feas += [tgt]
        feas = map(str, feas)
        content = (key + "_" + ds, ",".join(feas))
        ans += [content]
    return ans

@register_kernel
def f2(key, info, ex):
    omit = 30
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    win = 20
    for idx in select:
        feas = []
        for i in range(win):
            n = idx + i
            feas += [info[row][n]
                     for row in [1, 11, 12, 13, 14, 19, 20]]            
        for i in range(1, win):
            n = idx + i
            feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9]]

        #windows = [1, 2, 3, 5, 7, 15, 20]
        windows = [5, 10, 15, 20]
        for w in windows:
            #items = map(lambda x: x[idx:idx+win], info)
            #feas += genStatus(items[15:19])
            rates = info[1][idx:idx+win]
            feas += rateCount(rates)

        feas += [ex[row][idx] for row in range(1, len(ex))]
        ds = info.ds[idx]
        tgt = info.tgt[idx]
        feas += [tgt]
        feas = map(str, feas)
        content = (key + "_" + ds, ",".join(feas))
        ans += [content]
    return ans
