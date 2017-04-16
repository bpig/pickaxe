# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/3/16"

from common import *
from sklearn import metrics
from mlp_feeder import read_predict_sets
from simple import kernel
from jsq_estimator import JSQestimator
import gain
import filter_by_rule

def getCheckPoint(model_dir):
    checkPointFile = model_dir + "/checkpoint"
    if not os.path.exists(checkPointFile + ".bak"):
        subprocess.call("cp %s %s.bak" % (checkPointFile, checkPointFile), shell=True)
    models = filter(lambda _: _.endswith("00001"), os.listdir(model_dir))
    models = map(lambda _: _.split("-")[1], models)
    models = sorted(models, key=lambda x:int(x))
    models = filter(lambda x: x!= "1", models)
    models = models[200:]
    print models
    return models

def setCheckPoint(model_dir, model):
    tmpl = 'model_checkpoint_path: "model.ckpt-%s-?????-of-00001"\n'
    with open(model_dir + "/checkpoint", "w") as fout:
        fout.write(tmpl % model)

def genAns(pp, foutFile, predSet):
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
    
    fout = open(foutFile, "w")
    for ds in sorted(ans.keys()):
        st = ans[ds]
        st = sorted(st, key=lambda x: x[1], reverse=True)
        st = map(lambda (x, y, z): (x, str(y), str(z)), st)
        st = map(lambda x: "_".join(x), st)
        fout.write(ds + "," + ",".join(st) + "\n")

def pred(classifier, feas, tgts):
    y_predicted = [p['class'] for p in classifier.predict(feas, as_iterable=True)]
    y_predicted = np.asarray(y_predicted)
    idx = (y_predicted==1)
    return metrics.accuracy_score(tgts[idx], y_predicted[idx]), len(y_predicted[idx])

def searchModel(model, keys):
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
    
    model_dir = "model/" + model

    fe_version = cfg["fe"]
    datafile = "macro/fe/%s/test" % fe_version

    foutFile = "ans/" + model
    predSet = read_predict_sets(datafile)
    net = cfg["net"]
    keep_prob = 1.0
    
    versions = getCheckPoint(model_dir)
    idx = int(model[-2:])
    division = cfg["division"][idx]        
    tgts = np.asarray(map(lambda x: 0 if x < division else 1, predSet.tgt))

    ans = []
    for version in versions:
        key = model + "," + version
        if key in keys:
            continue
        setCheckPoint(model_dir, version)
        
        classifier = JSQestimator(model_fn=kernel(net, keep_prob), model_dir=model_dir)
        
        classifier.fit(predSet.fea, np.ones(len(predSet.fea), dtype=np.int), steps=0)

        te_acc, l1 = pred(classifier, predSet.fea, tgts)

        pp = classifier.predict(predSet.fea, as_iterable=True)
        f = "log/msearch_ans_" + model[:3]
        genAns(pp, f, predSet)
        filter_by_rule.process(f)
        money = gain.process(f + ".filter", 50, output=False)

        value = "%s,%s,%d,%.5f,%.5f\n" % (model, version, l1, money, te_acc)
        print "==" * 10
        print value,
        print
        ans += [value]
    
    return ans

def getkeys(logfile):
    try:
        return set([_[0] + "," + _[1] for _ in csv.reader(open(logfile)) if _ ])
    except:
        return set()

def getArgs():
    parser = ArgumentParser(description="Ms")
    parser.add_argument("-t", dest="t", required=True,
                        help="model")
    parser.add_argument("-a", dest="a", required=True, default="",
                        help="ans")
    parser.add_argument("-g", dest="g", default="",
                        help="gpu id")
    return parser.parse_args()

def getInput(tgt):
    fins = []
    for value in tgt.split("+"):
        key, subs = value.split(",")
        for n in subs:
            fins += [key + "0" + n]
    return fins

if __name__ == "__main__":
    args = getArgs()
    if args.g:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.g
    model = getInput(args.t)
    print model
    logfile = "log/" + args.a
    keys = getkeys(logfile)

    fout = open(logfile, "a")
    for m in model:
        ans = searchModel(m, keys)
        if not ans:
            continue
        for line in ans:
            fout.write(line)
        fout.write("\n")
        fout.flush()
