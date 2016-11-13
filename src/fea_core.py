# -*- coding:utf-8 -*-
from common import *
from data_loader import getFt, Ft

def bias(info, win):
    ct = len(info.ds)
    if ct < win:
        return []
    e = np.asarray(info.e, dtype=np.float32)
    value = np.empty(ct)
    for i in range(ct - win + 1):
        mean_e = e[i:i + win].mean()
        value[i] = (e[i] - mean_e) / mean_e * 100
    value = value[:-win + 1]
    return value


def cci(info, win):
    ct = len(info.ds)
    C = 0.015
    if ct < win:
        return[]
    h = np.asarray(info.h, dtype=np.float32)
    l = np.asarray(info.l, dtype=np.float32)
    e = np.asarray(info.e, dtype=np.float32)
    typ = (h + l + e) / 3
    value = np.empty(ct)
    for i in range(ct - win + 1):
        mean_typ = typ[i:i + win].mean()
        avedev_typ = abs(typ[i:i + win] - mean_typ).mean()
        value[i] = (typ[i] - mean_typ) / (C * avedev_typ)
    value = value[:-win + 1]
    return value

def cdp(info):
    h = np.asarray(info.h, dtype=np.float32)[1:]
    l = np.asarray(info.l, dtype=np.float32)[1:]
    e = np.asarray(info.e, dtype=np.float32)[1:]
    cdp = (h + l + e) / 3
    ah = cdp + (h - l)
    al = cdp - (h - l)
    nh = cdp * 2 - l
    nl = cdp * 2 - h
    return ah, nh, cdp, nl, al

def mtm(info, win1, win2):
    ct = len(info.ds)
    if ct < win1:
        return []
    e = np.asarray(info.e, dtype=np.float32)[:win1]
    n_e = np.asarray(info.e, dtype=np.float32)[win1:]
    mtm = e - n_e
    ct = len(mtm)
    if ct < win2:
        return mtm
    for i in range(ct - win2 + 1):
        mtmma = mtm[i:i + win2].mean()
    return mtm, mtmma

def osc(info, win):
    ct = len(info.ds)
    if ct < win:
        return []
    e = np.asarray(info.e, dtype=np.float32)
    value = np.empty(ct)
    for i in range(ct - win + 1):
        mean_e = e[i: i + win].mean()
        value = e[i] - mean_e
    value = value[:-win + 1]
    return value

def psy(info , win):
    ct = len(info.ds) - 1
    if ct < win:
        return []
    e = np.asarray(info.e, dtype=np.float32)[:-1]
    pe = np.asarray(info.pe, dtype=np.float32)[:-1]
    gain = e - pe
    value = np.empty(ct)
    for i in range(ct - win + 1):
        value = len(gain[i:i + win][gain[i:i + win] > 0]) / win * 100
    value = value[:-win + 1]
    return value

# win > 12
def vr(info, win):
    ct = len(info.ds) - 1
    if ct < win:
        return []
    e = np.asarray(info.e, dtype=np.float32)[:-1]
    pe = np.asarray(info.pe, dtype=np.float32)[:-1]
    v = np.asarray(info.volumn, dtype=np.float32)[:-1]
    gain = e - pe
    for i in range(ct - win + 1):
        avs = v[i:i + win][gain[i:i + win] > 0].sum()
        bvs = v[i:i + win][gain[i:i + win] < 0].sum()
        cvs = v[i:i + win][gain[i:i + win] == 0].sum()
        value = (avs + 0.5 * cvs) / (bvs + 0.5 * cvs)
    return value

def wms(info, win):
    ct = len(info.ds)
    if ct < win:
        return []
    e = np.asarray(info.e, dtype=np.float32)
    l = np.asarray(info.l, dtype=np.float32)
    h = np.asarray(info.h, dtype=np.float32)
    value = np.empty(ct)
    for i in range(ct - win + 1):
        hn = h[i:i + win].max()
        ln = l[i:i + win].min()
        value = (hn - e[i]) / (hn - ln) * 100
    value = value[:-win + 1]
    return value

def obv(info, win):
    ct = len(info.ds)
    e = np.asarray(info.e, dtype=np.float32)[:-1]
    pe = np.asarray(info.pe, dtype=np.float32)[:-1]
    gain = e - pe
    v = np.asarray(info.volumn, dtype=np.float32)
    value = np.empty(ct)
    value[-1] = v[-1]
    for i in range(-2, -ct - 1, -1):
        if gain[i+1] > 0:
            value[i] = value[i+1] + v[i]
        if gain[i+1] < 0:
            value[i] = value[i+1] - v[i]
    return value


    
