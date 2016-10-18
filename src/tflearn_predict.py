from sklearn import metrics
import numpy as np
import random
import time
import sys
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn

tf.logging.set_verbosity(tf.logging.INFO)

def loadFea(filename):
    keys = []
    values = []
    tgts = []
    ct = [0] * 2
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key = l[:pos]
        value = l[pos + 1:].split(",")
        tgt = float(value[-1])
        if tgt == -1:
            print key, "-1"
            continue
        value = np.asarray(value[:-1]).astype(np.float32)
        keys += [key]
        values += [value]
        tgts += [tgt]
        ct[tgt] += 1
    
    print ct
    return keys, values, tgts

# data, target = loadFea("../data/fe_20150907.cmvn")
# data, target, test_data, test_tgt = loadFea("../data/fe_20150907.cmvn")
print time.ctime()
# data, target, test_data, test_tgt = loadFea("data/fe_20150907.cmvn")
keys, values, tgts = loadFea("data/2015.fe")
print time.ctime()

def my_model(features, target):
    """DNN with three hidden layers, and dropout of 0.1 probability."""
    # Convert the target to a one-hot tensor of shape (length of features, 3) and
    # with a on-value of 1 for each one-hot vector of length 3.
    
    target = tf.one_hot(target, 2, 1, 0)
    
    features = layers.stack(features, layers.fully_connected, [800, 100, 10])
    
    prediction, loss = (
        tf.contrib.learn.models.logistic_regression(features, target)
    )
    
    train_op = tf.contrib.layers.optimize_loss(
        
        loss, tf.contrib.framework.get_global_step(), optimizer='Adam',
        learning_rate=0.001)
    
    return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op

# with tf.device('/gpu:0'):
# classifier = learn.Estimator(model_fn=my_model, model_dir="model/" + sys.argv[1])
classifier = learn.Estimator(model_dir="model/" + sys.argv[1])

y_predicted = [p['class'] for p in classifier.predict(values[:10], as_iterable=True)]

print y_predicted
# score = metrics.accuracy_score(test_tgt, y_predicted)

# print('Accuracy: {0:f}'.format(score))
