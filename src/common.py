# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

import sys
import os
import numpy as np
import math
import csv
try:
    import pandas as pd
    import yaml
except:
    pass
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
# from scipy import stats

class TimeLog:
    def __enter__(self, name=""):
        self.t = time.time()
        self.n = name

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "%s %.2fs" % (self.n, time.time() - self.t)
