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

def rsi(key, info, win):
    '''
    :param key: st name
    :param info: FT info
    :param win: win
    :return: list((date, value), (date, value))  , sorted by date reversed
    '''
    ct = len(info.ds) - 1
    if ct < win:
        return []
    e = np.asarray(info.e, dtype=np.float32)[:-1]
    pe = np.asarray(info.pe, dtype=np.float32)[:-1]
    gain = e - pe
    value = np.empty(ct)
    ave_gain = gain[-win:][gain[-win:] > 0].sum() / win
    ave_lost = -gain[-win:][gain[-win:] < 0].sum() / win
    value[-win] = 0 if ave_lost == 0 else 100 - 100 / (ave_gain / ave_lost + 1)
    for i in range(-win - 1, -ct - 1, -1):
        g = gain[i]
        ag = 0 if g < 0 else g
        al = 0 if g > 0 else -g
        ave_gain = (ag + ave_gain * (win - 1)) / win
        ave_lost = (al + ave_lost * (win - 1)) / win
        value[i] = 0 if ave_lost == 0 else 100 - 100 / (ave_gain / ave_lost + 1)
    value = value[:-win + 1]
    return zip(info.ds, value)

if __name__ == '__main__':
    print kernels
    k = kernels["base_fea"]
    print k([1.0] * 14)
