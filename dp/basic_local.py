#!/bin/env python
from common import *
from basic import *

if __name__ == "__main__":
    if not os.path.exists(FEA_DATA):
        os.mkdir(FEA_DATA)
    st_list = sorted(os.listdir(BASIC_DATA))
    columns = ["st", "dt", "s", "h", "l", "e", "v", "m", "t", "ft"]
    x = None
    xx = None
    ct = 0
    for st_code in tqdm(st_list):
        tgt = os.path.join(FEA_DATA, st_code)

        df = pd.read_csv(os.path.join(BASIC_DATA, st_code))
        assert len(df.columns) == len(columns)
        df.columns = columns
        df = cal(df)

        df.to_csv(tgt, index=False)

        df = comb_fea(df)

        df.to_csv(tgt, index=False, header=None)
        if x is None:
            x = df.sum()
            xx = (df * df).sum()
        else:
            x += df.sum()
            xx += (df * df).sum()
        ct += df.index.size

    x.to_csv("x")
    xx.to_csv("xx")
    mu = x / ct
    delta = xx / ct - mu * mu
    delta.fillna(0)
    delta **= .5
    delta += 1
    mu.to_csv("mu")
    delta.to_csv("delta")
