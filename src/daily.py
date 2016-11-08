# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/26"
from common import *
import filter_by_rule

def loadFile(fin):
    kv = {}
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        pos = l.find(",")
        key = l[:pos]
        items = l[pos + 1:].split(",")
        items = map(lambda x: x.split("_"), items)
        kv[key] = items
    return kv

def parseLine(l):
    l = l.strip()
    pos = l.find(",")
    key = l[:pos]
    items = [_.split("_")[0] for _ in l[pos + 1:].split(",")]
    weight = [float(_.split("_")[1]) for _ in l[pos + 1:].split(",")]
    return key, items, weight

if __name__ == "__main__":
    fin = "ans/" + sys.argv[1]
    
    filter_by_rule.process(fin, output=False)
    
    if len(sys.argv) == 3:
        ct = int(sys.argv[2])
    else:
        ct = 100
    
    l = next(open(fin + ".filter"))
    key, items, weight = parseLine(l)
    
    items = items[:ct]
    weight = weight[:ct]
    weight = np.asarray(weight)
    
    wmin = weight.min()
    wmax = weight.max()
    weight = (weight - wmin) / (wmax - wmin)
    weight[0] -= 0.00001
    weight[-1] = 0.00001

    if ct == 100:
        point = 33
        i1 = list(items[:point])
        random.shuffle(i1)
        items = i1 + items[point:]

    print ",".join(["", "code", "weight"])
    for i in range(ct):
        print ",".join(map(str, (i + 1, items[i], weight[i])))
        
        # print "stop", stop, "one", one, "new", n
