# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/31/16"

from common import *

if __name__ == '__main__':
    model = sys.argv[1]
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[model]

    fin = cfg["raw_fe"]
    tgt = "data/fe/%s/" % model

    os.system("mkdir -p %s" % tgt)
    tr = open(tgt + "train", "w")
    te = open(tgt + "test", "w")

    tr_begin = int(cfg["train_begin"])
    tr_end = int(cfg["train_end"])

    print "model {m}, train {tb} - {te}, test {te} - now".format(m=model, tb=tr_begin, te=tr_end)

    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)

    cf, ctr, cte = 0, 0
    for c, l in enumerate(files):
        if "dumper.list" in l:
            continue
        tgt = fin + "/" + l
        ds = int(l.split("_")[1])

        if ds < tr_begin:
            cf += 1
            continue

        content = "%s:%s\n" % (l, open(tgt).read())
        if ds < tr_end:
            tr.write(content)
            ctr += 1
        else:
            te.write(content)
            cte += 1

        if c % 10000 == 0:
            print time.ctime(), c
    
    print "cf %d, tr %d, te %d" % (cf, ctr, cte)
    

