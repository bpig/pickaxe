# -*- coding:utf-8 -*-
from common import *

def concatRecord(feas, info, idx, key):
    ds = info.ds[idx]
    tgt = info.tgt[idx]
    feas += [tgt]
    feas = map(str, feas)
    return (key + "_" + ds, ",".join(feas))

def fea_frame(func):
    @wraps(func)
    def _inter(key, info, ex, win=15):
        # omit = max(60, win)
        omit = win
        if len(info.ds) < omit:
            return []
        select = range(len(info.ds) - omit + 1)
        ans = []
        for idx in select:
            feas = func(info, ex, idx, win)
            if feas:
                ans += [concatRecord(feas, info, idx, key)]
        return ans
    return _inter

def getMoneyValue(info, idx):
    return [info[row][idx] for row in range(21, 62)]

def getIndicatorValue(info, idx):
    return [info[row][idx] for row in range(62, 68)]

def getMissValue(info, idx):
    return [info[row][idx] for row in range(68, 78)]

def getAdditionValue(info, idx):
    return [info[row][idx] for row in range(78, 96)]

def getAbsValue(info, idx):
    return [info[row][idx] for row in [2, 3, 5, 6, 7, 8, 9, 10]]

def getRevValue(info, idx):
    return [info[row][idx] for row in [1, 11, 12, 13, 14, 19, 20]]

def rateTrans(x):
    x = int(x)
    x = min(10, x)
    x = max(-10, x)
    x += 10
    return x

def rateHash(rate):
    ans = [0] * 21
    idx = rateTrans(rate)
    ans[idx] = 1
    return ans

def rateBucket(rates):
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
    res = [np.sum(vals), np.mean(vals), np.std(vals), max(vals), min(vals)]
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

def getDelta(value, win):
    delta = []
    for i in range(win + 1):
        delta += [value[i] - value[i+1]]
        
    delta2 = []
    for i in range(win):
        delta2 += [delta[i] - delta[i+1]]
    return delta, delta2

def flat(win, *arys):
    feas = []
    for i in range(win):
        for ary in arys:
            feas += list(ary[i])
    return feas

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

