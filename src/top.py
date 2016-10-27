# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/26"
from common import *

def parseLine(l):
    l = l.strip()
    pos = l.find(",")
    key = l[:pos]
    items = [_.split("_")[0] for _ in l[pos + 1:].split(",")]
    return key, items

if __name__ == "__main__":
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    if len(sys.argv) == 3:
        ct = int(sys.argv[2])
    else:
        ct = 5
    
    fin = "ans/" + cfg["tout"]
    l = next(open(fin))
    key, items = parseLine(l)
    
    print key, ",".join(map(str, items[:ct]))
