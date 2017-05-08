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
    df = df[df.m != 0]
    df.reset_index(drop=True, inplace=True)

    return df

def gain(predictFile):
    predict = pd.read_csv(predictFile)
    ds = predict['ds'].values
    stocks = get_data(min(ds), max(ds))

    for record in predict.values:
        ds = record[0]
        for i in range(1, len(record)):
            buySt = record[i]
            stock = stocks['st' == buySt]
            stock.sort_values('dt', asecending=False, inplace=True)
            info = stock.T.values
            index = info[0].index(ds)





if __name__ == "__main__":
    gain("../data/predict.txt")