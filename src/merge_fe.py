# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/31/16"

from common import *

def getArgs():
    parser = ArgumentParser(description="Merge")
    parser.add_argument("-t", dest="model", required=True,
                        help="fea model")
    parser.add_argument("-ds", dest="ds", default=None, type=int,
                        help="start time")
    return parser.parse_args()

def np_save(prefix, key, fea, tgt):
    key = np.asarray(key)
    fea = np.asarray(fea, dtype=np.float32)
    tgt = np.asarray(tgt, dtype=np.float32)
    np.save(prefix + ".key", key)
    np.save(prefix + ".fea", fea)
    np.save(prefix + ".tgt", tgt)

def mergeForPredict(model, ds):
    fin = "raw/%s_p" % model
    tgt = "data/fe/%s/daily/" % model
    fe = tgt + `ds` + ".fe"

    os.system("mkdir -p %s" % tgt)
    print "model {m}, predict {ds}".format(m=model, ds=ds)
    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)
    
    keys, feas, tgts = [], [], []
    for c, l in enumerate(files):
        if "dumper.list" in l:
            continue
        tgt = fin + "/" + l
        d = int(l.split("_")[1])

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

def mergeForTrain(model):
    fin = "raw/%s" % model
    tgt = "data/fe/%s/" % model
    tr = tgt + "train"
    te = tgt + "test"

    os.system("mkdir -p %s" % tgt)

    tr_begin = int(cfg["train_begin"])
    tr_end = int(cfg["train_end"])
    te_end = int(cfg["test_end"])

    print "model {m}, train {tb} - {te}, test {te} - {e}".format(
        m=model, tb=tr_begin, te=tr_end, e = te_end)

    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)

    tr_key, te_key = [], []
    tr_fea, te_fea = [], []
    tr_tgt, te_tgt = [], []
    for c, l in enumerate(files):
        if "dumper.list" in l:
            continue
        tgt = fin + "/" + l
        ds = int(l.split("_")[1])

        if ds < tr_begin:
            continue
            
        key = l
        values = np.fromstring(open(tgt).read(), sep=",", dtype=np.float32)
        tgt = values[-1]
        values = values[:-1]

        if tr_begin < ds < tr_end:
            if float(tgt) < 0:
                continue
            tr_key += [l]
            tr_fea += [values]
            tr_tgt += [tgt]
        elif tr_end <= ds < te_end:
            te_key += [l]
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

if __name__ == '__main__':
    args = getArgs()
    model = args.model
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]
    if not args.ds:
        mergeForTrain(model)
    else:
        mergeForPredict(model, args.ds)
