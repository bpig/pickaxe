# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

from common import *

Fea = namedtuple("Fea", ["key", "value", "tgt"])

def loadData(filename, hasTgt=True):
    print time.ctime(), "begin load data"
    datas = []
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        value = l[pos + 1:].split(",")
        if hasTgt:
            tgt = float(value[-1])
            value = value[:-1]
        else:
            tgt = 0.0
        value = np.asarray(value).astype(np.float32)
        datas.append(Fea(key, value, tgt))
    print time.ctime(), "finish load data"
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

def calMuDelta(fin, value):
    mu, delta = globalCal(value)
    np.save(fin + ".mu.npy", mu)
    np.save(fin + ".delta.npy", delta)
    return mu, delta

def loadMuDelta(fin):
    mu = np.load(fin + ".mu.npy")
    delta = np.load(fin + ".delta.npy")
    return mu, delta

def saveByNp(fin, keys, feas, tgts, shuffle=True):
    keyfile = fin + ".key.npy"
    feafile = fin + ".fea.npy"
    tgtfile = fin + ".tgt.npy"
    
    if shuffle:
        perm = np.arange(len(keys))
        np.random.shuffle(perm)
        keys = keys[perm]
        feas = feas[perm]
        tgts = tgts[perm]
    
    np.save(keyfile, keys)
    np.save(feafile, feas)
    np.save(tgtfile, tgts)

def getKFT(mu, delta, data):
    keys = np.asarray([fea.key for fea in data])
    feas = [(fea.value - mu) / delta for fea in data]
    feas = np.asarray(feas).astype(np.float32)
    tgts = np.asarray([fea.tgt for fea in data]).astype(np.float32)
    return keys, feas, tgts

def pdNormalize(fin):
    data = loadData(fin, hasTgt=False)
    mu, delta = loadMuDelta("2016.fe")
    
    keys, feas, tgts = getKFT(mu, delta, data)
    saveByNp(fin, keys, feas, tgts)

def process(fin, cal=True):
    data = loadData(fin)
    
    if cal:
        print time.ctime(), "cal fe.mu, fe.delta"
        value = [fea.value for fea in data]
        mu, delta = calMuDelta(fin, value)
    else:
        tgt = fin[:-2] + "tr"
        print "load mu, delta %s" % tgt
        mu, delta = loadMuDelta(tgt)
    
    keys, feas, tgts = getKFT(mu, delta, data)
    saveByNp(fin, keys, feas, tgts, shuffle=True)

if __name__ == '__main__':
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    if "predict" in cfg:
        fin = "data/" + cfg["predict"]
        pdNormalize(fin)
        sys.exit(0)
    
    train = "data/" + cfg["train"]
    test = "data/" + cfg["test"]
    process(train, cal=True)
    process(test, cal=False)
    
    # cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
    #       % (fin + ".tmp", fin + ".cmvn")
    # os.system(cmd)
    # os.system("rm -rf %s.tmp" % fin)
