import numpy as np
import os
import time
import datetime
import csv
import logging
import pickle
from pylab import *

import matplotlib.pyplot as plt

from keras.models import Model
from keras.optimizers import SGD
from keras.regularizers import l2
from keras.layers import *
from keras.layers.convolutional import *
from keras.layers.normalization import BatchNormalization
from keras.models import model_from_json
from keras.utils import np_utils
import keras.backend as K

import helpfuncs.date as date
import helpfuncs.finance as finance
from helpfuncs.ChooseChannel import ChooseChannel
from models import *


def init_log(save_path, phase='test'):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(current_dir, save_path + '%s.log' % phase)
    if os.path.exists(log_path):
        os.remove(log_path)
    logger = logging.getLogger(phase)
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


def load_data(datadir, phase):
    print 'loading test data'
    globals()['test_data'] = np.load(datadir + '%sData.npy'%phase)
    print 'loading test delta'
    globals()['test_delta'] = np.load(datadir + '%sDelta.npy'%phase)
    print 'loading test date'
    globals()['test_saledate'] = np.load(datadir + '%sSaleDate.npy'%phase)
    globals()['test_buydate'] = np.load(datadir + '%sBuyDate.npy'%phase)
    print 'loading test info'
    globals()['test_info'] = np.load(datadir + '%sInfo.npy'%phase)
    globals()['test_float_profit'] = np.load(datadir + '%sFloatProfit.npy'%phase)


def load_index(filedir):
    csvfile = open(filedir)
    csvfile.readline()
    reader = csv.reader(csvfile)
    index_dict_first= dict()
    index_dict_last = dict()
    for line in reader:
        date_str = date.datetostr(date.strtodatetime(line[0], '%Y-%m-%d'))
        index_dict_first[date_str] = float(line[1])
        index_dict_last[date_str] = float(line[3])
    return index_dict_first, index_dict_last


def process_predictions(pred, N, test_start_day, test_end_day):
    logger = logging.getLogger('test')
    maxNp = dict()
    maxNi = dict()
    sumP = dict()
    sumRealProfit = dict()
    date_num = dict()
    total = pred.shape[0]
    pos_total = 0.0
    processed_total = 0.0
    oneday = datetime.timedelta(days=1)
    for i in xrange(0, total):
        current_date = test_buydate[i]
        if date.datediff(test_start_day, current_date) < 0 or date.datediff(current_date, test_end_day) < 0:
            continue
        regression = pred[i][0]
        signal = regression
        processed_total += 1
        if test_delta[i] > 0:
            pos_total += 1
        if sumP.has_key(current_date):
            sumP[current_date] += signal
            sumRealProfit[current_date] += test_delta[i]
            date_num[current_date] += 1
        else:
            sumP[current_date] = signal
            sumRealProfit[current_date] = test_delta[i]
            date_num[current_date] = 1
        if test_info[i][0] > 50000.0:
            p = signal
            if maxNp.has_key(current_date) == False:
                maxNp[current_date] = [p]
                maxNi[current_date] = [i]
            else:
                insert_flag = False
                for k in xrange(len(maxNp[current_date])):
                    if p > maxNp[current_date][k]:
                        maxNp[current_date].insert(k, p)
                        maxNi[current_date].insert(k, i)
                        insert_flag = True
                        break
                if insert_flag == False:
                    maxNp[current_date].append(p)
                    maxNi[current_date].append(i)
                if len(maxNp[current_date]) > N:
                    maxNp[current_date].pop()
                    maxNi[current_date].pop()

    logger.info('pos/total: %f' % (pos_total / processed_total))
    return maxNp, maxNi, sumP, sumRealProfit, date_num

