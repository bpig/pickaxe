from common import *
import keras.backend as K
from mlp_feeder import read_data
from tk import loadModel

def genAns(pred, fout):
    ans = defaultdict(list)
    for c, p in enumerate(pred):
        if p[0] >= p[1]:
            continue
        prob = p[1]
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

if __name__ == "__main__":
    args = getArgs()
    
    model, idx = args.tgt.split(",")
    model = model + "0" + idx
    
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
    
    fe_version = cfg["fe"]
    if args.ds:
        datafile = "data/fe/%s/daily/%s.fe" % (fe_version, args.ds)
        fout = "ans/t" + model[1:]
    else:
        datafile = "data/fe/%s/test" % fe_version
        fout = "ans/" + model
    
    predSet = read_data(datafile)
    
    model_dir = "model/" + model
    model = loadModel(model_dir)

    pred = model.predict_proba(predSet.fea, batch_size=1024, verbose=1)
    genAns(pred, fout)
    logging.shutdown()
    K.clear_session()
