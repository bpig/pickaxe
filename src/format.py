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
        # if value[0] < "20151220":
        #     continue
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

def getStatus((rate, turnover)):
    rate = float(rate)
    if rate >= 9.9:
        return 2
    if rate <= -9.9:
        return 3
    if turnover == "NULL":
        return 1
    turnover = float(turnover)
    if turnover == 0.0:
        return 1
    return 0

def extend(v):
    status = map(getStatus, zip(v[1], v[9]))
    status2 = map(getStatus2, zip(v[4], v[5], v[8]))
    s10, e10 = zip(*status2)
    buy = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[5]))
    sell = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[8]))
    buy = [-1.0] + buy[:-1]
    sell = [-1.0, -1.0] + sell[:-2]
    tgt = map(lambda (x, y): -1.0 if x < 0 or y < 0 else y / x, zip(buy, sell))
    v += [status, s10, e10, tgt]
    for i in range(-4, 0):
        v[i] = map(str, v[i])

def dump(kv, filename):
    fout = open(filename, "w")
    fdebug = open(filename + ".debug", "w")
    
    for k, v in kv.items():
        v = sorted(v, key=lambda x: x[0], reverse=True)
        v = zip(*v)
        extend(v)
        
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
