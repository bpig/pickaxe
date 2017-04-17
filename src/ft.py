#!/bin/env python

from common import *
from fea_kernel import *
from fea_core import *
from data_loader import Cc


def getStatus(rate):
    if rate <= 0.901:
        return 2
    elif rate >= 1.099:
        return 1
    return 0


def getWavStatus(h_rate, l_rate):
    if h_rate >= 1.099 and l_rate <= 0.901:
        return 3
    elif l_rate <= 0.901:
        return 2
    elif h_rate >= 1.099:
        return 1
    return 0


def extend(key, v):
    for i in [2, 3, 4, 5, 6, 7, 8, 9]:
        v[i] = map(float, v[i])
    a_rate = map(lambda x, y: 0 if x == 0 else y / x, v[3][1:], v[3][:-1]) + [0]
    v_rate = map(lambda x, y: 0 if x == 0 else y / x, v[2][1:], v[2][:-1]) + [0]
    s_rate = map(lambda x, y: y / x, v[4], v[5])
    h_rate = map(lambda x, y: y / x, v[4], v[6])
    l_rate = map(lambda x, y: y / x, v[4], v[7])
    e_rate = map(lambda x, y: y / x, v[4], v[8])
    status = map(lambda turnover: 1 if turnover == 0.0 else 0, v[9])
    s_status = map(getStatus, s_rate)
    wav_status = map(getWavStatus, h_rate, l_rate)
    e_status = map(getStatus, e_rate)

    work_day = range(len(e_rate), 0, -1)

    for i in range(len(status)):
        if status[i] == 0:
            continue
        if s_status[i] != 0 or e_status[i] != 0 or wav_status[i] != 0:
            print "strange %s_%s %d %d %d %d" % \
                  (key, v[0][i], status[i], s_status[i], wav_status[i], e_status[i])

    buy = map(lambda x, y: float(y) if x != 1 else -1.0, status, v[5])
    sell = map(lambda x, y: float(y) if x != 1 else -1.0, status, v[8])
    buy = [-1.0] + buy[:-1]
    sell = [-1.0, -1.0] + sell[:-2]
    tgt = map(lambda x, y: -1.0 if x < 0 or y < 0 else y / x, buy, sell)
    v = v[:11] + [s_rate, h_rate, l_rate, e_rate,
                  status, s_status, wav_status, e_status,
                  a_rate, v_rate] + v[11:] + [tgt]
    # v += [s_rate, h_rate, l_rate, e_rate, status, s_status, wav_status, e_status,
    #       a_rate, v_rate, tgt]
    v = map(lambda x: map(str, x), v)
    work_day = map(str, work_day)
    aux = [v[0], work_day, v[4], v[5], v[6], v[7], v[8], v[15], v[16], v[18], v[2]]
    for i in range(len(aux)):
        aux[i] = aux[i][:200]
    return v, aux
