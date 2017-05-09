from common import *
import keras.backend as K
from feeder import read_data
from train import load_model
from operator import itemgetter


def gen_ans(pred, data, fout):
    mu = 1.00086540657
    delta = 0.0320974639281

    tgt = data.tgt * delta + mu
    pred = pred * delta + mu

    pred = pred.reshape(-1)
    tgt = tgt.reshape(-1)

    ans = zip(data.key, pred, tgt)
    ans = sorted(ans, key=itemgetter(1), reverse=True)

    data = defaultdict(list)
    debug = defaultdict(list)
    for ((k, ds), p, t) in ans:
        if p < 1:
            continue
        data[ds] += [k]
        debug[ds] += ["%s_%.2f_%.2f" % (k, p, t)]
    
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
        cfg = yaml.load(fin)[args.v]
        begin, end = map(int, cfg["test"].split("-"))
    with TimeLog("load data"):
        data = read_data(cfg["data"], begin, end)
    model = load_model("model/" + args.m)

    pred = model.predict(data.fea, batch_size=1024, verbose=1)
    gen_ans(pred, data, "ans/" + args.m)
    K.clear_session()


if __name__ == "__main__":
    args = get_args()
    predict(args)
