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
                kv[code] += item[1]
        cw = sorted(kv.items(), key=lambda x: x[1], reverse=True)
        cw = map(lambda x: x[0] + "_" + str(x[1]) + "_0.0", cw)
        fout.write(k + "," + ",".join(cw) + "\n")

def process(fins, fout):
    predictions = loadFile(fins)
    combine(predictions, fout)

def getArgs():
    parser = ArgumentParser(description="Combine")
    parser.add_argument("-t", dest="tgt", default=None,
                        help="target")
    parser.add_argument("-a", dest="a", default="tmp",
                        help="ans")
    parser.add_argument("-p", dest="p", default=None,
                        help="combine for predict")
    parser.add_argument("-g", dest="g", action="store_true", default=False,
                        help="cal gain")
    return parser.parse_args()

def getInput(tgt):
    fins = []
    for value in tgt.split("+"):
        key, subs = value.split(",")
        for n in subs:
            fins += ["ans/" + key + "0" + n]
    return fins

if __name__ == "__main__":
    args = getArgs()
    if args.p:
        key = args.p
        with open("conf/combine.yaml") as fin:
            tgt = str(yaml.load(fin)[key])
        fout = key
    else:
        assert args.tgt
        tgt = args.tgt
        fout = args.a

    fins = getInput(tgt)
    print "fins", fins
    print "fout", fout
    process(fins, "ans/" + fout)

    if args.g:
        os.system("python src/gain_by_p.py -t %s" % fout)
