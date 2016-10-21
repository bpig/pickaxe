from common import *
from sklearn import metrics
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn
from mlp_feeder import read_data_sets

def pred(classifier, feas, tgts):
    y_predicted = [p['class'] for p in classifier.predict(feas, as_iterable=True)]
    return metrics.accuracy_score(tgts, y_predicted)

def my_model(features, target):
    """DNN with three hidden layers, and dropout of 0.1 probability."""
    target = tf.one_hot(target, 2, 1, 0)
    
    features = layers.stack(features, layers.fully_connected, [512, 512, 512])

    features = layers.dropout(features, keep_prob=0.2)

    # features = layers.layer_norm(features)

    prediction, loss = tf.contrib.learn.models.logistic_regression(features, target)
    
    train_op = tf.contrib.layers.optimize_loss(
        loss, tf.contrib.framework.get_global_step(), optimizer='Adam',
        learning_rate=0.001)
    
    return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op

if __name__ == "__main__":
    tf.logging.set_verbosity(tf.logging.INFO)

    #data = read_data_sets("data/20.fe.cmvn.shuf", None)
    data = read_data_sets("data/15.fe.cmvn", None)

    config = learn.estimators.run_config.RunConfig(
        log_device_placement=False, save_summary_steps=100,
        save_checkpoints_secs=600, keep_checkpoint_max=2000)

    classifier = learn.Estimator(
        config=config, model_fn=my_model, model_dir="model/" + sys.argv[1])

    batch_step = 3
    batch_size = int(data.train.num_examples / batch_step)

    for epoch in range(1):
        for i in range(int(batch_step)):
            batch_x, batch_y = data.train.next_batch(batch_size)
            #classifier.partial_fit(batch_x, batch_y)
            classifier.fit(batch_x, batch_y, steps=100)
            print time.ctime(), "batch_step", i
    
        te_acc = pred(classifier, data.test.feas, data.test.tgts)
        ct = data.test.num_examples
        tr_acc = pred(classifier, data.train.feas[:ct], data.train.tgts[:ct])
        print time.ctime(), "finish epoch %d, train acc %.6f, test acc %.6f" \
            % (epoch, tr_acc, te_acc)






