#!/bin/env python

from common import *

def getKv(filename, kv, uniq, stripHeader=False):
    reader = csv.reader(open(filename))
    if stripHeader:
        next(reader)
    
    for row in reader:
        key = row[0]
        value = map(lambda x: "0.0" if x == "NULL" else x, row[1:])
        
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

# def getKv(filename, kv, uniq, stripHeader=False):
#     if not stripHeader:
#         df = pd.read_csv(filename, header=None)
#     else:
#         df = pd.read_csv(filename)

#     df = df.fillna(0.0)
#     for idx, row in df.iterrows():
#         key = row[0]
#         value = list(row[1:])

#         kid = key + "_" + str(value[0])
#         if kid in uniq:
#             continue
#         uniq.add(kid)

#         kv[key].append(value)
#     # code, dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares
#     #  -1    0    1      2       3     4  5    6    7   8      9        10

#     # dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares,
#     # s-rate, h-rate, l-rate, e-rate, status, s-status, wav-status, e-status, target
#     return kv, uniq

@np.vectorize
def getStatus(rate):
    if rate <= 0.901:
        return 2
    elif rate >= 1.099:
        return 1
    return 0

@np.vectorize
def getWavStatus(h_rate, l_rate):
    if h_rate >= 1.099 and l_rate <= 0.901:
        return 3
    elif l_rate <= 0.901:
        return 2
    elif h_rate >= 1.099:
        return 1
    return 0

def extend(key, v):
    for i in [4, 5, 6, 7, 8, 9]:
        v[i] = np.asarray(v[i], dtype=np.float)
    s_rate = v[5] / v[4]
    h_rate = v[6] / v[4]
    l_rate = v[7] / v[4]
    e_rate = v[8] / v[4]

    if e_rate[-1] > 1.20:
        # print key, v[0][-1], e_rate[-1], len(e_rate)
        work_day = np.arange(len(e_rate), 0, -1)
    else:
        work_day = np.arange(len(e_rate) + 120, 120, -1)
    
    status = (v[9] == 0.0).astype(int)
    
    s_status = getStatus(s_rate)
    wav_status = getWavStatus(h_rate, l_rate)
    e_status = getStatus(e_rate)
    
    for i in range(len(status)):
        if status[i] == 0:
            continue
        if s_status[i] != 0 or e_status[i] != 0 or wav_status[i] != 0:
            print "strange %s_%s %d %d %d %d" % (key, v[0][i], status[i], s_status[i], wav_status[i], e_status[i])
    
    buy = v[5].copy()
    buy[status == 1] = -1.0
    sell = v[8].copy()
    sell[status == 1] = -1.0
    
    buy = np.concatenate(([-1.0], buy[:-1]))
    if len(buy) == 1:
        sell = np.concatenate(([-1.0], sell[:-2]))
    else:
        sell = np.concatenate(([-1.0, -1.0], sell[:-2]))
    
    mark = np.logical_or(buy < 0, sell < 0)
    mark = np.logical_not(mark)
    tgt = np.empty(len(buy), dtype=float)
    tgt.fill(-1.0)
    
    assert len(mark) == len(buy), \
        "%s, %d, %d, %d" % (key, len(mark), len(buy), len(sell))
    assert len(mark) == len(sell)
    tgt[mark] = sell[mark] / buy[mark]
    
    v += [s_rate, h_rate, l_rate, e_rate, status, s_status, wav_status, e_status, tgt]
    
    return v, work_day

def dump(kv, filename):
    ct = len(kv)
    ary = np.empty(ct, dtype=np.object)
    for c, (k, v) in enumerate(kv.items()):
        v = sorted(v, key=lambda x: x[0], reverse=True)
        v = zip(*v)
        v, work_day = extend(k, v)
        v = np.asarray(v)
        ary[c] = [k, v, work_day]  # k:stock, v: list of list
    np.save(filename, ary)

def mergeSmallCsv(kv, uniq):
    smallCsvDir = "data/predict/cache"
    for d in os.listdir(smallCsvDir):
        if len(d) > 12 or not d.endswith(".csv"):
            continue
        getKv(smallCsvDir + "/" + d, kv, uniq)
        print d, len(kv), len(uniq)

def process(fin, fout, merge=False):
    kv = defaultdict(list)
    uniq = set()
    with TimeLog():
        getKv(fin, kv, uniq, True)
    print len(kv), len(uniq)
    if merge:
        mergeSmallCsv(kv, uniq)
    print "dump data"
    with TimeLog():
        dump(kv, fout)

if __name__ == "__main__":
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    fin = "data/" + cfg["raw"]
    fout = "data/" + cfg["data"]
    process(fin, fout, True)
