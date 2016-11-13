# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/13/16"

from common import *

if __name__ == '__main__':
    rd = csv.reader(open(sys.argv[1]))
    t3 = defaultdict(list)
    t50 = defaultdict(list)
    for r in rd:
        if not r:
            continue
        key = r[0]
        name = key + "_" + r[1]
        s3 = float(r[2])
        s50 = float(r[3])
        t3[key] += [(name, s3)]
        t50[key] += [(name, s50)]
    
    for k in t3.keys():
        t3[k] = sorted(t3[k], key=lambda x: -x[1])
        t50[k] = sorted(t50[k], key=lambda x: -x[1])

    print "top 3 select"
    for k in t3.keys():
        print k, t3[k][:5]

    print "top 50 select"
    for k in t50.keys():
        print k, t50[k][:5]
