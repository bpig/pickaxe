# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/26"
from common import *

def parseLine(l):
    l = l.strip()
    pos = l.find(",")
    key = l[:pos]
    items = [_.split("_")[0] for _ in l[pos + 1:].split(",")]
    weight = [sigmoid(_.split("_")[1]) for _ in l[pos + 1:].split(",")]
    return key, items, weight

def sigmoid(x):
    #return math.log(float(x), 2)
    return float(x)

if __name__ == "__main__":
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    if len(sys.argv) == 3:
        ct = int(sys.argv[2])
    else:
        ct = 50
    
    fin = "ans/" + cfg["tout"]
    l = next(open(fin))
    key, items, weight = parseLine(l)
    key = key[:ct]
    items = items[:ct]
    weight = weight[:ct]
    weight = np.asarray(weight)

    wmin = weight.min()
    wmax = weight.max()
    weight = (weight - wmin) / (wmax - wmin)
    weight[0] -= 0.00001
    weight[-1] = 0.00001
    print ",".join(["", "code", "weight"])
    for i in range(ct):
        print ",".join(map(str, (i+1, items[i], weight[i])))



