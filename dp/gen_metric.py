#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from common import *

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


def ComputeMA(stockData, derivativeData):
    stockData.sort_values('TRADE_DT', inplace=True)
    for ma in MAList:
        stockData['MA_' + str(ma)] = \
            pd.Series.rolling(stockData['S_DQ_ADJCLOSE'], window=ma).mean()
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for ma in MAList:
        derivativeData['MA_' + str(ma)] = stockData['MA_' + str(ma)]


def ComputeEMA(stockData, derivativeData):
    stockData.sort_values('TRADE_DT', inplace=True)
    for ema in EMAList:
        stockData['EMA_' + str(ema)] = \
            pd.Series.ewm(stockData['S_DQ_ADJCLOSE'], span=ema).mean()
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for ema in EMAList:
        derivativeData['EMA_' + str(ema)] = stockData['EMA_' + str(ema)]


def ComputeBIAS(stockData, derivativeData):
    for bias in BIASList:
        stockData['BIAS_' + str(bias)] \
            = (stockData['S_DQ_ADJCLOSE'] - stockData['MA_' + str(bias)]) / stockData['MA_' + str(bias)]

        derivativeData['BIAS_' + str(bias)] = stockData['BIAS_' + str(bias)]


def ComputeMTM(stockData, derivativeData):
    for mtm in MTMList:
        adjClosePre = stockData['S_DQ_ADJCLOSE'][mtm:].reset_index(drop=True)
        stockData['MTM_' + str(mtm)] = \
            (stockData['S_DQ_ADJCLOSE'] - adjClosePre) / adjClosePre

        derivativeData['MTM_' + str(mtm)] = stockData['MTM_' + str(mtm)]


def ComputePSY(stockData, derivativeData):
    stockData.sort_values('TRADE_DT', inplace=True)
    for psy in PSYList:
        stockData['PSY_' + str(psy)] = \
            pd.Series.rolling(stockData[stockData > 0]['MTM_1'], window=psy).count() / psy
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for psy in PSYList:
        derivativeData['PSY_' + str(psy)] = stockData['PSY_' + str(psy)][:-psy]


def ComputeRSI(stockData, derivativeData):
    stockData.sort_values('TRADE_DT', inplace=True)
    for rsi in RSIList:
        n1 = pd.Series.rolling(stockData[stockData > 0]['MTM_1'].fillna(0), window=rsi)
        n2 = pd.Series.rolling(stockData[stockData < 0]['MTM_1'].fillna(0), window=rsi)
        stockData['RSI_' + str(rsi)] = 1 - 1 / (1 - n1.sum() / n2.sum())
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for rsi in RSIList:
        derivativeData['RSI_' + str(rsi)] = stockData['RSI_' + str(rsi)][:-rsi]


def ComputeVR(stockData, derivativeData):
    stockData['VOLUME_PREV'] = stockData['S_DQ_VOLUME'][1:].reset_index(drop=True)

    stockData.sort_values('TRADE_DT', inplace=True)
    for vr in VRList:
        n1 = pd.Series.rolling(stockData['VOLUME_PREV'].replace(0, np.nan), window=vr)
        stockData['VR_' + str(vr)] = stockData['S_DQ_VOLUME'] / n1.mean()
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for vr in VRList:
        derivativeData['VR_' + str(vr)] = stockData['VR_' + str(vr)]


def ComputeOCDELTA(stockData, derivativeData):
    for OCDELTA in OCDELTAList:
        adjOpenPre = stockData['S_DQ_ADJOPEN'][OCDELTA:].reset_index(drop=True)
        stockData['OCDELTA_' + str(OCDELTA)] = (stockData['S_DQ_ADJCLOSE'] - adjOpenPre) / adjOpenPre

        derivativeData['OCDELTA_' + str(OCDELTA)] = stockData['OCDELTA_' + str(OCDELTA)]


