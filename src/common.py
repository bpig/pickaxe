# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

import sys
import os
import numpy as np
import logging
import math
import pickle
import csv
import datetime
import random
import time
import sys
import logging
import operator
from itertools import chain
from cStringIO import StringIO
from collections import defaultdict
from collections import namedtuple
from collections import Counter
import multiprocessing
import subprocess
import collections
import time
import random
from argparse import ArgumentParser
import itertools
from functools import wraps

try:
    import yaml
    import pandas as pd
    import tushare as ts
except:
    pass


# from scipy import stats

class TimeLog:
    def __init__(self, name=""):
        self.n = name

    def __enter__(self):
        self.t = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "%s %.2fs" % (self.n, time.time() - self.t)


class CD:
    def __init__(self, dirname):
        self.dirname = dirname

    def __enter__(self):
        self.cwd = os.getcwd()
        print "enter", self.dirname
        os.chdir(self.dirname)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "return to", self.cwd
        os.chdir(self.cwd)


def fea_length_extend(*args):
    ct = int(args[-1])
    ans = args[:-1]
    new_ans = []
    for i in range(len(ans)):
        item = np.zeros(ct)
        item[:len(ans[i])] = np.asarray(ans[i])
        new_ans += [item]
    if len(new_ans) == 1:
        return new_ans[0]
    return new_ans


def getInterval(interval):
    lt = interval.split(",")
    return [map(int, _.split("-")) for _ in lt]


def dsInInterval(ds, interval):
    for (bg, ed) in interval:
        if bg <= ds < ed:
            return True
    return False


FT_FILE = "raw/st.ft"
AUX_FILE = "raw/st.aux"


def init_log(save_path, name):
    log_path = save_path + '%s.log' % name
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)


def getArgs(desc=""):
    parser = ArgumentParser(description=desc)
    parser.add_argument("-t", dest="tgt",
                        help="tgt")
    parser.add_argument("-ds", dest="ds",
                        help="day")
    parser.add_argument("-a", dest="a", default="tmp",
                        help="ans")
    parser.add_argument("-g", dest="g", default="",
                        help="gpu id")
    parser.add_argument("-l", dest="load", action="store_true", default=False,
                        help="load model")
    parser.add_argument("-d", dest="d", action="store_true", default=False,
                        help="direct, no filter")
    parser.add_argument("-v", dest="v", action="store_true", default=False,
                        help="verbose")
    parser.add_argument("-c", dest="c", type=int, default=50,
                        help="ct")
    # for gain
    parser.add_argument("-n", dest="n", action="store_true", default=False,
                        help="new stock")
    parser.add_argument("-hi", dest="h", action="store_true", default=False,
                        help="high line ok")
    parser.add_argument("-st", dest="st", action="store_true", default=False,
                        help="2016 st")
    # for merge cc
    parser.add_argument("-u", dest="u", action="store_true", default=False,
                        help="update to hdfs")
    parser.add_argument("-m", dest="m", action="store_true", default=False,
                        help="merge cc")

    # for csearch
    parser.add_argument("-q", dest="q", action="store_true", default=False,
                        help="quick")

    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.g
    return args


def getUsedModel(tgt, checkExist=True):
    fins = []
    for value in tgt.split("+"):
        key, subs = value.split(",")
        for n in subs:
            fins += [key + "0" + n]
    if checkExist:
        fins = filter(lambda x: os.path.exists("model/" + x), fins)
    return fins


def readFile(filename, skipHead=True):
    fin = open(filename)
    if skipHead:
        next(fin)
    for l in fin:
        l = l.strip()
        if not l:
            continue
        yield l


if __name__ == '__main__':
    def a():
        return fea_length_extend(np.ones(4), np.ones(3), 5)


    s = a()
    print s