def compute_profits(maxNp, maxNi, N, RankStart, RankEnd, sumP, sumRealProfit, date_num, cost, interval, test_start_day, test_end_day, threshold, delta_scale, index_dict_first, index_dict_last):
    logger = logging.getLogger('test')
    loss_logger = logging.getLogger('loss')
    gain_logger = logging.getLogger('gain')
    logger.info('--------------------------------------')
    # compute every day profit
    format = "%Y%m%d"
    current_day = date.strtodatetime(test_start_day, format)
    oneday = datetime.timedelta(days=1)
    total_day = date.datediff(date.datetostr(current_day), test_end_day) + 1
    net_arr = np.ones((total_day))
    index_arr = np.ones((total_day))
    hedged_arr = np.ones((total_day))
    meanpredchosen_arr = np.zeros((total_day))
    realprof_arr = np.zeros((total_day))
    marketprof_arr = np.zeros((total_day))
    index_init = 0.
    current_profit = 1.0
    day = 1
    trade_day = 0
    valid_all = 0
    pos = 0.
    neg = 0.
    sum_win = 0.
    sum_lose= 0.
    limit_down = 0.
    mean_amount = 0.
    holding_stocks = []
    cash = [1. / (1 + interval)] * (1 + interval)
    it = 0
    float_profit = 0.0
    while date.datediff(date.datetostr(current_day), test_end_day) != 0:
        day_str = date.datetostr(current_day)
        logger.info('date:' + day_str)
        logger.info('buying: ')
        logger.info('current cash: ' + str(cash))
        # get mean prediction
        if sumP.has_key(day_str):
            mean_pred = sumP[day_str] / date_num[day_str]
        else:
            mean_pred = 0.
        if sumRealProfit.has_key(day_str):
            market_profit = sumRealProfit[day_str] / date_num[day_str]
        else:
            market_profit = 0.
        if maxNi.has_key(day_str):
            mean_pred_chosen = np.mean(maxNp[day_str])/delta_scale
        else:
            mean_pred_chosen = 0.
        logger.info('mean prediction: ' + str(mean_pred / delta_scale))
        logger.info('mean prediction chosen: ' + str(mean_pred_chosen))
        if index_arr[day] != index_arr[day - 1] and sumP.has_key(day_str):
            trade_day += 1
        # get position
        position = 1
        if mean_pred_chosen <= threshold[0]:
            position = 0
        elif mean_pred_chosen > threshold[1]:
            position = 1
        else:
            position = (mean_pred_chosen -
                        threshold[0]) / (threshold[1] - threshold[0])
        logger.info('today\'s position: ' + str(position))
        # get the market index at begining
        if index_init == 0:
            if index_dict_first.has_key(day_str):
                index_init = index_dict_first[day_str]
        # compute accumulated index
        if index_dict_last.has_key(day_str):
            index_arr[day] = index_dict_last[day_str] / index_init
        else:
            index_arr[day] = index_arr[day - 1]
        # buy
        real_prof = 0.0
        today_limitdown = 0.0
        if maxNi.has_key(day_str) and position > 0.:
            today_amount = 0.0
            rank = 0
            for (i, p) in zip(maxNi[day_str][RankStart:RankEnd], maxNp[day_str][RankStart:RankEnd]):
                rank += 1
                info = test_info[i]
                amount = position * (cash[it] if day > (interval + 1) else 1. / (interval + 1))
                amount /= (RankEnd - RankStart)
                logger.info('buying code: %06d' % info[2] + ', pred: %.5f' % (p / delta_scale) + ', amount: %.5f' % amount 
                            + ', last 3 day mean amount:%.4f'%(info[0]/10) + ', limit down:%d'%int(info[1]))
                holding_stocks.append((i, amount, day_str, it, trade_day))
                today_amount += amount
                mean_amount += info[0]/10
                # statistics
                valid_all += 1
                d = test_delta[i]
                real_prof += d
                if d-cost > 0:
                    pos += 1
                    sum_win += d-cost
                if d-cost < 0:
                    neg += 1
                    sum_lose += d-cost
                if info[1]:
                    limit_down += 1
                    today_limitdown += 1
            cash[it] -= today_amount
            real_prof /= (RankEnd - RankStart)
            it += 1
            it = it % (interval + 1)
            logger.info('pred and real: %f %f'%(mean_pred_chosen, real_prof))
            logger.info('today limit down: %d'%today_limitdown)
        # sell
        logger.info('selling: ')
        today_profit = 0.0
        remove_buffer = []
        for (i, amt, buy_date, this_it, buy_day) in holding_stocks:
            if test_saledate[i] == day_str:
                delta = test_delta[i] - cost
                if test_delta[i] <= -0.05:
                    loss_logger.info('code: %06d'%test_info[i][2] + ', delta: %.5f' % delta  + ', bought on ' + buy_date + ', sold on ' + day_str)
                if test_delta[i] >= 0.05:
                    gain_logger.info('code: %06d'%test_info[i][2] + ', delta: %.5f' % delta  + ', bought on ' + buy_date + ', sold on ' + day_str)
                logger.info('selling code: %06d' % test_info[i][2] + ', delta: %.5f' % delta + ', amount: %.5f' % amt
                            + ', position number: %d' % this_it
                            + ', bought on: ' + buy_date + ' limit_down:' + str(test_info[i][1]))
                today_profit += amt * delta
                cash[this_it] += amt * (1 + delta)
                remove_buffer.append((i, amt, buy_date, this_it, buy_day))
        for (i, amt, buy_date, this_it, buy_day) in remove_buffer:
            holding_stocks.remove(((i, amt, buy_date, this_it, buy_day)))
        float_profit = np.sum([test_float_profit[i][min(trade_day-buy_day, interval-1)]*amt for (i, amt, buy_date, this_it, buy_day) in holding_stocks])
        meanpredchosen_arr[day] = mean_pred_chosen
        realprof_arr[day] = real_prof
        marketprof_arr[day] = market_profit
        # compute accumulated profit
        current_profit += today_profit
        net = current_profit + float_profit
        net_arr[day] = net

        # compute hedged profit and print all profit data
        hedged_arr[day] = 1 + (net_arr[day] - index_arr[day])
        logger.info('current float profit: %f'%(float_profit))
        logger.info('today net profit: ' + str(net_arr[day]/net_arr[day-1] - 1))
        logger.info('today index profit: ' +
                    str(index_arr[day] / index_arr[day - 1] - 1.))
        logger.info('net: ' + str(net))
        logger.info('index: ' + str(index_arr[day]))
        logger.info('hedged: ' + str(hedged_arr[day]))
        day += 1
        current_day = current_day + oneday
        logger.info('--------------------------------------')
    logger.info('Pos: ' + str(pos / valid_all) + ' Neg: ' + str(neg / valid_all))
    logger.info('Pos average profit: ' + str(sum_win / pos) + ' Neg average profit: ' + str(sum_lose / neg))
    logger.info('Correlation: ' + str(np.corrcoef(meanpredchosen_arr,realprof_arr)[0][1]))
    logger.info('Sharpe Ratio: raw=%f, hedged=%f' %
                (finance.SharpeRatio(net_arr), finance.SharpeRatio(hedged_arr)))
    logger.info('Max Retreat: raw=%f, hedged=%f' %
                (finance.MaxRetreat(net_arr), finance.MaxRetreat(hedged_arr)))
    logger.info('3 day mean amount %f'%(mean_amount/valid_all))
    logger.info('limit down: ' + str(limit_down))
    logger.info('valid_all: ' + str(valid_all))
    diff = realprof_arr-marketprof_arr
    diff = diff[np.nonzero(diff)] - cost
    WinRate = float(len(diff[diff>0]))/float(np.count_nonzero(diff))
    logger.info( 'Daily win rate: %f'%WinRate )
    plt.bar(np.arange(0, len(diff)), diff, color='r')
    plt.xlabel('days')
    plt.ylabel('diff')
    figPath = os.path.join(current_dir, save_path + '/WinRate.png')
    savefig(figPath)
    return net_arr, index_arr, hedged_arr


