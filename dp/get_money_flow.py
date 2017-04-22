from common import *


def getAllDataByDate(conn, start_date='20040601', end_date='20170101'):
    sql1 = "SELECT S_INFO_WINDCODE, TRADE_DT, BUY_VALUE_EXLARGE_ORDER, SELL_VALUE_EXLARGE_ORDER, " + \
           "BUY_VOLUME_EXLARGE_ORDER, SELL_VOLUME_EXLARGE_ORDER, TRADES_COUNT, BUY_TRADES_EXLARGE_ORDER, " + \
           "SELL_TRADES_EXLARGE_ORDER, S_MFD_INFLOWVOLUME, NET_INFLOW_RATE_VOLUME, OPEN_MONEYFLOW_PCT_VOLUME_L, " + \
           "CLOSE_MONEYFLOW_PCT_VOLUME_L FROM asharemoneyflow " + \
           "WHERE TRADE_DT>='%s' and TRADE_DT<='%s';" % (start_date, end_date)

    with TimeLog('execute sql'):
        result1 = pd.read_sql(sql1, conn)

    return result1


def getDataByWindcode(st_code, all_data):
    with TimeLog(st_code + ", "):
        stock = all_data[all_data.S_INFO_WINDCODE == st_code]
        stock.drop('S_INFO_WINDCODE', axis=1, inplace=True)

        stock.sort(['TRADE_DT'], ascending=False, inplace=True)
        stock.reset_index(drop=True, inplace=True)

    return stock


if __name__ == '__main__':
    if not os.path.exists(MONEY_DATA):
        os.mkdir(MONEY_DATA)
    conn = connectSQL()
    all_data = getAllDataByDate(conn, start_date='20040601', end_date='20170101')
    codes = getWindcodes(conn)

    for (st,) in tqdm(codes):
        st_code = st.split('.')[0]
        tgt = os.path.join(MONEY_DATA, st_code + ".csv")
        if not st_code.isdigit():
            print st_code
            continue
        if os.path.exists(tgt):
            continue
        df = getDataByWindcode(st, all_data)
        df.to_csv(tgt, index=False)
        print 'saved!\n'
