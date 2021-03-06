# -*- coding:utf-8 -*-

from common import *
import global_info

# 15
# states
# 正常 0
# 停盘 1

# 16
# s-status
# 开盘正常 0
# 开盘涨停 1
# 开盘跌停 2

# 17
# wav-status
# 当天正常 0
# 当天有涨停 1
# 当天有跌停 2
# 当天有涨停又有跌停 3

# 18
# e-status
# 收盘正常 0
# 收盘涨停 1
# 收盘跌停 2

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


# dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares,
#  0,    1,      2,      3,  4, 5,    6,   7, 8,        9,     10,
# s-rate, h-rate, l-rate, e-rate, status, s-status, wav-status, e-status, target
#     11,     12,     13,     14,     15,       16,         17,       18,     19

# gb:
# amount, shares * e, status-0, status-1, s-status-0, s-status-1, s-status-2,
#  0            1        2         3         4            5            6
# wav-status-0, wav-status-1, wav-status-2, wav-status-3, e-status-0, e-status-1, e-status-2,
#   7                 8             9          10           11          12          13
# amount / (shares * e), rate
#       14                 15

def getGb(fin):
    if not fin:
        return None
    gb = {}
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        pos = l.find(",")
        ds = l[:pos]
        values = l[pos + 1:].split(",")
        gb[ds] = values
    return gb

def getSt(fin):
    dates = set()
    ary = np.load(fin)
    kv = {}
    for k, v in ary:
        ary[k] = v
        dates.update(v[0])
    return kv, sorted(dates)

def dump(st, fout, ds, predict=False):
    ct = 0
    for items in st.items():
        if ds not in items[1][0]:
            continue
        content = genOne(items, ds, predict)
        if content:
            fout.write(content)
            ct += 1
    return ct

def daySpan(d1, d2):
    v1 = datetime.datetime(int(d1[:4]), int(d1[4:6]), int(d1[6:]))
    v2 = datetime.datetime(int(d2[:4]), int(d2[4:6]), int(d2[6:]))
    return (v2 - v1).days

def genBasic(vals):
    vals = np.array(vals)
    res = [sum(vals), np.mean(vals), np.std(vals), max(vals), min(vals)]
    # if len(vals) > 7:
    #     res += [stats.skewtest(vals)]
    # if len(vals) > 20:
    #     res += [stats.kurtosistest(vals)]
    return res

def genStatus(status):
    ct0 = Counter(map(int, status[0]))
    ct1 = Counter(map(int, status[1]))
    ct2 = Counter(map(int, status[2]))
    ct3 = Counter(map(int, status[3]))
    return [ct0[0], ct0[1], ct1[0], ct1[1], ct1[2], ct2[0], ct2[1], ct2[2], ct2[3], ct3[0], ct3[1], ct3[2]]

def oneHotStatus(status, sstatus, wavstatus, estatus):
    arr1 = [0] * 2
    arr1[int(status)] = 1
    arr2 = [0] * 3
    arr2[int(sstatus)] = 1
    arr3 = [0] * 4
    arr3[int(wavstatus)] = 1
    if int(wavstatus) == 3:
        arr3[2] = 1
        arr3[3] = 1
    arr4 = [0] * 3
    arr4[int(estatus)] = 1
    return arr1 + arr2 + arr3 + arr4

def genOne(kv, ds, predict=False):
    feas = []
    key, values = kv  # values is [[ds],[..],[..]]
    
    index = values[0].index(ds)
    
    if not predict:
        if index <= 1:
            return ""
        # stock is stoped
        if values[15][index - 1] == 1 or values[15][index - 2] == 1:
            return ""
    else:
        if index != 0:
            print "index %s of %s must 0" % (ds, key)
            return ""
    
    windows = [2, 3, 5, 7, 15]  # , 30, 60]
    # windows = [2, 3, 5, 7, 10, 15, 20]
    # windows = [2, 3, 5, 7, 10]
    max_win = windows[-1]
    values = values[:, index:index + max_win]
    # values = map(lambda x: x[index:index + max_win], values)
    
    if len(values[0]) != max_win:
        # print "%s_%s, %d" % (key, ds, len(values[0]))
        return ""
    
    # today day fea
    for d in range(max_win):
        base_elem_idx = [1, 2, 3, 9, 10, 11, 12, 13, 14]
        feas += [values[base_elem_idx][d]]
        # feas += [values[_][d] for _ in [1, 2, 3, 9, 10, 11, 12, 13, 14]]
        feas += oneHotStatus(values[15][d], values[16][d], values[17][d], values[18][d])
    
    # win fea
    for window in windows:
        fea = []
        items = map(lambda x: x[:window], values)
        span = daySpan(items[0][-1], items[0][0])
        gain = items[8][0] / items[5][-1]
        for i in [1, 2, 3, 9, 10, 11, 12, 13, 14]:
            fea += genBasic(items[i])
        fea += genStatus(items[15:19])
        fea += [span, gain]
        feas += fea
    
    if not predict:
        tgt = values[-1][0]
        assert tgt > 0, "%s_%s %f" % (key, ds, tgt)
        feas += [tgt]
    # values = map(str, feas)
    return key + "_" + ds, feas

def process(fin, fout, ds=None):
    np.seterr(all='raise')
    st, dates = getSt(fin)
    if not ds:
        ds = dates[-1]
        print "process ds %s" % ds
    elif ds not in dates:
        print "%s not work day" % ds
        return
    fout = open(fout, "w")
    ct = dump(st, fout, ds, True)
    print time.ctime(), ds, ct

def genAll(fin, fout, filter_func):
    st, dates = getSt(fin)
    fout = open(fout, "w")
    dates = filter(filter_func, dates)
    total = len(dates)
    for c, ds in enumerate(dates):
        ct = dump(st, fout, ds)
        print time.ctime(), ds, c, "/", total, ct

if __name__ == "__main__":
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    fin = "macro/" + cfg["macro"]
    
    if "predict" in cfg:
        fout = "macro/" + cfg["predict"]
        process(fin, fout)
        sys.exit(0)
    
    fout1 = "macro/" + cfg["train"]
    fout2 = "macro/" + cfg["test"]
    
    if sys.argv[2] == "test":
        filter_func = lambda x: x >= "20160000"
        genAll(fin, fout2, filter_func)
    else:
        filter_func = lambda x: x < "20160000" and x >= "20060000"
        genAll(fin, fout1, filter_func)
