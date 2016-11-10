# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/26"
from common import *
import filter_by_rule

def parseLine(l):
    l = l.strip()
    pos = l.find(",")
    key = l[:pos]
    items = [_.split("_")[0] for _ in l[pos + 1:].split(",")]
    return key, items

if __name__ == "__main__":
    fin = "ans/" + sys.argv[1]
    # filter_by_rule.process(fin)
    # fin = fin + ".filter"
    
    if len(sys.argv) == 3:
        ct = int(sys.argv[2])
    else:
        ct = 6
    
    for l in open(fin):
        key, items = parseLine(l)
        print key, " ".join(map(str, items[:ct]))
