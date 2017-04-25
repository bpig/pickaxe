#!/bin/env python
from StringIO import StringIO
import pandas as pd
from pyspark import SparkConf
from pyspark import SparkContext


def getKv(line):
    if not line:
        return ""
    pos = line.find(",")
    key = line[:pos]
    value = line[pos + 1:]
    return key, value


def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "1000") \
        .set("spark.kryoserializer.buffer.max", "1000")
    sc = SparkContext(appName=appName, conf=sconf)
    # sc.addPyFile("dp/common.py")
    return sc


# def f(iterator): yield sum(iterator)
# rdd.mapPartitions(f).collect()

def cat(iterator):
    content = "\n".join(list(iterator))
    f = StringIO()
    f.write(content)
    df = pd.read_csv(f)
    return df


if __name__ == "__main__":
    sc = getSC()
    model = "f12"
    fin = "htk/" + "test.cc"
    rdd = sc.textFile(fin, 1000)
    rdd = rdd.map(getKv).filter(len).groupbyKey().mapValues(cat)
    rdd.collect()
    # groupByKey().mapValues(cal).filter(lambda x: len(x[1]))
    # rdd.cache()

    # fout_aux = "htk/ft/%s/aux" % model
    # rdd.map(lambda (x, y): (x, y[1])).saveAsSequenceFile(fout_aux)
    #
    # fout = "htk/ft/%s/ft" % model
    # rdd.map(lambda (x, y): (x, y[0])).saveAsSequenceFile(fout)
