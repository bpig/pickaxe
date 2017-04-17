import numpy as np
import os
import sys
import time
import datetime
import logging
from pylab import *
import matplotlib.pyplot as plt
from sklearn import preprocessing
import tushare as ts
import pandas as pd
import pickle

from keras.models import Model
from keras.optimizers import SGD
from keras.regularizers import l2
from keras.layers import *
from keras.layers.convolutional import *
from keras.layers.normalization import BatchNormalization
from keras.models import model_from_json
from keras.utils.visualize_util import plot
from keras.utils import np_utils

import helpfuncs.date as date
from data.generate_pydata import *
from helpfuncs.ChooseChannel import ChooseChannel

def init_log(save_path, pred_date):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(current_dir, save_path+'/'+pred_date+'_model1.6.0.docx')
    if os.path.exists(log_path):
        os.remove(log_path)
    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

def load_predData(data_path, data_length, pred_date):
    basicList = ['S_DQ_ADJOPEN', 'S_DQ_ADJHIGH', 'S_DQ_ADJLOW', 'S_DQ_ADJCLOSE', 'S_DQ_AVGPRICE',
                    'S_DQ_AMOUNT', 'S_DQ_TURN']
    derivativeList = ['TURNOVER_STD_10', 'MA_5', 'MA_10', 'MA_30', 'MA_60',
                        'PSY_5', 'PSY_10', 'RSI_5', 'RSI_10']
    additionalList=['TopOverCurrent_20','TopOverCurrent_125','TopDistance_20','TopDistance_125',
                    'MA5_GT_MA20_10',
                    'RootMTM_5','ACC_R_20','IV_A_20','IV_E_20', 'Z_SCORE', 'Z_SCORE_FREE',
                    'VROC_12', 'VRSI_6', 'VR_26', 'VOLUME_RATIO_5', 'VMACD_DIF_12', 'VMACD_DEA_26']
    marketList = ['AVGDELTA','AVGTURNOVER','UPSTOCKRATIO_0','UPSTOCKRATIO_5','DOWNSTOCKRATIO_5',
                  'MA5_GT_MA10_GT_MA20_Ratio','MA5_LT_MA10_LT_MA20_Ratio']

    market_data = loadMarketData(data_path)
    
    last_date = ''
    data_all = []
    code_all = []
    mean_amount_all = []
    today = date.datetostr(datetime.date.today())
    for codefile in os.listdir(data_path+'csvData_basic/'):
        code = codefile.split('.')[0]
        if int(code) > 0 and int(code)<700000:
            basic_data, derivative_data, additional_data = loadStockData(data_path, codefile)
            if additional_data is None:
                continue
            print code
            
            basic_data = basic_data[['TRADE_DT']+basicList]
            for derivative in derivativeList:
                basic_data[derivative] = derivative_data[derivative]
            for additional in additionalList:
                basic_data[additional] = additional_data[additional]
            if len(market_data)>0 and len(basic_data)>100:
                for market in marketList:
                    basic_data[market] = market_data[market]
            else:
                continue
            basic_data['S_DQ_TURN'] /= 5
            basic_data['TopOverCurrent_20'] -= 1
            basic_data['TopOverCurrent_125'] -= 1
            basic_data['ACC_R_20'] *= 50.
            basic_data['IV_A_20'] *= 100.
            basic_data['IV_E_20'] *= 50.
            basic_data['VROC_12'] = np.log(basic_data['VROC_12'].astype(float)/100 + 1)
            basic_data['VRSI_6'] /= 100.
            basic_data['VR_26'] = np.log(basic_data['VR_26'].astype(float))
            basic_data['VOLUME_RATIO_5'] = np.log(basic_data['VOLUME_RATIO_5'].astype(float))
            dates = basic_data['TRADE_DT'].as_matrix()
            dates = dates.astype(int).astype(str)

            for i in xrange(0, len(dates)):
                if date.datediff(dates[i], pred_date, format='%Y%m%d')>0:
                    last_i = i
                    break
            if len(basic_data)-last_i-1 < 100:
                continue
            if last_date == '':
                last_date = dates[last_i]
            elif date.datediff(last_date, dates[last_i], format='%Y%m%d') > 0:
                last_date = dates[last_i]
            elif date.datediff(last_date, dates[last_i], format='%Y%m%d') < 0:
                continue
            data = basic_data.as_matrix()[:, 1:]
            if checkValidData(data[last_i:last_i+data_length], 0) == False:
                continue

            if data.shape[0] >= last_i+data_length:
                mean_amount = np.mean(data[last_i:last_i+3, 5])
                if mean_amount <= 100000.:
                    continue
                data_local = normalize_local(data[last_i:last_i+data_length])
                if data_local is None:
                    continue
                data_all.append(data_local)
                code_all.append(code)
                mean_amount_all.append(mean_amount)
                print len(data_all)
    return np.array(data_all), code_all, mean_amount_all

