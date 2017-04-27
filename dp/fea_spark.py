#!/bin/env python
from StringIO import StringIO
import pandas as pd
from pyspark import SparkConf
from pyspark import SparkContext
from fea import *


def getKv(line):
    if not line:
        return ""
    pos = line.rfind(",")
    key = line[pos + 1:]
    value = line[:pos]
    return key, value


def getSC(appName='fea'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "1000") \
        .set("spark.kryoserializer.buffer.max", "1000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("fea.py")
    return sc


# def f(iterator): yield sum(iterator)
# rdd.mapPartitions(f).collect()

def read_csv(iterator):
    content = "\n".join(list(iterator))
    f = StringIO(content)
    # S_INFO_WINDCODE, TRADE_DT, S_DQ_ADJOPEN, S_DQ_ADJHIGH, S_DQ_ADJLOW, S_DQ_ADJCLOSE,
    # S_DQ_VOLUME, S_DQ_AMOUNT, S_DQ_TURN, S_DQ_FREETURNOVER
    columns = ["dt", "s", "h", "l", "e", "v", "m", "t", "ft"]
    df = pd.read_csv(f, header=None, names=columns)
    return df


def gen_fea((st_code, df)):
    df = cal(df)


if __name__ == "__main__":
    sc = getSC()
    model = "f12"
    fin = "htk/" + "merge.cc"
    rdd = sc.textFile(fin, 2)
    rdd = rdd.map(getKv).filter(len).groupByKey().mapValues(read_csv)
    print rdd.collect()
    # groupByKey().mapValues(cal).filter(lambda x: len(x[1]))
    # rdd.cache()

    # fout_aux = "htk/ft/%s/aux" % model
    # rdd.map(lambda (x, y): (x, y[1])).saveAsSequenceFile(fout_aux)
    #
    # fout = "htk/ft/%s/ft" % model
    # rdd.map(lambda (x, y): (x, y[0])).saveAsSequenceFile(fout)
