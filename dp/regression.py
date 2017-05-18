# coding:utf-8
from common import *

def gain(predictFile):
    predict = pickle.load(open(predictFile))
    ds = sorted(predict.keys())

    money = 1
    month = defaultdict(lambda : 1.0)

    for n, day in enumerate(ds):
        increase, count, r = 0, 0, 0
        for st_code in predict[day]:
            if count == 3:
                break
            tgt = BASIC_DATA + st_code
            stock = pd.DataFrame.from_csv(tgt, index_col=None)
            stock.rename(columns=COL, inplace=True)
            stock.sort_values('dt', inplace=True)
            stock.reset_index(drop=True, inplace=True)

            idx = stock[stock.dt == day].index[0]

            assert idx > 0
            if idx + 2 >= stock.index.size:
                # print "warning: %s no tomorrow data" % st_code
                break
            if stock.v[idx + 1] == 0:
                # print "warning: %s stop" % st_code
                continue

            buy = stock.e[idx + 1]
            pe_buy = stock.e[idx]
            if buy / pe_buy >= 1.06:
                # print "warning: %s can't buying" % st_code
                count += 1
                continue
            sell = stock.s[idx + 2]
            increase += sell / buy
            r += 1
            count += 1
            # print st_code, buy, sell, sell / buy
        
        if r > 0:
            rate = (increase  + 3 - r) / 3 - 0.0015
            money *= rate
            m = day / 100
            month[m] *= rate
            print day, rate, money


    total = money
    for m in sorted(month.keys()):
        print m, month[m]
    return total

if __name__ == "__main__":
    print gain("ans/%s.pl" % sys.argv[1])
