# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/2/16"

from common import *



def parseLine(l):
    l = l.strip()
    pos = l.find(",")
    key = l[:pos]
    items = [_.split("_")[0] for _ in l[pos + 1:].split(",")]
    weight = [float(_.split("_")[1]) for _ in l[pos + 1:].split(",")]
    return key, items, weight

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
    print key
    stock = loadFile("data/2010/2016.ft")
    aux = loadFile("data/2010/2016.ft.aux")
    st2016 = set(map(str.strip, open("data/2016.st")))
    
    ii = []
    stop = 0
    one = 0
    n = 0
    for i in range(len(items)):
        if len(ii) == ct:
            break
        item = items[i]
        if item in st2016:
            print "st", item
            continue
        idx = stock[item][0].index(key)
        if stock[item][15][idx] == '1':
            print "stop", item
            stop += 1
            continue
        
        if stock[item][6][idx] == stock[item][7][idx] \
                and float(stock[item][6][idx]) / float(stock[item][4][idx]) > 1.09:
            print "---", item
            one += 1
            continue
        
        if int(aux[item][1][idx]) <= 120:
            print "new", item, aux[item][1][idx]
            n += 1
            continue
        
        ii += [item]
    
    ct = len(ii)
    print "total", ct
    weight = weight[:len(ii)]
    weight = np.asarray(weight)
    
    wmin = weight.min()
    wmax = weight.max()
    weight = (weight - wmin) / (wmax - wmin)
    weight[0] -= 0.00001
    weight[-1] = 0.00001
    print ",".join(["", "code", "weight"])
    for i in range(ct):
        print ",".join(map(str, (i+1, ii[i], weight[i])))
    
    print "stop", stop, "one", one, "new", n
