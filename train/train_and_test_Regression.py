import numpy as np
import os
import sys
import time
import datetime
import csv
import logging
import matplotlib.pyplot as plt
from pylab import *
import pickle

from keras.models import Model
from keras.optimizers import SGD
from keras.regularizers import l2
from keras.layers import *
from keras.models import model_from_json
from keras.utils import plot_model
from keras.utils import np_utils
from keras.callbacks import LearningRateScheduler, EarlyStopping
import keras.backend as K
import tensorflow as tf

import helpfuncs.basic as L
import helpfuncs.date as date
import helpfuncs.finance as finance
from helpfuncs.ChooseChannel import ChooseChannel
from models import *


def init_log(save_path, name, phase):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(current_dir, save_path + '%s.log' % phase)
    if os.path.exists(log_path):
        os.remove(log_path)
    logger = logging.getLogger(name)
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


def load_data(states, data_length, interval):
    for state in states:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        DATA_DIR = "data/%s_pydata_L%d_T%d/" % (state, data_length, interval)
        DATA_DIR = os.path.join(current_dir, DATA_DIR)
        print 'loading %s data' % state
        globals()[state + '_data'] = np.load(DATA_DIR + state + 'Data.npy')
        print 'loading %s delta' % state
        globals()[state + '_delta'] = np.load(DATA_DIR + state + 'Delta.npy')
        globals()[state + '_labels'] = np.zeros_like(globals()[state + '_delta'], dtype=np.int32)
        if state == 'test':
            print 'loading test date'
            globals()[state + '_saledate'] = np.load(DATA_DIR + state + 'SaleDate.npy')
            globals()[state + '_buydate'] = np.load(DATA_DIR + state + 'BuyDate.npy')
            print 'loading test info'
            globals()[state + '_info'] = np.load(DATA_DIR + state + 'Info.npy')
            globals()[state + '_float_profit'] = np.load(DATA_DIR + state + 'FloatProfit.npy')
        if state == 'train':
            globals()[state + '_turnover'] = np.load(DATA_DIR + state + 'Turnover.npy')
            globals()[state + '_vr'] = np.load(DATA_DIR + state + 'VR.npy')


def load_index(filedir):
    csvfile = open(filedir)
    csvfile.readline()
    reader = csv.reader(csvfile)
    index_dict_first = dict()
    index_dict_last = dict()
    for line in reader:
        date_str = date.datetostr(date.strtodatetime(line[0], '%Y-%m-%d'))
        index_dict_first[date_str] = float(line[1])
        index_dict_last[date_str] = float(line[3])
    return index_dict_first, index_dict_last


def train(save_path, interval, data_length, nb_channel, delta_scale=20., lr=0.01, gamma=0.1, n_epochs=[5, 6, 6],
          weight_decay=0.001, batch_size=128):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    states = ['train', 'test']

    init_log(save_path, 'train', 'train')
    logger = logging.getLogger('train')

    # load data
    start_time = time.time()
    load_data(states, data_length, interval)
    duration = time.time() - start_time
    print "{} s to load data".format(duration)
    print np.max(np.abs(train_data))
    print np.mean(np.abs(train_delta))
    print np.std(train_delta)
    # define model and save it
    model = makeModel(data_length=data_length, nb_channel=nb_channel, weight_decay=weight_decay)
    model.summary()
    model_path = os.path.join(current_dir, save_path + "/model.json")
    f = open(model_path, 'w')
    model_json = model.to_json()
    f.write(model_json)
    f.close
    # save image of the model
    img_path = os.path.join(current_dir, save_path + "/model.png")
    plot_model(model, to_file=img_path, show_shapes=True)

    # compute training sample weight
    avgTurnoverList = np.array([max(min(max(turnover) - 5, 3), 1) for turnover in train_turnover])
    avgVRList = np.array([max(min(max(vr) - 3, 3), 1) for vr in train_vr])
    assert len(avgTurnoverList) == len(avgVRList)

    sampleWeight = (avgTurnoverList + avgVRList) / 2
    assert len(sampleWeight) == len(train_data)

    # train
    def lr_scheduler(epoch):
        learning_rate = lr
        ep = epoch
        for n_epoch in n_epochs:
            if ep - n_epoch < 0:
                break
            learning_rate *= gamma
            ep -= n_epoch
        print 'lr: %f' % learning_rate
        return learning_rate

    sgd = SGD(lr=lr, momentum=0.9)
    scheduler = LearningRateScheduler(lr_scheduler)
    model.compile(optimizer=sgd, loss='mse')
    history = model.fit(train_data, train_delta * delta_scale,
                        batch_size=batch_size, epochs=sum(n_epochs), callbacks=[scheduler])
    logger.info(str(dict(zip(history.epoch, history.history['loss']))))

    # save weights
    print 'saving...'
    weightPath = os.path.join(current_dir, save_path + '/weight.hdf5')
    model.save_weights(weightPath, overwrite=True)

    # release memories
    for state in states:
        del globals()[state + '_data']
        del globals()[state + '_delta']

    print 'training finished'
    return


