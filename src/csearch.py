#!/bin/env python
# -*- coding:utf-8 -*-
from common import *
import combine_ans
import gain

def getCbKey(cb):
    return "+".join(map(os.path.basename, cb))

def searchCb(cb):
    fout = "cb.tmp"
    combine_ans.process(cb, fout)
    gain50 = gain.process(fout, 50, output=False)
    gain3 = gain.process(fout, 3, output=False)
    
    cb = getCbKey(cb)
    value = "%s,%.5f,%.5f\n" % (cb, gain3, gain50)
    print "==" * 10
    print value,
    print
    return value, gain3, gain50

def allSearch(fins, fout):
    for i in range(1, len(fins) + 1):
        for cb in itertools.combinations(fins, i):
            print cb
            if getCbKey(cb) in keys:
                continue
            cb, _, _ = searchCb(cb)
            fout.write(cb)
            fout.flush()
    os.system("rm -f cb.tmp")

def quickSearch(fins, fout, q):
    queue = []
    while fins:
        tmp = []
        for f in fins:
            cb = queue + [f]
            _, g3, g50 = searchCb(cb)
            if q == "t":
                tmp += [(f, g3)]
            else:
                tmp += [(f, g50)]
        tmp = sorted(tmp, key=lambda (x, y): -y)
        select = tmp[0][0]
        queue += [select]
        print queue, tmp[0][1]
        fins.remove(select)

def getArgs():
    parser = ArgumentParser(description="Combine")
    parser.add_argument("-t", dest="tgt", require=True,
                        help="target")
    parser.add_argument("-a", dest="a", default="cs_tmp",
                        help="ans")
    parser.add_argument("-q", dest="q", default="",
                        help="quick")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    fins = combine_ans.getInput(args.tgt)
    logfile = "log/" + args.a
    print "fin", fins
    print "fout", logfile
    
    try:
        rd = csv.reader(open(logfile))
        keys = set([r[0] for r in rd])
    except:
        keys = set()
    fout = open(logfile, "a")
    if args.q:
        quickSearch(fins, fout, args.q)
    else:
        allSearch(fins, fout)
