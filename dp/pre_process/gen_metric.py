#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from dp.common import *

MAList = [5, 10, 20, 30, 60, 125]
EMAList = [5, 10, 20, 30, 60, 125]
BIASList = [5, 10, 20, 30, 60, 125]
MTMList = [1, 5, 10, 20, 30, 60, 125]
PSYList = [5, 10, 20, 30, 60, 125]
RSIList = [5, 10, 20, 30, 60, 125]
VRList = [5]  # volume ratio
OCDELTAList = [1, 4]  # T + n
AADELTAList = [5]  # T + n
OODELTAList = [1]  # T + n
TSTDList = [10]  # turnover std
TopOverCurrentList = [20, 60, 125]
TopDistanceList = [20, 60, 125]
MA5_GT_MA20List = [10]


def ComputeMA(stock, metric):
    stock.sort_values('TRADE_DT', inplace=True)
    for ma in MAList:
        stock['MA_' + str(ma)] = \
            pd.Series.rolling(stock['S_DQ_ADJCLOSE'], window=ma).mean()
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for ma in MAList:
        metric['MA_' + str(ma)] = stock['MA_' + str(ma)]


def ComputeEMA(stock, metric):
    stock.sort_values('TRADE_DT', inplace=True)
    for ema in EMAList:
        stock['EMA_' + str(ema)] = \
            pd.Series.ewm(stock['S_DQ_ADJCLOSE'], span=ema).mean()
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for ema in EMAList:
        metric['EMA_' + str(ema)] = stock['EMA_' + str(ema)]


def ComputeBIAS(stock, metric):
    for bias in BIASList:
        stock['BIAS_' + str(bias)] \
            = (stock['S_DQ_ADJCLOSE'] - stock['MA_' + str(bias)]) / stock['MA_' + str(bias)]

        metric['BIAS_' + str(bias)] = stock['BIAS_' + str(bias)]


def ComputeMTM(stock, metric):
    for mtm in MTMList:
        adjClosePre = stock['S_DQ_ADJCLOSE'][mtm:].reset_index(drop=True)
        stock['MTM_' + str(mtm)] = \
            (stock['S_DQ_ADJCLOSE'] - adjClosePre) / adjClosePre

        metric['MTM_' + str(mtm)] = stock['MTM_' + str(mtm)]


def ComputePSY(stock, metric):
    stock.sort_values('TRADE_DT', inplace=True)
    for psy in PSYList:
        stock['PSY_' + str(psy)] = \
            pd.Series.rolling(stock[stock > 0]['MTM_1'], window=psy).count() / psy
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for psy in PSYList:
        metric['PSY_' + str(psy)] = stock['PSY_' + str(psy)][:-psy]


def ComputeRSI(stock, metric):
    stock.sort_values('TRADE_DT', inplace=True)
    for rsi in RSIList:
        n1 = pd.Series.rolling(stock[stock > 0]['MTM_1'].fillna(0), window=rsi)
        n2 = pd.Series.rolling(stock[stock < 0]['MTM_1'].fillna(0), window=rsi)
        stock['RSI_' + str(rsi)] = 1 - 1 / (1 - n1.sum() / n2.sum())
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for rsi in RSIList:
        metric['RSI_' + str(rsi)] = stock['RSI_' + str(rsi)][:-rsi]


def ComputeVR(stock, metric):
    stock['VOLUME_PREV'] = stock['S_DQ_VOLUME'][1:].reset_index(drop=True)

    stock.sort_values('TRADE_DT', inplace=True)
    for vr in VRList:
        n1 = pd.Series.rolling(stock['VOLUME_PREV'].replace(0, np.nan), window=vr)
        stock['VR_' + str(vr)] = stock['S_DQ_VOLUME'] / n1.mean()
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for vr in VRList:
        metric['VR_' + str(vr)] = stock['VR_' + str(vr)]


def ComputeOCDELTA(stock, metric):
    for OCDELTA in OCDELTAList:
        adjOpenPre = stock['S_DQ_ADJOPEN'][OCDELTA:].reset_index(drop=True)
        stock['OCDELTA_' + str(OCDELTA)] = (stock['S_DQ_ADJCLOSE'] - adjOpenPre) / adjOpenPre

        metric['OCDELTA_' + str(OCDELTA)] = stock['OCDELTA_' + str(OCDELTA)]


def ComputeAADELTA(stock, metric):
    stock['ADJAVGPRICE'] = stock['S_DQ_AVGPRICE'] * stock['S_DQ_ADJFACTOR']

    for AADELTA in AADELTAList:
        adjAvgPre = stock['ADJAVGPRICE'][AADELTA:].reset_index(drop=True)
        stock['AADELTA_' + str(AADELTA)] = (stock['ADJAVGPRICE'] - adjAvgPre) / adjAvgPre

        metric['AADELTA_' + str(AADELTA)] = stock['AADELTA_' + str(AADELTA)]


