from common import *


def get_data(conn, start_date, end_date):
    sql1 = "SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_ADJOPEN, S_DQ_ADJHIGH, S_DQ_ADJLOW, S_DQ_ADJCLOSE, " + \
           "S_DQ_VOLUME, S_DQ_AMOUNT FROM ashareeodprices " + \
           "WHERE TRADE_DT>='%s' and TRADE_DT<='%s';" % (start_date, end_date)

    sql2 = "SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_TURN, S_DQ_FREETURNOVER FROM ashareeodderivativeindicator " + \
           "WHERE S_DQ_TURN is not NULL and TRADE_DT>='%s' and TRADE_DT<='%s';" % (start_date, end_date)

    with TimeLog('sql query1,'):
        df1 = pd.read_sql(sql1, conn)

    with TimeLog('sql query2,'):
        df2 = pd.read_sql(sql2, conn)

    df = df1.merge(df2, on=['TRADE_DT', 'S_INFO_WINDCODE'], how='inner')
    return df


@need_dir(BASIC_DATA)
def dump_data(conn, start_date, end_date):
    st_list = get_st_list(conn)
    assert st_list

    df = get_data(conn, start_date, end_date)
    empty_st = []
    for (st_code,) in tqdm(st_list):
        tgt = BASIC_DATA + st_code

        data = df[df.S_INFO_WINDCODE == st_code]
        if os.path.exists(tgt):
            ori = pd.DataFrame.from_csv(tgt)
            data = ori.append(data, ignore_index=True)
        if not data.empty:
            data.to_csv(tgt, index=False)
        else:
            empty_st += [st_code]

    print "\n".join(empty_st)
    print "no_data total", len(empty_st)


if __name__ == '__main__':
    start_date = sys.argv[1]
    try:
        end_date = sys.argv[2]
    except:
        end_date = start_date
    conn = conn_sql()
    with TimeLog("%s-%s" % (start_date, end_date)):
        dump_data(conn, start_date, end_date)
