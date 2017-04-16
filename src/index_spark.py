# -*- coding:utf-8 -*-

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from data_loader import Ft, Ft2, Ft3, Ft4
import fea2
import yaml

gb = []
gbSet = set(['20160831'])
for l in readFile("macro/000001.csv"):
    l = l.replace("-", "")
    items = l.split(",")
    elems = items[2:-1]
    elems = map(float, elems)
    if items[1] in gbSet:
        continue
    gb += [ [items[1]] + elems ]
    gbSet.add(items[1])
gb = sorted(gb, key=operator.itemgetter(0), reverse=True)

def genOneStock(kv):
    key, info = kv
    
    info = info.split(",")
    info = map(lambda x: x.split("_"), info)
    for i in range(1, len(info)):
        info[i] = map(float, info[i])
    info = Ft2(*info)
    
    ans = []
    for i in range(len(info.ds)):
        ds = info.ds[i]
        vol = info.volumn[i]
        amount = info.amount[i]

        pe = info.pe[i]
        s = info.s[i]
        high = info.high[i]
        low = info.low[i]
        e = info.e[i]
        shares = info.shares[i]

        r10 = 1 if e / pe >= 1.098 else 0
        r5 = 1 if e / pe >= 1.05 else 0
        r1 = 1 if 0.99 < e / pe < 1.01 else 0
        r_5 = 1 if e / pe <= 0.95 else 0
        r_10 = 1 if e / pe <= 0.902 else 0

        m10 = 1 if high / pe >= 1.098 else 0
        m5 = 1 if high / pe >= 1.05 else 0
        m_5 = 1 if low / pe <= 0.95 else 0
        m_10 = 1 if low / pe <= 0.902 else 0

        if (len(info.ds) - i) <= 60:
            r10 = r5 = r_5 = r_10 = m10 = m5 = m_5 = m10 = 0

        ans += [(ds, (vol, amount, e * shares, 
                 m10, m5, m_5, m_10, r10, r5, r1, r_5, r_10, 1))]
    return ans

def merge(x, y):
    ans = [x[i] + y[i] for i in range(len(x))]
    return ans

def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "1000") \
        .set("spark.kryoserializer.buffer.max", "1000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("src/common.py")
    sc.addPyFile("src/data_loader.py")
    return sc

def cal(iterator):
    total = list(iterator)
    total = sorted(total, key=operator.itemgetter(0), reverse=True)
    win = 15
    ans = []
    # assert len(gb) == len(total), "%d, %d, %s, %s" % (len(gb), len(total), 
    #                                                   gb[-1][0], total[-1][0])
    a = set([gb[_][0] for _ in range(len(gb))])
    b = set([total[_][0] for _ in range(len(total))])
    for v in a:
        if v not in b:
            assert False, v

    for i in range(1, len(total) - win):
        ds = total[i][0]
        assert gb[i][0] == ds, "%s, %s" % (gb[i][0] , ds)
        tgt = gb[i-1][2] / gb[i][2]
        feas = []
        for j in range(win):
            feas += gb[i+j][1:]
        for j in range(win):
            feas += total[i+j][1]
        feas += [tgt]
        feas = map(str, feas)
        feas = ",".join(feas)
        ans += [(ds, feas)]
    yield ans

if __name__ == "__main__":
    sc = getSC()
    
    fin = "htk/ft/f13/ft" 
    rdd = sc.sequenceFile(fin)
    
    fout = "htk/index/raw" 

    fe = rdd.map(genOneStock).filter(len).flatMap(lambda x: x)\
        .reduceByKey(merge).coalesce(1).mapPartitions(cal).flatMap(lambda x: x)
    fe.cache()
    print fe.count()
    fe.saveAsSequenceFile(fout)

