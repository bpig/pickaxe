#!/bin/env python
from common import *
from basic import *

if __name__ == "__main__":
    st_list = sorted(os.listdir(BASIC_DATA))
    columns = ["st", "dt", "s", "h", "l", "e", "v", "m", "t", "ft"]
    for st_code in st_list[:2]:
        df = pd.read_csv(os.path.join(BASIC_DATA, st_code))
        assert len(df.columns) == len(columns)
        df.columns = columns
        df = cal(df)
        tgt = os.path.join(FEA_DATA, st_code)
        df.to_csv(tgt, index=False)
