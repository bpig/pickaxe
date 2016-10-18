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
        tgts += [int(tgt)]

    return keys, np.array(values), np.array(tgts)

print time.ctime()

keys, values, tgts = loadFea("data/fe.3")
print values.shape
print tgts.shape
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


#classifier = learn.Estimator(model_fn=my_model, model_dir="model/" + sys.argv[1])
# classifier = learn.Estimator(model_fn=my_model, model_dir="model/m0.001")
classifier = learn.Estimator(model_fn=my_model, model_dir="model/111")

classifier.fit(values, tgts, steps=0)

pp =  classifier.predict(values, as_iterable=True)
print list(pp)

# y_predicted = [p['class'] for p in pp]

# print y_predicted
# score = metrics.accuracy_score(test_tgt, y_predicted)

# print('Accuracy: {0:f}'.format(score))
