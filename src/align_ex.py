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
            key = key.replace("-", "")
            yield key, value


if __name__ == "__main__":
    with TimeLog():
        base = dict(getKv("big.cc"))
    with TimeLog():
        addex = dict(getKv("additional.cc"))
    bk = set(base.keys())
    ak = set(addex.keys())
    print len(bk), len(ak)
    keys = bk.intersection(ak)
    print "new keys", len(keys)

    fout = open("macro/ex.cc", "w")
    for c, k in enumerate(keys):
        fout.write(k)
        fout.write(base[k])
        fout.write(addex[k])
        fout.write("\n")

        bl = len(base[k].split(","))
        al = len(addex[k].split(","))
        assert bl + al == 87, "%s %d, %d" % (k, bl, al)  # 68, 19

        if c % 1000000 == 0:
            print c
        fout.flush()

    cmd = "hdfs dfs -rmr htk/ex.cc"
    os.system(cmd)
    cmd = "hdfs dfs -put macro/ex.cc htk/ex.cc"
    os.system(cmd)