def process_predictions(pred, N, test_start_day, test_end_day, name):
    logger = logging.getLogger(name)
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
        if test_info[i][0] > 0.0:
            p = signal
            if not maxNp.has_key(current_date):
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
                if not insert_flag:
                    maxNp[current_date].append(p)
                    maxNi[current_date].append(i)
                if len(maxNp[current_date]) > N:
                    maxNp[current_date].pop()
                    maxNi[current_date].pop()

    logger.info('pos/total: %f of total: %d' % (pos_total / processed_total, total))
    return maxNp, maxNi, sumP, sumRealProfit, date_num


def compute_profits(maxNp, maxNi, sumP, sumRealProfit, date_num, cost, interval, test_start_day, test_end_day,
                    threshold, delta_scale, index_dict_first, index_dict_last, name, weight=False):
    logger = logging.getLogger(name)
    logger.info('--------------------------------------')
    # compute every day profit
    format = "%Y%m%d"
    current_day = date.strtodatetime(test_start_day, format)
    oneday = datetime.timedelta(days=1)
    total_day = date.datediff(date.datetostr(current_day), test_end_day) + 1
    net_arr = np.ones(total_day)
    index_arr = np.ones(total_day)
    hedged_arr = np.ones(total_day)
    meanpredchosen_arr = np.zeros(total_day)
    realprof_arr = np.zeros(total_day)
    marketprof_arr = np.zeros(total_day)
    index_init = 0.
    current_profit = 1.0
    day = 1
    trade_day = 0
    valid_all = 0
    acc = 0.
    neg = 0.
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
            mean_pred_chosen = np.mean(maxNp[day_str]) / delta_scale
        else:
            mean_pred_chosen = 0.
        logger.info('mean prediction: ' + str(mean_pred / delta_scale))
        logger.info('mean prediction chosen: ' + str(mean_pred_chosen))
        if index_arr[day] != index_arr[day - 1] and sumP.has_key(day_str):
            trade_day += 1

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
        if day_str in maxNi and position > 0.:
            today_amount = 0.0
            rank = 0
            for (i, p) in zip(maxNi[day_str], maxNp[day_str]):
                rank += 1
                info = test_info[i]
                amount = position * \
                         (cash[it] if day > (interval + 1) else 1. / (interval + 1))
                if weight:
                    l = len(maxNi[day_str])
                    amount = amount * (1.0 - (rank - 1) / float(l)) / (float(l) - ((float(l) - 1) / 2.0))
                else:
                    amount /= N
                logger.info(
                    'buying code: %06d' % info[2] + ', pred: %.5f' % (p / delta_scale) + ', amount: %.5f' % amount
                    + ', last 3 day mean amount:%.4f' % (info[0] / 10) + ', limit down:' + str(info[1]))
                holding_stocks.append((i, amount, day_str, it, trade_day))
                today_amount += amount
                mean_amount += info[0] / 10
                # statistics
                valid_all += 1
                d = test_delta[i]
                real_prof += d
                if d - cost > 0:
                    acc += 1
                if d - cost < 0:
                    neg += 1
                if info[1]:
                    limit_down += 1
                    today_limitdown += 1
            cash[it] -= today_amount
            real_prof /= len(maxNi[day_str])
            it += 1
            it = it % (interval + 1)
            logger.info('pred and real: %f %f' % (mean_pred_chosen, real_prof))
            logger.info('today limit down: %d' % today_limitdown)
        # sell
        logger.info('selling: ')
        today_profit = 0.0
        remove_buffer = []
        for (i, amt, buy_date, this_it, buy_day) in holding_stocks:
            if test_saledate[i] == day_str:
                delta = test_delta[i] - cost
                logger.info('selling code: %06d' % test_info[i][2] + ', delta: %.5f' % delta + ', amount: %.5f' % amt
                            + ', position number: %d' % this_it
                            + ', bought on: ' + buy_date + ' limit_down:' + str(test_info[i][1]))
                today_profit += amt * delta
                cash[this_it] += amt * (1 + delta)
                remove_buffer.append((i, amt, buy_date, this_it, buy_day))
        for (i, amt, buy_date, this_it, buy_day) in remove_buffer:
            holding_stocks.remove((i, amt, buy_date, this_it, buy_day))
        float_profit = np.sum(
            [test_float_profit[i][min(trade_day - buy_day, interval - 1)] * amt for (i, amt, buy_date, this_it, buy_day)
             in holding_stocks])
        meanpredchosen_arr[day] = mean_pred_chosen
        realprof_arr[day] = real_prof
        marketprof_arr[day] = market_profit
        # compute accumulated profit
        current_profit += today_profit
        net = current_profit + float_profit
        net_arr[day] = net

        # compute hedged profit and print all profit data
        hedged_arr[day] = 1 + (net_arr[day] - index_arr[day])
        logger.info('today profit: ' + str(today_profit))
        logger.info('float profit: %f' % float_profit)
        logger.info('today index profit: ' +
                    str(index_arr[day] / index_arr[day - 1] - 1.))
        logger.info('net: ' + str(net))
        logger.info('index: ' + str(index_arr[day]))
        logger.info('hedged: ' + str(hedged_arr[day]))
        day += 1
        current_day = current_day + oneday
        logger.info('--------------------------------------')
    logger.info('Pos: ' + str(acc / valid_all) +
                ' Neg: ' + str(neg / valid_all))
    logger.info('Correlation: ' + str(np.corrcoef(meanpredchosen_arr, realprof_arr)[0][1]))
    logger.info('Sharpe Ratio: raw=%f, hedged=%f' %
                (finance.SharpeRatio(net_arr), finance.SharpeRatio(hedged_arr)))
    logger.info('Max Retreat: raw=%f, hedged=%f' %
                (finance.MaxRetreat(net_arr), finance.MaxRetreat(hedged_arr)))
    logger.info('3 day mean amount %f' % (mean_amount / valid_all))
    logger.info(' limit down: ' + str(limit_down))
    logger.info('valid_all: ' + str(valid_all))
    # plt.plot(np.arange(0, day), realprof_arr-marketprof_arr, 'r')
    diff = realprof_arr - marketprof_arr
    diff = diff[np.nonzero(diff)] - cost
    WinRate = float(len(diff[diff > 0])) / float(np.count_nonzero(diff))
    logger.info('Daily win rate: %f' % WinRate)
    '''plt.bar(np.arange(0, len(diff)), diff, color='r')
    plt.xlabel('days')
    plt.ylabel('diff')
    plt.title('WinRate: %f'%WinRate)
    plt.show()'''
    return net_arr, index_arr, hedged_arr


