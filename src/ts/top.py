from src.common import *

if __name__ == '__main__':
    date = '2017-04-14'
    with TimeLog():
        df = ts.top_list(date)
        tgt = date
        df.to_csv("top/" + tgt + ".csv", encoding="gbk")
    print df
