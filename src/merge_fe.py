# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/31/16"

from common import *
from mlp_feeder import read_data_sets

def getFeaKeys(filename):
    for l in open(filename):
        pass

def mergeSmallCsv(uniq):
    smallCsvDir = "data/predict/cache"
    for d in os.listdir(smallCsvDir):
        if len(d) > 12 or not d.endswith(".fe"):
            continue
        smallCsvDir + "/" + d
        print d, len(kv), len(uniq)

if __name__ == '__main__':
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    fin = "data/" + cfg["test"]