def test(save_path, data_length, interval, test_start_day, test_end_day, name,
         threshold=[0.0, 0.0], cost=0.0015, N=20, delta_scale=20., recompute=False):
    start_time = time.time()
    INDEX_DIR = '/home/yingyang/DeepQuant/data/index/zh500.csv'
    logger = logging.getLogger(name)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    pred_path = os.path.join(current_dir, save_path + 'pred.npy')
    # load data and index, evaluate model
    load_data(['test'], data_length, interval)
    logger.info('loading index')
    index_dict_first, index_dict_last = load_index(INDEX_DIR)

    if not recompute and os.path.isfile(pred_path):
        pred = np.load(pred_path)
    else:
        # load model
        model_path = os.path.join(current_dir, save_path + "/model.json")
        # model = makeModel(data_length=15, nb_channel=39, weight_decay=0.001)
        # f = open(model_path, 'w')
        # model_json = model.to_json()
        # f.write(model_json)
        # f.close
        f = open(model_path, 'r')
        model_json = f.read()
        f.close
        weightPath = os.path.join(current_dir, save_path + '/weight.hdf5')
        model = model_from_json(model_json, {'ChooseChannel': ChooseChannel})
        model.compile(optimizer='sgd', loss='mean_squared_error')
        model.load_weights(weightPath)
        duration = time.time() - start_time
        logger.info("{} s to load model".format(duration))
        # calculate all predictions
        pred = np.array(model.predict(test_data, batch_size=1024, verbose=1))
        np.save(pred_path, pred)

    # process the predictions into dictionaries
    logger.info('processing...')
    print np.max(pred / delta_scale)
    maxNp, maxNi, sumP, sumRealProfit, date_num = process_predictions(
        pred, N, test_start_day, test_end_day, name)
    # compute every day profit
    profit_arr, index_arr, hedged_arr = \
        compute_profits(maxNp, maxNi, sumP, sumRealProfit, date_num, cost, interval,
                        test_start_day, test_end_day, threshold, delta_scale, index_dict_first, index_dict_last, name)
    # np.save(os.path.join(current_dir, save_path + 'profit.npy'), profit_arr)
    # np.save(os.path.join(current_dir, save_path + 'hs300.npy'), index_arr)

    maxNcode = {}
    for buydate in maxNi:
        for i in maxNi[buydate]:
            saledate = test_saledate[i]
            delta = test_delta[i]
            code = '%06d' % test_info[i][2]
            if maxNcode.has_key(buydate):
                maxNcode[buydate].append(code)
            else:
                maxNcode[buydate] = [code]
    output = open(os.path.join(current_dir, save_path + '/maxNcode.pkl'), 'wb')
    pickle.dump(maxNcode, output)
    output.close()

    _, ax1 = plt.subplots()
    days = date.datediff(test_start_day, test_end_day) + 1
    ax1.plot(np.arange(0, days), profit_arr, 'b', label='ours')
    ax1.plot(np.arange(0, days), index_arr, 'g', label='index')
    ax1.plot(np.arange(0, days), hedged_arr, 'r', label='hedged')
    ax1.set_xlabel('days')
    ax1.set_ylabel('profit')
    ax1.legend(loc='upper left')
    figPath = os.path.join(current_dir, save_path + '/%s_%s_threshold_%.3f_%.3f_%d.png' %
                           (test_start_day, test_end_day, threshold[0], threshold[1], N))
    savefig(figPath)
    logger.info('bye')
    return


