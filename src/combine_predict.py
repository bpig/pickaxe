# -*- coding:utf-8 -*-
from collections import Counter

from common import *

def loadFile(fins, weights):
    kv = {}
    weights = map(lambda x: float(x), weights)
    for i in range(len(fins)):
        for l in open(fins[i].strip()):
            l = l.strip()
            if not l:
                continue
            pos = l.find(",")
            ds = l[:pos]
            items = l[pos + 1:].split(",")
            items = map(lambda x: x.split("_"), items)
            items = map(lambda x: [x[0], float(x[1]) * weights[i], x[2]], items)
            if ds in kv.keys():
                kv[ds] += [items]
            else:
                kv[ds] = [items]
    return kv

def combine(predictions, fout):
    fout = open(fout, "w")
    cb = {}
    for k, v in predictions.items():
        kv = {}
        for items in v:
            for item in items:
                code = item[0] + "_" + item[2]
                if code in kv.keys():
                    kv[code] += item[1]
                else:
                    kv[code] = item[1]
        cw = []
        for c, w in kv.items():
            segs = c.split("_")
            code = segs[0]
            prob = segs[1]
            cw += [[code, w, prob]]
        cw = sorted(cw, key=lambda x: x[1], reverse=True)
        cw = map(lambda x: x[0] + "_" + str(x[1]) + "_" + x[2], cw)
        fout.write(k + "," + ",".join(cw) + "\n")

if __name__ == "__main__":
    with open("conf/predict.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    fins = cfg["input"].split(",")
    weights = cfg["weights"].split(",")
    fout = cfg["output"]
    predictions = loadFile(fins, weights)
    combine(predictions, fout)
