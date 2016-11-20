#!/bin/env python
# -*- coding:utf-8 -*-
from common import *
import combine_ans
import gain
import filter_by_rule

def getCbKey(cb):
    return "+".join(sorted(map(os.path.basename, cb)))

def searchCb(cb):
    fout = "log/cb.tmp"
    combine_ans.process(cb, fout)

    filter_by_rule.process(fout, output=False)
    gain50 = gain.process(fout+".filter", 50, output=False)
#    filter_by_rule.process(fout, newSt=True, high=True, st=True, output=False)
#    filter_by_rule.process(fout, newSt=True, high=True, st=True, output=False)
    gain3 = gain.process(fout+".filter", 3, output=False)
#    gain3 = gain.process(fout, 3, output=False)
    
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

def quickSearch(fins, fout, q, kv):
    queue = []
    while fins:
        tmp = []
        for f in fins:
            cb = queue + [f]
            key = getCbKey(cb)
            if key in kv:
                g3, g50 = kv[key]
            else:
                cb, g3, g50 = searchCb(cb)
                fout.write(cb)
                fout.flush()
            if q == "t":
                tmp += [(f, g3)]
            else:
                tmp += [(f, g50)]
        tmp = sorted(tmp, key=lambda (x, y): -y)
        select = tmp[0][0]
        queue += [select]
        print sorted(queue), tmp[0][1]
        fins.remove(select)

def getArgs():
    parser = ArgumentParser(description="Combine")
    parser.add_argument("-t", dest="tgt", required=True,
                        help="target")
    parser.add_argument("-a", dest="a", default="cs_tmp",
                        help="ans")
    parser.add_argument("-q", dest="q", default="",
                        help="quick")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    fins = combine_ans.getInput(args.tgt)
    if args.q == "t":
        logfile = "log/cs_top" 
    elif args.q == "d":
        logfile = "log/cs_daily" 
    else:
        logfile = "log/" + args.a
    print "fin", fins
    print "fout", logfile
    
    try:
        rd = csv.reader(open(logfile))
        kv = dict([("+".join(sorted(r[0].split("+"))), 
                    (float(r[1]), float(r[2]))) for r in rd])
    except:
        kv = {}
    fout = open(logfile, "a")
    if args.q:
        print "quich search"
        quickSearch(fins, fout, args.q, kv)
    else:
        allSearch(fins, fout, kv)

    os.system("rm -f log/cb.tmp")