def ComputeOODELTA(stock, metric):
    for OODELTA in OODELTAList:
        adjOpenPre = stock['S_DQ_ADJOPEN'][OODELTA:].reset_index(drop=True)
        stock['OODELTA_' + str(OODELTA)] = (stock['S_DQ_ADJOPEN'] - adjOpenPre) / adjOpenPre

        metric['OODELTA_' + str(OODELTA)] = stock['OODELTA_' + str(OODELTA)]


def ComputeTSTD(stock, metric):
    stock.sort_values('TRADE_DT', inplace=True)
    for tstd in TSTDList:
        stock['TURNOVER_STD_' + str(tstd)] \
            = pd.Series.rolling(stock['S_DQ_TURN'], window=tstd).std()
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for tstd in TSTDList:
        metric['TURNOVER_STD_' + str(tstd)] = stock['TURNOVER_STD_' + str(tstd)]


def ComputeTopOverCurrent(stock, metric):
    stock.sort_values('TRADE_DT', inplace=True)
    for toc in TopOverCurrentList:
        n1 = pd.Series.rolling(stock['S_DQ_ADJHIGH'], window=toc)
        stock['TopOverCurrent_' + str(toc)] = n1.max() / stock['S_DQ_ADJCLOSE']
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for toc in TopOverCurrentList:
        metric['TopOverCurrent_' + str(toc)] = stock['TopOverCurrent_' + str(toc)]


def ComputeTopDistance(stock, metric):
    stock.sort_values('TRADE_DT', inplace=True)
    for td in TopDistanceList:
        n1 = pd.Series.rolling(stock['S_DQ_ADJHIGH'], window=td).apply(np.argmax)
        stock['TopDistance_' + str(td)] = n1 / td

    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for td in TopDistanceList:
        metric['TopDistance_' + str(td)] = stock['TopDistance_' + str(td)]


def ComputeMA5_GT_MA20(stock, metric):
    stock['MA_5_minus_MA_20'] = stock['MA_5'] - stock['MA_20']

    stock.sort_values('TRADE_DT', inplace=True)
    for gt in MA5_GT_MA20List:
        stock['MA5_GT_MA20_' + str(gt)] = pd.Series.rolling(
            stock[stock > 0]['MA_5_minus_MA_20'], window=gt).count() / gt
    stock.sort_values('TRADE_DT', ascending=False, inplace=True)

    for gt in MA5_GT_MA20List:
        metric['MA5_GT_MA20_' + str(gt)] = stock['MA5_GT_MA20_' + str(gt)][:-gt]


def HandleData(st_code, no_halt=False):
    stock = pd.read_csv(os.path.join(BASIC_DATA, st_code), parse_dates=[0])

    if no_halt:
        stock = stock[stock['S_DQ_VOLUME'] > 0].reset_index(drop=True)

    if stock.empty:
        print st_code
        return

    metric = pd.DataFrame(stock['TRADE_DT'])

    ComputeMA(stock, metric)
    ComputeEMA(stock, metric)
    ComputeBIAS(stock, metric)
    ComputeMTM(stock, metric)
    ComputePSY(stock, metric)
    ComputeRSI(stock, metric)
    ComputeVR(stock, metric)
    ComputeOCDELTA(stock, metric)
    ComputeAADELTA(stock, metric)
    ComputeOODELTA(stock, metric)
    ComputeTSTD(stock, metric)
    ComputeTopOverCurrent(stock, metric)
    ComputeTopDistance(stock, metric)
    ComputeMA5_GT_MA20(stock, metric)

    assert not metric.empty, st_code
    metric['TRADE_DT'] = metric['TRADE_DT'].dt.strftime('%Y%m%d')

    if no_halt:
        tgt = os.path.join(NO_HALT_METRIC_DATA, st_code)
    else:
        tgt = os.path.join(METRIC_DATA, st_code)

    metric.to_csv(tgt, index=False)


if __name__ == '__main__':
    if not os.path.exists(NO_HALT_METRIC_DATA):
        os.mkdir(NO_HALT_METRIC_DATA)
    if not os.path.exists(METRIC_DATA):
        os.mkdir(METRIC_DATA)

    st_list = sorted(os.listdir(BASIC_DATA))
    try:
        no_halt = int(sys.argv[1])
    except:
        no_halt = False
    with TimeLog("metric, "):
        for st in tqdm(st_list):
            HandleData(st, no_halt)
