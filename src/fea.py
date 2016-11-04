# -*- coding:utf-8 -*-
from itertools import chain

from common import *
from data_loader import getFt, Aux

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

def dump(st, fout, ds, predict=False):
    ct = 0
    for items in st.items():
        if ds not in items.ds[0]:
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
    key, info = kv
    
    idx = info.ds.index(ds)
    
    if not predict:
        if idx <= 1:
            return ""
        # stock is stoped
        if info.status[idx - 1] == 1 or info.status[idx - 2] == 1:
            return ""
    else:
        if idx != 0:
            print "index %s of %s must 0" % (ds, key)
            return ""
    
    windows = [2, 3, 5, 7, 15]  # , 30, 60]
    # windows = [2, 3, 5, 7, 10, 15, 20]  # , 30, 60]
    # windows = [2, 3, 5, 7, 10]  # , 30, 60]
    max_win = windows[-1]
    info = map(lambda x: x[idx:idx + max_win], info)
    
    if len(info.ds) != max_win:
        # print "%s_%s, %d" % (key, ds, len(values[0]))
        return ""
    
    # today day fea
    for d in range(max_win):
        feas += [info[_][d] for _ in [1, 2, 3, 9, 10, 11, 12, 13, 14]]
        feas += oneHotStatus(info.status[d], info.s_status[d], info.wav_status[d], info.e_status[d])
    
    # win fea
    for window in windows:
        fea = []
        items = map(lambda x: x[:window], info)
        span = daySpan(items.ds[-1], items.ds[0])
        gain = items.e[0] / items.s[-1]
        for i in [1, 2, 3, 9, 10, 11, 12, 13, 14]:
            fea += genBasic(items[i])
        fea += genStatus(items[15:19])
        fea += [span, gain]
        feas += fea
    
    if not predict:
        tgt = info.tgt[0]
        assert tgt > 0, "%s_%s %f" % (key, ds, tgt)
        feas += [tgt]
    info = map(str, feas)
    return key + "_" + ds + ":" + ",".join(info) + "\n"

def process(fin, fout, ds=None):
    np.seterr(all='raise')
    st = getFt(fin)
    dates = set(chain(*map(lambda x: x.ds, st.values())))
    dates = sorted(dates)
    
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
    st = getFt(fin)
    dates = set(chain(*map(lambda x: x.ds, st.values())))
    dates = sorted(dates)
    
    fout = open(fout, "w")
    dates = filter(filter_func, dates)
    total = len(dates)
    for c, ds in enumerate(dates):
        ct = dump(st, fout, ds)
        print time.ctime(), ds, c, "/", total, ct

if __name__ == "__main__":
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    fin = "data/" + cfg["data"]
    
    if "predict" in cfg:
        fout = "data/" + cfg["predict"]
        process(fin, fout)
        sys.exit(0)
    
    fout1 = "data/" + cfg["train"]
    fout2 = "data/" + cfg["test"]
    
    if sys.argv[2] == "test":
        filter_func = lambda x: x >= "20160000"
        genAll(fin, fout2, filter_func)
    else:
        filter_func = lambda x: x < "20160000" and x >= "20060000"
        genAll(fin, fout1, filter_func)
