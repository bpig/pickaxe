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

if __name__ == '__main__':
    print kernels
    k = kernels["base_fea"]
    print k([1.0] * 14)
