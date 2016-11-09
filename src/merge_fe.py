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

if __name__ == '__main__':
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]

    fin = cfg["raw_fe"]
    tgt = "data/fe/%s/" % model
    tr = tgt + "train"
    te = tgt + "test"

    os.system("mkdir -p %s" % tgt)

    mu = "data/fe/%s/%s.mu.npy" % (model, model)
    delta = "data/fe/%s/%s.delta.npy" % (model, model)
    mu = np.load(mu)
    delta = np.load(delta)

    tr_begin = int(cfg["train_begin"])
    tr_end = int(cfg["train_end"])

    print "model {m}, train {tb} - {te}, test {te} - now".format(m=model, tb=tr_begin, te=tr_end)

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
        values = (values - mu) / delta

        if ds < tr_end:
            tr_key += [l]
            tr_fea += [values]
            tr_tgt += [tgt]
        else:
            te_key += [l]
            te_fea += [values]
            te_tgt += [tgt]

        if c % 10000 == 0:
            print time.ctime(), c

    print "train:", len(tr_key), len(tr_fea[0])
    print "test:", len(te_key), len(tr_fea[0])
    with TimeLog():
        np_save(tr, tr_key, tr_fea, tr_tgt)
    with TimeLog():
        np_save(te, te_key, te_fea, te_tgt)


    

