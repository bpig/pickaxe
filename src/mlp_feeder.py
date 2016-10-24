# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/19"

from __future__ import absolute_import
from __future__ import division

import gzip
import os
import collections
import numpy as np
import time

Datasets = collections.namedtuple('Datasets', ['train', 'test'])
PredictSets = collections.namedtuple('PredictSets', ['key', 'fea', 'tgt'])

from tensorflow.python.framework import dtypes

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

def loadFea(filename, cv=None):
    keys = []
    feas = []
    tgts = []
    
    for c, l in enumerate(open(filename)):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        k, ds = key.split("_")
        # if ds >= "20160800":
        #     continue
        value = l[pos + 1:].split(",")
        tgt = float(value[-1])
        fea = np.asarray(value[:-1]).astype(np.float32)
        
        keys += [key]
        feas += [fea]
        tgts += [tgt]
        if cv and c == cv:
            break
    ct = len(tgts)
    return keys, np.asarray(feas), np.asarray(tgts)

def base_data(datafile, cv=None, skip=False):
    keyfile = datafile + ".key.npy"
    feafile = datafile + ".fea.npy"
    tgtfile = datafile + ".tgt.npy"
    
    if not skip and os.path.exists(keyfile):
        keys = np.load(keyfile)
        feas = np.load(feafile)
        tgts = np.load(tgtfile)
    else:
        keys, feas, tgts = loadFea(datafile, cv)
        np.save(keyfile, keys)
        np.save(feafile, feas)
        np.save(tgtfile, tgts)
    return keys, feas, tgts

def read_data_sets(datafile, cv=None, skip=False, reshape=False):
    print time.ctime(), "begin load data"
    keys, feas, tgts = base_data(datafile, cv, skip)
    ct = len(tgts)
    print ct

    tgts = np.asarray(map(lambda x: 0 if x < 1.002 else 1, tgts))
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

def read_predict_sets(datafile, cv=None, skip=False):
    print time.ctime(), "begin load data"
    if skip:
        print "no cache"
    keys, feas, tgts = base_data(datafile, cv, skip)
    print time.ctime(), "finish load data"
    return PredictSets(key=keys, fea=feas, tgt=tgts)
