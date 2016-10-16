# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

import sys
import os
import numpy as np
import datetime
from collections import defaultdict
#from scipy import stats
#import yaml
from collections import namedtuple
import random

Fea = namedtuple("Fea", ["key", "value", "tgt"])

def loadFea(filename, shuffle=False):
    datas = []
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        value = l[pos + 1:].split(",")
        tgt = value[-1]
        value = np.asarray(value[:-1]).astype(np.float32)
        datas.append(Fea(key, value, tgt))
    if shuffle:
        random.shuffle(datas)
    return datas
