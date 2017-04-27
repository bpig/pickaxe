#!/bin/env python
from common import *
from basic import *


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


class MVN:
    def __init__(self):
        self.x = None
        self.xx = None
        self.ct = 0
        self.columns = []

    def collect(self, df):
        if not self.columns:
            self.columns = df.columns
        if self.x is None:
            self.x = df.sum()
            self.xx = (df * df).sum()
        else:
            self.x += df.sum()
            self.xx += (df * df).sum()
        self.ct += len(df)

    def dump(self):
        mu = self.x / self.ct
        delta = self.xx / self.ct - mu * mu
        delta.fillna(0)
        delta **= .5
        delta[delta == 0] = 1
        mu.index = self.columns
        delta.index = self.columns

        np.save(MVN_DATA + "mu.npy", mu.as_matrix())
        np.save(MVN_DATA + "delta.npy", delta.as_matrix())

        mu.to_csv(MVN_DATA + "mu")
        delta.to_csv(MVN_DATA + "delta")


@need_dir(MVN_DATA)
@need_dir(PROC_DATA)
@need_dir(FLAT_DATA)
def raw_fea():
    st_list = get_total_st()

    mvn = MVN()
    for st_code in tqdm(st_list):
        df = pd.read_csv(BASIC_DATA + st_code)
        assert len(df.columns) == len(COL)
        df.rename(columns=COL)

        df = proc_fea(df)
        df.to_csv(PROC_DATA + st_code, index=False)

        df = flat_fea(df)
        df.to_csv(FLAT_DATA + st_code, index=False)

        mvn.collect(df)
    mvn.dump()


if __name__ == "__main__":
    raw_fea()
    normalize_fea()