def test_all(modelset, save_path, data_path, phase, interval, data_length, test_start_day, test_end_day, index,
             threshold=[-0.01, 0.01], cost=0.0015, N=20, RankStart=0, RankEnd=50, delta_scale=20., recompute=False):
    index_dir = '/home/yingyang/DeepQuant/data/index/%s.csv'%index
    logger = logging.getLogger('test')

    # load data and index
    load_data(data_path, phase)
    logger.info('loading index')
    index_dict_first, index_dict_last = load_index(index_dir)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    pred_path = os.path.join(current_dir, save_path + '/pred.npy')
    if recompute == False and os.path.isfile(pred_path):
        mean_pred = np.load(pred_path)
    else:
        # process each model
        mean_pred = []
        nb_model = 0
        for model_name, model_list in modelset.items():
            for model_num in model_list:
                logger.info('processing model %s %d' % (model_name, model_num))
                # load model
                file_path = 'L%d/' % data_length + '%s/'%model_name + '%s' % model_num + '_T%d/' % interval
                model_path = os.path.join(current_dir, file_path + '/model.json')
                #model = globals()[model_name](data_length=15, nb_channel=39, weight_decay=0.001)
                #f = open(model_path, 'w')
                #model_json = model.to_json()
                #f.write(model_json)
                #f.close
                #continue
                f = open(model_path, 'r')
                model_json = f.read()
                f.close
                weight_path = os.path.join(current_dir, file_path + '/weight.hdf5')
                model = model_from_json(model_json, {'ChooseChannel': ChooseChannel})
                model.load_weights(weight_path)
                # calculate all predictions
                pred = model.predict(test_data, batch_size=1024, verbose=1)
                if len(pred)>1 and len(pred)<10:
                    pred = pred[0]
                if len(mean_pred) == 0:
                    mean_pred = np.array(pred)
                else:
                    mean_pred += np.array(pred)
                K.clear_session()
                nb_model += 1
        mean_pred /= nb_model
        np.save(pred_path, mean_pred)

    # process the predictions into dictionaries
    logger.info('processing...')
    maxNp, maxNi, sumP, sumRealProfit, date_num = process_predictions(
        mean_pred, N, test_start_day, test_end_day)

    output = open(os.path.join(current_dir, save_path + '/maxNi.pkl'), 'wb')
    pickle.dump(maxNi, output)
    output.close()
    test_records = []
    maxNcode = {}
    for buydate in maxNi:
        for i in maxNi[buydate]:
            saledate = test_saledate[i]
            delta = test_delta[i]
            code = '%06d'%test_info[i][2]
            if maxNcode.has_key(buydate):
                maxNcode[buydate].append(code)
            else:
                maxNcode[buydate] = [code]
            test_records.append([code, buydate, saledate, delta])
    output = open(os.path.join(current_dir, save_path + '/maxNcode.pkl'), 'wb')
    pickle.dump(maxNcode, output)
    output.close()
    np.save((os.path.join(current_dir, save_path + '/test_records.npy')), np.array(test_records))
    # compute every day profit
    net_arr, market_arr, hedged_arr = compute_profits(maxNp, maxNi, N, RankStart, RankEnd, sumP, sumRealProfit, date_num, cost, interval,
                                                         test_start_day, test_end_day, threshold, delta_scale, index_dict_first, index_dict_last)
    np.save(os.path.join(current_dir, save_path + '/profit.npy'), net_arr)
    np.save(os.path.join(current_dir, save_path + '/hedged_%s.npy'%index), hedged_arr)
    np.save(os.path.join(current_dir, save_path + '/%s.npy'%index), market_arr)

    _, ax1 = plt.subplots()
    days = date.datediff(test_start_day, test_end_day) + 1
    ax1.plot(np.arange(0, days), net_arr, 'b', label='ours')
    ax1.plot(np.arange(0, days), market_arr, 'g', label='index')
    ax1.plot(np.arange(0, days), hedged_arr, 'r', label='hedged')
    ax1.set_xlabel('days')
    ax1.set_ylabel('profit')
    ax1.legend(loc='upper left')
    figPath = os.path.join(current_dir, save_path + '/%s_%s_threshold_%.3f_%.3f_%d_%s.png' %
                           (test_start_day, test_end_day, threshold[0], threshold[1], N, index))
    savefig(figPath)
    logger.info('bye')
    return


