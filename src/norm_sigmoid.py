# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/16"

from common import *

Fea = namedtuple("Fea", ["key", "value", "tgt"])

def loadData(filename):
    datas = []
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        value = l[pos + 1].split(",")
        tgt = value[-1]
        value = np.asarray(value[:-1]).astype(np.float32)
        datas.append(Fea(key, value, tgt))
    return datas

def globalScale(values):
    minval = min(values)
    maxval = max(values)
    lower = -4
    upper = 4
    values = lower + (upper - lower) * (values - minval) / (maxval - minval)
    return values

def sigmoid(values):
    return 1/(1 + np.exp(-values))

def process(fin, foutName):
    data = loadData(fin)
    value = [fea.value for fea in data]
    value = globalScale(value)
    value = sigmoid(value)
    
    fout = open(foutName, "w")
    for c, fea in enumerate(data):
        fout.write(fea.key + ":" + ",".join(value[c]) + "," + fea.tgt + "\n")

if __name__ == '__main__':
    fin = sys.argv[1]
    process(fin, fin + ".sigmoid")


