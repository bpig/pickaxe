# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/13"
from common import *

kernels = {}

def register_kernel(func):
    kernels[func.__name__] = func
    return func

@register_kernel
def base_fea(values):
    pe = np.array(values[4])
    items = []
    items += [values[0]]  # dt
    items += [values[3]]  # amount
    items += [values[5] / pe]  # s / pe
    items += [values[6] / pe]  # high / pe
    items += [values[7] / pe]  # low / pe
    items += [values[8] / pe]  # e / pe
    items += [values[9]]  # turnover
    items += [values[8] / values[10]]  # e / high52
    items += [values[8] / values[11]]  # e / low52
    items += [values[13]]  # target
    return items

def emv(info, win):  # self version
    ct = len(info.e)
    if ct < win:
        return fea_length_extend([], [], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)
    pe = np.asarray(info.pe, dtype=np.float32)
    volumn = np.asarray(info.volumn, dtype=np.float32)
    volumn[volumn == 0] = 1
    dis = e - pe
    ans = dis / volumn
    ans_ma = sma(ans, win)
    return fea_length_extend(ans, ans_ma, len(info.ds))

def cr(info, win):
    ct = len(info.pe)
    if ct < win:
        return fea_length_extend([], len(info.ds))
    high = np.asarray(info.high, dtype=np.float32)
    low = np.asarray(info.low, dtype=np.float32)
    mid = (high + low) / 2
    pre_mid = mid[1:]
    h = high[:-1] - pre_mid
    h[h < 0] = 0
    l = pre_mid - low[:-1]
    l[l < 0] = 0
    
    ct = len(pre_mid) - win + 1
    ans = np.empty(ct)
    for i in range(ct):
        l_sum = l[i:i + win].sum()
        if l_sum == 0:
            l_sum = 1
        ans[i] = h[i:i + win].sum() / l_sum
    return fea_length_extend(ans, len(info.ds))

def br(info, win):
    ct = len(info.pe)
    if ct < win:
        return fea_length_extend([], len(info.ds))
    pe = np.asarray(info.pe, dtype=np.float32)
    high = np.asarray(info.high, dtype=np.float32)
    low = np.asarray(info.low, dtype=np.float32)
    h = high - pe
    h[h < 0] = 0
    l = pe - low
    l[l < 0] = 0
    
    ct = ct - win + 1
    ans = np.empty(ct)
    for i in range(ct):
        l_sum = l[i:i + win].sum()
        if l_sum == 0:
            l_sum = 1
        ans[i] = h[i:i + win].sum() / l_sum
    return fea_length_extend(ans, len(info.ds))

def kdj(info, rsv_win, k_win, d_win):
    ct = len(info.e)
    if ct < rsv_win + k_win + d_win - 2:
        return fea_length_extend([],[],[], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)
    high = np.asarray(info.high, dtype=np.float32)
    low = np.asarray(info.low, dtype=np.float32)
    rsv = np.empty(ct - rsv_win + 1)
    for i in range(ct - rsv_win + 1):
        high_max = high[i:i + rsv_win].max()
        low_min = low[i:i + rsv_win].min()
        diff = high_max - low_min
        if diff == 0:
            diff = 1
        rsv[i] = (e[i] - high_max) / diff
    k = sma(rsv, k_win)
    d = sma(k, d_win)
    k = k[:len(d)]
    j = 3 * k - 2 * d
    return fea_length_extend(k, d, j, len(info.ds))

def sma(col, win):
    ct = len(col)
    if ct < win:
        return []
    col = np.asarray(col, dtype=np.float32)
    
    ct = ct - win + 1
    ans = np.empty(ct)
    for i in range(ct):
        ans[i] = col[i:i + win].mean()
    
    return ans

def ema(col, sma_value, win):
    assert len(col) >= len(sma_value)
    if len(sma_value) == 0:
        return []
    ct = len(sma_value)
    col = np.asarray(col[:ct], dtype=np.float32)
    factor = 2.0 / (1 + win)
    ans = np.empty(ct)
    ans[-1] = sma_value[-1]
    for i in range(-2, -ct - 1, -1):
        ans[i] = (col[i] - ans[i + 1]) * factor + ans[i + 1]
    return ans

def macd(info, long_win, short_win, m):
    if len(info.ds) < long_win + short_win + m - 1:
        return fea_length_extend([], [], [], len(info.ds))
    long_ma = sma(info.e, long_win)
    long_ema = ema(info.e, long_ma, long_win)
    
    short_ma = sma(info.e, short_win)
    short_ema = ema(info.e, short_ma, short_win)

    diff = short_ema[:len(long_ema)] - long_ema
    
    diff_ma = sma(diff, m)
    diff_ema = ema(diff, diff_ma, m)
    return fea_length_extend(diff, diff_ma, diff_ema, len(info.ds))

def boll(info, win):
    ct = len(info.ds)
    if ct < win:
        return fea_length_extend([],[], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)
    
    ct = ct - win + 1
    band_rate, band_std = np.empty((2, ct))
    for i in range(ct):
        e_win = e[i:i + win]
        std = e_win.std()
        mean = e_win.mean()
        if mean == 0:
            band_rate[i] = 0
        else:
            band_rate[i] = std / mean 
        band_std[i] = std
    return fea_length_extend(band_rate, band_std, len(info.ds))

def rsi(info, win):
    ct = len(info.e) - 1
    if ct < win:
        return fea_length_extend([], len(info.ds))
    e = np.asarray(info.e, dtype=np.float32)[:-1]
    pe = np.asarray(info.pe, dtype=np.float32)[:-1]
    gain = e - pe
    
    rsi_value = np.empty(ct)
    ave_gain = gain[-win:][gain[-win:] > 0].sum() / win
    ave_lost = -gain[-win:][gain[-win:] < 0].sum() / win
    rsi_value[-win] = 0 if ave_lost == 0 else 100 - 100 / (ave_gain / ave_lost + 1)
    for i in range(-win - 1, -ct - 1, -1):
        g = gain[i]
        ag = 0 if g < 0 else g
        al = 0 if g > 0 else -g
        ave_gain = (ag + ave_gain * (win - 1)) / win
        ave_lost = (al + ave_lost * (win - 1)) / win
        rsi_value[i] = 0 if ave_lost == 0 else 100 - 100 / (ave_gain / ave_lost + 1)
    rsi_value = rsi_value[:-win + 1]
    return fea_length_extend(rsi_value, len(info.ds))

if __name__ == '__main__':
    print kernels
    k = kernels["base_fea"]
    print k([1.0] * 14)
