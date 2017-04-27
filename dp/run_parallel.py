from common import *


def split_list(par):
    st_list = get_total_st()
    step = (len(st_list) + par - 1) / par
    for i in range(0, len(st_list), step):
        tgt = PARA_DATA + "st_list%s" % i / step
        pickle.dump(st_list[i:i + step], open(tgt, "w"))


def run_parallel(par, phase):
    cmd = "parallel ./fea_parallel.py phase :::"
    for i in range(par):
        cmd += " %d" % i
    os.system(cmd)


def col_mu_delta(par):
    x = None
    xx = None
    ct = 0
    columns = None
    for n in range(par):
        i = PARA_DATA + "x%d" % n
        ii = PARA_DATA + "xx%d" % n
        v = PARA_DATA + "ct%d.npy" % n
        i = pd.Series.from_csv(i)
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
        block_fea = np.load(PARA_DATA + "fea%d.npy" % n)
        block_tgt = np.load(PARA_DATA + "tgt%d.npy" % n)
        fea += [block_fea]
        tgt += [block_tgt]
    fea = np.concatenate(fea)
    tgt = np.concatenate(tgt)
    np.save(TRAIN_DATA + "fea", fea)
    np.save(TRAIN_DATA + "tgt", tgt)


if __name__ == '__main__':
    makedirs(PARA_DATA)
    par = int(sys.argv[1])
    split_list(par)
    run_parallel(par, "raw")
    col_mu_delta(par)
    run_parallel(par, "norm")
    col_train_data(par)
