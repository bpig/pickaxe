from common import *
import keras.backend as K
from feeder import read_data
from train import load_model
from operator import itemgetter


def gen_ans(pred, data, fout):
    ans = zip(data.key, pred, data.tgt)
    ans = sorted(ans, key=itemgetter(2), reverse=True)[:10]

    for i in ans:
        print i[0][0], i[0][1], i[1][0], i[2][0]


def predict(args):
    makedirs("ans")
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[args.v]
        begin, end = map(int, cfg["test"].split("-"))
    data = read_data(cfg["data"], begin, end)
    model = load_model("model/" + args.m)

    pred = model.predict(data.fea, batch_size=1024, verbose=1)
    gen_ans(pred, data, "ans/" + args.m)
    K.clear_session()


if __name__ == "__main__":
    args = get_args()
    predict(args)
