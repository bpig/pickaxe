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
    # code, dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares, status, in, out, target
    return kv

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

# def refineSell(sell, status):
#     idx = len(sell) - 1
#     while sell[idx] != -1.0 and idx >= 0:
#         idx -= 1
#     for i in range(idx, 0, -1):
#         if sell[i - 1] == -1.0:
#             sell[i - 1] = sell[i]
#     sell = map(lambda (x, y): y if x != 1 else -1.0, zip(status, sell))
#     return sell

def extend(v):
    status = map(getStatus, zip(v[1], v[9]))
    buy = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[5]))
    sell = map(lambda (x, y): float(y) if x != 1 else -1.0, zip(status, v[8]))
    buy = buy[1:] + [-1.0]
    sell = sell[2:] + [-1.0, -1.0]
    tgt = map(lambda (x, y): -1.0 if x < 0 or y < 0 else y / x, zip(buy, sell))
    v += [status, buy, sell, tgt]
    for i in range(-4, 0):
        v[i] = map(str, v[i])

def dump(kv, filename):
    fout = open(filename, "w")
    for k, v in kv.items():
        v = sorted(v, key=lambda x: x[0], reverse=True)
        v = zip(*v)
        extend(v)
        v = map(lambda x: "_".join(x), v)
        fout.write(k + "," + ",".join(v) + "\n")

def process(fin, fout):
    kv = getKv(fin)
    dump(kv, fout)

if __name__ == "__main__":
    fin = sys.argv[1]
    fout = sys.argv[2]
    process(fin, fout)
