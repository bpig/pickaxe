# -*- coding:utf-8 -*-
from common import *
from data_loader import Ft, getFt, getFtEx

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

def genOneStock(key, info, ex):
    if len(info.ds) < 120:
        return []
    select = range(len(info.ds) - 120 + 1)
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
