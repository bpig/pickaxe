from sklearn import metrics
import numpy as np
import random
import time
import sys
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn

tf.logging.set_verbosity(tf.logging.INFO)

def tgtMap(tgt):
    return 0 if tgt < 1.002 else 1

def loadFea(filename):
    datas = []
    tgts = []
    a = []
    ct = [0] * 2
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        # key = l[:pos]
        value = l[pos + 1:].split(",")
        tgt = tgtMap(float(value[-1]))
        value = np.asarray(value[:-1]).astype(np.float32)
        a += [(value, tgt)]
        ct[tgt] += 1
    
    print ct
    random.shuffle(a)
    # a = a[:100000]
    point = int(len(a) * 0.9)
    train = a[:point]
    test = a[point:]
    
    train_data, train_tgt = zip(*train)
    test_data, test_tgt = zip(*test)
    # datas = np.array(datas)
    # tgts = np.array(tgts)
    return np.array(train_data), np.array(train_tgt), np.array(test_data), np.array(test_tgt)

# data, target = loadFea("../data/fe_20150907.cmvn")
# data, target, test_data, test_tgt = loadFea("../data/fe_20150907.cmvn")
print time.ctime()
# data, target, test_data, test_tgt = loadFea("data/fe_20150907.cmvn")
data, target, test_data, test_tgt = loadFea("data/20.fe.2015.sigmoid")
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
classifier = learn.Estimator(model_fn=my_model, model_dir="model/" + sys.argv[1])

classifier.fit(data, target, steps=1500)

print time.ctime()
y_predicted = [p['class'] for p in classifier.predict(test_data, as_iterable=True)]
score = metrics.accuracy_score(test_tgt, y_predicted)

print('Accuracy: {0:f}'.format(score))
