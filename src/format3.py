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

def genEx(v):
    ex = []
    ex += [np.asarray(v[0], dtype=np.float64)]
    
    cc = Cc(*v[:11])
#    for i in [5, 10, 15]:
    base_ex = []
    for i in [5, 10, 20, 60]:
        # emv_value, emv_ma = emv(cc, i)
        
        # cr_value = cr(cc, i)
        # br_value = br(cc, i)
        
        sma_value = sma(cc.e, i)
        ema_value = ema(cc.e, sma_value, i)
        sma_value = fea_length_extend(sma_value, len(cc.ds))
        ema_value = fea_length_extend(ema_value, len(cc.ds))
        bias_value = bias(cc, i)
        v_value = vvv(cc, i)
        # boll_rate, boll_std = boll(cc, i)
        
        # rsi_value = rsi(cc, i)

        # cci_value = cci(cc, i)
        
        # osc_value = osc(cc, i)
        # psy_value = psy(cc, i)
        # wms_value = wms(cc, i)
        # obv_value = obv(cc, i)
        base_ex += [
            sma_value ,
            # ema_value, bias_value, v_value,
            # emv_value, emv_ma, cr_value, br_value, 
            # boll_rate, boll_std, 
            # rsi_value, cci_value, osc_value, psy_value, wms_value,
            # obv_value
        ]
    # base_ex += [base_ex[0] / base_ex[4]]
    # base_ex[-1][np.isinf(base_ex[-1])] = 0
    # base_ex += [base_ex[1] / base_ex[5]]
    # base_ex[-1][np.isinf(base_ex[-1])] = 0
    # base_ex += [base_ex[2] / base_ex[6]]
    # base_ex[-1][np.isinf(base_ex[-1])] = 0
    # base_ex += [base_ex[3] / base_ex[7]]
    # base_ex[-1][np.isinf(base_ex[-1])] = 0

    ex += base_ex
    # # for (a, b, c) in [(4, 2, 2), (9, 3, 3), (16, 4, 4)]:
    for (a, b, c) in [(9, 3, 3)]:
        k, d, j = kdj(cc, a, b, c)
        ex += [k, d, j]
    
    # # for (l, s, m) in [(5, 3, 2), (10, 5, 3), (15, 7, 5)]:
    # for (l, s, m) in [(5, 3, 2)]:
    #     diff, diff_ma, diff_ema = macd(cc, l, s, m)
    #     ex += [diff]
    
    # ex += [cdp(cc)]
    
    # for (a, b) in [(4, 2), (8, 4), (12, 6)]:
    #     mtm_value, mtma = mtm(cc, a, b)
    #     ex += [mtm_value, mtma]
    
    # for a in [10, 15]:
    #     vr_value = vr(cc, a)
    #     ex += [vr_value]


    return ex

# open,close,high,low,volume
def extend(key, v):
    for i in [2, 3, 4, 5, 6]:
        v[i] = map(float, v[i])
    rate = map(lambda x, y: 0 if x == 0 else y / x, v[3][1:], v[3][:-1]) + [0]
    v_rate = map(lambda x, y: 0 if x == 0 else y / x, v[6][1:], v[6][:-1]) + [0]
    
#    ex = genEx(v)
#    ex = []
    
    work_day = range(len(e_rate), 0, -1)
    
    buy = [-1.0] + v[2][:-1]
    sell = [-1.0, -1.0] + v[3][:-2]

    tgt = map(lambda x, y: y / x, buy, sell)
    v = v + [rate, v_rate, tgt]
    v = map(lambda x: map(str, x), v)

    # work_day = map(str, work_day)
    # aux = [v[0], work_day, v[4], v[5], v[6], v[7], v[8], v[15], v[16], v[18]]
    # for i in range(len(aux)):
    #     aux[i] = aux[i][:200]
    return v

