#!/bin/env python
from common import *
from sklearn import metrics
import tensorflow as tf
import tensorflow.contrib.layers.python.layers as layers
import tensorflow.contrib.learn.python.learn as learn
from mlp_feeder import read_data_sets
from simple import kernel

def pred(classifier, feas, tgts):
    y_predicted = [p['class'] for p in classifier.predict(feas, as_iterable=True)]
    return metrics.accuracy_score(tgts, y_predicted)

def train(data, net, keep_prob, model):
    logfile = "log/gs_%s" % model
    fout = open(logfile, "a")
    config = learn.estimators.run_config.RunConfig(
        log_device_placement=False, save_summary_steps=100,
        save_checkpoints_secs=6000, keep_checkpoint_max=2000)

    model_dir = "model/tmp"
    os.system("rm -rf %s" % model_dir)
    print "try", net, keep_prob
    fout.write("try [%s] %.3f\n" % (",".join(map(str, net)), keep_prob))
    classifier = learn.Estimator(
        config=config, model_fn=kernel(net, keep_prob), model_dir=model_dir)

    bs = int(data.train.num_examples / 30)
    print "small example:", bs, data.test.num_examples

    batch_x, batch_y = data.train.next_batch(bs)
    for i in range(10):
        classifier.fit(batch_x, batch_y, steps=100)
    
        te_acc = pred(classifier, data.test.feas[:bs], data.test.tgts[:bs])
        tr_acc = pred(classifier, batch_x, batch_y)
        print
        print "epoch %d, train acc %.6f, test acc %.6f" % (i, tr_acc, te_acc)
        fout.write("epoch %d, train acc %.6f, test acc %.6f\n" % (i, tr_acc, te_acc))
        print
        fout.flush()

if __name__ == "__main__":
    tf.logging.set_verbosity(tf.logging.INFO)
    model = sys.argv[1]
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
        fe_version = cfg["fe"]
        datafile = "data/fe/%s/train" % fe_version
        data = read_data_sets(datafile, 1.01)

    with open("conf/net.yaml") as fin:
        nets = yaml.load(fin)["net"]
        
    for net in nets:
        for prob in [0.2, 0.3, 0.4]:
            train(data, net, prob, model)
