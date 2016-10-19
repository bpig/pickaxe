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
    for c, l in enumerate(open(filename)):
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
        # if c == 20000:
        #     break
    
    print ct
    # random.shuffle(a)
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
data, target, test_data, test_tgt = loadFea("data/20.fe.2015.cmvn.shuf")
print len(data[0])
print time.ctime()

def my_model(features, target):
    """DNN with three hidden layers, and dropout of 0.1 probability."""
    # Convert the target to a one-hot tensor of shape (length of features, 3) and
    # with a on-value of 1 for each one-hot vector of length 3.
    
    target = tf.one_hot(target, 2, 1, 0)
    
    # sigmoid scala
    #    features = layers.stack(features, layers.fully_connected, [2056, 1024, 1024, 512, 64, 8]) # 0.647676
    #    features = layers.stack(features, layers.fully_connected, [800, 100, 10]) # f2  0.650175
    #    features = layers.stack(features, layers.fully_connected, [512, 256, 32, 8]) # f3  0.636182
    #    features = layers.stack(features, layers.fully_connected, [512, 32, 8]) # f4  0.651674
    
    # cmvn scala, 2w
    #    features = layers.stack(features, layers.fully_connected, [512, 32, 8]) # f5 0.700150
    # f6 0.691654
    #    features = layers.stack(features, layers.fully_connected, [512, 256, 256, 32, 8])
    
    # full
    # f7 0.805802
    #    features = layers.stack(features, layers.fully_connected, [512, 128, 8])
    # v2 1400, 0.805802, Train Accuracy: 0.914740,  700, 0.748649, Train Accuracy: 0.848748
    #    features = layers.stack(features, layers.fully_connected, [512, 128, 8])
    
    # v3, 700, 0.750673, Train Accuracy: 0.939611, 1400, Train Accuracy: 0.960253, Test Accuracy: 0.746624
    features = layers.stack(features, layers.fully_connected, [512, 256, 256, 32, 8])
    
    prediction, loss = (
        tf.contrib.learn.models.logistic_regression(features, target)
    )
    
    train_op = tf.contrib.layers.optimize_loss(
        
        loss, tf.contrib.framework.get_global_step(), optimizer='Adam',
        learning_rate=0.001)
    
    return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op

# with tf.device('/gpu:0'):
classifier = learn.Estimator(model_fn=my_model, model_dir="model/" + sys.argv[1])

classifier.fit(data, target, steps=700)

print time.ctime()
ct = len(test_data)

y_predicted = [p['class'] for p in classifier.predict(data[:ct], as_iterable=True)]
score = metrics.accuracy_score(target[:ct], y_predicted)

print('Train Accuracy: {0:f}'.format(score))

y_predicted = [p['class'] for p in classifier.predict(test_data, as_iterable=True)]
score = metrics.accuracy_score(test_tgt, y_predicted)

print('Test Accuracy: {0:f}'.format(score))
