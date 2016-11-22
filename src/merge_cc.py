#!/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/11/16"
from common import *
import wget
import os

def yesterday(dt, days=-1):
    return dt + datetime.timedelta(days=days)

def download(today):
    checkpoint = "no_data_checkpoint"
    try:
        noData = set([_.strip() for _ in open(checkpoint)])
    except:
        noData = set()
    fout = open(checkpoint, "a")
    
    now = datetime.datetime(int(today[:4]), int(today[4:6]), int(today[6:]))
    
    print now.year, now.month, now.day
    dates = []
    while len(dates) < 15:
        tmpl = "%04d-%02d-%02d"
        ds = tmpl % (now.year, now.month, now.day)
        if ds in noData:
            now = yesterday(now)
            continue
        print "valid", ds
        downloadByDs(ds)
        if valid(ds):
            dates += [ds]
        else:
            fout.write(ds + "\n")
        now = yesterday(now)
    return dates

def valid(ds):
    f = "cache/price_" + ds + ".csv"
    ff = "cache/derivativeindicator_" + ds + ".csv"
    if not os.path.isfile(f):
        return False
    lf = len(open(f).readlines())
    if lf <= 10:
        os.remove(f)
        os.remove(ff)
        return False
    return True

def downloadByDs(ds):
    tmpl = "http://61.130.4.98:8000/download/%s_%s.csv"
    f = "price_" + ds + ".csv"
    ff = "derivativeindicator_" + ds + ".csv"
    with CD("cache"):
        files = os.listdir(".")
        if ff not in files:
            url = tmpl % ("derivativeindicator", ds)
            print url
            wget.download(url)
        if f not in files:
            url = tmpl % ("price", ds)
            print url
            wget.download(url)

# price.S_INFO_WINDCODE, price.TRADE_DT, price.S_DQ_PCTCHANGE, price.S_DQ_VOLUME, price.S_DQ_AMOUNT, price.S_DQ_ADJPRECLOSE, price.S_DQ_ADJOPEN, price.S_DQ_ADJHIGH, price.S_DQ_ADJLOW, price.S_DQ_ADJCLOSE, big.S_DQ_FREETURNOVER, big.FREE_SHARES_TODAY
#                 code,             dt,                 rate,            volumn,            amount,                     pe,                  s,               high,               low,                   e,              turnover,                shares

# price
# 0   "OBJECT_ID",
# 1   "TRADE_DT",
# 2   "S_INFO_WINDCODE",
# 3   "CRNCY_CODE",
# 4   "S_DQ_PRECLOSE",
# 5   "S_DQ_OPEN",
# 6   "S_DQ_HIGH",
# 7   "S_DQ_LOW",
# 8   "S_DQ_CLOSE",
# 9   "S_DQ_CHANGE",
# 10  "S_DQ_PCTCHANGE",
# 11  "S_DQ_VOLUME",
# 12  "S_DQ_AMOUNT",
# 13  "S_DQ_ADJPRECLOSE",
# 14  "S_DQ_ADJOPEN",
# 15  "S_DQ_ADJHIGH",
# 16  "S_DQ_ADJLOW",
# 17  "S_DQ_ADJCLOSE",
# 18  "S_DQ_ADJFACTOR",
# 19  "S_DQ_AVGPRICE",
# 20  "S_DQ_TRADESTATUS",
# 21  "OPDATE",
# 22  "OPMODE"

