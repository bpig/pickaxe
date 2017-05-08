from common import *

def get_data(start_date, end_date):
    sql = "SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_ADJOPEN, S_DQ_ADJHIGHT, S_DQ_ADJLOW, S_DQ_ADJCLOSE, " \
          + "S_DQ_VOLUME, S_DQ_AMOUNT, S_DQ_TURN, S_DQ_FREETURNOVER FROM ashareeeodprices " \
          + "WHERE TRADE_DT>='%s' and TRADE_DT<='%s';" % (start_date, end_date)

    conn = conn_sql()

    with TimeLog('sql query,'):
        df = pd.read_sql(sql, conn)

    assert len(df.columns) == len(COL)
    df.rename(columns=COL, inplace=True)

    return df

def gain(predictFile):
    predict = pd.read_csv(predictFile)
    ds = predict['ds'].values
    stocks = get_data(min(ds), max(ds))

    money = [0.5, 0.5]

    for n, record in enumerate(predict.values):
        flag = n % 2
        increase, count = 0, 0
        ds = record[0]
        for i in range(1, len(record)):
            if count == 3:
                break
            buySt = record[i]
            stock = stocks['st' == buySt]
            stock.sort_values('dt', asecending=True, inplace=True)
            info = stock.T.values
            index = info[1].index(ds)
            assert index > 0
            if index + 1 >= len(info[1]):
                print "warning: % no tomorrow data" % buySt
                continue
            if info[7][index + 1] == 0:
                print "warning: %s stop, 无法买入" % buySt
                continue
            buyPrice = float(info[5][index])
            if float(info[4][index + 1]) > buyPrice:
                print "warning: %s too expensive to buy, 无法买入" % buySt
                continue
            sellPrice = float(info[5][index + 1])
            if float(info[3][index + 2] < sellPrice):
                sellPrice = float(info[5][index + 2]) * 0.9
            increase += sellPrice / buyPrice
            count += 1
        
        if count > 0:
            money[flag] *= (increase / count - 0.0015)

        total = sum(money)
        return total

if __name__ == "__main__":
    print gain("../data/predict.txt")
