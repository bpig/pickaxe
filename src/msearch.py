# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/3/16"

from common import *
from mlp_feeder import read_predict_sets
from simple import kernel
from jsq_estimator import JSQestimator
import gain

def getCheckPoint(model_dir):
    checkPointFile = model_dir + "/checkpoint"
    if not os.path.exists(checkPointFile + ".bak"):
        subprocess.call("cp %s %s.bak" % (checkPointFile, checkPointFile), shell=True)
    models = filter(lambda _: _.endswith("00001"), os.listdir(model_dir))
    models = map(lambda _: _.split("-")[1], models)
    models = sorted(models, key=lambda x:int(x))
    models = filter(lambda x: x!= "1", models)
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

def searchModel(model, keys):
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
    
    model_dir = "model/" + model

    fe_version = cfg["fe"]
    datafile = "data/fe/%s/test" % fe_version    

    foutFile = "ans/" + model
    predSet = read_predict_sets(datafile, {})
    net = cfg["net"]
    keep_prob = 1.0
    
    versions = getCheckPoint(model_dir)

    ans = []
    for version in versions:
        key = model + "," + version
        if key in keys:
            continue
        setCheckPoint(model_dir, version)
        
        classifier = JSQestimator(model_fn=kernel(net, keep_prob), model_dir=model_dir)
        
        classifier.fit(predSet.fea, predSet.tgt.astype(np.int), steps=0)
        
        pp = classifier.predict(predSet.fea, as_iterable=True)
        
        genAns(pp, foutFile, predSet)

        gain50 = gain.process(foutFile, 50, output=False)
        gain3 = gain.process(foutFile, 3, output=False)

        value = "%s,%s,%.5f,%.5f\n" % (model, version, gain3, gain50)
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
