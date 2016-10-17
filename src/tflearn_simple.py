from sklearn import metrics
import numpy as np
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn

def tgtMap(tgt):
    return 0 if tgt < 1.102 else 1

def loadFea(filename):
    datas = []
    tgts = []
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        # key = l[:pos]
        value = l[pos + 1:].split(",")
        tgt = tgtMap(float(value[-1]))
        value = np.asarray(value[:-1]).astype(np.float32)
        
        datas += [value]
        tgts += [tgt]
    
    datas = np.array(datas)
    tgts = np.array(tgts)
    return datas, tgts

data, target = loadFea("../data/fe_20150907.cmvn")

def my_model(features, target):
    """DNN with three hidden layers, and dropout of 0.1 probability."""
    # Convert the target to a one-hot tensor of shape (length of features, 3) and
    # with a on-value of 1 for each one-hot vector of length 3.
    target = tf.one_hot(target, 2, 1, 0)
    
    # Create three fully connected layers respectively of size 10, 20, and 10 with
    # each layer having a dropout probability of 0.1.
    features = layers.stack(features, layers.fully_connected, [1000, 200, 20])
    
    # Create two tensors respectively for prediction and loss.
    prediction, loss = (
        tf.contrib.learn.models.logistic_regression(features, target)
    )
    
    # Create a tensor for training op.
    train_op = tf.contrib.layers.optimize_loss(
        loss, tf.contrib.framework.get_global_step(), optimizer='Adagrad',
        learning_rate=0.1)
    
    return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op

classifier = learn.Estimator(model_fn=my_model)
print data.shape
print target.shape
print target[0]

classifier.fit(data, target, steps=2000)

y_predicted = [p['class'] for p in classifier.predict(data, as_iterable=True)]

score = metrics.accuracy_score(target, y_predicted)

print('Accuracy: {0:f}'.format(score))
