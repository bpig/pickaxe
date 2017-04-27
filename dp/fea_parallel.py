#!/bin/env python
from common import *
from fea import *


@need_dir(FEA_DATA)
def normalize_fea(st_list, gid):
    mu = pd.Series.from_csv(MVN_DATA + "mu").reset_index(drop=True)
    delta = pd.Series.from_csv(MVN_DATA + "delta").reset_index(drop=True)

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
    np.save(PARA_DATA + "fea_%s.npy" % gid, fea)

    tgt = df[df.columns[-1]].as_matrix().reshape(-1, 1).astype(np.float32)
    np.save(PARA_DATA + "tgt_%s.npy" % gid, tgt)


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
        df.to_csv(PROC_DATA + st_code, index=False)

        df = flat_fea(df)
        df.to_csv(FLAT_DATA + st_code, index=False)

        mvn.collect(df)
    mvn.raw_dump(gid)


if __name__ == "__main__":
    makedirs(PARA_DATA)
    st_list = open(sys.argv[1]).readlines()
    st_list = map(str.strip, st_list)
    st_list = filter(len, st_list)
    gid = sys.argv[2]
    raw_fea(st_list, gid)
    # normalize_fea(st_list, gid)
