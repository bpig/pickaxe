# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/19"

# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Functions for downloading and reading MNIST data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gzip
import os
import collections
import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin

Datasets = collections.namedtuple('Datasets', ['train','test'])

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


def tgtMap(tgt):
    # m1 = 0.7363636363636363
    # m2 = 1.3444444444444443
    m1 = 0.8
    m2 = 1.2
    if tgt < m1:
        tgt = 0.8
    elif tgt > m2:
        tgt = m2
    ans = (tgt - m1) / (m2 - m1)
    # assert ans >= 0.0, ans
    # assert ans <= 1.0, ans
    return ans

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
        tgt = tgtMap(float(value[-1]))
        fea = np.asarray(value[:-1]).astype(np.float32)

        keys += [key]
        feas += [fea]
        tgts += [tgt]
        if cv and c == cv:
            break
    ct = len(tgts)
    return keys, np.asarray(feas), np.asarray(tgts).reshape([ct, 1])
    

def read_data_sets(datafile, cv=None, skip=False):
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

    point = int(len(keys) * .9)

    tr_x = feas[:point]
    tr_y = tgts[:point]

    te_x = feas[point:]
    te_y = tgts[point:]
    
    train = DataSet(tr_x, tr_y)
    test = DataSet(te_x, te_y)
    
    return Datasets(train=train, test=test)

