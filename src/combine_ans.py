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

if __name__ == "__main__":
    prefix = sys.argv[1][:3]
    key = sys.argv[1][1:]
    with open("conf/combine.yaml") as fin:
        subs = str(yaml.load(fin)[key])
    fins = map(lambda x: ("ans/%s0" % prefix) + x, subs)
    print fins
    fout = "ans/%s" % sys.argv[1]
    process(fins, fout)
