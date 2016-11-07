# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/31/16"

from common import *

if __name__ == '__main__':
    fin = sys.argv[1] # raw/2010_15/ 
    tr = open(sys.argv[2] + ".tr", "w")
    te = open(sys.argv[2] + ".te", "w")

    if len(sys.argv) == 4:
        point = sys.argv[3]
    else:
        point = "20160500"

    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)

    ctr, cte = 0, 0
    for c, l in enumerate(files):
        if "dumper.list" in l:
            continue
        tgt = fin + "/" + l
        ds = l.split("_")[1]

        content = "%s:%s\n" % (l, open(tgt).read())
        if ds < "20101200":
            continue
        if ds < point:
            tr.write(content)
            ctr += 1
        else:
            te.write(content)
            cte += 1

        if c % 10000 == 0:
            print time.ctime(), c
    
    print "tr %d, te %d" % (ctr, cte)
    

