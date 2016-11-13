# -*- coding:utf-8 -*-
from common import *
from data_loader import getFt, Ft
from fea_kernel import *
from fea_core import *

def dump(st, fout, ds, predict=False):
    ct = 0
    for key, info in st.items():
        if ds not in info.ds:
            continue
        content = genOne(key, info, ds, predict)
        if content:
            fout.write(content)
            ct += 1
    return ct

def daySpan(d1, d2):
    v1 = datetime.datetime(int(d1[:4]), int(d1[4:6]), int(d1[6:]))
    v2 = datetime.datetime(int(d2[:4]), int(d2[4:6]), int(d2[6:]))
    return (v2 - v1).days

def genBasic(vals):
    vals = np.asarray(vals, dtype=np.float32)
    res = [np.mean(vals), np.std(vals), max(vals), min(vals)]
    return res

def genStatus(status):
    ct0 = Counter(status[0])
    ct1 = Counter(status[1])
    ct2 = Counter(status[2])
    ct3 = Counter(status[3])
    return [ct0['0'], ct0['1'],
            ct1['0'], ct1['1'], ct1['2'],
            ct2['0'], ct2['1'], ct2['2'], ct2['3'],
            ct3['0'], ct3['1'], ct3['2']]

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

def genOne(key, info, ds, predict=False):
    idx = info.ds.index(ds)
    if not predict:
        if idx <= 1:
            return ""
        # stock is stoped
        if info.status[idx - 1] == 1 or info.status[idx - 2] == 1:
            return ""
    elif idx != 0:
        print "index %s of %s must 0" % (ds, key)
        return ""
    
    windows = [2, 3, 5, 7, 10, 15, 20, 30, 60, 90, 120]
    # windows = [2, 3, 5, 7, 15]  # , 30, 60]
    # windows = [2, 3, 5, 7, 10, 15, 20]  # , 30, 60]
    # windows = [2, 3, 5, 7, 10]  # , 30, 60]
    max_win = windows[-1]
    info = Ft(*map(lambda x: x[idx:idx + max_win], info))
    
    if len(info.ds) != max_win:
        # print "%s_%s, %d" % (key, ds, len(values[0]))
        return ""
    
    feas = genOneFe(info, windows)
    if not predict:
        tgt = info.tgt[0]
        assert tgt > 0, "%s_%s %f" % (key, ds, tgt)
        feas += [tgt]
    info = map(str, feas)
    return key + "_" + ds + ":" + ",".join(info) + "\n"

def genOneFe(info, wins):
    feas = []
    maxWin = 15  # wins[-1]
    # today day fea
    for d in range(maxWin):
        feas += [info[_][d] for _ in [1, 2, 3, 9, 10, 11, 12, 13, 14]]
        feas += oneHotStatus(info.status[d], info.s_status[d],
                             info.wav_status[d], info.e_status[d])
        
    
    # win fea
    for win in wins:
        fea = []
        items = Ft(*map(lambda x: x[:win], info))
        for i in [1, 2, 3, 9, 10, 11, 12, 13, 14]:
            fea += genBasic(items[i])
        fea += genStatus(items[15:19])
        span = daySpan(items.ds[-1], items.ds[0])
        gain = float(items.e[0]) / float(items.s[-1])
        fea += [span, gain]
        feas += fea
    return feas

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
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    ds = sys.argv[2]
    fin = "data/" + cfg["data"]
    fout = "data/fe/%s/daily/%s.fe" % (model, ds)
    with TimeLog():
        process(fin, fout, ds)
