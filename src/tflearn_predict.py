from common import *
from sklearn import metrics
import tensorflow as tf
from mlp_feeder import read_predict_sets
from tflearn_simple import my_model
from jsq_estimator import JSQestimator

if __name__ == "__main__":
    # predSet = read_predict_sets("data/20.fe.2016.cmvn.shuf")
    predSet = read_predict_sets("data/15.2016.fe.cmvn")

    model_dir = "model/" + sys.argv[1]

    classifier = JSQestimator(model_fn=my_model, model_dir=model_dir)

    classifier.fit(predSet.fea, predSet.tgt.astype(np.int), steps=0)

    pp = classifier.predict(predSet.fea, as_iterable=True)

    ans = defaultdict(list)

    for c, p in enumerate(pp):
        if p['class'] == 0:
            continue
        prob = p['prob'][1]
        key, date = predSet.key[c].split("_")
        tgt = predSet.tgt[c]
        ans[date] += [(key, prob, tgt)]

    fout = open("2016_b.ans", "w")
    for ds in sorted(ans.keys()):
        st = ans[ds]
        st = sorted(st, key=lambda x:x[1], reverse=True)
        st = map(lambda (x, y, z):(x, str(y), str(z)), st)
        st = map(lambda x:"_".join(x), st)
        fout.write(ds + "," + ",".join(st) + "\n")