def process_predictions(pred, code_all, mean_amount_all, N):
    maxNp = []
    maxNCodes=[]
    maxNmeanamount = []
    mean_pred = np.sum(pred) / pred.shape[0]
    for i in xrange(0, N):
        tempi = np.argmax(pred)
        maxNp.append(pred[tempi])
        maxNCodes.append(code_all[tempi])
        maxNmeanamount.append(mean_amount_all[tempi])
        pred = np.delete(pred, tempi, axis=0)
        code_all = np.delete(code_all, tempi, axis=0)
    return maxNp, maxNCodes, mean_pred, maxNmeanamount

def predict(modelset, threshold, delta_scale, dataset, data_length, pred_date, interval, data_path):
    logger = logging.getLogger('test')
    data_all, code_all, mean_amount_all = load_predData(data_path, data_length, pred_date)
    #process each model
    current_dir = os.path.dirname(os.path.realpath(__file__))
    total_pred = []
    nb_model = 0
    for model_name, model_list in modelset.items():
        for model_num in model_list:
        #load model
            print 'processing model %s %d' % (model_name, model_num)
            file_path = 'L%d/' % data_length + '%s/'%model_name + '%s' % model_num + '_T%d/' % interval
            model_path = os.path.join(current_dir, file_path +'/model.json')
            f = open(model_path, 'r')
            model_json = f.read()
            f.close
            weight_path = os.path.join(current_dir, file_path+'/weight.hdf5')
            model = model_from_json(model_json, {'ChooseChannel': ChooseChannel})
            model.load_weights(weight_path)
            model.compile(optimizer='sgd', loss='mean_squared_error')
            #calculate all predictions
            pred = model.predict(data_all, batch_size=256, verbose=1)
            if len(pred)>1 and len(pred)<10:
                pred = pred[0]
            if len(total_pred) == 0:
                total_pred = pred
            else:
                total_pred += pred
            K.clear_session()
            nb_model += 1
    total_pred /= nb_model

    maxNp, maxNCodes, mean_pred, maxNmeanamount = process_predictions(total_pred, code_all, mean_amount_all, N)
    mean_pred /= delta_scale
    mean_pred_chosen = np.mean(maxNp[:N/2])/delta_scale
    position = 1
    if mean_pred_chosen < threshold[0]:
        position = 0
    elif mean_pred_chosen > threshold[1]:
        position = 1
    else:
        position = (mean_pred_chosen - threshold[0])/(threshold[1]-threshold[0])

    logger.info('average prediction: %f'%mean_pred)
    logger.info('average prediction of chosen: %f'%mean_pred_chosen)
    logger.info('position: %f'%position)
    counter = 0
    for code,p in zip(maxNCodes, maxNp):
        counter += 1
        logger.info('#%d code: %s pred: %f'%(counter, code, p/delta_scale))
        if counter == N/2:
            logger.info('\n\n\n')

    for i in xrange(N):
        maxNCodes[i] = '="%s"'%maxNCodes[i]
    csv_path = os.path.join(current_dir, 'predictions/'+'/'+pred_date+'_model1.5.1.csv')
    M1 = {'code':maxNCodes[:N/2], 'pred':(np.squeeze(maxNp[:N/2])/delta_scale).astype(str)}
    df1 = pd.DataFrame(M1, index=range(1, N/2+1))
    M2 = {'code':maxNCodes[N/2:], 'pred':(np.squeeze(maxNp[N/2:])/delta_scale).astype(str)}
    df2 = pd.DataFrame(M2, index=range(N/2+1, N+1))
    df = pd.concat([df1, pd.DataFrame([['',''],['',''],['','']],index=['','',''],columns=['code','pred']), df2])
    df.to_csv(csv_path)
    print 'mean amount: %f'%(np.mean(maxNmeanamount))


if __name__ == '__main__':
    with open(os.path.expanduser("~/.keras/keras.json"), "w") as fh:
        fh.write('{ "image_dim_ordering": "tf", "epsilon": 1e-07, "floatx": "float32", "backend": "tensorflow" }')
    dataset = 2
    interval = 1
    N = 100
    data_length = 15
    delta_scale = 20.0
    threshold = [0.00, 0.00]
    pred_date = sys.argv[1]
    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_path = '/home/yingyang/DeepQuant/data/'
    modelset = {
                'ThinConv1Lstm1':   [3,5],
                'WideConv1Lstm1':   [7],
                'ThinConv2Lstm1':   [1,],
                'WideConv2Lstm1':   [1,2,4,8],
                'ThinConv1Fc4': [2],
                'ExpFuse4Conv1Fc4': [5],
                'ExpSepConv1Lstm1': [2],
                'ExpVolumeGuidedConv1Lstm1': [1],
                'ThinBranch4Conv1MergeLstm1': [1,3],
                'mtThinConv1Lstm1': [],
                'mtThinConv2Lstm1': [1,2],
                'mtWideConv1Lstm1': [2],
                'mtWideConv2Lstm1': [],
                }
    if os.path.exists(os.path.join(current_dir, 'predictions/')) == False:
        os.mkdir(os.path.join(current_dir, 'predictions/'))
    init_log('predictions/', pred_date)

    predict(modelset, threshold, delta_scale, dataset, data_length, pred_date, interval, data_path)

    with open(os.path.expanduser("~/.keras/keras.json"), "w") as fh:
        fh.write('{ "image_dim_ordering": "tf", "epsilon": 1e-07, "floatx": "float32", "backend": "tensorflow" }')