def ComputeAADELTA(stockData, derivativeData):
    stockData['ADJAVGPRICE'] = stockData['S_DQ_AVGPRICE'] * stockData['S_DQ_ADJFACTOR']

    for AADELTA in AADELTAList:
        adjAvgPre = stockData['ADJAVGPRICE'][AADELTA:].reset_index(drop=True)
        stockData['AADELTA_' + str(AADELTA)] = (stockData['ADJAVGPRICE'] - adjAvgPre) / adjAvgPre

        derivativeData['AADELTA_' + str(AADELTA)] = stockData['AADELTA_' + str(AADELTA)]


def ComputeOODELTA(stockData, derivativeData):
    for OODELTA in OODELTAList:
        adjOpenPre = stockData['S_DQ_ADJOPEN'][OODELTA:].reset_index(drop=True)
        stockData['OODELTA_' + str(OODELTA)] = (stockData['S_DQ_ADJOPEN'] - adjOpenPre) / adjOpenPre

        derivativeData['OODELTA_' + str(OODELTA)] = stockData['OODELTA_' + str(OODELTA)]


def ComputeTSTD(stockData, derivativeData):
    stockData.sort_values('TRADE_DT', inplace=True)
    for tstd in TSTDList:
        stockData['TURNOVER_STD_' + str(tstd)] \
            = pd.Series.rolling(stockData['S_DQ_TURN'], window=tstd).std()
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for tstd in TSTDList:
        derivativeData['TURNOVER_STD_' + str(tstd)] = stockData['TURNOVER_STD_' + str(tstd)]


def ComputeTopOverCurrent(stockData, derivativeData):
    stockData.sort_values('TRADE_DT', inplace=True)
    for toc in TopOverCurrentList:
        n1 = pd.Series.rolling(stockData['S_DQ_ADJHIGH'], window=toc)
        stockData['TopOverCurrent_' + str(toc)] = n1.max() / stockData['S_DQ_ADJCLOSE']
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for toc in TopOverCurrentList:
        derivativeData['TopOverCurrent_' + str(toc)] = stockData['TopOverCurrent_' + str(toc)]


def ComputeTopDistance(stockData, derivativeData):
    stockData.sort_values('TRADE_DT', inplace=True)
    for td in TopDistanceList:
        n1 = pd.Series.rolling(stockData['S_DQ_ADJHIGH'], window=td).apply(np.argmax)
        stockData['TopDistance_' + str(td)] = n1 / td

    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for td in TopDistanceList:
        derivativeData['TopDistance_' + str(td)] = stockData['TopDistance_' + str(td)]


def ComputeMA5_GT_MA20(stockData, derivativeData):
    stockData['MA_5_minus_MA_20'] = stockData['MA_5'] - stockData['MA_20']

    stockData.sort_values('TRADE_DT', inplace=True)
    for gt in MA5_GT_MA20List:
        stockData['MA5_GT_MA20_' + str(gt)] = pd.Series.rolling(
            stockData[stockData > 0]['MA_5_minus_MA_20'], window=gt).count() / gt
    stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

    for gt in MA5_GT_MA20List:
        derivativeData['MA5_GT_MA20_' + str(gt)] = stockData['MA5_GT_MA20_' + str(gt)][:-gt]


def HandleData(st_code, no_halt=False):
    stock = pd.read_csv(os.path.join(BASIC_DATA, st_code), parse_dates=[0])

    if no_halt:
        stock = stock[stock['S_DQ_VOLUME'] > 0].reset_index(drop=True)

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

    assert len(metric['TRADE_DT']) > 0, st_code
    metric['TRADE_DT'] = metric['TRADE_DT'].dt.strftime('%Y%m%d')

    if no_halt:
        metric.to_csv(os.path.join(NO_HALT_METRIC_DATA, st_code))
    else:
        metric.to_csv(os.path.join(METRIC_DATA, st_code))


if __name__ == '__main__':
    st_list = sorted(os.listdir(BASIC_DATA))
    try:
        no_halt = int(sys.argv[1])
    except:
        no_halt = False
    with TimeLog("metric, "):
        for st in tqdm(st_list):
            HandleData(st, no_halt)
