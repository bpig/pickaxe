import os

from common import *

if __name__ == '__main__':
    st_list = sorted(os.listdir(BASIC_DATA))
    df = None
    for st in st_list[:2] + ["300359.csv"]:
        print st
        stock = pd.read_csv(os.path.join(BASIC_DATA, st), parse_dates=[0])
        stock['code'] = st[:-4]
        if df is None:
            df = stock.copy()
        else:
            df = df.append(stock, ignore_index=True)
    df.fillna(0, inplace=True)
    df.to_csv("merge.cc", index=False, header=False)
