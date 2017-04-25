import tushare as ts
from dp.common import *


def download(name, dest_dir):
    tgt = os.path.join(dest_dir, name + ".csv")
    df = ts.get_hist_data(name, start=start_date, end=end_date, retry_count=5, pause=0.005)
    df.to_csv(tgt)


if __name__ == '__main__':
    start_date = '2015-04-01'
    end_date = '2017-10-12'

    dest_dir = os.path.join(curDir(), "index")
    download("zh500", dest_dir)
    download("hs300", dest_dir)
