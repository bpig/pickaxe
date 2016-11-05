# -*- coding:utf-8 -*-
from common import *

def transform(weight):
    def _inner(l):
        x = l.split("_")
        return x[0], float(x[1]) * weight, x[2]
    
    return _inner

def loadFile(fins):
    kv = defaultdict(list)
    for (fin, weight) in fins:
        for l in open(fin):
            l = l.strip()
            if not l:
                continue
            pos = l.find(",")
            ds = l[:pos]
            items = l[pos + 1:].split(",")
            items = map(transform(weight), items)
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

if __name__ == "__main__":
    with open("conf/combine.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    fins = cfg["input"]
    print fins
    if "weights" in cfg:
        weights = cfg["weights"]
    else:
        weights = [1.0] * len(fins)
    fout = cfg["output"]
    predictions = loadFile(zip(fins, weights))
    combine(predictions, fout)
