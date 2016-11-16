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

def getArgs():
    parser = ArgumentParser(description="Gain")
    parser.add_argument("-t", dest="tgt", required=True,
                        help="target")
    parser.add_argument("-f", dest="f", action="store_true", default=False,
                        help="filter")
    parser.add_argument("-c", dest="c", default=6, type=int, 
                        help="cal count")
    parser.add_argument("-d", dest="d", action="store_true", default=False,
                        help="direct, no filter")
    parser.add_argument("-hi", dest="h", action="store_true", default=False,
                        help="high line ok")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    fin = "ans/" + args.tgt
    if args.f:
        filter_by_rule.process(fin)
        fin = fin + ".filter"
    
    for l in open(fin):
        key, items = parseLine(l)
        seq = " "
        if args.c > 10:
            seq = "\n"
        print key, seq.join(map(str, items[:args.c]))
