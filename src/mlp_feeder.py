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
        self._index_in_epoch = 0
        self._num_examples = len(feas)
    
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
    else:
        print "no cache", keyfile
        keys, feas, tgts = loadFea(datafile)
        np.save(keyfile, keys)
        np.save(feafile, feas)
        np.save(tgtfile, tgts)
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
    
    tr_x = feas
    tr_y = tgts
    
    te_x = feas[point:]
    te_y = tgts[point:]
    
    train = DataSet(tr_x, tr_y)
    test = DataSet(te_x, te_y)
    print time.ctime(), "finish load data"
    return Datasets(train=train, test=test)

def get_small_k_f_t(filename, uniq, k, f):
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos1 = l.find(":")
        key = l[:pos1]
        if key in uniq:
            continue
        fea = l[pos1 + 1:].split(",")
        k.append(key)
        f.append(fea)

def merge_small_predict(keys, feas, tgts):
    uniq = set(keys)
    small_fes = "data/predict/cache/"
    
    mu, delta = cmvn.loadMuDelta("data/predict/2016.fe")
    
    k = []
    f = []
    for d in os.listdir(small_fes):
        if d > 11 and not d.endswith(".fe"):
            continue
        print "load", small_fes + d
        get_small_k_f_t(small_fes + d, uniq, k, f)
    
    k = np.asarray(k)
    f = np.asarray(f, dtype=np.float32)
    f = (f - mu) / delta
    t = np.ones(len(k), dtype=np.float32)
    # return k, f, t
    keys = np.concatenate((keys, k))
    feas = np.concatenate((feas, f))
    tgts = np.concatenate((tgts, t))
    return keys, feas, tgts

def read_predict_sets(datafile, cache=True):
    print time.ctime(), "begin load data", datafile
    keys, feas, tgts = base_data(datafile, cache)
    tgts = tgts.astype(np.float32)
    feas = feas.astype(np.float32)
    
    # keys, feas, tgts = merge_small_predict(keys, feas, tgts)
    
    tgts = tgts.astype(np.float32)
    feas = feas.astype(np.float32)
    
    print "total", len(keys), "dim", len(feas[0]), tgts.dtype
    print time.ctime(), "finish load data"
    return PredictSets(key=keys, fea=feas, tgt=tgts)
