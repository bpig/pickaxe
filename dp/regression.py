# coding:utf-8
from common import *

def gain(predictFile):
    predict = pickle.load(open(predictFile))
    ds = sorted(predict.keys())

    #money = [0.5, 0.5]
    money = 1

    for n, day in enumerate(ds):
        #flag = n % 2
        increase, count = 0, 0
        for st_code in predict[day]:
            if count == 3:
                break
            tgt = BASIC_DATA + st_code
            stock = pd.DataFrame.from_csv(tgt)
            stock.rename(columns=COL, inplace=True)
            stock.sort_values('dt', inplace=True)
            stock.reset_index(drop=True, inplace=True)

            idx = stock[stock.dt == day].index[0]

            assert idx > 0
            if idx + 2 >= stock.index.size:
                # print "warning: %s no tomorrow data" % st_code
                break
            if stock.v[idx + 1] == 0:
                print "warning: %s stop" % st_code
                continue
            buy = stock.e[idx + 1]
            # if stock.l[idx + 1] > buy:
            #     # print "warning: %s too expensive to buy" % st_code
            #     continue
            sell = stock.s[idx + 2]
            # if stock.h[idx + 2] < sell:
            #     sell = stock.l[idx + 2]
            increase += sell / buy
            count += 1
            print st_code, buy, sell, sell / buy
        
        if count > 0:
            rate = increase / count - 0.0015
         #   money[flag] *= rate
            money *= rate
            print day, rate
            print

    total = sum(money)
    return total

if __name__ == "__main__":
    print gain("ans/big20.pl")
