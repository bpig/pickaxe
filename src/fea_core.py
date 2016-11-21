# -*- coding:utf-8 -*-
from common import *
from data_loader import Ft

def bias(info, win):
    ct = len(info.ds)
    if ct < win:
        return fea_length_extend([], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)
    
    ct = ct - win + 1
    value = np.empty(ct)
    for i in range(ct):
        mean_e = e[i:i + win].mean()
        value[i] = (e[i] - mean_e) / mean_e
    return fea_length_extend(value, len(info.ds))

def cci(info, win):
    ct = len(info.ds)
    C = 0.015
    if ct < win:
        return fea_length_extend([], len(info.ds))
    h = np.asarray(info.high, dtype=np.float32)
    l = np.asarray(info.low, dtype=np.float32)
    e = np.asarray(info.e, dtype=np.float32)
    typ = (h + l + e) / 3
    
    ct = ct - win + 1
    value = np.empty(ct)
    for i in range(ct):
        mean_typ = typ[i:i + win].mean()
        avedev_typ = np.abs(typ[i:i + win] - mean_typ).mean()
        if avedev_typ == 0:
            avedev_typ = 1
        value[i] = (typ[i] - mean_typ) / (C * avedev_typ)
    return fea_length_extend(value, len(info.ds))

def cdp(info):  # may be useless
    h = np.asarray(info.high, dtype=np.float32)
    l = np.asarray(info.low, dtype=np.float32)
    e = np.asarray(info.e, dtype=np.float32)
    cdp = (h + l + e) / 3
    ah = cdp + (h - l)
    al = cdp - (h - l)
    nh = cdp * 2 - l
    nl = cdp * 2 - h
    return fea_length_extend(ah, nh, cdp, nl, al, len(info.ds))

def mtm(info, win1, win2):
    ct = len(info.ds)
    if ct < win1 + win2 - 1:
        return fea_length_extend([], [], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)[:-win1]
    n_e = np.asarray(info.e, dtype=np.float32)[win1:]
    
    mtm = e - n_e
    ct = len(mtm) - win2 + 1
    mtmma = np.empty(ct)
    for i in range(ct):
        mtmma[i] = mtm[i:i + win2].mean()
    return fea_length_extend(mtm, mtmma, len(info.ds))

def osc(info, win):
    ct = len(info.ds)
    if ct < win:
        return fea_length_extend([], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)
    
    ct = ct - win + 1
    value = np.empty(ct)
    for i in range(ct):
        mean_e = e[i: i + win].mean()
        value[i] = e[i] - mean_e
    return fea_length_extend(value, len(info.ds))

def psy(info, win):
    ct = len(info.ds) - 1
    if ct < win:
        return fea_length_extend([], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)[:-1]
    pe = np.asarray(info.pe, dtype=np.float32)[:-1]
    gain = e - pe
    
    ct = ct - win + 1
    value = np.empty(ct)
    for i in range(ct):
        value[i] = gain[i:i + win][gain[i:i + win] > 0].size / 1.0 / win
    
    return fea_length_extend(value, len(info.ds))

# win > 12
def vr(info, win):
    ct = len(info.ds) - 1
    if ct < win:
        return fea_length_extend([], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)[:-1]
    pe = np.asarray(info.pe, dtype=np.float32)[:-1]
    v = np.asarray(info.volumn, dtype=np.float32)[:-1]
    
    ct = ct - win + 1
    value = np.empty(ct)
    gain = e - pe
    for i in range(ct):
        avs = v[i:i + win][gain[i:i + win] > 0].sum()
        bvs = v[i:i + win][gain[i:i + win] < 0].sum()
        cvs = v[i:i + win][gain[i:i + win] == 0].sum()
        dom = bvs + 0.5 * cvs
        if dom == 0:
            dom = 1
        value[i] = (avs + 0.5 * cvs) / dom
    return fea_length_extend(value, len(info.ds))

def wms(info, win):
    ct = len(info.ds)
    if ct < win:
        return fea_length_extend([], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)
    l = np.asarray(info.low, dtype=np.float32)
    h = np.asarray(info.high, dtype=np.float32)
    
    ct = ct - win + 1
    value = np.empty(ct)
    for i in range(ct):
        hn = h[i:i + win].max()
        ln = l[i:i + win].min()
        diff = hn - ln
        if diff == 0:
            diff = 1
        value[i] = (hn - e[i]) / diff
    return fea_length_extend(value, len(info.ds))

def obv(info, win):
    ct = len(info.ds)
    e = np.asarray(info.e, dtype=np.float32)
    pe = np.asarray(info.pe, dtype=np.float32)
    gain = e - pe
    v = np.asarray(info.volumn, dtype=np.float32)
    
    value = np.empty(ct)
    value[-1] = v[-1]
    for i in range(-2, -ct - 1, -1):
        if gain[i] > 0:
            value[i] = value[i + 1] + v[i]
        elif gain[i] < 0:
            value[i] = value[i + 1] - v[i]
        else:
            value[i] = value[i + 1]
    return fea_length_extend(value, len(info.ds))

def vvv(info, win):
    ct = len(info.ds)
    if ct < win:
        return fea_length_extend([], len(info.ds))
    v = np.asarray(info.volumn, dtype=np.float32)
    value = np.empty(ct)
    for i in range(ct - win + 1):
        mean_v = v[i:i + win].mean()
        value[i] = v[i] / mean_v
    return fea_length_extend(value, len(info.ds))
