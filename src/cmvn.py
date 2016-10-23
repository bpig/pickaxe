# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

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

def process(fin, foutName):
    data = loadData(fin)
    value = [fea.value for fea in data]
    mu, delta = globalCal(value)
    np.save(fin+".mu.npy", mu)
    np.save(fin+".delta.npy", delta)
    fout = open(foutName, "w")
    for fea in data:
        v = (fea.value - mu) / delta
        v = map(str, v)
        fout.write(fea.key + ":" + ",".join(v) + "," + fea.tgt + "\n")

if __name__ == '__main__':
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]

    fin = sys.argv[2]
    fin = cfg[fin]
    process(fin, fin + ".tmp")

    cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
          % (fin + ".tmp", fin + ".cmvn")
    os.system(cmd)
    os.system("rm -rf %s.tmp" % fin)
    
