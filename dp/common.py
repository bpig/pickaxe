import pymysql
import os
import sys
import pandas as pd
import time
import datetime
from tqdm import tqdm
import numpy as np

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


def strtodatetime(datestr, format="%Y%m%d"):
    return datetime.datetime.strptime(datestr, format)


def datetostr(date):
    return date.strftime('%Y%m%d')


def datediff(beginDate, endDate, format="%Y%m%d"):
    bd = strtodatetime(beginDate, format)
    ed = strtodatetime(endDate, format)
    delta = ed - bd
    return delta.days
