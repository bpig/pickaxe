# -*- coding:utf-8 -*-

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from data_loader import Ft, Ft2
import fea2
import yaml

def genOneStock(kv):
    key, (info, ex) = kv

    info = info.split(",")
    info = map(lambda x: x.split("_"), info)
    info = Ft2(*info)

    f = StringIO(ex)
    ex = np.load(f)

    return fea2.genOneStock(key, info, ex)

def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "1000") \
        .set("spark.kryoserializer.buffer.max", "1000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("src/data_loader.py")
    sc.addPyFile("src/fea2.py")
    sc.addPyFile("src/common.py")
    return sc

def test2(ex):
    ex = np.load(StringIO(ex))
    return ex[0][:3]

def test1(info):
    info = info.split(",")
    info = map(lambda x: x.split("_"), info)
    info = Ft(*info)
    return info.ds[:3]

if __name__ == "__main__":
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    sc = getSC()
    
    fin_ex = "htk/ft/%s/ex" % model
    ex = sc.sequenceFile(fin_ex)
    # print ex.mapValues(test).collect()[:30]
    
    # fin_aux = "htk/ft/%s/aux" % model
    # aux = sc.sequenceFile(fin_aux)
    
    fin = "htk/ft/%s/ft" % model
    ft = sc.sequenceFile(fin)
    #print ft.mapValues(test1).collect()[:30]

    rdd = ft.join(ex)
    
    fout = "htk/fe/%s/raw" % model
    
    fe = rdd.map(genOneStock).filter(len).flatMap(lambda x: x)
    fe.saveAsSequenceFile(fout)

# spark-submit  --num-executors 700 --executor-cores 1 --executor-memory 5g src/fea_spark.py 2010
