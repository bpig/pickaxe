#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from dp.common import *

stock_datas = [BASIC_DATA, METRIC_DATA]

removeSubnew = 3

deltaDict = defaultdict(list)
turnoverDict = defaultdict(list)
freeTurnoverDict = defaultdict(list)
ocDeltaDict = defaultdict(list)
aa5DeltaDict = defaultdict(list)
ooDeltaDict = defaultdict(list)
vrDict = defaultdict(list)

avgDeltaDict = {}
avgTurnoverDict = {}
avgFreeTurnoverDict = {}
upStockRatioDict = {}
upStock5RatioDict = {}
downStock5RatioDict = {}
avgOCDeltaDict = {}
stdOCDeltaDict = {}
avgAA5DeltaDict = {}
stdAA5DeltaDict = {}
avgOODeltaDict = {}

turnoverQuintile_1 = {}
turnoverQuintile_2 = {}
turnoverQuintile_3 = {}
turnoverQuintile_4 = {}
vrQuintile_1 = {}
vrQuintile_2 = {}
vrQuintile_3 = {}
vrQuintile_4 = {}


def collect_by_date(s, kv):
    for date, value in s.iteritems():
        if np.isnan(value):
            continue
        kv[date].append(value)


def HandleEachStockData(st_code, removeSubnew):
    frames = []
    for data in stock_datas:
        oneFileData = pd.read_csv(os.path.join(data, st_code), parse_dates=[0], index_col=[0])
        frames.append(oneFileData)
    stock = pd.concat(frames, axis=1, join_axes=[frames[0].index])

    # remove subnew
    if removeSubnew != 0:
        stock = stock.iloc[:-removeSubnew]

    # remove halt
    stock = stock[stock['S_DQ_VOLUME'] > 0]

    collect_by_date(stock['MTM_1'], deltaDict)
    collect_by_date(stock['S_DQ_TURN'], turnoverDict)
    collect_by_date(stock['S_DQ_FREETURNOVER'], freeTurnoverDict)
    collect_by_date(stock['OCDELTA_1'], ocDeltaDict)
    collect_by_date(stock['AADELTA_5'], aa5DeltaDict)
    collect_by_date(stock['OODELTA_1'], ooDeltaDict)
    collect_by_date(stock['VR_5'], vrDict)


