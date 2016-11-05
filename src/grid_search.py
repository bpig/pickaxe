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

def train(data, net, keep_prob):
    config = learn.estimators.run_config.RunConfig(
        log_device_placement=False, save_summary_steps=100,
        save_checkpoints_secs=6000, keep_checkpoint_max=2000)

    model_dir = "model/tmp"
    os.system("rm -rf %s" % model_dir)
    print "xxx, try", net, keep_prob
    classifier = learn.Estimator(
        config=config, model_fn=kernel(net, keep_prob), model_dir=model_dir)

    bs = int(data.train.num_examples / 30)
    print "small example:", bs, data.test.num_examples

    batch_x, batch_y = data.train.next_batch(bs)
    for i in range(8):
        classifier.fit(batch_x, batch_y, steps=100)
    
        te_acc = pred(classifier, data.test.feas[:bs], data.test.tgts[:bs])
        tr_acc = pred(classifier, batch_x, batch_y)
        print
        print "xxx, finish epoch %d, train acc %.6f, test acc %.6f" \
            % (i, tr_acc, te_acc)
        print

if __name__ == "__main__":
    tf.logging.set_verbosity(tf.logging.INFO)
    model = sys.argv[1]
    #net = sys.argv[2]
    net = "net"

    with open("conf/model.yaml") as fin:
        model_cfg = yaml.load(fin)[model]
        data = "data/" + model_cfg["data"]
        data = read_data_sets(data)

    with open("conf/net.yaml") as fin:
        cfg = yaml.load(fin)
        
    for net in cfg[net]:
        for prob in [0.2, 0.3, 0.4]:
            train(data, net, prob)
