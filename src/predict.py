#!/bin/env python
from common import *
from sklearn import metrics
import tensorflow as tf
from mlp_feeder import read_data
from simple import kernel
from jsq_estimator import JSQestimator

if __name__ == "__main__":
    args = getArgs()
    if args.g:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.g
    
    model, idx = args.tgt.split(",")
    model = model + "0" + idx
    
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
    
    fe_version = cfg["fe"]
    if args.ds:
        datafile = "macro/fe/%s/daily/%s.fe" % (fe_version, args.ds)
        fout = "ans/t" + model[1:]
    else:
        datafile = "macro/fe/%s/test" % fe_version
        fout = "ans/" + model
    
    predSet = read_data(datafile)
    
    model_dir = "model/" + model
    
    net = cfg["net"]

    keep_prob = 1.0
    classifier = JSQestimator(model_fn=kernel(net, keep_prob), model_dir=model_dir)
    
    classifier.fit(predSet.fea, np.ones(len(predSet.fea), dtype=np.int), steps=0)
    
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
    
    fout = open(fout, "w")
    for ds in sorted(ans.keys()):
        st = ans[ds]
        st = sorted(st, key=lambda x: x[1], reverse=True)
        st = map(lambda (x, y, z): (x, str(y), str(z)), st)
        st = map(lambda x: "_".join(x), st)
        fout.write(ds + "," + ",".join(st) + "\n")
