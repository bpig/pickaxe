from common import *


def getWindcodes(conn):
    start_time = time.time()
    print 'getting codes...'
    cur = conn.cursor()
    sql = 'select distinct S_INFO_WINDCODE from ashareeodprices;'
    cur.execute(sql)
    codes = cur.fetchall()
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)
    return codes


def getAllDataByDate(conn, start_date='20040601', end_date='20170101'):
    sql1 = "SELECT S_INFO_WINDCODE, TRADE_DT, BUY_VALUE_EXLARGE_ORDER, SELL_VALUE_EXLARGE_ORDER, " + \
           "BUY_VOLUME_EXLARGE_ORDER, SELL_VOLUME_EXLARGE_ORDER, TRADES_COUNT, BUY_TRADES_EXLARGE_ORDER, " + \
           "SELL_TRADES_EXLARGE_ORDER, S_MFD_INFLOWVOLUME, NET_INFLOW_RATE_VOLUME, OPEN_MONEYFLOW_PCT_VOLUME_L, " + \
           "CLOSE_MONEYFLOW_PCT_VOLUME_L FROM asharemoneyflow " + \
           "WHERE TRADE_DT>='%s' and TRADE_DT<='%s';" % (start_date, end_date)

    with TimeLog('execute sql'):
        result1 = pd.read_sql(sql1, conn)

    return result1


def getDataByWindcode(windcode, result1):
    start_time = time.time()
    print 'processing %s...' % windcode

    final_result = result1[result1.S_INFO_WINDCODE == windcode]
    final_result.drop('S_INFO_WINDCODE', axis=1, inplace=True)

    final_result.sort(['TRADE_DT'], ascending=False, inplace=True)
    final_result.reset_index(drop=True, inplace=True)

    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)

    return final_result


if __name__ == '__main__':
    dest_path = 'csvData_moneyflow/'
    current_dir = curDir()
    if not os.path.exists(os.path.join(current_dir, dest_path)):
        os.mkdir(os.path.join(current_dir, dest_path))
    conn = connectSQL()
    result1 = getAllDataByDate(conn, start_date='20040601', end_date='20170101')
    codes = getWindcodes(conn)

    for (code,) in tqdm(codes):
        codenum = code.split('.')[0]
        file_path = dest_path + codenum + '.csv'
        if not codenum.isdigit():
            continue
        if os.path.exists(file_path):
            continue
        df = getDataByWindcode(code, result1)
        df.to_csv(os.path.join(current_dir, dest_path) + codenum + '.csv')
        print 'saved!\n'
