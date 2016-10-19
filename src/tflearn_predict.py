from sklearn import metrics
import numpy as np
import random
import time
import sys
from collections import defaultdict
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn

# tf.logging.set_verbosity(tf.logging.INFO)

def loadFea(filename):
    keys = []
    values = []
    tgts = []
    for c, l in enumerate(open(filename)):
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
        if c == 1000000:
            break
    return keys, np.array(values), np.array(tgts)

print time.ctime()

keys, values, tgts = loadFea("data/20.fe.2016.cmvn")
print values.shape
print tgts.shape
print time.ctime()

def my_model(features, target):
    target = tf.one_hot(target, 2, 1, 0)
    features = layers.stack(features, layers.fully_connected, [512, 128, 8])
    prediction, loss = (
        tf.contrib.learn.models.logistic_regression(features, target)
    )
    
    train_op = tf.contrib.layers.optimize_loss(
        loss, tf.contrib.framework.get_global_step(), optimizer='Adam',
        learning_rate=0.001)
    return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op


classifier = learn.Estimator(model_fn=my_model, model_dir="model/2016_07_600")

classifier.fit(values, tgts.astype(np.int), steps=0)

pp =  classifier.predict(values, as_iterable=True)


ans = defaultdict(list)

for c, p in enumerate(pp):
    if p['class'] == 0:
        continue
    prob = p['prob'][1]
    key, date = keys[c].split("_")
    tgt = tgts[c]
    ans[date] += [(key, prob, tgt)]

    #print keys[c], p['class'], p['prob'], tgts[c]

fout = open("2016_89.ans", "w")
for ds in sorted(ans.keys()):
    st = ans[ds]
    st = sorted(st, key=lambda x:x[1], reverse=True)
    st = map(lambda (x, y, z):(x, str(y), str(z)), st)
    st = map(lambda x:"_".join(x), st)
    fout.write(ds + "," + ",".join(st) + "\n")


# y_predicted = [p['class'] for p in pp]

# print y_predicted
# score = metrics.accuracy_score(test_tgt, y_predicted)

# print('Accuracy: {0:f}'.format(score))
