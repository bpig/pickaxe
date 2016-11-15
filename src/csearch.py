# -*- coding:utf-8 -*-
from common import *
import combine_ans
import gain_by_p

def getCbKey(cb):
    return "+".join(map(os.path.basename, cb))

def searchCb(cb):
    fout = "cb.tmp"
    combine_ans.process(cb, fout)
    gain50 = gain_by_p.process(fout, 50, output=False)
    gain3 = gain_by_p.process(fout, 3, output=False)

    cb = getCbKey(cb)
    value = "%s,%.5f,%.5f\n" % (cb, gain3, gain50)
    print "==" * 10
    print value,
    print
    return value

if __name__ == "__main__":
    key = sys.argv[1]
    with open("conf/combine.yaml") as fin:
        subs = str(yaml.load(fin)[key])
    fins = map(lambda x: ("ans/v%s0" % key[:2]) + x, subs)

    logfile = "log/cb_" + key
    try:
        rd = csv.reader(open(logfile))
        keys = set([r[0] for r in rd])
    except:
        keys = set()

    fout = open(logfile, "a")
    
    for i in range(2, len(fins) + 1):
        for cb in itertools.combinations(fins, i):
            print cb
            if getCbKey(cb) in keys:
                continue
            cb = searchCb(cb)
            fout.write(cb)
            fout.flush()
    os.system("rm -f cb.tmp")
