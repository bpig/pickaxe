from train import *
from collections import defaultdict

tv = int(sys.argv[1])

def loadStock(filename):
    c = 0
    kv = defaultdict(list)
    dim = 0
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key, dt = l[:pos].split("_")
        l = l[pos+1:]
        # if dt < "20160500":
        #     continue
        items = l.split(",")
        dim = len(items)
        xx = map(float, items)
        x = np.reshape(xx, (dim, 1))
        kv[dt] += [(key, x)]
        c += 1
        if c == tv:
            break
    return kv

def select(money):
    return sorted(money, key=lambda x:-x[1])

def predict(model, kv):
    net = load(model)
    dt = sorted(kv.keys())
    for c, d in enumerate(dt):
        lt = kv[d]
        money = []
        hot = 0
        for key, x in lt:
            yy = net.feedforward(x)
            idx = np.argmax(yy)
            prob = yy[idx][0]
            if idx != 3:
                continue
            if prob >= 0.85:
                hot += 1
                money += [(key, prob)]
        if not money:
            continue

        # if len(money) >= 10:
        skip = ""
        if hot >= 10:
            skip = "skip"
        money = select(money)[:10]
        print d,
        for k, p in money:
            print k, "--", p, "|",
        print skip

    # print sum(v) / len(v), total

if __name__ == "__main__":
    kv = loadStock("2016.p")
    idx = 48
    model = "m22/model_%d" % idx
    predict(model, kv)


