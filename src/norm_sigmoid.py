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
        value = l[pos + 1:].split(",")
        tgt = value[-1]
        value = np.asarray(value[:-1]).astype(np.float32)
        datas.append(Fea(key, value, tgt))
    return datas

def globalScale(values):
    # minval = values.min()
    # maxval = values.max()
    # lower = -4
    # upper = 4
    # values = lower + (upper - lower) * (values - minval) / (maxval - minval)
    # return values
    return doScale(values, -4, 4)

def doScale(arr, lower, upper):
    minval = arr.min()
    maxval = arr.max()
    return lower + (upper - lower) * (arr - minval) / (maxval - minval + 0.1)

def scaleByColumn(values):
    for i in range(len(values[0])):
        cl = values[:, i:i+1]
        values[:, i:i+1] = doScale(cl, -4, 4)
    return values

def sigmoid(values):
    return 1 / (1 + np.exp(-values))

def process(fin):
    data = loadData(fin)
    value = np.array([fea.value for fea in data])
    value = scaleByColumn(value)
    value = sigmoid(value)
    fout = open(fin + ".sigmoid", "w")
    for c, fea in enumerate(data):
        v = value[c]
        v = map(str, v)
        fout.write(fea.key + ":" + ",".join(v) + "," + fea.tgt + "\n")

if __name__ == '__main__':
    fin = sys.argv[1]
    process(fin)
