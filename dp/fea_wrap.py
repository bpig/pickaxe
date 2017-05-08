#!/bin/env python
from common import *
from fea import *


@need_dir(FEA_DATA)
@need_dir(PARA_DATA + "norm")
def normalize_fea(st_list, gid):
    mu = pd.Series.from_csv(MVN_DATA + "mu")
    delta = pd.Series.from_csv(MVN_DATA + "delta")
    mu["dt"] = 0
    delta["dt"] = 1
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
        st.dt = st.dt.astype(np.int)
        st['st'] = st_code
        if df is None:
            df = st
        else:
            df = df.append(st, ignore_index=True)

    key = df[["st", "dt"]].as_matrix()
    np.save(PARA_DATA + "norm/key%s.npy" % gid, key)

    tgt = df["tgt"].as_matrix().reshape(-1, 1).astype(np.float32)
    np.save(PARA_DATA + "norm/tgt%s.npy" % gid, tgt)

    df.drop(["dt", "tgt", "st"], axis=1, inplace=True)
    fea = df.as_matrix().astype(np.float32)
    np.save(PARA_DATA + "norm/fea%s.npy" % gid, fea)



@need_dir(MVN_DATA)
@need_dir(PROC_DATA)
@need_dir(FLAT_DATA)
@need_dir(PARA_DATA + "mvn")
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
    phase, gid = sys.argv[1:]
    tgt = PARA_DATA + "st_list/%s" % gid
    st_list = pickle.load(open(tgt))
    if phase == "raw":
        raw_fea(st_list, gid)
    elif phase == "norm":
        normalize_fea(st_list, gid)
