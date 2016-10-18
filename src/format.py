#!/bin/env python

from common import *

def getline(filename):
    for c, l in enumerate(open(filename)):
        l = l.strip()
        if "code" in l or not l:
            continue
        yield l

def getKv(filename):
    kv = defaultdict(list)
    for l in getline(filename):
        pos = l.find(",")
        key = l[:pos]
        value = l[pos + 1:].split(",")
        if value[9] == 'NULL':
            value[9] = "0.0"
        kv[key].append(value)
    # code, dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares
    #  -1    0    1      2       3     4  5    6    7   8      9        10
    
    # dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares,
    # s-rate, h-rate, l-rate, e-rate, status, s-status, e-status, wav-status, target
    return kv

def getStatus2(args):
    pe, s, e = map(float, args)
    st = [0, 0]
    if s / pe >= 1.099:
        st[0] = 1
    if e / pe <= 0.901:
        st[1] = 1
    return st

def getSstatus(s_rate):
    return 1 if s_rate >= 1.099 else 0

def getEstatus(e_rate):
    return 1 if e_rate <= 0.901 else 0

def getWavStatus((h_rate, l_rate)):
    if h_rate >= 1.099 and l_rate <= 0.901:
        return 3
    elif l_rate <= 0.901:
        return 2
    elif h_rate >= 1.099:
        return 1
    return 0

def getStatus(turnover):
    turnover = float(turnover)
    return 1 if turnover == 0.0 else 0

def extend(key, v):
    for i in [4, 5, 6, 7, 8]:
        v[i] = map(float, v[i])
    s_rate = map(lambda (x, y): y / x, zip(v[5], v[4]))
    h_rate = map(lambda (x, y): y / x, zip(v[6], v[4]))
    l_rate = map(lambda (x, y): y / x, zip(v[7], v[4]))
    e_rate = map(lambda (x, y): y / x, zip(v[8], v[4]))
    status = map(getStatus, v[9])
    s_status = map(getSstatus, s_rate)
    e_status = map(getSstatus, e_rate)
    wav_status = map(getWavStatus, zip(h_rate, l_rate))
    
    for i in range(len(status)):
        if status[i] == 0:
            continue
        if s_status[i] != 0 or e_status[i] != 0 or wav_status[i] != 0:
            print "strange %s_%s %d %d %d %d" % (key, v[0][i], status[i], s_status[i], e_status[i], wav_status[i])
    
    buy = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[5]))
    sell = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[8]))
    buy = [-1.0] + buy[:-1]
    sell = [-1.0, -1.0] + sell[:-2]
    tgt = map(lambda (x, y): -1.0 if x < 0 or y < 0 else y / x, zip(buy, sell))
    v += [s_rate, h_rate, l_rate, e_rate, status, s_status, e_status, wav_status, tgt]
    v = map(lambda x: map(str, x), v)
    return v

def dump(kv, filename):
    fout = open(filename, "w")
    fdebug = open(filename + ".debug", "w")
    
    for k, v in kv.items():
        v = sorted(v, key=lambda x: x[0], reverse=True)
        v = zip(*v)
        v = extend(k, v)
        
        # for debug
        d = zip(*v)
        for l in d:
            key = k + "_" + l[0]
            value = ",".join(l[1:])
            fdebug.write(key + "," + value + "\n")
        
        # normal output
        v = map(lambda x: "_".join(x), v)
        fout.write(k + "," + ",".join(v) + "\n")

def process(fin, fout):
    kv = getKv(fin)
    dump(kv, fout)

if __name__ == "__main__":
    fin = sys.argv[1]
    fout = sys.argv[2]
    process(fin, fout)
