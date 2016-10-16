# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

from common import *
import tensorflow as tf

DataSet = namedtuple("DataSet", ["fea", "tgt"])

def tgtClassify(num):
    return 0 if num <= 1.002 else 1

def transform(feas):
    n_samples = len(feas)
    n_features = len(feas.value[0])
    data = np.zeros((n_samples, n_features), dtype=np.float32)
    target = np.zeros((n_samples,), dtype=np.int)
    
    for i, fea in enumerate(feas):
        # target[i] = np.asarray(tgtClassify(fea.tgt), dtype=np.int)
        target[i] = tgtClassify(fea.tgt)
        data[i] = np.asarray(fea.value)
    return DataSet(data, target)

def getData(fin):
    feas = loadFea(fin, True)
    point = int(len(feas) * 0.9)
    trainSet = transform(feas[:point])
    testSet = transform(feas[point:])
    return trainSet, testSet

if __name__ == '__main__':
    fin = sys.argv[1]
    trainSet, testSet = getData(fin)
    
    n_features = len(trainSet.fea[0])
    # Specify that all features have real-value data
    feature_columns = [tf.contrib.layers.real_valued_column("", dimension=n_features)]
    
    # Build 3 layer DNN with 10, 20, 10 units respectively.
    classifier = tf.contrib.learn.DNNClassifier(
        feature_columns=feature_columns, hidden_units=[30], n_classes=2)
    
    # Fit model.
    classifier.fit(x=trainSet.data, y=trainSet.target, steps=2000)
    
    # Evaluate accuracy.
    accuracy_score = classifier.evaluate(x=testSet.data, y=testSet.target)["accuracy"]
    print('Accuracy: {0:f}'.format(accuracy_score))
