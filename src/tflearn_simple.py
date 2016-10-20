from sklearn import metrics
import numpy as np
import random
import time
import sys
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn
from mlp_feeder import read_data_sets

tf.logging.set_verbosity(tf.logging.INFO)

data = read_data_sets("data/20.fe.cmvn.shuf", None, True)

def pred(classifier, feas, tgts, msg):
    y_predicted = [p['class'] for p in classifier.predict(feas, as_iterable=True)]
    score = metrics.accuracy_score(tgts, y_predicted)
    print('%s acc: %.6f'% (msg, score))

def my_model(features, target):
    """DNN with three hidden layers, and dropout of 0.1 probability."""
    target = tf.one_hot(target, 2, 1, 0)
    
    features = layers.stack(features, layers.fully_connected, [512, 128, 8])
    
    prediction, loss = tf.contrib.learn.models.logistic_regression(features, target)
    
    train_op = tf.contrib.layers.optimize_loss(
        loss, tf.contrib.framework.get_global_step(), optimizer='Adam',
        learning_rate=0.001)
    
    return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op

# with tf.device('/gpu:0'):

classifier = learn.Estimator(model_fn=my_model, model_dir="model/" + sys.argv[1])

classifier.fit(data.train._feas, data.train._tgts, steps=1000)

ct = data.test.num_examples
pred(classifier, data.train.feas[:ct], data.train.tgts[:ct], "train")
pred(classifier, data.test.feas, data.test.tgts, "test")

