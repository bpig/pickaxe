# -*- coding:utf-8 -*-
from common import *
import combine_ans
import gain_by_p

def searchCb(cb):
    fout = "cb.tmp"
    combine_ans.process(cb, fout)
    gain50 = gain_by_p.process(fout, 50, output=False)
    gain3 = gain_by_p.process(fout, 3, output=False)
    
    cb = ",".join(map(os.path.basename, cb))
    value = "%s,%.5f,%.5f\n" % (cb, gain3, gain50)
    print "==" * 10
    print value,
    print
    return value

if __name__ == "__main__":
    model = sys.argv[1]
    with open("conf/combine.yaml") as fin:
        cfg = yaml.load(fin)[model]
    fins = cfg["input"]
    fout = open("log/cb_" + model, "a")
    
    for i in range(2, len(fins) + 1):
        for cb in itertools.combinations(fins, i):
            print cb
            fout.write(cb)
