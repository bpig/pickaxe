from __future__ import print_function

import mlp_feeder
import os
import time
from collections import defaultdict
#mnist = mlp_feeder.read_data_sets("data/20.fe.2016.cmvn.shuf")
print(time.ctime())
mnist = mlp_feeder.read_predict_sets("data/20.fe.2016.cmvn.shuf", None)
print(time.ctime())

model_path = "rr/2015"

import tensorflow as tf

# Network Parameters
n_hidden_1 = 256  # 1st layer number of features
n_hidden_2 = 256  # 2nd layer number of features
n_hidden_3 = 8  # 3nd layer number of features
n_input = 1673  # MNIST data input (img shape: 28*28)
n_classes = 1  # MNIST total classes (0-9 digits)

# tf Graph input
x = tf.placeholder("float", [None, n_input])
y = tf.placeholder("float", [None, n_classes])

# Create model
def multilayer_perceptron(x, weights, biases):
    # Hidden layer with RELU activation
    layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
    layer_1 = tf.nn.relu(layer_1)
    # Hidden layer with RELU activation
    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    layer_2 = tf.nn.relu(layer_2)
    # Hidden layer with RELU activation
    # layer_3 = tf.add(tf.matmul(layer_2, weights['h3']), biases['b3'])
    # layer_3 = tf.nn.relu(layer_3)
    # Output layer with linear activation
    out_layer = tf.matmul(layer_2, weights['out']) + biases['out']
    return out_layer

# Store layers weight & bias
weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'b3': tf.Variable(tf.random_normal([n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

# Construct model
pred = multilayer_perceptron(x, weights, biases)


# Initializing the variables
init = tf.initialize_all_variables()

saver = tf.train.Saver(max_to_keep=200)


idx = 85
# Launch the graph
with tf.Session() as sess:
    sess.run(init)

    suffix = "." + str(idx)
    if os.path.exists(model_path + suffix):
        saver.restore(sess, model_path + suffix)
        print("Model restored from file")

    predict = sess.run(pred, feed_dict={x: mnist.fea})

    pp = zip(mnist.key, predict, mnist.tgt)
    pp = sorted(pp, key=lambda x:x[1], reverse=True)
    pp = filter(lambda x:x[1] <= 1.0 and x[1] >= 0.0, pp)

    fout = open("hihihi.debug", "w")
    for p in pp:
        fout.write("%s,%.4f,%.4f\n" % p)
    
    pp = filter(lambda x:x[1] >= 0.52, pp)

    kv = defaultdict(list)
    for (key,prob,t) in pp:
        k, ds = key.split("_")
        kv[ds] += [(k, prob, t)]

    fout = open("2016.ans.reg", "w")
    for ds in sorted(kv.keys()):
        lt = kv[ds]
        lt = sorted(lt, key=lambda x:x[1], reverse=True)
        lt = map(lambda x:"%s_%f_%f" % x ,lt)
        fout.write(ds + "," + ",".join(lt) + "\n")
    
