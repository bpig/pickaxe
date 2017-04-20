from common import *


def getAllDataByDate(conn, start_date, end_date):
    sql1 = "SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_ADJOPEN, S_DQ_ADJHIGH, S_DQ_ADJLOW, S_DQ_ADJCLOSE, " + \
           "S_DQ_ADJFACTOR, S_DQ_AVGPRICE , S_DQ_VOLUME, S_DQ_AMOUNT FROM ashareeodprices " + \
           "WHERE TRADE_DT>='%s' and TRADE_DT<='%s';" % (start_date, end_date)

    sql2 = "SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_TURN, S_DQ_FREETURNOVER FROM ashareeodderivativeindicator " + \
           "WHERE S_DQ_TURN is not NULL and TRADE_DT>='%s' and TRADE_DT<='%s';" % (start_date, end_date)

    with TimeLog('sql query1,'):
        table1 = pd.read_sql(sql1, conn)

    with TimeLog('sql query2,'):
        table2 = pd.read_sql(sql2, conn)

    table = table1.merge(table2, on=['TRADE_DT', 'S_INFO_WINDCODE'], how='inner')
    return table


def getDataByWindcode(windcode, table):
    data = table[table.S_INFO_WINDCODE == windcode]
    data.drop('S_INFO_WINDCODE', axis=1, inplace=True)

    cols = list(data)
    cols.append(cols.pop(cols.index('S_DQ_ADJFACTOR')))

    data = data.ix[:, cols]
    data.sort_values(
        ['TRADE_DT'], ascending=False, inplace=True)
    data.reset_index(drop=True, inplace=True)

    return data


def addData(conn, start_date, end_date):
    codes = getWindcodes(conn)
    assert codes

    dest_path = os.path.join(curDir(), BASIC_DATA)
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    table = getAllDataByDate(conn, start_date, end_date)

    for (code,) in tqdm(codes):
        codenum = code.split('.')[0]
        tgt = os.path.join(dest_path, codenum + '.csv')

        data = getDataByWindcode(code, table)
        if os.path.exists(tgt):
            data = pd.DataFrame.from_csv(tgt)
            data = data.append(data, ignore_index=True)
        if len(data):
            data.to_csv(tgt, index=False)
        else:
            return code
    return ""


if __name__ == '__main__':
    start_date = sys.argv[1]
    try:
        end_date = sys.argv[2]
    except:
        end_date = start_date
    conn = connectSQL()
    no_data_code = set()
    with TimeLog("%s-%s" % (start_date, end_date)):
        code = addData(conn, start_date, end_date)
        if code:
            no_data_code.add(code)
    print "\n".join(no_data_code)
    print "no_data total", len(no_data_code)
    
