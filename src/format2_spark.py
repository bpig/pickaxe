#!/bin/env python

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from fea_kernel import *
from fea_core import *
import format2
import yaml


def getKv(line):
    if "code" in line or not line:
        return []
    pos = line.find(",")
    key = line[:pos]

    value = line[pos + 1:].replace("NULL", "0.0")
    return key, value


def cal(lt):
    lt = map(lambda x: x.split(","), lt)
    lt = sorted(lt, key=lambda x: x[0], reverse=True)
    # lt = filter(lambda x:x[0] > "20140000", lt)
    if not lt:
        return []
    lt = zip(*lt)

    lt, aux, ex = format2.extend(key="no_use", v=lt)

    lt = map(lambda x: "_".join(x), lt)
    lt = ",".join(lt)

    aux = map(lambda x: "_".join(x), aux)
    aux = ",".join(aux)

    f = StringIO()
    ex = np.asarray(ex)
    for i in range(len(ex)):
        ex[i] = np.nan_to_num(ex[i])
    np.save(f, ex)
    return lt, aux, bytearray(f.getvalue())


def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "1000") \
        .set("spark.kryoserializer.buffer.max", "1000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("src/data_loader.py")
    sc.addPyFile("src/fea.py")
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
    rdd = sc.textFile(fin, 1000)
    rdd = rdd.map(getKv).filter(len).groupByKey().mapValues(cal).filter(lambda x: len(x[1]))
    rdd.cache()

    fout_ex = "htk/ft/%s/ex" % model
    rdd.map(lambda (x, y): (x, y[2])).saveAsSequenceFile(fout_ex)

    fout_aux = "htk/ft/%s/aux" % model
    rdd.map(lambda (x, y): (x, y[1])).saveAsSequenceFile(fout_aux)

    fout = "htk/ft/%s/ft" % model
    rdd.map(lambda (x, y): (x, y[0])).saveAsSequenceFile(fout)
