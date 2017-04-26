#!/bin/env python
from common import *
from basic import *


def normalize_fea():
    if not os.path.exists(FEA_DATA):
        os.mkdir(FEA_DATA)
    st_list = sorted(os.listdir(BASIC_DATA))
    mu = pd.read_csv(os.path.join(RAW_DATA, "mu"), index=False, header=False)
    delta = pd.read_csv(os.path.join(RAW_DATA, "delta"), index=False, header=False)

    for st_code in tqdm(st_list):
        st = pd.read_csv(os.path.join(RAW_DATA, st_code), index=False, header=False)
        st = (st - mu) / delta
        tgt = os.path.join(FEA_DATA, st_code)
        st.to_csv(tgt, index=False, header=None)


def raw_fea():
    if not os.path.exists(RAW_DATA):
        os.mkdir(RAW_DATA)
    st_list = sorted(os.listdir(BASIC_DATA))
    columns = ["st", "dt", "s", "h", "l", "e", "v", "m", "t", "ft"]
    x = None
    xx = None
    ct = 0
    for st_code in tqdm(st_list):
        tgt = os.path.join(RAW_DATA, st_code)

        df = pd.read_csv(os.path.join(BASIC_DATA, st_code))
        assert len(df.columns) == len(columns)
        df.columns = columns
        df = cal(df)

        # df.to_csv(tgt, index=False)

        df = comb_fea(df)

        df.to_csv(tgt, index=False, header=None)
        if x is None:
            x = df.sum()
            xx = (df * df).sum()
        else:
            x += df.sum()
            xx += (df * df).sum()
        ct += df.index.size

    mu = x / ct
    delta = xx / ct - mu * mu
    delta.fillna(0)
    delta **= .5
    delta += 1
    mu.to_csv(os.path.join(RAW_DATA, "mu"), index=False)
    delta.to_csv(os.path.join(RAW_DATA, "delta"), index=False)


if __name__ == "__main__":
    raw_fea()
    normalize_fea()
