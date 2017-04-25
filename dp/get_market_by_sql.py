import MySQLdb
import os
import time
import numpy as np
import pandas as pd


def connectSQL():
    conn = MySQLdb.connect('192.168.3.131', 'yyzc', 'yyzc_123', 'daily_data')
    return conn


def getAllDataByDate(conn, start_date='20040601'):
    sql1 = "SELECT TRADE_DT, D, D1 FROM additional_data_4 WHERE TRADE_DT>'%s';" % start_date
    start_time = time.time()
    print 'executing query1...'
    result1 = pd.read_sql(sql1, conn).rename(columns={'TRADE_DT': 'TRADE_DT',
                                                      'D': 'MA5_GT_MA10_GT_MA20_Ratio',
                                                      'D1': 'MA5_LT_MA10_LT_MA20_Ratio'})
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)

    final_result = result1
    final_result.sort_values(['TRADE_DT'], ascending=False, inplace=True)
    final_result['TRADE_DT'] = pd.to_datetime(final_result['TRADE_DT']).dt.strftime('%Y%m%d')
    final_result.reset_index(drop=True, inplace=True)
    final_result['TRADE_DT'] = final_result['TRADE_DT'].astype(str)

    return final_result


if __name__ == '__main__':
    dest_path = 'csvData_market_additional/'
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(os.path.join(current_dir, dest_path)):
        os.mkdir(os.path.join(current_dir, dest_path))
    conn = connectSQL()
    df = getAllDataByDate(conn, start_date='20040601')
    df.to_csv(os.path.join(current_dir, dest_path) + 'market_additional.csv')
    print 'saved!\n'
