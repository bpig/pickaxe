#!/bin/env python

from common import *
from fea_kernel import *
from fea_core import *

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
        if ds < "20160000":
            continue
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

def getWavStatus((h_rate, l_rate)):
    if h_rate >= 1.099 and l_rate <= 0.901:
        return 3
    elif l_rate <= 0.901:
        return 2
    elif h_rate >= 1.099:
        return 1
    return 0

def extend(key, v):
    for i in [4, 5, 6, 7, 8, 9]:
        v[i] = map(float, v[i])
    s_rate = map(lambda (x, y): y / x, zip(v[4], v[5]))
    h_rate = map(lambda (x, y): y / x, zip(v[4], v[6]))
    l_rate = map(lambda (x, y): y / x, zip(v[4], v[7]))
    e_rate = map(lambda (x, y): y / x, zip(v[4], v[8]))
    status = map(lambda turnover: 1 if turnover == 0.0 else 0, v[9])
    s_status = map(getStatus, s_rate)
    wav_status = map(getWavStatus, zip(h_rate, l_rate))
    e_status = map(getStatus, e_rate)
    
    ex = []
    ex += [v[0]]
    
    emv_3 = emv(v, 3)
    emv_5 = emv(v, 5)
    emv_7 = emv(v, 7)
    emv_10 = emv(v, 10)
    emv_15 = emv(v, 15)
    emv_26 = emv(v, 26)
    ex += [emv_3, emv_5, emv_7, emv_10, emv_15, emv_26]
    
    cr_3 = cr(v, 3)
    cr_5 = cr(v, 5)
    cr_7 = cr(v, 7)
    cr_10 = cr(v, 10)
    cr_15 = cr(v, 15)
    cr_26 = cr(v, 26)
    ex += [cr_3, cr_5, cr_7, cr_10, cr_15, cr_26]
    
    br_3 = br(v, 3)
    br_5 = br(v, 5)
    br_7 = br(v, 7)
    br_10 = br(v, 10)
    br_15 = br(v, 15)
    br_26 = br(v, 26)
    ex += [br_3, br_5, br_7, br_10, br_15, br_26]
    
    _, _, j_2 = kdj(v, 4, 2, 2)
    _, _, j_3 = kdj(v, 9, 3, 3)
    _, _, j_4 = kdj(v, 16, 4, 4)
    _, _, j_5 = kdj(v, 25, 5, 5)
    ex += [j_2, j_3, j_4, j_5]
    
    sma_3 = sma(v.e, 3)
    sma_5 = sma(v.e, 5)
    sma_7 = sma(v.e, 7)
    sma_10 = sma(v.e, 10)
    sma_15 = sma(v.e, 15)
    sma_26 = sma(v.e, 26)
    # sma3, sma5, sma7, sma10, sma15, sma26 = map(sma, [v.e] * 6, [3, 5, 7, 10, 15, 26])
    ex += [sma_3, sma_5, sma_7, sma_10, sma_15, sma_26]
    
    ema_3 = ema(v.e, sma_3, 3)
    ema_5 = ema(v.e, sma_5, 5)
    ema_7 = ema(v.e, sma_5, 7)
    ema_10 = ema(v.e, sma_5, 10)
    ema_15 = ema(v.e, sma_5, 15)
    ema_26 = ema(v.e, sma_5, 26)
    ex += [ema_3, ema_5, ema_7, ema_10, ema_15, ema_26]
    
    macd_5 = macd(v, 5, 3, 2)
    macd_10 = macd(v, 10, 5, 3)
    macd_15 = macd(v, 15, 7, 5)
    macd_26 = macd(v, 26, 12, 9)
    ex += [macd_5, macd_10, macd_15, macd_26]
    
    _, _, _, boll_3 = boll(v, 3);
    _, _, _, boll_5 = boll(v, 5);
    _, _, _, boll_7 = boll(v, 7);
    _, _, _, boll_10 = boll(v, 10);
    _, _, _, boll_15 = boll(v, 15);
    _, _, _, boll_26 = boll(v, 26);
    ex += [boll_3, boll_5, boll_7, boll_10, boll_15, boll_26]
    
    rsi_3 = rsi(v, 3)
    rsi_5 = rsi(v, 5)
    rsi_7 = rsi(v, 7)
    rsi_10 = rsi(v, 10)
    rsi_15 = rsi(v, 15)
    rsi_26 = rsi(v, 26)
    ex += [rsi_3, rsi_5, rsi_7, rsi_10, rsi_15, rsi_26]
    
    bias_3 = bias(v, 3)
    bias_5 = bias(v, 5)
    bias_7 = bias(v, 7)
    bias_10 = bias(v, 10)
    bias_15 = bias(v, 15)
    bias_26 = bias(v, 26)
    ex += [bias_3, bias_5, bias_7, bias_10, bias_15, bias_26]
    
    cci_3 = cci(v, 3)
    cci_5 = cci(v, 5)
    cci_7 = cci(v, 7)
    cci_10 = cci(v, 10)
    cci_15 = cci(v, 15)
    cci_26 = cci(v, 26)
    ex += [cci_3, cci_5, cci_7, cci_10, cci_15, cci_26]
    
    ex += [cdp(v)]
    
    mtm_4, mtma_4 = mtm(v, 4, 2)
    mtm_8, mtma_8 = mtm(v, 8, 4)
    mtm_12, mtma_12 = mtm(v, 12, 6)
    mtm_20, mtma_20 = mtm(v, 20, 10)
    mtm_26, mtma_26 = mtm(v, 26, 13)
    ex += [mtm_4, mtma_4, mtm_8, mtma_8, mtm_12, mtma_12, mtm_20, mtma_20, mtm_26, mtma_26]
    
    osc_3 = osc(v, 3)
    osc_5 = osc(v, 5)
    osc_7 = osc(v, 7)
    osc_10 = osc(v, 10)
    osc_15 = osc(v, 15)
    osc_26 = osc(v, 26)
    ex += [osc_3, osc_5, osc_7, osc_10, osc_15, osc_26]
    
    psy_3 = psy(v, 3)
    psy_5 = psy(v, 5)
    psy_7 = psy(v, 7)
    psy_10 = psy(v, 10)
    psy_15 = psy(v, 15)
    psy_26 = psy(v, 26)
    ex += [psy_3, psy_5, psy_7, psy_10, psy_15, psy_26]
    
    vr_12 = vr(v, 12)
    vr_26 = vr(v, 26)
    ex += [vr_12, vr_26]
    
    wms_3 = wms(v, 3)
    wms_5 = wms(v, 5)
    wms_7 = wms(v, 7)
    wms_10 = wms(v, 10)
    wms_15 = wms(v, 15)
    wms_26 = wms(v, 26)
    ex += [wms_3, wms_5, wms_7, wms_10, wms_15, wms_26]
    
    obv_3 = obv(v, 3)
    obv_5 = obv(v, 5)
    obv_7 = obv(v, 7)
    obv_10 = obv(v, 10)
    obv_15 = obv(v, 15)
    obv_26 = obv(v, 26)
    ex += [obv_3, obv_5, obv_7, obv_10, obv_15, obv_26]
    
    work_day = range(len(e_rate), 0, -1)
    
    for i in range(len(status)):
        if status[i] == 0:
            continue
        if s_status[i] != 0 or e_status[i] != 0 or wav_status[i] != 0:
            print "strange %s_%s %d %d %d %d" % (key, v[0][i], status[i], s_status[i], wav_status[i], e_status[i])
    
    buy = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[5]))
    sell = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[8]))
    buy = [-1.0] + buy[:-1]
    sell = [-1.0, -1.0] + sell[:-2]
    tgt = map(lambda (x, y): -1.0 if x < 0 or y < 0 else y / x, zip(buy, sell))
    v += [s_rate, h_rate, l_rate, e_rate, status, s_status, wav_status, e_status, tgt]
    v = map(lambda x: map(str, x), v)
    work_day = map(str, work_day)
    return v, [v[0], work_day], ex

