#!/bin/env python
from common import *
from basic import *

if __name__ == "__main__":
    st_list = sorted(os.listdir(BASIC_DATA))
    columns = ["dt", "s", "h", "l", "e", "av", "v", "m", "t", "ft"]
    for st in st_list[:2]:
        df = pd.read_csv(st)
        df.columns = columns
        st_code = st[:-4]
        df = cal(df)
        df.to_csv(st_code + ".fea", index=False)
