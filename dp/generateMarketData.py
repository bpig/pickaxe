#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import csv
import datetime, calendar
import time
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

stockDataPathList = ['csvData_basic//',
                     'csvData_derivative//']
marketDataPath = 'csvData_market//'

deltaDict = {}
turnoverDict = {}
freeTurnoverDict = {}
ocDeltaDict = {}
aa5DeltaDict = {}
ooDeltaDict = {}
vrDict = {}

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


def SeparateByDate(oneStockDict, usedDict):
    for date in oneStockDict:
        if np.isnan(oneStockDict[date]):
            continue
        if date not in usedDict:
            usedDict[date] = []
        usedDict[date].append(oneStockDict[date])


def HandleEachStockData(fileName):
    frames = []
    for stockDataPath in stockDataPathList:
        oneFileData = pd.read_csv(os.path.join(stockDataPath, fileName), parse_dates=[1], index_col=[1]).drop(
            'Unnamed: 0', axis=1)
        frames.append(oneFileData)
    stockData = pd.concat(frames, axis=1, join_axes=[frames[0].index])

    # remove halt
    stockData = stockData[stockData['S_DQ_VOLUME'] > 0]

    SeparateByDate(stockData['MTM_1'].to_dict(), deltaDict)
    SeparateByDate(stockData['S_DQ_TURN'].to_dict(), turnoverDict)
    SeparateByDate(stockData['S_DQ_FREETURNOVER'].to_dict(), freeTurnoverDict)
    SeparateByDate(stockData['OCDELTA_1'].to_dict(), ocDeltaDict)
    SeparateByDate(stockData['AADELTA_5'].to_dict(), aa5DeltaDict)
    SeparateByDate(stockData['OODELTA_1'].to_dict(), ooDeltaDict)
    SeparateByDate(stockData['VR_5'].to_dict(), vrDict)


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

    dataNameList = ['TRADE_DT',
                    'AVGDELTA', 'AVGTURNOVER', 'AVGFREETURNOVER', 'UPSTOCKRATIO_0', 'UPSTOCKRATIO_5',
                    'DOWNSTOCKRATIO_5',
                    'TurnoverQuintile_1', 'TurnoverQuintile_2', 'TurnoverQuintile_3', 'TurnoverQuintile_4',
                    'VRQuintile_1', 'VRQuintile_2', 'VRQuintile_3', 'VRQuintile_4',
                    'AVGRELATIVEDELTA', 'AVGAADELTA_5', 'AVGOODELTA_1', 'STDOCDELTA_1', 'STDAADELTA_5']
    # print pd.DataFrame.from_dict(avgDeltaDict, orient='index')
    marketData = pd.DataFrame({'AVGDELTA': avgDeltaDict,
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
    marketData['TRADE_DT'] = marketData.index
    marketData.sort_values('TRADE_DT', ascending=False, inplace=True)
    marketData = marketData.reset_index(drop=True).loc[:, dataNameList]

    if len(marketData['TRADE_DT']) > 0:
        # date to int format
        marketData['TRADE_DT'] = marketData['TRADE_DT'].dt.strftime('%Y%m%d')

    marketData.to_csv(os.path.join(marketDataPath, 'market.csv'))


if __name__ == '__main__':
    start_time = time.time()
    for fileName in os.listdir(stockDataPathList[0]):
        print fileName

        HandleEachStockData(fileName)

        duration = time.time() - start_time
        print 'done. {}s used.\n'.format(duration)
    generateMarketData()

    duration = time.time() - start_time
    print 'done. {}s used.\n'.format(duration)
