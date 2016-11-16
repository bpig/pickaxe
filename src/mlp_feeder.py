# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/19"

# from __future__ import absolute_import
# from __future__ import division

from common import *
import cmvn

Datasets = collections.namedtuple('Datasets', ['train', 'test'])
PredictSets = collections.namedtuple('PredictSets', ['key', 'fea', 'tgt'])

class DataSet(object):
    def __init__(self, feas, tgts):
        self._feas = feas
        self._tgts = tgts
        self._epochs_completed = 0
        self._num_examples = len(feas)
        self._index_in_epoch = len(feas)

    
    @property
    def feas(self):
        return self._feas
    
    @property
    def tgts(self):
        return self._tgts
    
    @property
    def num_examples(self):
        return self._num_examples
    
    @property
    def epochs_completed(self):
        return self._epochs_completed
    
    def next_batch(self, batch_size):
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._feas = self._feas[perm]
            self._tgts = self._tgts[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._feas[start:end], self._tgts[start:end]

def loadFea(filename):
    keys = []
    feas = []
    tgts = []
    
    for c, l in enumerate(open(filename)):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        # k, ds = key.split("_")
        # if ds >= "20160800":
        #     continue
        value = l[pos + 1:].split(",")
        tgt = float(value[-1])
        fea = np.asarray(value[:-1]).astype(np.float32)
        
        keys += [key]
        feas += [fea]
        tgts += [tgt]
    ct = len(tgts)
    return keys, np.asarray(feas), np.asarray(tgts)

def base_data(datafile, cache=True):
    keyfile = datafile + ".key.npy"
    feafile = datafile + ".fea.npy"
    tgtfile = datafile + ".tgt.npy"
    
    if cache and os.path.exists(keyfile):
        print "using cached"
        keys = np.load(keyfile)
        feas = np.load(feafile)
        tgts = np.load(tgtfile)
    # else:
    #     print "no cache", keyfile
    #     keys, feas, tgts = loadFea(datafile)
    #     np.save(keyfile, keys)
    #     np.save(feafile, feas)
    #     np.save(tgtfile, tgts)
    return keys, feas, tgts

def read_data_sets(datafile, division=1.002, cache=True, reshape=False):
    print time.ctime(), "begin load data"
    keys, feas, tgts = base_data(datafile, cache)
    ct = len(tgts)
    tgts = tgts.astype(np.float32)
    feas = feas.astype(np.float32)
    print "total", ct, "dim", len(feas[0]), tgts.dtype, "division", division
    tgts = np.asarray(map(lambda x: 0 if x < division else 1, tgts))
    if reshape:
        tgts = tgts.reshape([ct, 1])
    point = int(len(keys) * .9)
    
    tr_x = feas[:point]
    tr_y = tgts[:point]
    
    te_x = feas[point:]
    te_y = tgts[point:]
    
    train = DataSet(tr_x, tr_y)
    test = DataSet(te_x, te_y)
    print time.ctime(), "finish load data"
    return Datasets(train=train, test=test)

def merge_daily(keys, feas, tgts, cfg):
    uniq = set(keys)
    fe_version = cfg["fe"]
    k = []
    f = []
    daily_fe = "data/fe/%s/daily/" % fe_version
    for d in os.listdir(daily_fe):
        if d > 11 and not d.endswith(".fe"):
            continue
        print "load", daily_fe + d
        k1, f1, t1 = base_data(daily_fe + d, cfg["cache"])
        for i in range(len(k1)):
            if k1[i] in uniq:
                continue
            uniq.add(k1[i])
            k.append(k1[i])
            f.append(f1[i])
    if not k:
        return keys, feas, tgts
    
    k = np.asarray(k)
    f = np.asarray(f, dtype=np.float32)
    t = np.ones(len(k), dtype=np.float32)
    if not keys:
        return k, f, t
    keys = np.concatenate((keys, k))
    feas = np.concatenate((feas, f))
    tgts = np.concatenate((tgts, t))
    return keys, feas, tgts

def read_predict_sets(datafile, cfg):
    if "cache" not in cfg:
        cfg["cache"] = True
    if "merge" not in cfg:
        cfg["merge"] = False
    if "nobig" not in cfg:
        cfg["nobig"] = False

    print time.ctime(), "begin load data", datafile
    
    if not cfg["nobig"]:
        keys, feas, tgts = base_data(datafile, cfg["cache"])
        tgts = tgts.astype(np.float32)
        feas = feas.astype(np.float32)
    else:
        keys, feas, tgts = [], [], []
    if cfg["merge"]:
        keys, feas, tgts = merge_daily(keys, feas, tgts, cfg)
    
    tgts = tgts.astype(np.float32)
    feas = feas.astype(np.float32)

    print "total", len(keys), "dim", len(feas[0]), tgts.dtype
    print time.ctime(), "finish load data"
    return PredictSets(key=keys, fea=feas, tgt=tgts)
