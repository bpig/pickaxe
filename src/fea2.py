# -*- coding:utf-8 -*-
from common import *

kernels = {}

def register_kernel(func):
    kernels[func.__name__] = func
    return func

def rateCount(rates):
    def trans(x):
        x = int(x + 10)
        x = min(10, x)
        x = max(-10, x)
        return x
    rates = map(trans, rates)
    ans = [0] * 21
    for r in rates:
        ans[r] += 1
    return ans

def genBasic(vals):
    vals = np.asarray(vals, dtype=np.float32)
    res = [np.mean(vals), np.std(vals), max(vals), min(vals)]
    return res

def normalize(value):
    v = np.asarray(value, dtype=np.float32)
    v = (v - v.mean()) / v.std()
    return list(v)

def filterByStop(info, win):
    return np.any(np.asarray(info.volumn[idx:idx+win]) == 0) \
        or np.any(np.asarray(info.amount[idx:idx+win]) == 0)
    
def genStatus(status):
    ct0 = Counter(map(int, status[0]))
    ct1 = Counter(map(int, status[1]))
    ct2 = Counter(map(int, status[2]))
    ct3 = Counter(map(int, status[3]))
    return [ct0[0], ct0[1],
            ct1[0], ct1[1], ct1[2],
            ct2[0], ct2[1] + ct2[3], ct2[2] + ct2[3], ct2[3],
            ct3[0], ct3[1], ct3[2]]

def oneHotStatus(status, sstatus, wavstatus, estatus):
    arr1 = [0] * 2
    arr1[int(status)] = 1
    arr2 = [0] * 3
    arr2[int(sstatus)] = 1
    arr3 = [0] * 4
    arr3[int(wavstatus)] = 1
    if int(wavstatus) == 3:
        arr3[1] = 1
        arr3[2] = 1
        arr3[3] = 1
    arr4 = [0] * 3
    arr4[int(estatus)] = 1
    return arr1 + arr2 + arr3 + arr4

def concatRecord(feas, info, idx):
    ds = info.ds[idx]
    tgt = info.tgt[idx]
    feas += [tgt]
    feas = map(str, feas)
    return (key + "_" + ds, ",".join(feas))

@register_kernel
def f1(key, info, ex, win=15):
    omit = 30
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    for idx in select:
        feas = []
        for i in range(win):
            n = idx + i
            feas += [info[row][n]
                     for row in [1, 2, 3, 9, 10, 11, 12, 13, 14, 19, 20]]
            feas += oneHotStatus(info.status[n], info.s_status[n],
                                 info.wav_status[n], info.e_status[n])
        feas += [ex[row][idx] for row in range(1, len(ex))]
        ans += [concatRecord(feas, info, idx)]
    return ans

@register_kernel
def f2(key, info, ex, win=15):
    omit = 30
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    for idx in select:
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
            feas += rateCount(rates)

        for i in range(win):
            n = idx + i
            feas += [ex[row][n] for row in range(1, len(ex))]
        ans += [concatRecord(feas, info, idx)]
    return ans

@register_kernel
def f3(key, info, ex, win=15):
    omit = 60
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    for idx in select:
        feas = []
        for i in range(win):
            n = idx + i
            feas += [info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9, 10]]
            feas += [info[row][n]
                     for row in [1, 11, 12, 13, 14, 19, 20]]

        for i in range(1, win):
            n = idx + i
            feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9]]

        windows = [2, 3, 5, 7, 15]
        for w in windows:
            feas += rateCount(info[1][idx:idx+w])
            for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
                feas += genBasic(info[i][idx:idx+w])
        ans += [concatRecord(feas, info, idx)]
    return ans

@register_kernel
def f4(key, info, ex, win=15):
    omit = 60
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    for idx in select:
        feas = []
        for i in range(win):
            n = idx + i
            feas += [info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9, 10]]
            feas += [info[row][n]
                     for row in [1, 11, 12, 13, 14, 19, 20]]

        for i in range(1, win):
            n = idx + i
            feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9]]

        windows = [2, 3, 5, 7, 15]
        for w in windows:
            feas += rateCount(info[1][idx:idx+w])
            for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
                feas += genBasic(info[i][idx:idx+w])

        for i in range(win):
            n = idx + i
            feas += [ex[row][n] for row in range(1, len(ex))]
        ans += [concatRecord(feas, info, idx)]
    return ans

@register_kernel
def f5(key, info, ex, win=15):
    omit = 60
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    for idx in select:
        feas = []
        if filterByStop(info, win):
            continue

        for i in range(win):
            n = idx + i
            feas += [info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9, 10]]
            feas += [info[row][n]
                     for row in [1, 11, 12, 13, 14, 19, 20]]

        for i in range(1, win):
            n = idx + i
            feas += [0 if info[row][n] == 0 else info[row][idx] / info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9]]

        windows = [2, 3, 5, 7, 15]
        for w in windows:
            feas += rateCount(info[1][idx:idx+w])
            for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
                feas += genBasic(info[i][idx:idx+w])
        ans += [concatRecord(feas, info, idx)]
    return ans

@register_kernel
def f6(key, info, ex, win=15):
    omit = 60
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    for idx in select:
        feas = []
        for i in range(win):
            n = idx + i
            feas += [info[row][n]
                     for row in [2, 3, 5, 6, 7, 8, 9, 10]]
            feas += [info[row][n]
                     for row in [1, 11, 12, 13, 14, 19, 20]]

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
            feas += rateCount(info[1][idx:idx+w])
            for i in [2, 3, 9, 11, 12, 13, 14, 19, 20]:
                feas += genBasic(info[i][idx:idx+w])
        ans += [concatRecord(feas, info, idx)]
    return ans


@register_kernel
def f7(key, info, ex, win=60):
    omit = 60
    if len(info.ds) < omit:
        return []
    select = range(len(info.ds) - omit + 1)
    ans = []
    for idx in select:
        feas = []
        if filterByStop(info, win):
            continue

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
        ans += [concatRecord(feas, info, idx)]
    return ans

@register_kernel
def f8(key, info, ex, win=60):
    return f3(key, info, ex, win)

@register_kernel
def f9(key, info, ex, win=120):
    return f3(key, info, ex, win)
