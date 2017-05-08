# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/19"

# from __future__ import absolute_import
# from __future__ import division

from common import *

Datasets = collections.namedtuple(
    'Datasets', ['key', 'fea', 'tgt'])


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
            # Shuffle the macro
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


def base_data(datafile):
    feafile = datafile + "fea.npy"
    tgtfile = datafile + "tgt.npy"
    keyfile = datafile + "key.npy"

    feas = np.load(feafile)
    tgts = np.load(tgtfile)
    keys = np.load(keyfile)
    return keys, feas, tgts


def read_data(datafile, begin, end):
    print time.ctime(), "begin load data"
    keys, feas, tgts = base_data(datafile)

    ct = len(tgts)
    index = np.asarray([True] * ct)
    for c, (k, d) in enumerate(keys):
        if d < begin or d > end:
            index[c] = False

    keys = keys[index]
    tgts = tgts[index]
    feas = feas[index]

    tgts = tgts.astype(np.float32)
    feas = feas.astype(np.float32)
    print "total", ct, "dim", len(feas[0]), tgts.dtype

    print time.ctime(), "finish load data"
    return Datasets(key=keys, fea=feas, tgt=tgts)
