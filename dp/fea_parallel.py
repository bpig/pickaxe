#!/bin/env python
from common import *
from fea import *


@need_dir(FEA_DATA)
def normalize_fea(st_list, gid):
    mu = pd.Series.from_csv(MVN_DATA + "mu")
    delta = pd.Series.from_csv(MVN_DATA + "delta")
    df = None
    for st_code in tqdm(st_list):
        try:
            st = pd.read_csv(FLAT_DATA + st_code)
        except:
            continue
        if st.empty:
            continue
        st = (st - mu) / delta
        st.to_csv(FEA_DATA + st_code, index=False)
        if df is None:
            df = st
        else:
            df = df.append(st, ignore_index=True)

    fea = df[df.columns[:-1]].as_matrix().astype(np.float32)
    np.save(PARA_DATA + "norm/fea%s.npy" % gid, fea)

    tgt = df[df.columns[-1]].as_matrix().reshape(-1, 1).astype(np.float32)
    np.save(PARA_DATA + "norm/tgt%s.npy" % gid, tgt)


@need_dir(MVN_DATA)
@need_dir(PROC_DATA)
@need_dir(FLAT_DATA)
def raw_fea(st_list, gid):
    mvn = MVN()
    for st_code in tqdm(st_list):
        df = pd.read_csv(BASIC_DATA + st_code)
        assert len(df.columns) == len(COL)
        df.rename(columns=COL, inplace=True)

        df = proc_fea(df)
        if df.empty:
            continue
        df.to_csv(PROC_DATA + st_code, index=False)

        df = flat_fea(df)
        if df.empty:
            continue
        df.to_csv(FLAT_DATA + st_code, index=False)
        mvn.collect(df)
    mvn.raw_dump(gid)


if __name__ == "__main__":
    makedirs(PARA_DATA)
    phase, gid = sys.argv[1:]
    tgt = PARA_DATA + "st_list/%s" % gid
    st_list = pickle.load(open(tgt))
    if phase == "raw":
        raw_fea(st_list, gid)
    elif phase == "norm":
        normalize_fea(st_list, gid)
