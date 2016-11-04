# -*- coding:utf-8 -*-

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from data_loader import Ft
import fea

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
    if len(ds) < maxWin + 2:
        return key, None
    
    feas = []
    for i in range(2, len(ds) - maxWin + 1):
        info = Ft(*map(lambda x: x[i:i + maxWin], items))
        # stock is stoped
        if info.status[i - 1] == 1 or info.status[i - 2] == 1:
            continue
        fe = genOneFe(info, wins)
        feas += [(key + "_" + info.ds[0], fe)]
    return key, feas

def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "2000") \
        .set("spark.kryoserializer.buffer.max", "2000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("data_loader.py")
    sc.addPyFile("fea.py")
    return sc

if __name__ == "__main__":
    with open("conf/spark.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    sc = getSC()
    fin = cfg["data"]
    fout = cfg["output"]
    ft = sc.textFile(fin)
    ft.map(process).values().filter(len) \
        .flatMap(lambda x: x).saveAsSequenceFile(fout)
