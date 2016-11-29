import MySQLdb
import os
import time
import numpy as np
import pandas as pd

def connectSQL():
    conn = MySQLdb.connect('localhost', 'yyzc', 'yyzc', 'daily_data')
    return conn

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
    sql1 = 'SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_ADJOPEN, S_DQ_ADJHIGH, S_DQ_ADJLOW, S_DQ_ADJCLOSE, S_DQ_ADJFACTOR, S_DQ_AVGPRICE \
                    , S_DQ_VOLUME, S_DQ_AMOUNT FROM ashareeodprices WHERE \
                     TRADE_DT>\'%s\' and TRADE_DT<\'%s\';' % (start_date, end_date)
    sql2 = 'SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_TURN, S_DQ_FREETURNOVER FROM ashareeodderivativeindicator WHERE \
                     S_DQ_TURN is not NULL and TRADE_DT>\'%s\' and TRADE_DT<\'%s\';' % (start_date, end_date)
    start_time = time.time()
    print 'executing query1...'
    result1 = pd.read_sql(sql1, conn)
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)
    
    start_time = time.time()
    print 'executing query2...'
    result2 = pd.read_sql(sql2, conn)
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)
    return result1, result2

def getDataByWindcode(windcode, result1, result2):
    start_time = time.time()
    print 'processing %s...' % windcode
    
    data1 = result1[result1.S_INFO_WINDCODE == windcode]
    data2 = result2[result2.S_INFO_WINDCODE == windcode]
    data1.drop('S_INFO_WINDCODE', axis=1, inplace=True)
    data2.drop('S_INFO_WINDCODE', axis=1, inplace=True)
    
    if len(data1) != len(data2):
        print 'check failed: different length!'
    final_result = data1.merge(data2, on='TRADE_DT', how='inner')
    cols = list(final_result)
    cols.append(cols.pop(cols.index('S_DQ_ADJFACTOR')))
    final_result = final_result.ix[:, cols]
    final_result.sort(['TRADE_DT'], ascending=False, inplace=True)
    final_result.reset_index(drop=True, inplace=True)
    
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)
    
    return final_result

if __name__ == '__main__':
    dest_path = 'csvData_basic/'
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(os.path.join(current_dir, dest_path)) == False:
        os.mkdir(os.path.join(current_dir, dest_path))
    conn = connectSQL()
    result1, result2 = getAllDataByDate(conn, start_date='20040601', end_date='20170101')
    codes = getWindcodes(conn)
    counter = 0
    length = len(codes)
    for (code,) in codes:
        counter += 1
        codenum = code.split('.')[0]
        file_path = dest_path + codenum + '.csv'
        if codenum.isdigit() == False:
            continue
        if os.path.exists(file_path):
            continue
        print code
        print '%d out of %d' % (counter, length)
        df = getDataByWindcode(code, result1, result2)
        df.to_csv(os.path.join(current_dir, dest_path) + codenum + '.csv')
        print 'saved!\n'