def generateMarketData():
    sortedDeltaDict = [(k, len(deltaDict[k])) for k in sorted(deltaDict.keys())]
    for p in sortedDeltaDict:
        print 'date:', p[0], 'stock num:', p[1]

    for date in deltaDict:
        avgDeltaDict[date] = np.mean(deltaDict[date])
        avgTurnoverDict[date] = np.mean(turnoverDict[date])
        avgFreeTurnoverDict[date] = np.mean(freeTurnoverDict[date])

        upStockRatio = 0.0
        upStock5Ratio = 0.0
        downStock5Ratio = 0.0
        stockNum = len(deltaDict[date])
        for delta in deltaDict[date]:
            if delta >= 0.0:
                upStockRatio += 1
            if delta >= 0.05:
                upStock5Ratio += 1
            if delta <= -0.05:
                downStock5Ratio += 1
        upStockRatio /= stockNum
        upStock5Ratio /= stockNum
        downStock5Ratio /= stockNum

        upStockRatioDict[date] = upStockRatio
        upStock5RatioDict[date] = upStock5Ratio
        downStock5RatioDict[date] = downStock5Ratio

        avgOCDeltaDict[date] = np.mean(ocDeltaDict[date])
        stdOCDeltaDict[date] = np.std(ocDeltaDict[date])
        avgOODeltaDict[date] = np.mean(ooDeltaDict[date])
        if date not in aa5DeltaDict:
            avgAA5DeltaDict[date] = np.nan
            stdAA5DeltaDict[date] = np.nan
        else:
            avgAA5DeltaDict[date] = np.mean(aa5DeltaDict[date])
            stdAA5DeltaDict[date] = np.std(aa5DeltaDict[date])

        stockNum = len(turnoverDict[date])
        sortedTurnover = sorted(turnoverDict[date])
        turnoverQuintile_1[date] = sortedTurnover[4 * stockNum / 5]
        turnoverQuintile_2[date] = sortedTurnover[3 * stockNum / 5]
        turnoverQuintile_3[date] = sortedTurnover[2 * stockNum / 5]
        turnoverQuintile_4[date] = sortedTurnover[stockNum / 5]

        if date not in vrDict:
            vrQuintile_1[date] = np.nan
            vrQuintile_2[date] = np.nan
            vrQuintile_3[date] = np.nan
            vrQuintile_4[date] = np.nan
        else:
            stockNum = len(vrDict[date])
            sortedVR = sorted(vrDict[date])
            vrQuintile_1[date] = sortedVR[4 * stockNum / 5]
            vrQuintile_2[date] = sortedVR[3 * stockNum / 5]
            vrQuintile_3[date] = sortedVR[2 * stockNum / 5]
            vrQuintile_4[date] = sortedVR[stockNum / 5]

    dataNameList = ['TRADE_DT', 'AVGDELTA', 'AVGTURNOVER',
                    'AVGFREETURNOVER', 'UPSTOCKRATIO_0',
                    'UPSTOCKRATIO_5', 'DOWNSTOCKRATIO_5',
                    'TurnoverQuintile_1', 'TurnoverQuintile_2',
                    'TurnoverQuintile_3', 'TurnoverQuintile_4',
                    'VRQuintile_1', 'VRQuintile_2', 'VRQuintile_3',
                    'VRQuintile_4', 'AVGRELATIVEDELTA', 'AVGAADELTA_5',
                    'AVGOODELTA_1', 'STDOCDELTA_1', 'STDAADELTA_5']

    market = pd.DataFrame({'AVGDELTA': avgDeltaDict,
                           'AVGTURNOVER': avgTurnoverDict,
                           'AVGFREETURNOVER': avgFreeTurnoverDict,
                           'UPSTOCKRATIO_0': upStockRatioDict,
                           'UPSTOCKRATIO_5': upStock5RatioDict,
                           'DOWNSTOCKRATIO_5': downStock5RatioDict,
                           'TurnoverQuintile_1': turnoverQuintile_1,
                           'TurnoverQuintile_2': turnoverQuintile_2,
                           'TurnoverQuintile_3': turnoverQuintile_3,
                           'TurnoverQuintile_4': turnoverQuintile_4,
                           'VRQuintile_1': vrQuintile_1,
                           'VRQuintile_2': vrQuintile_2,
                           'VRQuintile_3': vrQuintile_3,
                           'VRQuintile_4': vrQuintile_4,
                           'AVGRELATIVEDELTA': avgOCDeltaDict,
                           'AVGAADELTA_5': avgAA5DeltaDict,
                           'AVGOODELTA_1': avgOODeltaDict,
                           'STDOCDELTA_1': stdOCDeltaDict,
                           'STDAADELTA_5': stdAA5DeltaDict
                           })
    market['TRADE_DT'] = market.index
    market.sort_values('TRADE_DT', ascending=False, inplace=True)
    market = market.reset_index(drop=True).loc[:, dataNameList]

    assert not market.empty
    market['TRADE_DT'] = market['TRADE_DT'].dt.strftime('%Y%m%d')

    market.to_csv(os.path.join(MARKET_DATA, 'market.csv'), index=False)


if __name__ == '__main__':
    if not os.path.exists(MARKET_DATA):
        os.mkdir(MARKET_DATA)

    stocks = sorted(os.listdir(BASIC_DATA))
    with TimeLog("handle each stock, "):
        for st_code in tqdm(stocks):
            HandleEachStockData(st_code, removeSubnew)

    with TimeLog("gen market data"):
        generateMarketData()
