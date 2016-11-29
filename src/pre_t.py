from common import *
from keras.models import model_from_json
import keras.backend as K
from mlp_feeder import read_data

def getArgs():
    parser = ArgumentParser(description="Predict")
    parser.add_argument("-t", dest="m",
                        help="model")
    parser.add_argument("-ds", dest="ds",
                        help="day")
    parser.add_argument("-g", dest="g", default="",
                        help="gpu id")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    if args.g:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.g
    
    model, idx = args.m.split(",")
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
    
    model_path = model_dir + "/model.json"
    with open(model_path, 'r') as f:
        model_json = f.read()
        model = model_from_json(model_json)
    
    weightPath = model_dir + '/weight.hdf5'
    model.load_weights(weightPath)
    
    pred = model.predict_proba(predSet.fea, batch_size=1024, verbose=1)
    
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
    
    logging.shutdown()
    K.clear_session()
