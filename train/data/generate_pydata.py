# -*- coding: utf-8 -*-
import csv
import os
import sys
import pandas as pd
import numpy as np
import datetime, calendar, time
import pickle
import random
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
import helpfuncs.date as date

train_data =[]
train_delta = []
val_data =[]
val_delta = []
test_data =[]
test_delta = []
test_saledate = []
test_buydate = []
test_info = [] # 涨停(bool)|跌停(bool)|股票代码(string)
test_float_profit = []
recent_data =[]
recent_delta = []
recent_saledate = []
recent_buydate = []
recent_info = [] # 涨停(bool)|跌停(bool)|股票代码(string)
recent_float_profit = []

def normalize_local(data_):
    data_price = np.concatenate((data_[:,0:5], data_[:,8:12]), axis=1)
    data_price = (data_price-data_price.mean())/data_price.std()
    data_local = data_[:,5:6]
    data_local = preprocessing.scale(data_local)
    data_abs = np.concatenate((data_[:, 6:8], data_[:, 12:]), axis=1)
    normalized = np.concatenate((data_price, data_local, data_abs), axis=1)
    if np.max(np.abs(data_abs)) >= 25 or np.max(np.abs(normalized)) > 30:
        print '%s, %d'%(str(np.max(np.abs(data_abs), axis=0)),np.argmax(np.max(np.abs(data_abs), axis=0)))
        return None
    return normalized[::-1,:].astype(np.float32)

def loadMarketData(file_path):
    market_file_path = file_path + 'csvData_marketNoSubnew/market.csv'
    globals()['market_data'] =pd.DataFrame.from_csv(market_file_path)
    globals()['market_data'].index = market_data['TRADE_DT']
    return market_data

def loadStockData(file_path, codefile):
    basic_file_path = file_path + 'csvData_basic/' + codefile
    derivative_file_path = file_path + 'csvData_derivativeNoHalt/' + codefile
    if os.path.isfile(derivative_file_path) == False:
        print 'derivative data don\'t exist, skipped!\n'
        return None, None

    basic_data = pd.DataFrame.from_csv(basic_file_path)
    derivative_data = pd.DataFrame.from_csv(derivative_file_path)

    basic_data['S_DQ_AVGPRICE'] = basic_data['S_DQ_AVGPRICE']*basic_data['S_DQ_ADJFACTOR']
    basic_data.index = basic_data['TRADE_DT']
    derivative_data.index = derivative_data['TRADE_DT']

    return basic_data, derivative_data

def checkValidData(data, T):
    valid = True
    if np.min(data[T:,5])==0. or np.isnan(np.sum(data)):
        valid = False
    for i in range(len(data)-1):
        if (data[i, 1] - data[i+1, 3])/data[i+1, 3] > 0.106 or (data[i, 2] - data[i+1, 3])/data[i+1, 3] < -0.106:
            valid = False
            break
    return valid

def checkStrong(data):
    for i in range(10):
        if data[i,6]*5>10 and (data[i,1]-data[i+1,3])/data[i+1,3]:
            return True
        if data[i, 20]>np.log(5) and (data[i,1]-data[i+1,3])/data[i+1,3]:
            return True
    return False

