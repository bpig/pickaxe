import pymysql
import os
import sys
import pandas as pd
import time
import datetime
from tqdm import tqdm
import numpy as np
from collections import defaultdict
from StringIO import StringIO
import collections

pd.options.mode.chained_assignment = None

BASIC_DATA = "basic_data/"
METRIC_DATA = "metric_data/"
NO_HALT_METRIC_DATA = "no_halt_metric_data/"
MARKET_DATA = "market_data/"
MONEY_DATA = "money_data/"

PROC_DATA = "proc_data/"
FLAT_DATA = "flat_data"
FEA_DATA = "fea_data/"
MVN_DATA = "mvn_data/"
TRAIN_DATA = "train_data/"

COL = {
    "S_INFO_WINDCODE": "st",
    "TRADE_DT": "dt",
    "S_DQ_ADJOPEN": "s",
    "S_DQ_ADJHIGH": "h",
    "S_DQ_ADJLOW": "l",
    "S_DQ_ADJCLOSE": "e",
    "S_DQ_VOLUME": "v",
    "S_DQ_AMOUNT": "m",
    "S_DQ_TURN": "t",
    "S_DQ_FREETURNOVER": "ft",
}


class TimeLog:
    def __init__(self, name=""):
        self.n = name

    def __enter__(self):
        self.t = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "%s %.2fs" % (self.n, time.time() - self.t)


def need_dir(dirname):
    if not os.path.exists(dirname):
        print "mkdir,", dirname
        os.mkdir(dirname)

    def wrap(fun):
        def _inter(*args):
            fun(*args)

        return _inter

    return wrap


def cur_dir():
    return os.path.dirname(os.path.realpath(__file__))


def get_total_st():
    return sorted(os.listdir(FEA_DATA))


def conn_sql():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='jxb',
        passwd='jxb',
        db='daily_data')
    return conn


def get_st_list(conn):
    with TimeLog('getting codes'):
        cur = conn.cursor()
        sql = "select distinct S_INFO_WINDCODE from ashareeodprices"
        cur.execute(sql)
        codes = cur.fetchall()
    return codes


def strtodatetime(datestr, format="%Y%m%d"):
    return datetime.datetime.strptime(datestr, format)


def datetostr(date):
    return date.strftime('%Y%m%d')


def datediff(beginDate, endDate, format="%Y%m%d"):
    bd = strtodatetime(beginDate, format)
    ed = strtodatetime(endDate, format)
    delta = ed - bd
    return delta.days
