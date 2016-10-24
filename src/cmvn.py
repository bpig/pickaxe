# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

from common import *

Fea = namedtuple("Fea", ["key", "value", "tgt"])
Pd = namedtuple("Fea", ["key", "value"])

def loadData(filename):
    print time.ctime(), "begin load data"
    datas = []
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        value = l[pos + 1:].split(",")
        tgt = float(value[-1])
        value = np.asarray(value[:-1]).astype(np.float32)
        datas.append(Fea(key, value, tgt))
    print time.ctime(), "finish load data"
    return datas

def loadData2(filename):
    datas = []
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        value = l[pos + 1:].split(",")
        value = np.asarray(value).astype(np.float32)
        datas.append(Pd(key, value))
    return datas

def globalCal(data):
    x = np.sum(data, 0)
    xx = np.array([n * n for n in data])
    xx = np.sum(xx, 0)
    ct = len(data)
    mu = x / ct
    delta = xx / ct - mu * mu
    delta = np.maximum(delta, 0)
    
    delta **= .5
    delta += 1
    return mu, delta

def calMuDelta(value):
    mu, delta = globalCal(value)
    np.save(fin + ".mu.npy", mu)
    np.save(fin + ".delta.npy", delta)
    # print mu
    # print delta
    return mu, delta

def loadMuDelta(fin):
    mu = np.load(fin + ".mu.npy")
    delta = np.load(fin + ".delta.npy")    
    return mu, delta

def pdNormalize(fin):
    data = loadData2(fin)
    mu, delta = loadMuDelta("2016.fe")

    keyfile = fin + ".key.npy"
    feafile = fin + ".fea.npy"
    tgtfile = fin + ".tgt.npy"

    keys = np.asarray([fea.key for fea in data])

    feas = []
    for fea in data:
        v = (fea.value - mu) / delta
        feas += [v]
    feas = np.asarray(feas)
    tgts = np.array([1.0] * len(keys))

    np.save(keyfile, keys)
    np.save(feafile, feas)
    np.save(tgtfile, tgts)

def process(fin):
    data = loadData(fin)
    value = [fea.value for fea in data]

    print time.ctime(), "cal fe.mu, fe.delta"
    mu, delta = calMuDelta(value)

    keyfile = fin + ".key.npy"
    feafile = fin + ".fea.npy"
    tgtfile = fin + ".tgt.npy"

    keys = np.asarray([fea.key for fea in data])

    feas = []
    for fea in data:
        v = (fea.value - mu) / delta
        feas += [v]
    feas = np.asarray(feas)

    tgts = np.asarray([fea.tgt for fea in data])

    perm = np.arange(len(keys))
    np.random.shuffle(perm)
    keys = keys[perm]
    feas = feas[perm]
    tgts = tgts[perm]

    np.save(keyfile, keys)
    np.save(feafile, feas)
    np.save(tgtfile, tgts)

if __name__ == '__main__':
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]

    if "predict" in cfg:
        fin = "data/" + cfg["predict"]
        pdNormalize(fin, fin + ".cmvn")
        sys.exit(0)

    fin = sys.argv[2]
    fin = "data/" + cfg[fin]
    process(fin)

    # cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
    #       % (fin + ".tmp", fin + ".cmvn")
    # os.system(cmd)
    # os.system("rm -rf %s.tmp" % fin)
    
