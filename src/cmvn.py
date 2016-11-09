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
    dirname = os.path.dirname(fin)
    np.save(dirname + "fe.mu.npy", mu)
    np.save(dirname + "fe.delta.npy", delta)
    return mu, delta

def loadMuDelta(fin):
    dirname = os.path.dirname(fin)
    mu = np.load(dirname + "fe.mu.npy")
    delta = np.load(dirname + "fe.delta.npy")
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
    mu, delta = loadMuDelta("/home/shuai.li/pickaxe/data/2010/15/fe")
    
    keys, feas, tgts = getKFT(mu, delta, data)
    saveByNp(fin, keys, feas, tgts)

def process(fin, cal=True, shuffle=True):
    data = loadData(fin)
    
    if cal:
        print time.ctime(), "cal fe.mu, fe.delta"
        value = [fea.value for fea in data]
        mu, delta = calMuDelta(fin, value)
    else:
        print "load mu, delta for %s" % fin
        mu, delta = loadMuDelta(fin)
    
    keys, feas, tgts = getKFT(mu, delta, data)
    saveByNp(fin, keys, feas, tgts, shuffle=shuffle)

if __name__ == '__main__':
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    
    tgt = "data/fe/%s/" % model
        
    train = tgt + "train"
    test = tgt + "test"
    process(train, cal=True)
    process(test, cal=False, shuffle=False)
    
    # cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
    #       % (fin + ".tmp", fin + ".cmvn")
    # os.system(cmd)
    # os.system("rm -rf %s.tmp" % fin)
