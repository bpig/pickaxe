#!/bin/env python
from common import *
from sklearn import metrics
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn
from mlp_feeder import read_data_sets


def pred(classifier, feas, tgts):
    y_predicted = [p['class'] for p in classifier.predict(feas, as_iterable=True)]
    return metrics.accuracy_score(tgts, y_predicted)

def kernel(net, keep_prob):
    def _model(features, target):
        target = tf.one_hot(target, 2, 1, 0)
        
        features = layers.stack(features, layers.fully_connected, net)
        features = layers.dropout(features, keep_prob=keep_prob)

        prediction, loss = tf.contrib.learn.models.logistic_regression(features, target)
    
        train_op = tf.contrib.layers.optimize_loss(
            loss, tf.contrib.framework.get_global_step(), optimizer='Adam',
            learning_rate=0.001)
    
        return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op
    return _model

def getArgs():
    parser = ArgumentParser(description="Predict")
    parser.add_argument("-t", dest="m", 
                        help="model")
    parser.add_argument("-g", dest="g", default="",
                        help="gpu id")
    return parser.parse_args()

if __name__ == "__main__":
    tf.logging.set_verbosity(tf.logging.INFO)
    args = getArgs()
    if args.g:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.g

    model = args.m    
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]

    fe_version = cfg["fe"]

    datafile = "data/fe/%s/train" % fe_version

    idx = int(model[-2:])
    division = cfg["division"][idx]
    data = read_data_sets(datafile, division)

    print "model={m}, data={d}".format(d=datafile, m=model)

    config = learn.estimators.run_config.RunConfig(
        log_device_placement=False, save_summary_steps=100,
        save_checkpoints_secs=600, keep_checkpoint_max=2000)

    model_dir = "model/" + model

    net = cfg["net"]
    keep_prob = cfg["keep_prob"]
    classifier = learn.Estimator(
        config=config, model_fn=kernel(net, keep_prob), model_dir=model_dir)

    batch_step = cfg["batch_step"]
    batch_size = int(data.train.num_examples / batch_step)

    if "epoch" in cfg:
        epochs = cfg["epoch"]
    else:
        epochs = 1

    for epoch in range(epochs):
        for i in range(batch_step):
            batch_x, batch_y = data.train.next_batch(batch_size)
            classifier.fit(batch_x, batch_y, steps=1)
            print time.ctime(), "batch_step", i
    
        # te_acc = pred(classifier, data.test.feas, data.test.tgts)
        # tr_acc = pred(classifier, data.train.feas[:ct], data.train.tgts[:ct])
        # print time.ctime(), "epoch %d, train acc %.6f, test acc %.6f" \
        #     % (epoch, tr_acc, te_acc)

        tr_acc = pred(classifier, data.test.feas, data.test.tgts)
        print
        print time.ctime(), "finish epoch %d, train acc %.6f" % (epoch, tr_acc)
        print







