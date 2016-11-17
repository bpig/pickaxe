#!/bin/env python

from common import *
from fea_kernel import *
from fea_core import *
from data_loader import Cc

def getline(filename):
    for c, l in enumerate(open(filename)):
        l = l.strip()
        if "code" in l or not l:
            continue
        yield l

def getKv(filename, kv, uniq):
    for l in getline(filename):
        pos = l.find(",")
        key = l[:pos]
        
        value = l[pos + 1:].replace("NULL", "0.0")
        value = value.split(",")
        ds = value[0]
        # if ds < "20160000":
        #     continue
        kid = key + "_" + value[0]
        if kid in uniq:
            continue
        uniq.add(kid)
        
        kv[key].append(value)
    # code, dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares
    #  -1    0    1      2       3     4  5    6    7   8      9        10
    
    # dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares,
    # s-rate, h-rate, l-rate, e-rate, status, s-status, wav-status, e-status, target
    return kv, uniq

def getStatus(rate):
    if rate <= 0.901:
        return 2
    elif rate >= 1.099:
        return 1
    return 0

def getWavStatus(h_rate, l_rate):
    if h_rate >= 1.099 and l_rate <= 0.901:
        return 3
    elif l_rate <= 0.901:
        return 2
    elif h_rate >= 1.099:
        return 1
    return 0

def extend(key, v):
    for i in [2, 3, 4, 5, 6, 7, 8, 9]:
        v[i] = map(float, v[i])
    a_rate = map(lambda x, y: 0 if x == 0 else y / x, v[3][1:], v[3][:-1]) + [0]
    v_rate = map(lambda x, y: 0 if x == 0 else y / x, v[2][1:], v[2][:-1]) + [0]
    s_rate = map(lambda x, y: y / x, v[4], v[5])
    h_rate = map(lambda x, y: y / x, v[4], v[6])
    l_rate = map(lambda x, y: y / x, v[4], v[7])
    e_rate = map(lambda x, y: y / x, v[4], v[8])
    status = map(lambda turnover: 1 if turnover == 0.0 else 0, v[9])
    s_status = map(getStatus, s_rate)
    wav_status = map(getWavStatus, h_rate, l_rate)
    e_status = map(getStatus, e_rate)
    
    ex = []
    ex += [np.asarray(v[0], dtype=np.float64)]
    
    cc = Cc(*v)
    for i in [3, 5, 7, 10, 15, 26, 60, 120]:
        emv_value, emv_ma = emv(cc, i)
        
        cr_value = cr(cc, i)
        br_value = br(cc, i)
        
        sma_value = sma(cc.e, i)
        ema_value = ema(cc.e, sma_value, 3)
        sma_value = fea_length_extend(sma_value, len(cc.ds))
        ema_value = fea_length_extend(ema_value, len(cc.ds))
        
        boll_rate, boll_std = boll(cc, i)
        
        rsi_value = rsi(cc, i)
        bias_value = bias(cc, i)
        cci_value = cci(cc, i)
        
        osc_value = osc(cc, i)
        psy_value = psy(cc, i)
        wms_value = wms(cc, i)
        obv_value = obv(cc, i)
        ex += [emv_value, emv_ma, cr_value, br_value, sma_value, ema_value,
               boll_rate, boll_std,
               rsi_value, bias_value, cci_value, osc_value, psy_value, wms_value,
               obv_value]
    
    for (a, b, c) in [(4, 2, 2), (9, 3, 3), (16, 4, 4), (25, 5, 5), (49, 7, 7)]:
        k, d, j = kdj(cc, a, b, c)
        ex += [k, d, j]
    
    for (l, s, m) in [(5, 3, 2), (10, 5, 3), (15, 7, 5), (26, 12, 9), (52, 26, 13)]:
        diff, diff_ma, diff_ema = macd(cc, l, s, m)
        ex += [diff, diff_ma, diff_ema]
    
    # ex += [cdp(cc)]
    
    for (a, b) in [(4, 2), (8, 4), (12, 6), (20, 10), (26, 13), (52, 26)]:
        mtm_value, mtma = mtm(cc, a, b)
        ex += [mtm_value, mtma]
    
    for a in [10, 15, 26, 52]:
        vr_value = vr(cc, a)
        ex += [vr_value]
    
    work_day = range(len(e_rate), 0, -1)
    
    for i in range(len(status)):
        if status[i] == 0:
            continue
        if s_status[i] != 0 or e_status[i] != 0 or wav_status[i] != 0:
            print "strange %s_%s %d %d %d %d" % \
                  (key, v[0][i], status[i], s_status[i], wav_status[i], e_status[i])
    
    buy = map(lambda x, y: float(y) if x != 1 else -1.0, status, v[5])
    sell = map(lambda x, y: float(y) if x != 1 else -1.0, status, v[8])
    buy = [-1.0] + buy[:-1]
    sell = [-1.0, -1.0] + sell[:-2]
    tgt = map(lambda x, y: -1.0 if x < 0 or y < 0 else y / x, buy, sell)
    v += [s_rate, h_rate, l_rate, e_rate, status, s_status, wav_status, e_status,
          a_rate, v_rate, tgt]
    v = map(lambda x: map(str, x), v)
    work_day = map(str, work_day)
    return v, [v[0], work_day], ex

def dump(kv, filename):
    fout = open(filename, "w")
    fout1 = open(filename + ".aux", "w")
    ex_keys = []
    ex_values = []
    # fdebug = open(filename + ".debug", "w")
    for c, (k, v) in enumerate(kv.items()):
        v = sorted(v, key=lambda x: x[0], reverse=True)
        v = zip(*v)
        v, aux, ex = extend(k, v)
        
        # normal output
        v = map(lambda x: "_".join(x), v)
        fout.write(k + "," + ",".join(v) + "\n")
        
        aux = map(lambda x: "_".join(x), aux)
        fout1.write(k + "," + ",".join(aux) + "\n")
        
        ex_values += [ex]
        ex_keys += [k]
        if c % 50 == 0:
            print time.ctime(), c
    
    np.save(filename + ".value.ex", np.asarray(ex_values))
    np.save(filename + ".key.ex", np.asarray(ex_keys))

def mergeDailyCsv(kv, uniq):
    dailyCsv = "data/daily"
    with CD(dailyCsv):
        for d in os.listdir("."):
            if len(d) > 12 or not d.endswith(".csv"):
                continue
            getKv(d, kv, uniq)
            print d, len(kv), len(uniq)

def process(fin, fout, merge=False):
    kv = defaultdict(list)
    uniq = set()
    getKv(fin, kv, uniq)
    print len(kv), len(uniq)
    if merge:
        mergeDailyCsv(kv, uniq)
    dump(kv, fout)

if __name__ == "__main__":
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    
    fin = "data/" + cfg["raw"]
    fout = "data/" + cfg["data"]
    process(fin, fout, merge=False)