if __name__ == '__main__':
    with open(os.path.expanduser("~/.keras/keras.json"), "w") as fh:
        fh.write('{ "image_dim_ordering": "tf", "epsilon": 1e-07, "floatx": "float32", "backend": "tensorflow" }')
    phase = sys.argv[1]
    phase_train = phase == 'train'
    test_recompute = phase_train or phase == 'retest'
    data_length = int(sys.argv[2])
    nb_channel = 41
    interval = 5
    cost = 0.0015
    N = 20
    lr = 0.01
    n_epoch = [8, 6, 6, 4]
    weight_decay = 0.001
    batch_size = 2048
    delta_scale = 10.0
    threshold = [-100, -100]
    model_name = sys.argv[3]
    names = sys.argv[4:]
    makeModel = globals()[model_name]
    # makeModel = globals()[name.split('_')[0]]
    test_start_day = '20160701'
    test_end_day = '20170101'

    config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
    session = tf.Session(config=config)
    K.set_session(session)

    for name in names:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        save_path = 'L%d/' % data_length + '%s/' % model_name + '%s' % name + '_T%d/' % interval
        if not os.path.exists(os.path.join(current_dir, 'L%d/' % data_length)):
            os.mkdir(os.path.join(current_dir, 'L%d/' % data_length))
        if not os.path.exists(os.path.join(current_dir, 'L%d/' % data_length + '%s/' % model_name)):
            os.mkdir(os.path.join(current_dir, 'L%d/' % data_length + '%s/' % model_name))
        if not os.path.exists(os.path.join(current_dir, save_path)):
            os.mkdir(os.path.join(current_dir, save_path))
        # train and test
        init_log(save_path + test_start_day + '_' + test_end_day +
                 '_%.3f_%.3f_%d_' % (threshold[0], threshold[1], N), name, 'test')
        if phase_train:
            train(save_path, interval, data_length, nb_channel, delta_scale,
                  lr=lr, n_epochs=n_epoch, weight_decay=weight_decay, batch_size=batch_size)
        test(save_path, data_length, interval, test_start_day, test_end_day, name,
             threshold=threshold, cost=cost, N=N, delta_scale=delta_scale, recompute=test_recompute)
        logging.shutdown()
        K.clear_session()
