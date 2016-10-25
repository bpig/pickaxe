from common import *
from sklearn import metrics
import tensorflow as tf
from mlp_feeder import read_predict_sets
from tflearn_simple import kernel
from jsq_estimator import JSQestimator

if __name__ == "__main__":
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]

    datafile = "data/" + cfg["pdata"]
    if "pcache" in cfg:
        predSet = read_predict_sets(datafile, cfg["pcache"])
    else:
        predSet = read_predict_sets(datafile)

    model_dir = "model/" + cfg["model"]

    net = cfg["net"]
    keep_prob = cfg["keep_prob"]
    classifier = JSQestimator(model_fn=kernel(net, keep_prob), model_dir=model_dir)

    print predSet.fea.dtype
    classifier.fit(predSet.fea, predSet.tgt.astype(np.int), steps=0)

    pp = classifier.predict(predSet.fea, as_iterable=True)

    ans = defaultdict(list)

    for c, p in enumerate(pp):
        if p['class'] == 0:
            continue
        prob = p['prob'][1]
        if "_" in predSet.key[c]:
            key, date = predSet.key[c].split("_")
        else:
            date = predSet.key[c]
            key = "gb"
        tgt = predSet.tgt[c]
        ans[date] += [(key, prob, tgt)]

    fout = "ans/" + cfg["pout"]
    fout = open(fout, "w")
    for ds in sorted(ans.keys()):
        st = ans[ds]
        st = sorted(st, key=lambda x:x[1], reverse=True)
        st = map(lambda (x, y, z):(x, str(y), str(z)), st)
        st = map(lambda x:"_".join(x), st)
        fout.write(ds + "," + ",".join(st) + "\n")


