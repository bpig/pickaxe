#!/bin/env python
# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/31/16"

from common import *

def np_save(prefix, key, fea, tgt):
    key = np.asarray(key)
    fea = np.asarray(fea, dtype=np.float32)
    tgt = np.asarray(tgt, dtype=np.float32)
    np.save(prefix + ".key", key)
    np.save(prefix + ".fea", fea)
    np.save(prefix + ".tgt", tgt)

def mergeForPredict(model, ds):
    fin = "raw/%sp" % model
    tgt = "data/fe/%s/daily/" % model
    fe = tgt + ds + ".fe"
    
    os.system("mkdir -p %s" % tgt)
    print "model {m}, predict {ds}".format(m=model, ds=ds)
    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)

    ct = len(ds)
    ds = int(ds)
    keys, feas, tgts = [], [], []
    for c, l in enumerate(files):
        if "dumper.list" in l:
            continue
        tgt = fin + "/" + l
        d = int(l.split("_")[1][:ct])
        
        if d != ds:
            continue
        key = l
        values = np.fromstring(open(tgt).read(), sep=",", dtype=np.float32)
        tgt = 0.0
        fea = values[:-1]
        
        keys += [key]
        feas += [fea]
        tgts += [tgt]
    
    print "predict:", len(keys), len(feas[0])
    print "save to", fe
    with TimeLog():
        np_save(fe, keys, feas, tgts)

def mergeFt(fin, fout):
    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)
    print fin, "->", fout
    fout = open(fout, "w")
    for f in files:
        if "dumper.list" in f:
            continue
        fout.write(f + "," + open(fin + f).read() + "\n")

def mergeForTrain(model):
    fin = "raw/%s" % model
    tgt = "data/fe/%s/" % model
    tr = tgt + "train"
    te = tgt + "test"
    
    os.system("mkdir -p %s" % tgt)
    
    tr_interval = getInterval(cfg["train"])
    te_interval = getInterval(cfg["test"])
    
    print "model", model, "train", tr_interval, "test", te_interval
    
    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)
    
    tr_key, te_key = [], []
    tr_fea, te_fea = [], []
    tr_tgt, te_tgt = [], []
    for c, key in enumerate(files):
        if "dumper.list" in key:
            continue
        tgt = fin + "/" + key
        ds = int(key.split("_")[1])
        
        values = np.fromstring(open(tgt).read(), sep=",", dtype=np.float32)
        tgt = values[-1]
        values = values[:-1]
        
        if dsInInterval(ds, tr_interval):
            if float(tgt) < 0:
                continue
            tr_key += [key]
            tr_fea += [values]
            tr_tgt += [tgt]
        elif dsInInterval(ds, te_interval):
            te_key += [key]
            te_fea += [values]
            te_tgt += [tgt]
        else:
            continue
        
        if c % 10000 == 0:
            print time.ctime(), c
    
    if tr_fea:
        print "train:", len(tr_key), len(tr_fea[0])
        with TimeLog():
            np_save(tr, tr_key, tr_fea, tr_tgt)
    if te_fea:
        print "test:", len(te_key), len(te_fea[0])
        with TimeLog():
            np_save(te, te_key, te_fea, te_tgt)

def download(tgt, model):
    if tgt == "p":
        cmd = "java -jar raw/smsr_dumper htk/fe/{m}/cmvn_p raw/{m}p".format(m=model)
    elif tgt == "t":
        cmd = "java -jar raw/smsr_dumper htk/fe/{m}/cmvn raw/{m}".format(m=model)
    elif tgt == "ft":
        cmd = "java -jar raw/smsr_dumper htk/ft/{m}/ft raw/{m}t".format(m=model)
    elif tgt == "aux":
        cmd = "java -jar raw/smsr_dumper htk/ft/{m}/aux raw/{m}x".format(m=model)
    else:
        return
    os.system(cmd)

def getArgs():
    parser = ArgumentParser(description="Merge")
    parser.add_argument("-t", dest="model", required=True,
                        help="fea model")
    parser.add_argument("-ds", dest="ds", default="",
                        help="start time")
    parser.add_argument("-d", dest="download", default="",
                        help="download from spark")
    parser.add_argument("-m", dest="m", action="store_true", default=False,
                        help="merge for train")
    return parser.parse_args()

if __name__ == '__main__':
    args = getArgs()
    model = args.tgt
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    
    download(args.download, model)
    
    if args.ds:
        mergeForPredict(model, args.ds)
    
    if args.m:
        mergeForTrain(model)

    if args.download == "ft":
        ft = "raw/%st/" % model
        mergeFt(ft, FT_FILE)
    if args.download == "aux":
        aux = "raw/%sx/" % model
        mergeFt(aux, AUX_FILE)
