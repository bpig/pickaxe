#!/bin/env python
from common import *
from basic import *


def normalize_fea():
    if not os.path.exists(FEA_DATA):
        os.mkdir(FEA_DATA)
    st_list = sorted(os.listdir(RAW_DATA))
    mu = pd.read_csv(os.path.join(MVN_DATA, "mu"), index_col=None, header=None)[0]
    delta = pd.read_csv(os.path.join(MVN_DATA, "delta"), index_col=None, header=None)[0]

    df = None
    for st_code in tqdm(st_list):
        try:
            st = pd.read_csv(os.path.join(RAW_DATA, st_code), index_col=None, header=None)
        except:
            continue
        if st.empty:
            continue
        st = (st - mu) / delta
        tgt = os.path.join(FEA_DATA, st_code)
        st.to_csv(tgt, index=False, header=None)
        if df is None:
            df = st
        else:
            df = df.append(st, ignore_index=True)

    fea = df[df.columns[:-1]].as_matrix()
    print df.shape
    print fea.shape
    np.save("fea.npy", fea)

    tgt = df[df.columns[-1]].as_matrix().reshape(-1, 1)
    print tgt.shape
    np.save("tgt.npy", tgt)


def raw_fea():
    if not os.path.exists(RAW_DATA):
        os.mkdir(RAW_DATA)
    if not os.path.exists(MVN_DATA):
        os.mkdir(MVN_DATA)
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
        if df.empty:
            continue
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
    delta[delta == 0] = 1
    mu.to_csv(os.path.join(MVN_DATA, "mu"), index=False)
    delta.to_csv(os.path.join(MVN_DATA, "delta"), index=False)


if __name__ == "__main__":
    # raw_fea()
    normalize_fea()
