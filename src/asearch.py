# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/13/16"

from common import *

def printDict(kv):
    for k in sorted(kv.keys()):
        print k, 
        for n, s in kv[k][-5:][::-1]:
            n = "%4s" % n
            print n + "_" + "%.4f" % s,
        print 


if __name__ == '__main__':
    rd = csv.reader(open(sys.argv[1]))
    t3 = defaultdict(list)
    t50 = defaultdict(list)
    for r in rd:
        if not r:
            continue
        key = "cb"
        name = r[0]
        s3 = float(r[-2])
        s50 = float(r[-1])
        t3[key] += [(name, s3)]
        t50[key] += [(name, s50)]

    print "last 3 select"
    printDict(t3)
    print "last 50 select"
    printDict(t50)

    
    for k in sorted(t3.keys()):
        t3[k] = sorted(t3[k], key=lambda x: x[1])
        t50[k] = sorted(t50[k], key=lambda x: x[1])

    print "top 3 select"
    printDict(t3)
    print "top 50 select"
    printDict(t50)
