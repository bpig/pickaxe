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
    gain50 = gain.process(fout + ".filter", 50, output=False)
    
    cb = getCbKey(cb)
    value = "%s,%.5f\n" % (cb, gain50)
    print "==" * 10
    print value,
    print
    return value, gain50

def allSearch(fins, fout, kv):
    for i in range(1, len(fins) + 1):
        for cb in itertools.combinations(fins, i):
            print cb
            if getCbKey(cb) in kv:
                continue
            cb,  _ = searchCb(cb)
            fout.write(cb)
            fout.flush()

def trans2tgt(queue):
    kv = defaultdict(str)
    for t in sorted(queue):
        t = t.replace("ans/", "")
        key = t[:3]
        idx = t[4:]
        kv[key] += idx
    ans = [k + "," + kv[k] for k in sorted(kv.keys())]
    return "+".join(ans)

def quickSearch(fins, fout, q, kv):
    queue = []
    while fins:
        tmp = []
        for f in fins:
            cb = queue + [f]
            key = getCbKey(cb)
            if key in kv:
                g50 = kv[key]
            else:
                cb, g50 = searchCb(cb)
                fout.write(cb)
                fout.flush()
            tmp += [(f, g50)]
        tmp = sorted(tmp, key=lambda (x, y): -y)
        select = tmp[0][0]
        queue += [select]
        #print sorted(queue), tmp[0][1]
        print trans2tgt(queue), tmp[0][1]
        fins.remove(select)

if __name__ == "__main__":
    args = getArgs()
    fins = combine_ans.getInput(args.tgt)
    if args.q:
        logfile = "log/cs_daily_g50"
    else:
        logfile = "log/cs_all_g50"
    print "fin", fins
    print "fout", logfile
    
    try:
        rd = csv.reader(open(logfile))
        kv = dict([(r[0], float(r[1])) for r in rd])
    except:
        kv = {}
    fout = open(logfile, "a")
    if args.q:
        print "quich search"
        quickSearch(fins, fout, args.q, kv)
    else:
        print "all search"
        allSearch(fins, fout, kv)
    
    os.system("rm -f log/cb.tmp")