if __name__ == '__main__':
    recompute = False
    phase = sys.argv[1]
    index = 'zh500'
    data_length = 15
    interval = 5
    cost = 0.0015# + 0.004
    RankStart = int(sys.argv[2])
    RankEnd   = int(sys.argv[3])
    N = RankEnd
    delta_scale = 10.
    #threshold = [0, 0]
    threshold = [-100, -100]
    modelset = {
                'ThinConv1Fc4': [2,3,5],
                'WideConv1Fc4': [4,6,7],
                'ThinConv1Fc5': [8],
                'ExpMarketGuidedThinConv1Fc4': [4],
                'ThinConv1Fc4_withoutMA': [4,5],
                'ThinConv1Lstm1':[6],
                'ThinConv2Lstm1':[2],
                }
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if phase == 'test':
        test_start_day = '20160701'
        test_end_day = '20170101'
    elif phase == 'recent':
        #recompute = True
        test_start_day = '20170213'
        test_end_day = '20170317'
    data_path = "data/%s_pydata_L%d_T%d/" % (phase, data_length, interval)
    data_path = os.path.join(current_dir, data_path)

    #save_path = 'L%d/' % data_length + phase + '_L%d' % data_length + '+'.join(modelset) + '/'
    save_path = 'L%d/' % data_length + phase + '_all/'
    if os.path.exists(os.path.join(current_dir, save_path)) == False:
        os.mkdir(os.path.join(current_dir, save_path))

    init_log(save_path + test_start_day + '_' + test_end_day +
             '_%d_%d_%d_%s_' % (RankStart, RankEnd, N, index))
    init_log(save_path, 'loss')
    init_log(save_path, 'gain')
    test_all(modelset, save_path, data_path, phase, interval, data_length, test_start_day, test_end_day, index,
             threshold, cost, N, RankStart, RankEnd, delta_scale, recompute=recompute)
