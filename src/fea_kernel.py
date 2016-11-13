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

def cr(info, win):
    ct = len(info.pe)
    if ct < win:
        return []
    high = np.asarray(info.high, dtype=np.float32)
    low = np.asarray(info.low, dtype=np.float32)
    mid = (high + low) / 2
    pre_mid = mid[1:]
    h = high[:-1] - pre_mid
    h[h < 0] = 0
    l = pre_mid - low[:-1]
    l[l < 0] = 0
    ct = len(pre_mid)
    ans = np.empty(ct - win + 1)
    for i in range(ct - win + 1):
        l_sum = l[i:i + win].sum()
        if l_sum == 0:
            l_sum = 1
        ans[i] = h[i:i + win].sum() / l_sum
    return ans

def br(info, win):
    ct = len(info.pe)
    if ct < win:
        return []
    pe = np.asarray(info.pe, dtype=np.float32)
    high = np.asarray(info.high, dtype=np.float32)
    low = np.asarray(info.low, dtype=np.float32)
    h = high - pe
    h[h < 0] = 0
    l = pe - low
    l[l < 0] = 0
    ans = np.empty(ct - win + 1)
    for i in range(ct - win + 1):
        l_sum = l[i:i + win].sum()
        if l_sum == 0:
            l_sum = 1
        ans[i] = h[i:i + win].sum() / l_sum
    return ans

def kdj():
    pass

def sma(col, win):
    ct = len(col)
    if ct < win:
        return []
    ans = np.empty(ct)
    col = np.asarray(col, dtype=np.float32)
    for i in range(ct - win + 1):
        ans[i] = col[i:i + win].mean()
    ans = ans[:-win + 1]
    
    return ans

def ema(col, sma_value, win):
    assert len(col) >= len(sma_value)
    ct = len(sma_value)
    col = np.asarray(col[:ct], dtype=np.float32)
    factor = 2.0 / (1 + win)
    ans = np.empty(ct)
    ans[-1] = sma_value[-1]
    for i in range(-2, -ct - 1, -1):
        ans[i] = (col[i] - ans[i + 1]) * factor + ans[i + 1]
    return ans

def macd(info, long_win, short_win, m):
    long_ma = sma(info.e, long_win)
    long_ema = ema(info.e, long_ma, long_win)
    
    short_ma = sma(info.e, short_win)
    short_ema = ema(info.e, short_ma, short_win)
    
    diff = short_ema[:len(long_ema)] - long_ema
    
    diff_ma = sma(diff, m)
    diff_ema = ema(diff, diff_ma, m)
    return diff_ema

def boll(info, win):
    ct = len(info.ds)
    if ct < win:
        return []
    ds = info.ds[:-win + 1]
    band_mid, band_upper, band_lower = np.empty((3, len(ds)))
    e = np.asarray(info.e, dtype=np.float32)
    for i in range(ct - win + 1):
        e_win = e[i:i + win]
        std = e_win.std()
        mean = e_win.mean()
        band_mid[i] = mean
        band_upper[i] = mean + std * 2
        band_lower[i] = mean - std * 2
    band_width = (band_upper - band_lower) / band_mid
    return ds, band_upper, band_mid, band_lower, band_width

def rsi(info, win):
    ct = len(info.e) - 1
    if ct < win:
        return []
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
    return rsi_value

if __name__ == '__main__':
    print kernels
    k = kernels["base_fea"]
    print k([1.0] * 14)
