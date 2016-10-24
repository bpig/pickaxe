# -*- coding:utf-8 -*-
from collections import Counter

from common import *

def loadFile(fins):
    kv = {}
    for i in range(len(fins)):
        for l in open(fins[i].strip()):
            l = l.strip()
            if not l:
                continue
            pos = l.find(",")
            ds = l[:pos]
            items = l[pos + 1:].split(",")
            items = map(lambda x: x.split("_"), items)
            for item in items:
                key = ds + "_" + item[0]
                if key in kv.keys():
                    kv[key][i] = item[1]
                else:
                    kv[key] = [0] * len(fins)
                    kv[key][i] = item[1]
    return kv

def combine(predictions, weights, fout):
    fout = open(fout, "w")
    cb = {}
    for k, v in predictions.items():
        v = np.array(v, float)
        weights = np.array(weights, float)
        cval = (v * weights).sum()
        segs = k.split("_")
        ds = segs[0]
        code = segs[1]
        if ds in cb.keys():
            cb[ds] += [[code, cval]]
        else:
            cb[ds] = [[code, cval]]

    for k, v in cb.items():
        v = sorted(v, key=lambda x: x[1], reverse=True)
        v = map(lambda x: x[0]+"_"+str(x[1]), v)
        fout.write(k + "," + ",".join(v) + "\n")

if __name__ == "__main__":
    with open("../conf/predict.yaml") as fin:
        cfg = yaml.load(fin)["f0"]
    fins = cfg["input"].split(",")
    weights = cfg["weights"].split(",")
    fout = cfg["output"]
    predictions = loadFile(fins)
    combine(predictions, weights, fout)