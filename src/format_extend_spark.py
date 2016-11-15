#!/bin/env python

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from fea_kernel import *
from fea_core import *
import format_extend

def getKv(line):
    if "code" in line or not line:
        return []
    pos = line.find(",")
    key = line[:pos]
    
    value = line[pos + 1:].replace("NULL", "0.0")
    return key, value
    # code, dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares
    #  -1    0    1      2       3     4  5    6    7   8      9        10
    
    # dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares,
    # s-rate, h-rate, l-rate, e-rate, status, s-status, wav-status, e-status, target

def ft(lt):
    lt = map(lambda x: x.split(","), lt)
    lt = sorted(lt, key=lambda x: x[0], reverse=True)
    lt = zip(*lt)
    lt, aux, ex = format_extend.extend(k, lt)
    lt = map(lambda x: "_".join(x), lt)
    aux = map(lambda x: "_".join(x), aux)
    f = StringIO()
    np.save(f, ex)
    return lt, aux, bytearray(f.getvalue())

def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "1000") \
        .set("spark.kryoserializer.buffer.max", "1000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("src/data_loader.py")
    sc.addPyFile("src/format_extend.py")
    sc.addPyFile("src/fea_kernel.py")
    sc.addPyFile("src/fea_core.py")
    sc.addPyFile("src/common.py")
    return sc

if __name__ == "__main__":
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    sc = getSC()
    fin = "htk/" + cfg["raw"]
    ft = sc.textFile(fin, 500)
    ft = ft.map(getKv).filter(len).groupByKey().mapValues(ft)
    ft.cache()
    
    fout_ex = "htk/ft/%s/ex" % model
    ft.map(lambda x, y: (x, y[2])).saveAsSequenceFile(fout_ex)
    
    fout_aux = "htk/ft/%s/aux" % model
    ft.map(lambda x, y: (x, y[1])).saveAsSequenceFile(fout_aux)
    
    fout = "htk/ft/%s/ft" % model
    ft.map(lambda x, y: (x, y[0])).saveAsSequenceFile(fout)