def processFile(file_path, codefile, id_, start_date, end_date, phase, DATA_LENGTH, T, maxhalt=12):
    basic_data, derivative_data = loadStockData(file_path, codefile)
    if derivative_data is None:
        return 0
    ########################## prepare data ############################
    basicList = ['S_DQ_ADJOPEN', 'S_DQ_ADJHIGH', 'S_DQ_ADJLOW', 'S_DQ_ADJCLOSE', 'S_DQ_AVGPRICE',
                    'S_DQ_AMOUNT', 'S_DQ_TURN']
    derivativeList = ['TURNOVER_STD_10', 'MA_5', 'MA_10', 'MA_30', 'MA_60',
                    'BIAS_5', 'BIAS_10', 'BIAS_30', 'BIAS_60',
                    'PSY_5', 'PSY_10', 'PSY_20', 'PSY_60', 'RSI_5', 'RSI_10', 'VR_5',
                    'TopOverCurrent_20','TopOverCurrent_125','TopDistance_20','TopDistance_125',
                    'MA5_GT_MA20_10',]
    marketList = ['AVGDELTA','AVGTURNOVER','UPSTOCKRATIO_0','UPSTOCKRATIO_5','DOWNSTOCKRATIO_5',
                  'TurnoverQuintile_1','TurnoverQuintile_2','TurnoverQuintile_3','TurnoverQuintile_4',
                  'VRQuintile_1','VRQuintile_2','VRQuintile_3','VRQuintile_4']
    if len(basic_data) == 0:
        return 0

    basic_data = basic_data[['TRADE_DT']+basicList]
    for derivative in derivativeList:
        basic_data[derivative] = derivative_data[derivative]
    if len(market_data)>0 and len(basic_data)>100:
        for market in marketList:
            basic_data[market] = market_data[market]
    else:
        return 0
    
    turnover_arr = basic_data['S_DQ_TURN'].copy().as_matrix()
    vr_arr = basic_data['VR_5'].copy().as_matrix()
    basic_data['S_DQ_TURN'] /= 5
    basic_data['TopOverCurrent_20'] -= 1
    basic_data['TopOverCurrent_125'] -= 1
    basic_data['VR_5'] = np.log(basic_data['VR_5'].astype(float))

    data = basic_data.as_matrix()[:, 1:]
    date_arr = basic_data['TRADE_DT'].as_matrix()
    date_arr = date_arr.astype(int).astype(str)
    length = len(data)
    print 'length: %d'%length
    if length < DATA_LENGTH+T:
        print 'too short, skipped!\n'
        return 0
    ############################ process ############################
    counter = 0
    for i in xrange(length-DATA_LENGTH-T-1):
        if length-i-T<=100:
            continue
        ############################## checks ##################################
        strt = i+T+DATA_LENGTH
        end = i+T+1
        if date_arr[i] > end_date or date_arr[i] < start_date:
            continue
        if checkValidData(data[i:strt+1], T) == False:
            continue
        normed_data = normalize_local(data[end:strt+1])
        if normed_data is None:
            continue

        ########################################################################
        if phase == 'test' or phase == 'recent':
            buy_date = date_arr[i+T]
            #mean amount for the last 3 days
            mean_amount = np.mean(data[end:end+3, 5])
            #limit down when selling / determine the actual sale date
            first_profit = (data[i+T,0]-data[end,3])/data[end,3]
            if first_profit > 0.0988:
                continue
            last_profit = (data[i,3]-data[i+1,3])/data[i+1,3]
            limit_down = last_profit<=-0.0988
            suspend = data[i,6]==0
            if limit_down or suspend:
                k = i-1
                while abs(data[k,1]-data[k,2])<=0.00001 and k>=0:
                    k -= 1
                if k<0:
                    continue
                sale_date = date_arr[k]
                delta = (data[k,4]-data[i+T,4])/data[i+T,4]
            else:
                sale_date = date_arr[i]
                delta = (data[i,4]-data[i+T,4])/data[i+T,4]
            strong = checkStrong(data[end:strt+1])
            float_profit = [(data[i+T-t,3]-data[i+T,4])/data[i+T,4] for t in range(T)]
            globals()[phase+'_data'].append(normed_data)
            globals()[phase+'_delta'].append(delta)
            globals()[phase+'_saledate'].append(sale_date)
            globals()[phase+'_buydate'].append(buy_date)
            globals()[phase+'_info'].append([mean_amount, limit_down, id_, strong])
            globals()[phase+'_float_profit'].append(float_profit)

        elif phase == 'train':
            if np.min(data[i:i+T+1,5])==0:
                continue
            delta = (data[i,4]-data[i+T,4])/data[i+T,4]
            delta -= market_data['AVGAADELTA_5'][int(date_arr[i])]
            #delta /= market_data['STDAADELTA_5'][int(date_arr[i])]
            globals()[phase+'_data'].append(normed_data)
            globals()[phase+'_delta'].append(delta)
            globals()[phase+'_turnover'].append(turnover_arr[i:i+T+1])
            globals()[phase+'_vr'].append(vr_arr[i:i+T+1])
        counter += 1
    print '%d data processed'%counter
    return counter

def saveData(dest_path, phase):
    print 'writing %s data...'%phase
    print '---- shape: ' + str(np.array(globals()[phase+'_data']).shape)
    np.save(dest_path+phase+'Data' + '.npy', globals()[phase+'_data'])
    del globals()[phase+'_data']
    print 'writing %s delta...'%phase
    np.save(dest_path+phase+'Delta' + '.npy', globals()[phase+'_delta'])
    del globals()[phase+'_delta']
    if phase == 'test' or phase == 'recent':
        print 'writing %s infos...'%phase
        np.save(dest_path+phase+'SaleDate' + '.npy', globals()[phase+'_saledate'])
        np.save(dest_path+phase+'BuyDate' + '.npy', globals()[phase+'_buydate'])
        np.save(dest_path+phase+'Info' + '.npy', globals()[phase+'_info'])
        np.save(dest_path+phase+'FloatProfit' + '.npy', globals()[phase+'_float_profit'])
        del globals()[phase+'_saledate']
        del globals()[phase+'_buydate']
        del globals()[phase+'_info']
    if phase == 'train':
        print 'writing %s infos...'%phase
        np.save(dest_path+phase+'Turnover' + '.npy', globals()[phase+'_turnover'])
        np.save(dest_path+phase+'VR' + '.npy', globals()[phase+'_vr'])

if __name__ == '__main__':
    DATA_LENGTH = int(sys.argv[2])
    T = 5
    phase = sys.argv[1]
    current_dir = os.path.dirname(os.path.realpath(__file__))

    if phase == 'train':
        start_date = '20050101'
        end_date = '20160630'
    elif phase == 'test':
        start_date = '20160630'
        end_date = '20170330'
    elif phase == 'recent':
        start_date = '20161231'
        end_date = '20171231'
    src_path = '/home/yingyang/DeepQuant/data/'
    dest_path = '%s_pydata_L%d_T%d/'%(phase, DATA_LENGTH, T)
    src_path = os.path.join(current_dir, src_path)
    if os.path.exists(dest_path) == False:
        os.mkdir(dest_path)

    counter = 0
    start_time = time.time()
    num = 0
    length = len(os.listdir(src_path+'csvData_basic/'))

    loadMarketData(src_path)
    for codefile in os.listdir(src_path+'csvData_basic/'):
        print codefile
        num += 1
        print '%d out of %d'%(num, length)
        counter += processFile(src_path, codefile, int(codefile.split('.')[0]), start_date, end_date, phase, DATA_LENGTH, T)
        print 'totally %d data\n'%counter
        duration = time.time() - start_time
        print 'done. {}s used.\n'.format(duration)

    saveData(dest_path, phase)
