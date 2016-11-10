# -*- coding:utf-8 -*-

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from data_loader import Ft
import fea
import yaml

def genOneFe(info, wins):
    feas = fea.genOneFe(info, wins)
    tgt = info.tgt[0]
    assert tgt > 0
    feas += [tgt]
    info = map(str, feas)
    return ",".join(info)

def process(line):
    pos = line.find(",")
    key = line[:pos]
    value = line[pos + 1:]
    items = value.split(",")
    items = map(lambda x: x.split("_"), items)
    ds = items[0]
    wins = [2, 3, 5, 7, 15]
    maxWin = wins[-1]
    
    ct = len(ds) - 2 - maxWin
    if ct < 0:
        return key, []
    
    feas = []
    for i in range(2, ct + 2):
        info = Ft(*map(lambda x: x[i:i + maxWin], items))
        # stock is stoped
        if items[15][i - 1] == '1' or items[15][i - 2] == '1':
            continue
        fe = genOneFe(info, wins)
        feas += [(key + "_" + info.ds[0], fe)]
    return key, feas

def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "2000") \
        .set("spark.kryoserializer.buffer.max", "2000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("src/data_loader.py")
    sc.addPyFile("src/fea.py")
    sc.addPyFile("src/common.py")
    return sc

def select(tb, te):
    def _inter(kv):
        ds = int(kv[0].split("_")[1])
        if tb < ds < te:
            return True
        return False
    return _inter

def trans(content):
    value = content.split(",")[:-1]
    return np.asarray(value).astype(np.float32)

def cal(iterator):
    x = next(iterator)
    xx = x * x
    for y in iterator:
        x += y
        xx += y * y
    yield x, xx

def normal(mu, delta):
    def _inter(x):
        k, v = x
        value = v.split(",")
        tgt = value[-1]
        value = np.asarray(value[:-1]).astype(np.float32)
        value = (value - mu) / delta
        fea = ",".join(map(str, list(value) + [tgt]))
        return k, fea
    return _inter

if __name__ == "__main__":
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    sc = getSC()
    fin = "htk/" + cfg["fe"]
    ft = sc.sequenceFile(fin)
    tb = cfg["train_begin"]
    te = cfg["train_end"]
    ft = ft.filter(select(tb, te)).values().map(trans)
    ft.cache()
    ct = ft.count()
    print ct
    ft = ft.mapPartitions(cal).reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]))

    mu, delta = ft
    mu /= ct
    delta = delta / ct - mu * mu
    delta = np.maximum(delta, 0)

    delta **= .5
    delta += 1
    print len(mu), len(delta)
    np.save("md/" + model + ".mu.npy", mu)
    np.save("md/" + model + ".delta.npy", delta)

    print "begin normal"
    fout = fin + "n"

    ft = sc.sequenceFile(fin)
    ft = ft.map(normal(mu, delta)).saveAsSequenceFile(fout)
    


# spark-submit  --num-executors 500 --executor-cores 1 --executor-memory 5g src/fea_spark.py 2010
