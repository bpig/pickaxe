from train import *
from collections import defaultdict

tv = int(sys.argv[1])

def loadStock(filename):
    c = 0
    kv = defaultdict(list)
    dim = 0
    ct = [0] * 4
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        key, dt = l[:pos].split("_")
        l = l[pos + 1:]
        if dt < "20160800":
            continue
        items = l.split(",")
        dim = len(items) - 1
        xx = map(float, items[:-1])
        x = np.reshape(xx, (dim, 1))
        yy = float(items[-1])
        y = vectorized_result(yy)
        ct[np.argmax(y)] += 1
        kv[dt] += [(key, x, yy)]
        c += 1
        if c == tv:
            break
    print ct
    return kv

def select(money):
    return sorted(money, key=lambda x: -x[1])

def check(model, kv, output=False):
    net = load(model)
    dt = sorted(kv.keys())
    total = [0.5, 0.5]
    st = 60
    
    ct = 0.0
    c3 = 0.0
    
    for c, d in enumerate(dt):
        lt = kv[d]
        money = []
        hot = 0
        for key, x, y in lt:
            yy = net.feedforward(x)
            idx = np.argmax(yy)
            prob = yy[idx][0]
            if idx != 3:
                continue
            if y >= 1.002:
                c3 += 1
            ct += 1
            # if prob >= 0.85:
            #     hot += 1
            money += [(key, prob, y)]
        if not money:
            continue
        # print money
        # if len(money) >= 10:
        # if hot >= 10:
        #     money = [("skip", 1.0, 1.0)]
        money = select(money)[:5]
        e = 0.0
        for k, p, m in money:
            e += m
        e /= len(money)
        e -= 0.0015
        idx = c % 2
        total[idx] *= e
        if output:
            print d, "%.3f" % sum(total), "[%.3f, %.3f]" % tuple(total), len(money), "%.3f" % e, ":",
            for c, (k, p, m) in enumerate(money):
                print k, "-- %.3f" % p, "(%.3f)" % m,
                if c != len(money) - 1:
                    print "|",
            # print c3 / ct
            print "\n"
    # print sum(v) / len(v), total
    return total

if __name__ == "__main__":
    kv = loadStock("2016.test")
    s = int(sys.argv[2])
    e = int(sys.argv[3])
    output = sys.argv[4] == 'o'
    for idx in range(s, e):
        print "======"
        model = "m56a/model_%d" % idx
        total = check(model, kv, output)
        print "idx %d summary:" % idx, sum(total), total
