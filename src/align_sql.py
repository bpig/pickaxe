# coding:utf-8
from common import *


def getKv(*args):
    for filename in args:
        for l in open("macro/" + filename):
            l = l.strip()
            if not l or "code" in l or "S_INFO" in l:
                continue
            pos = l.find(",")
            pos = l.find(",", pos + 1)
            key = l[:pos]
            value = l[pos:]
            yield key, value


if __name__ == "__main__":
    cmd = "scp -P 8022 yingyang@61.130.4.98:/home/yingyang/公共的/sql/m.cc macro"
    os.system(cmd)
    cmd = "scp -P 8022 yingyang@61.130.4.98:/home/yingyang/公共的/sql/i.cc macro"
    os.system(cmd)

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

    fout = open("macro/big.cc", "w")
    for c, k in enumerate(keys):
        fout.write(k)
        fout.write(base[k])
        fout.write(moneyflow[k])
        fout.write(indicator[k])
        fout.write("\n")

        bl = len(base[k].split(","))
        ml = len(moneyflow[k].split(","))
        il = len(indicator[k].split(","))
        assert bl + ml + il == 70, "%s %d, %d, %d" % (k, bl, ml, il)

        if c % 1000000 == 0:
            print c
        fout.flush()

    cmd = "hdfs dfs -rmr htk/big.cc"
    os.system(cmd)
    cmd = "hdfs dfs -put macro/big.cc htk/big.cc"
    os.system(cmd)
