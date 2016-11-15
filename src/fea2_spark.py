# -*- coding:utf-8 -*-

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from data_loader import Ft
import fea2
import yaml

def genOneStock(kv):
    key, (info, ex) = kv
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

if __name__ == "__main__":
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    sc = getSC()
    
    fin_ex = "htk/ft/%s/ex" % model
    ex = sc.sequenceFile(fin_ex)
    
    # fin_aux = "htk/ft/%s/aux" % model
    # aux = sc.sequenceFile(fin_aux)
    
    fin = "htk/ft/%s/ft" % model
    ft = sc.sequenceFile(fin)
    
    rdd = ft.join(ex)
    
    fout = "htk/fe/%s" % model
    
    fe = rdd.map(genOneStock).filter(len).flatMap(lambda x: x)
    fe.saveAsSequenceFile(fout)

# spark-submit  --num-executors 700 --executor-cores 1 --executor-memory 5g src/fea_spark.py 2010
