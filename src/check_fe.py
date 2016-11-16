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

def checkDs(fe_version, ds):
    te = "data/fe/%s/test" % fe_version
    print te
    te_k, te_f, te_t = mlp_feeder.base_data(te)
    ds = "data/fe/%s/daily/%s.fe" % (fe_version, ds)
    print ds
    ds_k, ds_f, ds_t = mlp_feeder.base_data(ds)
    for i in range(len(ds_f)):
        k = ds_k[i]
        #print k
        idx = np.where(te_k == k)[0][0]
        tf = te_f[idx]
        df = ds_f[i]
        # tgt = "raw/f8/000001.SZ_20161114"
        # v = np.fromstring(open(tgt).read(), sep=",", dtype=np.float32)[:-1]
        # if np.array_equal(v, tf):
        #     print "v equal tf"
        # if np.array_equal(v, df):
        #     print "v equal df"

        if not np.array_equal(tf, df):
            print te_k[idx], ds_k[i]
            select = tf != df
            # print df
            # print df[select]
            for j in range(len(te_f)):
                if np.array_equal(df, te_f[j]):
                    print te_k[j], ds_k[i]
                    break
#        sys.exit(1)

if __name__ == "__main__":
    fe_version = "f8"
    checkDs(fe_version, "20161116")

    
