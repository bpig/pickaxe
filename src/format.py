#!/bin/env python

from common import *

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
    return v, [v[0], work_day]

def dump(kv, filename):
    fout = open(filename, "w")
    fout1 = open(filename + ".aux", "w")
    # fdebug = open(filename + ".debug", "w")
    for c, (k, v) in enumerate(kv.items()):
        v = sorted(v, key=lambda x: x[0], reverse=True)
        v = zip(*v)
        v, aux = extend(k, v)
        
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

def mergeDailyCsv(kv, uniq):
    dailyCsv = "macro/daily"
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
    
    fin = "macro/" + cfg["raw"]
    fout = "macro/2010/2016.ft"
    process(fin, fout, model, merge=True)
