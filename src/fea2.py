# -*- coding:utf-8 -*-
from common import *
from data_loader import Ft, getFt, getFtEx

def getBaseInfo(fin):
    st = getFt(fin)
    ex = getFtEx(fin)
    assert set(st.keys()) == set(ex.keys())
    for key in st.keys():
        yield key, st[key], ex[key]

def process(ds=None):
    ans = []
    for key, info, exinfo in getBaseInfo():
        ans += genOneStock(key, info, exinfo, ds)
    return ans

def oneHotStatus(status, sstatus, wavstatus, estatus):
    arr1 = [0] * 2
    arr1[int(status)] = 1
    arr2 = [0] * 3
    arr2[int(sstatus)] = 1
    arr3 = [0] * 4
    arr3[int(wavstatus)] = 1
    if int(wavstatus) == 3:
        arr3[2] = 1
        arr3[3] = 1
    arr4 = [0] * 3
    arr4[int(estatus)] = 1
    return arr1 + arr2 + arr3 + arr4

def genOneStock(key, info, ex, ds=None):
    win = 15
    if ds:
        if ds in info.ds:
            select = [info.ds.index(ds)]
        else:
            print "ds %s is not available" % ds
            return []
    else:
        select = range(len(info.ds) - win)
    
    ans = []
    for idx in select:
        feas = []
        # assert len(info) == 20, len(info)
        for i in range(win):
            feas += [info[row][idx - i]
                     for row in [1, 2, 3, 9, 10, 11, 12, 13, 14, 19, 20]]
            feas += oneHotStatus(info.status[idx - i], info.s_status[idx - i],
                                 info.wav_status[idx - i], info.e_status[idx - i])
        feas += [ex[row][idx] for row in range(1, len(ex))]
        ds = info.ds[idx]
        tgt = info.tgt[idx]
        feas += [tgt]
        feas = map(str, feas)
        content = (key + "_" + ds, ",".join(feas))
        ans += [content]
    return ans
