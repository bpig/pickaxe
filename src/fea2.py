# -*- coding:utf-8 -*-
from common import *
from fea2_base import *

kernels = {}

def register_kernel(func):
    kernels[func.__name__] = func
    return func

@register_kernel
@fea_frame
def f2(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        n = idx + i
        feas += [info[row][n]
                 for row in [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 19, 20]]

    for i in range(1, win):
        n = idx + i
        feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9]]

    windows = [5, 10, 15]
    for w in windows:
        rates = info[1][idx:idx+w]
        feas += rateBucket(rates)

    for i in range(win):
        n = idx + i
        feas += [ex[row][n] for row in range(1, len(ex))]
    return feas

@register_kernel
@fea_frame
def f3(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)

    for i in range(1, win):
        n = idx + i
        feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                 for row in [2, 3, 5, 6, 7, 8, 9]]

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])[1:]
    return feas

@register_kernel
@fea_frame
def f4(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)

    for i in range(1, win):
        n = idx + i
        feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                 for row in [2, 3, 5, 6, 7, 8, 9]]

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])[1:]

    for i in range(win):
        n = idx + i
        feas += [ex[row][n] for row in range(1, len(ex))]
    return feas

@register_kernel
@fea_frame
def f5(info, ex, idx, win=15):
    feas = []
    if filterByStop(info, win):
        return []

    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)

    for i in range(1, win):
        n = idx + i
        feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                 for row in [2, 3, 5, 6, 7, 8, 9]]

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])[1:]
    return feas

@register_kernel
@fea_frame
def f6(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)

    low = info.low[idx+ win - 1]
    vol = info.volumn[idx+ win - 1]
    amount = info.amount[idx+ win - 1]
    turnover = info.turnover[idx+ win - 1]
    for i in range(win):
        n = idx + i
        feas += [0 if low == 0 else info[row][n] / low
                     for row in [5, 6, 7, 8]]
        feas += [0 if vol == 0 else info[2][n] / vol]
        feas += [0 if amount == 0 else info[3][n] / amount]
        feas += [0 if turnover == 0 else info[9][n] / turnover]

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])[1:]
    return feas


@register_kernel
@fea_frame
def f7(info, ex, idx, win=60):
    feas = []
    if filterByStop(info, win):
        return []

    low = info.low[idx+ win - 1]
    vol = info.volumn[idx+ win - 1]
    amount = info.amount[idx+ win - 1]
    turnover = info.turnover[idx+ win - 1]

    value, vols, amounts, turnovers = [], [], [], []

    for i in range(win):
        n = idx + i
        value += [0 if low == 0 else info[row][n] / low
                  for row in [5, 6, 7, 8]]
        vols += [0 if vol == 0 else info.volumn[n] / vol]
        amounts += [0 if amount == 0 else info.amount[n] / amount]
        turnovers += [0 if turnover == 0 else info.turnover[n] / turnover]

    feas += normalize(value)
    feas += normalize(vols)
    feas += normalize(amounts)
    feas += normalize(turnovers)

    v = []
    for  row in [5, 6, 7, 8]:
        v += [info[row][n] for n in range(idx, idx+win)]
    feas += normalize(v)

    for row in [1, 2, 3, 9, 11, 12, 13, 14, 19, 20]:
        v = [info[row][n] for n in range(idx, idx+win)]
        feas += normalize(v)
    return feas

@register_kernel
def f8(info, ex, idx, win=60):
    return f3(info, ex, idx, win)

@register_kernel
def f9(info, ex, idx, win=120):
    return f3(info, ex, idx, win)

@register_kernel
@fea_frame
def f10(info, ex, idx, win=15):
    feas = []
    value = []
    for i in range(win + 2):
        value += [np.asarray(getAbsValue(info, idx + i))]

    delta, delta2 = getDelta(value, win)

    return flat(win, value, delta, delta2)

@register_kernel
@fea_frame
def f11(info, ex, idx, win=15):
    v1, v2 = [], []
    for i in range(win + 2):
        v1 += [np.asarray(getAbsValue(info, idx + i))]
        v2 += [np.asarray(getRevValue(info, idx + i))]
    d1, d11 = getDelta(v1, win)
    d2, d22 = getDelta(v2, win)
    
    return flat(win, v1, d1, d11, v2, d2, d22)

@register_kernel
@fea_frame
def f12(info, ex, idx, win=15):
    v1, v2 = [], []
    for i in range(win + 2):
        v1 += [np.asarray(getAbsValue(info, idx + i))]
    d1, d11 = getDelta(v1, win)
        
    for i in range(win):        
        v2 += getRevValue(info, idx + i)

    feas = flat(win, v1, d1, d11)
    for r in v2:
        feas += rateHash(r)
    return feas

@register_kernel
@fea_frame
def f13(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        
    v2 = []
    for i in range(win):        
        v2 += getRevValue(info, idx + i)

    for r in v2:
        feas += rateHash(r)

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        for i in [2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])

    return feas

@register_kernel
@fea_frame
def f14(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])
        for i in range(22, 69):
            feas += genBasic(info[i][idx:idx+w])
    return feas

@register_kernel
@fea_frame
def f15(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)
        feas += getMoneyValue(info, idx + i)
        feas += getIndicatorValue(info, idx + i)
        feas += getMissValue(info, idx + i)

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])
        for i in range(21, 78):
            feas += genBasic(info[i][idx:idx+w])
    return feas

@register_kernel
@fea_frame
def f16(info, ex, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)
        feas += getMoneyValue(info, idx + i)
        feas += getIndicatorValue(info, idx + i)
        feas += getMissValue(info, idx + i)
        feas += getAdditionValue(info, idx + i)

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])
        for i in range(21, 96):
            feas += genBasic(info[i][idx:idx+w])
    return feas

@register_kernel
@fea_frame
def f17(info, mix, idx, win=15):
    feas = []
    for i in range(win):
        feas += getAbsValue(info, idx + i)
        feas += getRevValue(info, idx + i)

    for i in range(1, win):
        n = idx + i
        feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                 for row in [2, 3, 5, 6, 7, 8, 9]]

    windows = [2, 3, 5, 7, 15]
    for w in windows:
        feas += rateBucket(info[1][idx:idx+w])
        for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
            feas += genBasic(info[i][idx:idx+w])[1:]
    if feas:
        feas += mix[1]
    return feas
