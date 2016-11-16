from common import *

import mlp_feeder

def checkNum(fe_version):
    tr = "data/fe/%s/train" % fe_version
    te = "data/fe/%s/test" % fe_version
    tr_k, tr_f, tr_t = mlp_feeder.base_data(tr)
    te_k, te_f, te_t = mlp_feeder.base_data(te)

    tr_ds = sorted(set(map(lambda x: x.split("_")[1], tr_k)), reverse=True)[:5]
    te_ds = sorted(set(map(lambda x: x.split("_")[1], te_k)), reverse=True)[:5]
    print len(tr_k), tr_ds
    print len(te_k), te_ds

def checkContent(fe_version):
    raw_dir = "raw/%s" % fe_version
    with CD(raw_dir):
        lt = os.listdir(".")
        lt = filter(lambda x: not "dumper" in x, lt)
        lt = sorted(lt, key=lambda x: x.split("_")[1], reverse=True)
        print lt[:3]
        mark = {}
        for c, f in enumerate(lt):
            ds = f.split("_")[1]
            data = open(f).read()
            if data not in mark:
                mark[data] = f
            else:
                print f, "->", mark[data]
            if c % 10000 == 0:
                print c + 1, len(mark)


if __name__ == "__main__":
    fe_version = sys.argv[1]
    checkContent(fe_version)

    
