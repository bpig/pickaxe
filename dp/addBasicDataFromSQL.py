import MySQLdb
import os
import sys
import numpy as np
import pandas as pd
import time
import datetime

def strtodatetime(datestr,format="%Y%m%d"):
    return datetime.datetime.strptime(datestr,format)

def datetostr(date):
    return date.strftime('%Y%m%d')

def datediff(beginDate,endDate,format="%Y%m%d"):
    bd=strtodatetime(beginDate,format)
    ed=strtodatetime(endDate,format)
    delta = ed - bd
    return delta.days

def connectSQL():
    conn = MySQLdb.connect('192.168.3.131', 'yyzc', 'yyzc_123', 'daily_data')
    return conn

def getWindcodes(conn, date):
    start_time = time.time()
    print 'getting codes...'
    cur = conn.cursor()
    sql = 'select distinct S_INFO_WINDCODE from ashareeodprices WHERE TRADE_DT=\'%s\';' %date
    cur.execute(sql)
    codes = cur.fetchall()
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)
    return codes

def getAllDataByDate(conn, date):
    sql1 = 'SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_ADJOPEN, S_DQ_ADJHIGH, S_DQ_ADJLOW, S_DQ_ADJCLOSE, S_DQ_ADJFACTOR, S_DQ_AVGPRICE \
                    , S_DQ_VOLUME, S_DQ_AMOUNT FROM ashareeodprices WHERE \
                     TRADE_DT=\'%s\';' %date
    sql2 = 'SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_TURN, S_DQ_FREETURNOVER FROM ashareeodderivativeindicator WHERE \
                     S_DQ_TURN is not NULL and TRADE_DT=\'%s\';' %date
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
    print 'processing %s...'%windcode

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

def addData(conn, date):
    dest_path = 'csvData_basic/'
    current_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(current_dir, dest_path)
    if os.path.exists(dest_path) == False:
        os.mkdir(dest_path)

    result1, result2 = getAllDataByDate(conn, date)
    codes = getWindcodes(conn, date)
    if len(codes)==0:
        print 'No new data!'
        exit()
    counter = 0;
    total = len(codes)
    for (code,) in codes:
        counter += 1
        print '#%d out of %d'%(counter, total)
        codenum = code.split('.')[0]
        file_path = dest_path + codenum + '.csv'

        final_result = getDataByWindcode(code, result1, result2)
        if os.path.exists(file_path):
            data = pd.DataFrame.from_csv(file_path)
            final_result = final_result.append(data, ignore_index=True)
        final_result.to_csv(os.path.join(current_dir, dest_path) + codenum + '.csv')

if __name__ == '__main__':
    dates = sys.argv[1:]
    oneday = datetime.timedelta(days=1)
    conn = connectSQL()
    for current_date in dates:
        start_time = time.time()
        print current_date
        addData(conn, current_date)
        duration = time.time() - start_time
        print 'saved! {}s used.\n'.format(duration)
