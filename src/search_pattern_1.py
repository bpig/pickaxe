# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/30"

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

def process(predictFile, stockFile, outfile, date):
    stock = loadFile(stockFile)
    predict = {}
    for k, v in loadFile(predictFile).items():
        v = sorted(v, key=lambda x: float(x[1]), reverse=True)
        predict[k] = v
    res = search(predict, stock, outfile, date)


def search(predict, stock, outfile, date):
    fout = open(outfile, 'w')
    ds = sorted(predict.keys(), key=lambda  x: x)
    if date:
        if date not in ds:
            print ds
            print "ds is not in predict result"
        else:
            ss = ds.index(date)
            ds = ds[ss:]
    for d in ds:
        res = []
        for rec in predict[d]:
            key = rec[0]
            if key not in stock.keys():
                continue
            items = stock[key]
            if d not in items[0]:
                continue
            index = items[0].index(d)
            positive = 0
            for i in range(index, index + 10):
                if i >= len(items[0]):
                    break
                if items[15][i] == '1' or items[16][i] == '1':
                    continue
                es = float(items[8][i]) / float(items[5][i])
                if  es > 1.0 and es < 1.03:
                    positive += 1
                elif es < 1:
                    positive -= 1
            if positive > 7:
                res += [[key, rec[1], rec[2]]]
        if len(res) > 0:
            res = sorted(res, key=lambda x: x[1], reverse=True)
            res = map(lambda x: x[0] + "_" + str(x[1]) + "_" + x[2], res)
            fout.write(d + "," + ",".join(res) + "\n")
            
if __name__ == "__main__":
    predictFile = "test/2016_comb"
    stockFile = "test/2016.ft.2"
    outfile = "test/2016_comb_after_search1"
    process(predictFile, stockFile, outfile, "20161019")