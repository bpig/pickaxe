# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/31/16"

from common import *

if __name__ == '__main__':
    fin = sys.argv[1]
    fout = open(sys.argv[2], "w")

    files = os.listdir(fin)
    files = sorted(files)
    print "total %d files" % len(files)

    for c, l in enumerate(files):
        if "dumper.list" in l:
            continue
        tgt = fin + "/" + l
        fout.write(l)
        fout.write(":")
        fout.write(open(tgt).read())
        fout.write("\n")
        if c % 10000 == 0:
            print time.ctime(), c
    

