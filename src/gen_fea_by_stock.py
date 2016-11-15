# -*- coding:utf-8 -*-
from common import *
from data_loader import getFt, Ft, getFtEx
from fea_kernel import *
from fea_core import *

def getBaseInfo(fin):
    st = getFt(fin)
    ex = getFtEx(fin)
    assert set(st.keys()) == set(ex.keys())
    for key in st.keys():
        yield key, st[key], ex[key]

def dump(fout, ds=None, predict=False):
    ct = 0
    fout = open(fout, "w")
    for key, info, exinfo in getBaseInfo():
        ct += genOne(key, info, exinfo, fout, ds, predict)
    return ct

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

def genOne(key, info, exinfo, fout, ds=None, predict=False):
    ct = 0
    if ds:
        if ds in info.ds:
            idx = [info.ds.index(ds)]
            if not predict and idx <=1:
                print "ds %s train is not available"  % ds
                return ct
        else:
            print "ds %s is not available"  % ds
            return ct
    else:
        if not predict:
            idx = [_ for _ in range(2, len(info.ds))]
        else:
            idx = [_ for _ in range(0, len(info.ds))]

    for d in idx:
        feas = []
        feas += [info[_][d] for _ in [1, 2, 3, 9, 10, 11, 12, 13, 14]]
        feas += oneHotStatus(info.status[d], info.s_status[d],
                             info.wav_status[d], info.e_status[d])
        feas += [exinfo[_][d] for _ in range(1, len(exinfo))]
        ds = info[0][d]
        if not predict:
            tgt = info.tgt[d]
            assert tgt > 0, "%s_%s %f" % (key, ds, tgt)
            feas += [tgt]
        info = map(str, feas)
        content = key + "_" + ds + ":" + ",".join(info) + "\n"
        if content:
            fout.write(content)
            ct += 1
    return ct


