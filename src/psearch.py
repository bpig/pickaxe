# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/3/16"

from common import *
from pre_t import genAns
from tk import loadModel
from mlp_feeder import read_data
import gain
import filter_by_rule

def getModels(model_dir):
    models = sorted(os.listdir(model_dir))
    models = filter(lambda x: x.endswith("hdf5"), models)
    print models
    return models

def searchModel(model, keys, fout):
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
    
    model_dir = "model/" + model
    
    fe_version = cfg["fe"]
    datafile = "data/fe/%s/test" % fe_version
    
    models = getModels(model_dir)
    predSet = read_data(datafile)
    
    for m in models:
        key = "%s,%s" % (model, m)
        if key in keys:
            continue
        
        core = loadModel(model_dir, m)
        
        pred = core.predict_proba(predSet.fea, batch_size=1024, verbose=1)
        f = "log/ps_" + model[:3]
        genAns(pred, predSet, f)
        filter_by_rule.process(f)
        money = gain.process(f + ".filter", 50, output=False)
        
        value = "%s,%.5f\n" % (key, money)
        print "==" * 10
        print value,
        print
        fout.write(value + "\n")
        fout.flush()

def getkeys(logfile):
    try:
        return set([_[0] + "," + _[1] for _ in csv.reader(open(logfile)) if _])
    except:
        return set()

def getInput(tgt):
    fins = []
    for value in tgt.split("+"):
        key, subs = value.split(",")
        for n in subs:
            fins += [key + "0" + n]
    return fins

if __name__ == "__main__":
    args = getArgs()
    model = getInput(args.tgt)
    print model
    logfile = "log/" + args.a
    keys = getkeys(logfile)
    
    fout = open(logfile, "a")
    for m in model:
        searchModel(m, keys, fout)
