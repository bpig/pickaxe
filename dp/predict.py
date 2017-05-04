from common import *
import keras.backend as K
from feeder import read_data
from train import load_model


def gen_ans(pred, predSet, fout):
    ans = defaultdict(list)
    for c, p in enumerate(pred):
        if p[0] >= p[1]:
            continue
        prob = p[1]
        key, date = predSet.key[c].split("_")
        tgt = predSet.tgt[c]
        ans[date] += [(key, prob, tgt)]

    fout = open(fout, "w")
    for ds in sorted(ans.keys()):
        st = ans[ds]
        st = sorted(st, key=lambda x: x[1], reverse=True)
        st = map(lambda (x, y, z): (x, str(y), str(z)), st)
        st = map(lambda x: "_".join(x), st)
        fout.write(ds + "," + ",".join(st) + "\n")


def predict(args):
    datafile = "macro/fe/"
    fout = "ans/" + args.m
    predSet = read_data(datafile)
    model = load_model(args.m + ".hdf5")

    pred = model.predict_proba(predSet.fea, batch_size=1024, verbose=1)
    gen_ans(pred, predSet, fout)
    K.clear_session()


if __name__ == "__main__":
    args = get_args()
    predict(args)
