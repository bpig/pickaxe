# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/23"
from common import *
import wget
import time
import os
import sys


def yesterday(dt, days=-1):
    return dt + datetime.timedelta(days=days)

def download():
    now = datetime.datetime.now()
    print now.year, now.month, now.day
    while True:
        prev = yesterday(now)
        print prev.year, prev.month, prev.day
        ds = str(prev.year) + "-" + str(prev.month) + "-" + str(prev.day)
        downloadByDs(ds)
        if wc(ds):
            break
        else:
            now = prev
    return ds
            
def wc(ds):
    f = "price_" + ds + ".csv"
    if not os.path.isfile(f):
        return False
    lf = len(open(f).readlines())
    if lf <= 10:
        os.remove(f)
        return False
    return True

def downloadByDs(ds):
    tmpl = "http://60.191.48.94:8000/download/%s_%s.csv"
    print time.ctime()
    url = tmpl % ("derivativeindicator", ds)
    wget.download(url)
    url = tmpl % ("price", ds)
    wget.download(url)
    print time.ctime()


#price.S_INFO_WINDCODE, price.TRADE_DT, price.S_DQ_PCTCHANGE, price.S_DQ_VOLUME, price.S_DQ_AMOUNT, price.S_DQ_ADJPRECLOSE, price.S_DQ_ADJOPEN, price.S_DQ_ADJHIGH, price.S_DQ_ADJLOW, price.S_DQ_ADJCLOSE, big.S_DQ_FREETURNOVER, big.FREE_SHARES_TODAY
#                 code,             dt,                 rate,            volumn,            amount,                     pe,                  s,               high,               low,                   e,              turnover,                shares

# price
#0   "OBJECT_ID",
#1   "TRADE_DT",
#2   "S_INFO_WINDCODE",
#3   "CRNCY_CODE",
#4   "S_DQ_PRECLOSE",
#5   "S_DQ_OPEN",
#6   "S_DQ_HIGH",
#7   "S_DQ_LOW",
#8   "S_DQ_CLOSE",
#9   "S_DQ_CHANGE",
#10  "S_DQ_PCTCHANGE",
#11  "S_DQ_VOLUME",
#12  "S_DQ_AMOUNT",
#13  "S_DQ_ADJPRECLOSE",
#14  "S_DQ_ADJOPEN",
#15  "S_DQ_ADJHIGH",
#16  "S_DQ_ADJLOW",
#17  "S_DQ_ADJCLOSE",
#18  "S_DQ_ADJFACTOR",
#19  "S_DQ_AVGPRICE",
#20  "S_DQ_TRADESTATUS",
#21  "OPDATE",
#22  "OPMODE"

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


def process(ds):
    outfile = ds + ".csv"
    pricefile = "price_"+ ds + ".csv"
    bigfile = "derivativeindicator_" + ds + ".csv"
    fout = open(outfile, "w")
    indicator = {}
    price = {}
    indicator = transformOne(bigfile, "big", 39)
    price = transformOne(pricefile, "price", 23)
    for k, v in price.items():
        if k not in indicator.keys():
            continue
        indicatorValue = indicator[k]
        record = [k, v[1]] + v[10: 18] + [indicatorValue[18], indicatorValue[25]]
        outStr = ",".join(record) + "\n"
        fout.write(outStr)
            

def transformOne(filename, table, ct):
    keys = set()
    dict = {}
    for l in open(filename).read().replace('"', '').split("\n"):
        if not l:
            continue
        if "OBJECT" in l:
            ans = l
            continue
        items = l.split(",")
        items = map(lambda s: s.strip(), items)
        if items[0] in keys:
            print "dup", l
        keys.add(items[0])
        assert len(items) == ct, str(len(items)) + ":" + l
        for i in range(len(items)):
            if not items[i]:
                items[i] = "NULL"
        if table == "price":
            items[-3] = "NULL"
            dict[items[2]] = items
        else:
            dict[items[1]] = items
    return dict

if __name__ == "__main__":
    os.chdir("../data/predict")
    ds = download()
    print ds
    process(ds)