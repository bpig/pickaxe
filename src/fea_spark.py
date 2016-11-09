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
    # wins = [2, 3, 5, 7, 15]
    wins = [2, 3, 5, 7, 10, 15, 20, 30, 60]
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

if __name__ == "__main__":
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    sc = getSC()
    fin = "htk/" + cfg["ft"]
    fout = "htk/" + cfg["fe"]
    print "fin", fin
    print "fout", fout
    ft = sc.textFile(fin, 500)
    fe = ft.map(process).values().filter(len).flatMap(lambda x: x)
    fe.saveAsSequenceFile(fout)

# spark-submit  --num-executors 700 --executor-cores 1 --executor-memory 5g src/fea_spark.py 2010
