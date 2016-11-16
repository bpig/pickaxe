# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *

Aux = collections.namedtuple('Aux', ['ds', 'work_day'])
Ft = collections.namedtuple(
    'Ft',
    ['ds', 'rate', 'volumn', 'amount', 'pe', 's', 'high', 'low', 'e', 'turnover',
     'shares', 's_rate', 'h_rate', 'l_rate', 'e_rate',
     'status', 's_status', 'wav_status', 'e_status', 'tgt'])

Ft2 = collections.namedtuple(
    'Ft',
    ['ds', 'rate', 'volumn', 'amount', 'pe', 's', 'high', 'low', 'e', 'turnover',
     'shares', 's_rate', 'h_rate', 'l_rate', 'e_rate',
     'status', 's_status', 'wav_status', 'e_status', 'a_rate', 'v_rate', 'tgt'])


Cc = collections.namedtuple(
    'Cc',
    ['ds', 'rate', 'volumn', 'amount', 'pe', 's', 'high', 'low', 'e', 'turnover',
     'shares'])


# states,正常 0,停盘 1
# s-status,开盘正常 0,开盘涨停 1,开盘跌停 2
# wav-status,当天正常 0,当天有涨停 1,当天有跌停 2,当天有涨停又有跌停 3
# e-status,收盘正常 0,收盘涨停 1,收盘跌停 2

# dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares,
#  0,    1,      2,      3,  4, 5,    6,   7, 8,        9,     10,
# s-rate, h-rate, l-rate, e-rate, status, s-status, wav-status, e-status, target
#     11,     12,     13,     14,     15,       16,         17,       18,     19

Ans = collections.namedtuple("Ans", ['code', 'prob', 'tgt'])

def getLine(fin):
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        yield l

def getKv(fin):
    for l in getLine(fin):
        pos = l.find(",")
        yield l[:pos], l[pos + 1:]

def getFtKv(fin):
    for key, value in getKv(fin):
        items = value.split(",")
        items = map(lambda x: x.split("_"), items)
        yield key, items

def getFt(fin, dtype=Ft):
    kv = {}
    for k, v in getFtKv(fin):
        kv[k] = dtype(*v)
    return kv

def getFtEx(fin):
    keyfile = fin + ".key.ex.npy"
    valuefile = fin + ".value.ex.npy"
    keys = np.load(keyfile)
    values = np.load(valuefile)
    assert len(keys) == len(values), \
        "%d keys not equal %d values" % (len(keys), len(values))
    return dict(zip(keys, values))

def getAns(fin):
    def ansTrans(x):
        return Ans(*x.split("_"))
    
    for key, value in getKv(fin):
        yield key, map(ansTrans, value.split(","))

def formatAns(_):
    return "_".join(_)

if __name__ == '__main__':
    # aux = getFt("data/2010/2016.ft.aux", Aux)
    # keys = aux.keys()
    # key = keys[0]
    # print len(aux[key].ds), len(aux[key].work_day)
    
    # ft = getFt("data/2010/2016.ft")
    # print len(ft[key].ds), len(ft[key].target)
    
    for k, ans in getAns("ans/2016_pc"):
        print k, [_.code for _ in ans]

# key           600227.SH
# values
# 0  dt         20160309_20160308_20160307_20160306_20160305_20160304,
# 1  rate       3.0_3.0_3.0_-9.9_-9.9_3.0,
# 2  volumn     3000_3000_3000_3000_3000_3000,
# 3  amount     3000_3000_3000_3000_3000_3000,
# 4  pe         10.0_10.0_10.0_10.0_10.0_10.0,
# 5  start      10.1_10.1_8.3_8.19_9.1_10.1,
# 6  high       10.3_10.3_8.3_8.19_9.1_10.1,
# 7  low        10.0_10.0_8.3_8.19_9.1_10.1,
# 8  end        10.2_10.2_8.3_8.19_9.1_10.1,
# 9  turnover   2.0_2.0_4.0_3.0_3.0_2.0,
# 10 shares     3000_3000_3000_3000_3000_3000,
# 11 s-rate     1.01_1.01_0.83_0.819_0.91_1.01,
# 12 h-rate     1.03_1.03_0.83_0.819_0.91_1.01,
# 13 l-rate     1.0_1.0_0.83_0.819_0.91_1.01,
# 14 e-rate     1.02_1.02_0.83_0.819_0.91_1.01,
# 15 status     0_0_0_0_0_0,
# 16 s-status   0_0_2_2_0_0,
# 17 wav-status 0_0_2_2_0_0,
# 18 e-status   0_0_2_2_0_0,
# 19 target     -1.0_-1.0_1.0099009901_1.22891566265_1.01343101343_0.9


# gb:
# amount, shares * e, status-0, status-1, s-status-0, s-status-1, s-status-2,
#  0            1        2         3         4            5            6
# wav-status-0, wav-status-1, wav-status-2, wav-status-3, e-status-0, e-status-1, e-status-2,
#   7                 8             9          10           11          12          13
# amount / (shares * e), rate
#       14                 15