# "OBJECT_ID","S_INFO_WINDCODE","TRADE_DT","CRNCY_CODE","S_VAL_MV","S_DQ_MV","S_PQ_HIGH_52W_",
#           0,                1,         2,           3,         4,        5,               6,
# "S_PQ_LOW_52W_","S_VAL_PE","S_VAL_PB_NEW","S_VAL_PE_TTM","S_VAL_PCF_OCF","S_VAL_PCF_OCFTTM",
#               7,         8,             9,            10,             11,                12
# "S_VAL_PCF_NCF","S_VAL_PCF_NCFTTM","S_VAL_PS","S_VAL_PS_TTM","S_DQ_TURN","S_DQ_FREETURNOVER",
#              13,                14,        15,            16,         17,                 18,
# "TOT_SHR_TODAY","FLOAT_A_SHR_TODAY","S_DQ_CLOSE_TODAY","S_PRICE_DIV_DPS","S_PQ_ADJHIGH_52W",
#               19,                20,                21,               22,                23,
# "S_PQ_ADJLOW_52W","FREE_SHARES_TODAY","NET_PROFIT_PARENT_COMP_TTM","NET_PROFIT_PARENT_COMP_LYR",
#                24,                 25
# "NET_ASSETS_TODAY","NET_CASH_FLOWS_OPER_ACT_TTM","NET_CASH_FLOWS_OPER_ACT_LYR","OPER_REV_TTM","OPER_REV_LYR","NET_INCR_CASH_CASH_EQU_TTM","NET_INCR_CASH_CASH_EQU_LYR","UP_DOWN_LIMIT_STATUS","LOWEST_HIGHEST_STATUS","OPDATE","OPMODE"


def genCsv(dates, csvname):
    dates = sorted(dates, reverse=True)
    fout = open(csvname, "w")
    for ds in dates:
        pricefile = "cache/price_" + ds + ".csv"
        bigfile = "cache/derivativeindicator_" + ds + ".csv"
        indicator = transformOne(bigfile, "big", 39)
        price = transformOne(pricefile, "price", 23)
        for k, v in price.items():
            if k not in indicator.keys():
                continue
            indicatorValue = indicator[k]
            record = [k, v[1]] + v[10: 18] + [indicatorValue[18], indicatorValue[25]]
            outStr = ",".join(record) + "\n"
            fout.write(outStr)
    return dates[0]

def transformOne(filename, table, ct):
    keys = set()
    kv = {}
    for l in open(filename).read().replace('"', '').split("\n"):
        if not l:
            continue
        if "OBJECT" in l:
            continue
        items = l.split(",")
        items = map(lambda s: s.strip(), items)
        if items[0] in keys:
            print "dup", l
            continue
        keys.add(items[0])
        assert len(items) == ct, str(len(items)) + ":" + l
        for i in range(len(items)):
            if not items[i]:
                items[i] = "NULL"
        if table == "price":
            items[-3] = "NULL"
            kv[items[2]] = items
        else:
            kv[items[1]] = items
    return kv

def mergeCc(cc, dailydt):
    fout = open("data/total.cc", "w")
    keys = set()
    for l in open(cc):
        l = l.strip()
        if not l:
            continue
        pos = l.find(",")
        pos = l.find(",", pos + 1)
        key = l[:pos]
        fout.write(l + "\n")
        keys.add(key)
    
    c = 0
    with CD(dailydt):
        for f in os.listdir("."):
            if not f.endswith("csv"):
                continue
            print "merge", f
            for l in open(f):
                l = l.strip()
                if not l:
                    continue
                pos = l.find(",")
                pos = l.find(",", pos + 1)
                key = l[:pos]
                if key in keys:
                    continue
                fout.write(l + "\n")
                keys.add(key)
                c += 1
    print "total merge", c

def getArgs():
    parser = ArgumentParser(description="Merge")
    parser.add_argument("-ds", dest="ds", default="",
                        help="today date")
    parser.add_argument("-u", dest="u", action="store_true", default=False,
                        help="update to hdfs")
    parser.add_argument("-m", dest="m", action="store_true", default=False,
                        help="merge cc")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    today = args.ds
    os.system("mkdir -p data/daily/cache")
    
    dailydt = "data/daily/"
    cc = "data/2010.cc"

    if today:
        with CD(dailydt):
            csv = "%s.csv" % today
            if not os.path.exists(csv):
                dates = download(today)
                print dates
                genCsv(dates, csv)
            else:
                print "%s in cache" % csv
    if args.m:
        mergeCc(cc, dailydt)

    if args.u:
        cmd = "hdfs dfs -rmr htk/2010.cc"
        os.system(cmd)
        cmd = "hdfs dfs -put data/total.cc htk/2010.cc"
        os.system(cmd)
        cmd = "hdfs dfs -ls htk"
        os.system(cmd)

    
