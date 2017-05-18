from common import *
import keras.backend as K
from feeder import read_data
from train import load_model
from operator import itemgetter


def gen_ans(pred, data, fout):
    mu = 1.03372599616
    delta = 0.059838518055

    tgt = data.tgt * delta + mu
    pred = pred * delta + mu

    pred = pred.reshape(-1)
    tgt = tgt.reshape(-1)

    ans = zip(data.key, pred, tgt)
    ans = sorted(ans, key=itemgetter(1), reverse=True)

    data = defaultdict(list)
    debug = defaultdict(list)
    for ((k, ds), p, t) in ans:
        data[ds] += [k]
        debug[ds] += ["%s_%.3f_%.3f" % (k, p, t)]
    
    pickle.dump(data, open(fout + ".pl", "w"))
    
    fout = open(fout, "w")
    for ds in sorted(data.keys()):
        fout.write(`ds` + "\n")
        fout.write("\n".join(debug[ds][:10]))
        fout.write("\n")

    # fout = open(fout + ".debug", "w")
    # for ds in sorted(data.keys()):
    #     fout.write(`ds` + ",")
    #     fout.write(",".join(data[ds]))
    #     fout.write("\n")


def predict(args):
    makedirs("ans")
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[args.p]
        begin, end = map(int, cfg["test"].split("-"))
    with TimeLog("load data"):
        data = read_data(cfg["data"], begin, end)
    if not args.m:
        args.m = args.p
    model = load_model("model/" + args.m) #, model_file="e3.hdf5")

    pred = model.predict(data.fea, batch_size=1024, verbose=1)
    gen_ans(pred, data, "ans/" + args.m)
    K.clear_session()


if __name__ == "__main__":
    args = get_args()
    predict(args)
