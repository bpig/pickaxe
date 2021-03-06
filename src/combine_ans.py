#!/bin/env python
# -*- coding:utf-8 -*-
from common import *

def transform(l):
    x = l.split("_")
    return x[0], float(x[1]), x[2]

def loadFile(fins):
    kv = defaultdict(list)
    for fin in fins:
        for l in open(fin):
            l = l.strip()
            if not l:
                continue
            pos = l.find(",")
            ds = l[:pos]
            items = l[pos + 1:].split(",")
            items = map(transform, items)
#            items = filter(lambda x: x[1] > 0.6, items)
            kv[ds] += [items]
    return kv

def combine(predictions, fout):
    fout = open(fout, "w")
    for k in sorted(predictions.keys()):
        v = predictions[k]
        kv = defaultdict(float)
        for items in v:
            for item in items:
                code = item[0]  # + "_" + item[2]
#                kv[code] = 1 - (1 - kv[code]) * (1 - item[1])
                kv[code] += item[1]
        cw = sorted(kv.items(), key=lambda x: x[1], reverse=True)
        cw = map(lambda x: x[0] + "_" + str(x[1]) + "_0.0", cw)
        fout.write(k + "," + ",".join(cw) + "\n")

def process(fins, fout):
    predictions = loadFile(fins)
    combine(predictions, fout)

def getInput(tgt):
    fins = []
    for value in tgt.split("+"):
        try:
            key, subs = value.split(",")
        except:
            key = value
            subs = "123456"
        for n in subs:
            fins += ["ans/" + key + "0" + n]
    return fins

if __name__ == "__main__":
    args = getArgs()
    tgt = args.tgt
    fout = args.a
    
    fins = getInput(tgt)
    print "fins", fins
    print "fout", fout
    process(fins, "ans/" + fout)
    
    if args.c:
        direct = "-d" if args.d else ""
        verbose = "-v" if args.v else ""
        os.system("python src/gain.py -t %s -c %d %s %s" % (fout, args.c, direct, verbose))
    print " ".join(sys.argv)
