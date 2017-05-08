from common import *
import keras.backend as K
from feeder import read_data
from train import load_model
from operator import itemgetter

def gen_ans(pred, predSet, fout):
    ans = zip(predSet.key, pred, predSet.tgt)
    ans = sorted(ans, key=itemgetter(2), reverse=True)[:10]

    for i in ans:
        print i[0][0], i[0][1], i[1][0], i[2][0]

    
    # fout = open(fout, "w")
    # for ds in sorted(ans.keys()):
    #     st = ans[ds]
    #     st = sorted(st, key=lambda x: x[1], reverse=True)
    #     st = map(lambda (x, y, z): (x, str(y), str(z)), st)
    #     st = map(lambda x: "_".join(x), st)
    #     fout.write(ds + "," + ",".join(st) + "\n")


def predict(args):
    makedirs("ans")
    datafile = "train_data/"
    fout = "ans/" + args.m
    predSet = read_data(datafile)
    model = load_model("model/" + args.m)

    pred = model.predict(predSet.fea, batch_size=1024, verbose=1)
    gen_ans(pred, predSet, fout)
    K.clear_session()


if __name__ == "__main__":
    args = get_args()
    predict(args)
