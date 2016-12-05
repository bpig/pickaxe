from common import *

def getKv(*args):
    for filename in args:
        for l in open("data/" + filename):
            l = l.strip()
            if not l or "code" in l or "S_INFO" in l:
                continue
            pos = l.find(",")
            pos = l.find(",", pos + 1)
            key = l[:pos]
            value = l[pos:]
            yield key, value

if __name__ == "__main__":
    with TimeLog():
        base = dict(getKv("total.cc"))
    with TimeLog():
        indicator = dict(getKv("asharel2indicators.cc", "i.cc"))
    with TimeLog():
        moneyflow = dict(getKv("asharemoneyflow.cc", "m.cc"))
    bk = set(base.keys())
    ik = set(indicator.keys())
    mk = set(moneyflow.keys())
    print len(bk), len(ik), len(mk)
    keys = bk.intersection(ik).intersection(mk)
    print len(keys)
    
    fout = open("data/big.cc", "w")
    for c, k in enumerate(keys):
        fout.write(k)
        fout.write(base[k])
        fout.write(moneyflow[k])
        fout.write(indicator[k])
        fout.write("\n")
        if c % 1000000 == 0:
            print c
        

        
