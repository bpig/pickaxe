# -*- coding:utf-8 -*-
from common import *
from data_loader import getFt, Ft

def bias(key, info, win):
    ct = len(info.ds)
    if ct < win:
        return []
    e = np.asarray(info.e, dtype=np.float32)
    value = np.empty(ct)
    for i in range(ct - win + 1):
        mean_e = e[i:i + win].mean()
        value[i] = (e[i] - mean_e) / mean_e * 100
    value = value[:-win + 1]
    return zip(info.ds, value)


def cci(key, info, win):
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
    return zip(info.ds, value)

def cdp(key, info, win):
    ct = len(info.ds)-1
    if ct < win:
        return[]
    h = np.asarray(info.h, dtype=np.float32)[1:]
    l = np.asarray(info.l, dtype=np.float32)[1:]
    e = np.asarray(info.e, dtype=np.float32)[1:]
    cdp = (h + l + e) / 3
    ah = cdp + (h - l)
    al = cdp - (h - l)
    nh = cdp * 2 - l
    nl = cdp * 2 - h
    return zip(info.ds, ah), zip(info.ds, nh), zip(info.ds, cdp), zip(info.ds, nl), zip(info.ds, al)

def mtm
