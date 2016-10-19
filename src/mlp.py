from __future__ import print_function

import mlp_feeder
import os
import time

#mnist = mlp_feeder.read_data_sets("data/20.fe.2016.cmvn.shuf")
print(time.ctime())
mnist = mlp_feeder.read_data_sets("data/20.fe.2015.cmvn.shuf", None)
print(time.ctime())
model_path = "reg/2015"
import tensorflow as tf

# Parameters

learning_rate = 0.0001
training_epochs = 200
batch_size = 128
display_step = 10

# Network Parameters
n_hidden_1 = 512  # 1st layer number of features
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
    layer_3 = tf.add(tf.matmul(layer_2, weights['h3']), biases['b3'])
    layer_3 = tf.nn.relu(layer_3)
    # Output layer with linear activation
    out_layer = tf.matmul(layer_3, weights['out']) + biases['out']
    return out_layer

# Store layers weight & bias
weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_hidden_3, n_classes]))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'b3': tf.Variable(tf.random_normal([n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

# Construct model
pred = multilayer_perceptron(x, weights, biases)

# Define loss and optimizer
#cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(pred, y))
cost = tf.reduce_mean(tf.pow(pred - y, 2))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Initializing the variables
init = tf.initialize_all_variables()


saver = tf.train.Saver()

# Launch the graph
with tf.Session() as sess:
    sess.run(init)

    if os.path.exists(model_path):
        saver.restore(sess, model_path)
        print("Model restored from file")

    # Training cycle
    for epoch in range(training_epochs):
        avg_cost = 0.
        total_batch = int(mnist.train.num_examples / batch_size)
        # Loop over all batches
        for i in range(total_batch):
            batch_x, batch_y = mnist.train.next_batch(batch_size)
            # Run optimization op (backprop) and cost op (to get loss value)
            _, c = sess.run([optimizer, cost], feed_dict={x: batch_x,
                                                          y: batch_y})
            # Compute average loss
            avg_cost += c / total_batch
        # Display logs per epoch step
        if epoch % display_step == 0:
            print(time.ctime(), "Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))
    print("Optimization Finished!")

    save_path = saver.save(sess, model_path)
    print("Model saved in file: %s" % save_path)

    # Test model
    # correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    # Calculate accuracy
    # accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    # print("Accuracy:", accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))
    # predict = pred.eval({x: mnist.test.images})
    predict, cost = sess.run([pred, cost], feed_dict={x: mnist.test.feas,
                                                      y: mnist.test.tgts})
    print(cost)
    pp = zip(predict, mnist.test.tgts)
    pp = sorted(pp, key=lambda x:x[0], reverse=True)
    fout = open("hihihi", "w")
    total = 0
    for c, p in enumerate(pp):
        total += p[1]
        fout.write("%.2f,%.2f - %.2f\n" % (p[0], p[1], total / (c+1)))
    
