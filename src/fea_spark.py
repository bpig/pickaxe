# -*- coding:utf-8 -*-

from common import *
from pyspark import SparkConf
from pyspark import SparkContext
from data_loader import Ft, Ft2, Ft3, Ft4
import fea2
import yaml


def genOneStock(func, ftType):
    def _inter(kv):
        key, (info, ex) = kv

        info = info.split(",")
        info = map(lambda x: x.split("_"), info)
        for i in range(1, len(info)):
            info[i] = map(float, info[i])
        info = ftType(*info)

        f = StringIO(ex)
        ex = np.load(f)

        c = cat[key[:-3]]
        mix = (ex, c, gb)
        return func(key, info, mix)

    return _inter


def getSC(appName='aux'):
    sconf = SparkConf().set("spark.hadoop.validateOutputSpecs", "false") \
        .set("spark.akka.frameSize", "1000") \
        .set("spark.kryoserializer.buffer.max", "1000")
    sc = SparkContext(appName=appName, conf=sconf)
    sc.addPyFile("src/fea2.py")
    sc.addPyFile("src/fea2_base.py")
    sc.addPyFile("src/common.py")
    return sc


if __name__ == "__main__":
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    sc = getSC()

    fin_ex = "htk/ft/%s/ex" % model
    ex = sc.sequenceFile(fin_ex)

    fin = "htk/ft/%s/ft" % model
    ft = sc.sequenceFile(fin)

    rdd = ft.join(ex)

    fout = "htk/fe/%s/raw" % model

    feaFunc = fea2.kernels[cfg["func"]] if "func" in cfg else fea2.f2
    ftMap = {
        "ft3": Ft3,
        "ft4": Ft4,
    }

    ftType = ftMap[cfg["ft_type"]] if "ft_type" in cfg else Ft2

    print feaFunc, ftType
    fe = rdd.map(genOneStock(feaFunc, ftType)).filter(len).flatMap(lambda x: x)
    fe.saveAsSequenceFile(fout)

# spark-submit  --num-executors 700 --executor-cores 1 --executor-memory 5g src/fea_spark.py 2010
