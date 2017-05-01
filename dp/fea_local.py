#!/bin/env python
from common import *
from fea import *


@need_dir(FEA_DATA)
def normalize_fea():
    st_list = get_total_st()
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
    np.save(TRAIN_DATA + "fea.npy", fea)

    tgt = df[df.columns[-1]].as_matrix().reshape(-1, 1).astype(np.float32)
    np.save(TRAIN_DATA + "tgt.npy", tgt)


@need_dir(MVN_DATA)
@need_dir(PROC_DATA)
@need_dir(FLAT_DATA)
def raw_fea():
    st_list = get_total_st()
    st_list = os.listdir(FLAT_DATA)
    mvn = MVN()
    for st_code in tqdm(st_list):
        df = pd.read_csv(BASIC_DATA + st_code)
        assert len(df.columns) == len(COL)
        df.rename(columns=COL, inplace=True)

        df = proc_fea(df)
        df.to_csv(PROC_DATA + st_code, index=False)

        df = flat_fea(df)
        df.to_csv(FLAT_DATA + st_code, index=False)
        try:
            df = pd.read_csv(FLAT_DATA + st_code)
        except:
            print st_code
            continue
        mvn.collect(df)
    mvn.dump()


if __name__ == "__main__":
    raw_fea()
#    normalize_fea()
