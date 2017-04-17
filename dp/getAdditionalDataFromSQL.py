import MySQLdb
import os
import time
import numpy as np
import pandas as pd


def connectSQL():
    conn = MySQLdb.connect('192.168.3.131', 'yyzc', 'yyzc_123', 'daily_data')
    return conn


def getWindcodes(conn):
    start_time = time.time()
    print 'getting codes...'
    cur = conn.cursor()
    sql = 'select distinct code from additional_data_2;'
    cur.execute(sql)
    codes = cur.fetchall()
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)
    return codes


def getAllDataByDate(conn, start_date='20040601', end_date='20180101'):
    sql1 = 'SELECT code, TRADE_DT, \
		     A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R \
                     FROM additional_data_2 WHERE \
                     TRADE_DT>\'%s\' and TRADE_DT<\'%s\';' % (start_date, end_date)
    sql2 = 'SELECT code, TRADE_DT, \
		     A, A1, B, B1, C, E, E1, F, G_A, G_B, G_R, H_A, H_B, H_E, I1, I2, J1, J2, J3, J4, J5, J6, J7, J8 \
                     FROM additional_data_3 WHERE \
                     TRADE_DT>\'%s\' and TRADE_DT<\'%s\';' % (start_date, end_date)
    start_time = time.time()
    print 'executing query1...'
    result1 = pd.read_sql(sql1, conn)
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)

    print 'executing query2...'
    result2 = pd.read_sql(sql2, conn).rename(columns={'code':'code','TRADE_DT':'TRADE_DT',
                                                      'A':'TopOverCurrent_20','A1':'TopOverCurrent_125','B':'TopDistance_20','B1':'TopDistance_125',
                                                      'C':'MA5_GT_MA20_10','E':'Sqrt_Yield_over_Volume_Open','E1':'Sqrt_Yield_over_Volume_Close',
                                                      'F':'RootMTM_5','G_A':'ACC_A_20','G_B':'ACC_B_20','G_R':'ACC_R_20',
                                                      'H_A':'IV_A_20','H_B':'IV_B_20','H_E':'IV_E_20','I1':'Z_SCORE','I2':'Z_SCORE_FREE',
                                                      'J1':'VROC_12','J2':'VRSI_6','J3':'VR_26','J4':'VOLUME_RATIO_5',
                                                      'J5':'VMACD_DIF_12','J6':'VMACD_DEA_26','J7':'VMACD_MACD_9','J8':'VSTD_10'})
    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)

    return result1, result2


def getDataByWindcode(windcode, result1, result2):
    start_time = time.time()
    print 'processing %s...'%windcode

    data1 = result1[result1.code == windcode]
    data2 = result2[result2.code == windcode.split('.')[0]]
    data1.drop('code', axis=1, inplace=True)
    data2.drop('code', axis=1, inplace=True)

    final_result = data1.merge(data2, on='TRADE_DT', how='inner')
    final_result.sort(['TRADE_DT'], ascending=False, inplace=True)
    final_result['TRADE_DT'] = pd.to_datetime(final_result['TRADE_DT']).dt.strftime('%Y%m%d')
    final_result.reset_index(drop=True, inplace=True)
    final_result['TRADE_DT'] = final_result['TRADE_DT'].astype(str)

    duration = time.time() - start_time
    print 'done. {}s used.'.format(duration)
    
    return final_result


if __name__ == '__main__':
    dest_path = 'csvData_additional/'
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(os.path.join(current_dir, dest_path)) == False:
        os.mkdir(os.path.join(current_dir, dest_path))
    conn = connectSQL()
    result1, result2 = getAllDataByDate(conn, start_date='20040601', end_date='20180101')
    codes = getWindcodes(conn)
    counter = 0
    length = len(codes)
    for code in codes:
        counter += 1
        code = code[0]
        codenum = code.split('.')[0]
        file_path = dest_path + codenum + '.csv'
        if codenum.isdigit() == False:
            continue
        #if os.path.exists(file_path):
        #    continue
        print code
        print '%d out of %d' % (counter, length)
        df = getDataByWindcode(code, result1, result2)
        df.to_csv(os.path.join(current_dir, dest_path) + codenum + '.csv')
        print 'saved!\n'