def dump(kv, filename):
    fout = open(filename, "w")
    fout1 = open(filename + ".aux", "w")
    fout2 = open(filename + ".ex", "w")
    # fdebug = open(filename + ".debug", "w")
    for c, (k, v) in enumerate(kv.items()):
        v = sorted(v, key=lambda x: x[0], reverse=True)
        v = zip(*v)
        v, aux, ex = extend(k, v)
        
        # for debug
        # d = zip(*v)
        # for l in d:
        #     key = k + "_" + l[0]
        #     value = ",".join(l[1:])
        #     fdebug.write(key + "," + value + "\n")
        
        # normal output
        v = map(lambda x: "_".join(x), v)
        fout.write(k + "," + ",".join(v) + "\n")
        
        aux = map(lambda x: "_".join(x), aux)
        fout1.write(k + "," + ",".join(aux) + "\n")
        
        ex = map(lambda x: "_".join(x), ex)
        fout2.write(k + ", " + ",".join(ex) + "\n")

def mergeDailyCsv(kv, uniq):
    dailyCsv = "data/daily"
    with CD(dailyCsv):
        for d in os.listdir("."):
            if len(d) > 12 or not d.endswith(".csv"):
                continue
            getKv(d, kv, uniq)
            print d, len(kv), len(uniq)

def process(fin, fout, model, merge=False):
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
    process(fin, fout, model, merge=True)
