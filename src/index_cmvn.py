# -*- coding:utf-8 -*-

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
import yaml

def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "2000") \
        .set("spark.kryoserializer.buffer.max", "2000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("src/data_loader.py")
    sc.addPyFile("src/common.py")
    return sc

def select(interval):
    lt = getInterval(interval)
    
    def _inter(kv):
        ds = int(kv[0])
        return dsInInterval(ds, lt)
    
    return _inter

def trans(content):
    value = content.split(",")[:-1]
    arr = np.asarray(value).astype(np.float64)
    return arr

def cal(total):
    def _inter(iterator):
        n = next(iterator)
        x = n / total
        xx = n * n / total
        for y in iterator:
            x += y / total
            xx += y * y / total
        yield x, xx
    
    return _inter

def normal(mu, delta):
    def _inter(x):
        k, v = x
        value = v.split(",")
        tgt = value[-1]
        value = np.asarray(value[:-1]).astype(np.float64)
        value = (value - mu) / delta
        fea = ",".join(map(str, list(value) + [tgt]))
        return k, fea
    
    return _inter

if __name__ == "__main__":
    sc = getSC()
    fin = "htk/index/raw"
    mu_file = "md/index.mu.npy"
    delta_file = "md/index.delta.npy" 
    ft = sc.sequenceFile(fin)
    
    if len(sys.argv) == 3:
        fout = "htk/fe/%s/cmvn_p" % model
        print fout
        mu = np.load(mu_file)
        delta = np.load(delta_file)
        interval = cfg["predict"]
        print interval
        ft = ft.filter(select(interval))
        print ft.count()
        ft = ft.map(normal(mu, delta)).saveAsSequenceFile(fout)
        sys.exit(0)
    
    tr_interval = "20100000-20160500"
    ft = ft.filter(select(tr_interval)).values().map(trans)
    ft.cache()
    ct = ft.count()
    print ct
    
    ft = ft.mapPartitions(cal(ct))
    ft = ft.reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]))
    
    mu, delta = ft
    delta = delta - mu * mu
    delta = np.maximum(delta, 0)
    delta **= .5
    delta[delta == 0] = 1
    
    print mu
    print delta
    
    print len(mu)
    np.save(mu_file, mu)
    np.save(delta_file, delta)
    
    print time.ctime(), "begin normal"
    fout = "htk/index/cmvn"
    
    ft = sc.sequenceFile(fin)
    interval = "20100000-20160500,20160500-20161230"
    ft = ft.filter(select(interval))
    ft = ft.map(normal(mu, delta)).saveAsSequenceFile(fout)

# spark-submit  --num-executors 500 --executor-cores 1 --executor-memory 5g src/fea_spark.py 2010
