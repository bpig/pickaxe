from common import *


def split_list(par):
    st_list = get_total_st()
    step = (len(st_list) + par - 1) / par
    makedirs(PARA_DATA + "st_list")
    for i in range(0, len(st_list), step):
        tgt = PARA_DATA + "st_list/%d" % (i / step)
        pickle.dump(st_list[i:i + step], open(tgt, "w"))


def run_parallel(par, phase):
    cmd = "parallel  ./fea_parallel.py %s :::" % phase
    for i in range(par):
        cmd += " %d" % i
    os.system(cmd)


def col_mu_delta(par):
    x = None
    xx = None
    ct = 0
    columns = None
    for n in range(par):
        i = PARA_DATA + "mvn/x%d" % n
        ii = PARA_DATA + "mvn/xx%d" % n
        v = PARA_DATA + "mvn/ct%d.npy" % n
        try:
            i = pd.Series.from_csv(i)
        except:
            continue
        if n == 0:
            columns = i.index
        i.reset_index(drop=True, inplace=True)
        ii = pd.Series.from_csv(ii).reset_index(drop=True)
        v = int(np.load(v))
        if x is None:
            x = i
            xx = ii
        else:
            x += i
            xx += ii
        ct += v
    mu = x / ct
    delta = xx / ct - mu * mu
    delta.fillna(0)
    delta **= .5
    delta[delta == 0] = 1
    mu.index = columns
    delta.index = columns

    np.save(MVN_DATA + "mu.npy", mu.as_matrix())
    np.save(MVN_DATA + "delta.npy", delta.as_matrix())

    mu.to_csv(MVN_DATA + "mu")
    delta.to_csv(MVN_DATA + "delta")


def col_train_data(par):
    fea = []
    tgt = []
    for n in range(par):
        block_fea = np.load(PARA_DATA + "norm/fea%d.npy" % n)
        block_tgt = np.load(PARA_DATA + "norm/tgt%d.npy" % n)
        fea += [block_fea]
        tgt += [block_tgt]
    fea = np.concatenate(fea)
    tgt = np.concatenate(tgt)
    np.save(TRAIN_DATA + "fea", fea)
    np.save(TRAIN_DATA + "tgt", tgt)


if __name__ == '__main__':
    if sys.argv[1] == "clean":
        with TimeLog("clean"):
            os.system("rm -rf %s %s %s %s %s" % (
                PARA_DATA, PROC_DATA, MVN_DATA, 
                FLAT_DATA, FEA_DATA))
        exit(0)

    makedirs(PARA_DATA)
    makedirs(TRAIN_DATA)
    par = int(sys.argv[1])
    split_list(par)
    with TimeLog("run raw"):
        run_parallel(par, "raw")
    with TimeLog("col mu delta"):
        col_mu_delta(par)
    with TimeLog("run norm"):
        run_parallel(par, "norm")
    with TimeLog("col train data"):
        col_train_data(par)
