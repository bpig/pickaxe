# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

import sys
import os
import numpy as np
import math
import csv
import datetime
import random
import time
import sys
import logging
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

try:
    import pandas as pd
    import yaml
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

if __name__ == '__main__':
    def a():
        return fea_length_extend(np.ones(4), np.ones(3), 5)
    
    s = a()
    print s
