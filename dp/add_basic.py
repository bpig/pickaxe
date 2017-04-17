import pymysql
import os
import sys
import numpy as np
import pandas as pd
import time
import datetime
from tqdm import tqdm

pd.options.mode.chained_assignment = None

class TimeLog:
    def __init__(self, name=""):
        self.n = name

    def __enter__(self):
        self.t = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "%s %.2fs" % (self.n, time.time() - self.t)

def curDir():
    return os.path.dirname(os.path.realpath(__file__))    

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
    conn = pymysql.connect(
            host='localhost', 
            port=3306, 
            user='jxb', 
            passwd='jxb', 
            db='daily_data')
    return conn

def getWindcodes(conn, date):
    with TimeLog('getting codes'):
        cur = conn.cursor()
        sql = "select distinct S_INFO_WINDCODE from ashareeodprices WHERE TRADE_DT='%s';" %date
        cur.execute(sql)
        codes = cur.fetchall()
    return codes

def getAllDataByDate(conn, date):
    sql1 = "SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_ADJOPEN, S_DQ_ADJHIGH, " + \
        "S_DQ_ADJLOW, S_DQ_ADJCLOSE, S_DQ_ADJFACTOR, S_DQ_AVGPRICE, " + \
        "S_DQ_VOLUME, S_DQ_AMOUNT FROM ashareeodprices " + \
        "WHERE TRADE_DT='%s';" %date

    sql2 = "SELECT S_INFO_WINDCODE, TRADE_DT, S_DQ_TURN, S_DQ_FREETURNOVER " + \
        "FROM ashareeodderivativeindicator " + \
        "WHERE S_DQ_TURN is not NULL and TRADE_DT='%s';" %date

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

def addData(conn, date):
    codes = getWindcodes(conn, date)
    if not len(codes):
        print 'No new data!'
        exit()

    dest_path = "csvData_basic"
    dest_path = os.path.join(curDir(), dest_path)
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    table = getAllDataByDate(conn, date)

    for (code,) in tqdm(codes):
        codenum = code.split('.')[0]
        tgt = os.path.join(dest_path, codenum + '.csv')

        data = getDataByWindcode(code, table)
        if os.path.exists(tgt):
            data = pd.DataFrame.from_csv(tgt)
            data = data.append(data, ignore_index=True)
        data.to_csv(tgt)

if __name__ == '__main__':
    dates = sys.argv[1:]
    conn = connectSQL()
    for current_date in dates:
        with TimeLog(current_date):
            addData(conn, current_date)
