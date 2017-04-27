from common import *

if __name__ == '__main__':
    st_list = get_total_st()
    df = None
    for st in st_list:
        stock = pd.read_csv(BASIC_DATA + st)
        stock.rename(columns=COL)
        stock = stock[stock.m != 0]
        if df is None:
            df = stock
        else:
            df = df.append(stock, ignore_index=True)
    df.to_csv("merge.cc", index=False, header=False)
