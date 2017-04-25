from dp.common import *

if __name__ == '__main__':
    st_list = sorted(os.listdir(BASIC_DATA))
    df = None
    for st in st_list[:2]:
        stock = pd.read_csv(os.path.join(BASIC_DATA, st), parse_dates=[0])
        if not df:
            df = stock.copy()
        else:
            df.append(st, axis=1)
    df.to_csv("merge.cc", ignore_index=False)
