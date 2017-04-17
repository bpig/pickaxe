import pymysql
import os
import sys
import pandas as pd
import time
import datetime
from tqdm import tqdm

pd.options.mode.chained_assignment = None


class TimeLog:
    def __init__(self, name=""):
        self.n = name

    def __enter__(self):
        self.t = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "%s %.2fs" % (self.n, time.time() - self.t)


def curDir():
    return os.path.dirname(os.path.realpath(__file__))


def connectSQL():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='jxb',
        passwd='jxb',
        db='daily_data')
    return conn
