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

stockDataPathList = ['csvData_basic//']#['E://DeepQuant//raw_data//csvData_updated//']#['csvData_basic//', 'csvData_moneyflow//']
derivativeDataPath = 'csvData_derivativeNoHalt//'#'C://Users//zhangdeng//Downloads//csvData_derivative//'

MAList = [5, 10, 20, 30, 60, 125]
EMAList = [5, 10, 20, 30, 60, 125]
BIASList = [5, 10, 20, 30, 60, 125]
MTMList = [1, 5, 10, 20, 30, 60, 125]
PSYList = [5, 10, 20, 30, 60, 125]
RSIList = [5, 10, 20, 30, 60, 125]
VRList = [5]                         # volume ratio
OCDELTAList = [1, 4]				 # T + n
AADELTAList = [5]					 # T + n
OODELTAList = [1]				 	 # T + n
TSTDList = [10]						 # turnover std
TopOverCurrentList = [20, 60, 125]
TopDistanceList = [20, 60, 125]
MA5_GT_MA20List = [10]

def ComputeMA(stockData, derivativeData):
	stockData.sort_values('TRADE_DT', inplace = True)
	for ma in MAList:
		stockData['MA_' + str(ma)] = pd.Series.rolling(stockData['S_DQ_ADJCLOSE'], window = ma).mean()
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for ma in MAList:
		derivativeData['MA_' + str(ma)] = stockData['MA_' + str(ma)]

def ComputeEMA(stockData, derivativeData):
	stockData.sort_values('TRADE_DT', inplace = True)
	for ema in EMAList:
		stockData['EMA_' + str(ema)] = pd.Series.ewm(stockData['S_DQ_ADJCLOSE'], span = ema).mean()
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for ema in EMAList:
		derivativeData['EMA_' + str(ema)] = stockData['EMA_' + str(ema)]

def ComputeBIAS(stockData, derivativeData):
	for bias in BIASList:
		stockData['BIAS_' + str(bias)] = (stockData['S_DQ_ADJCLOSE'] - stockData['MA_' + str(bias)]) / stockData['MA_' + str(bias)]
		
		derivativeData['BIAS_' + str(bias)] = stockData['BIAS_' + str(bias)]

def ComputeMTM(stockData, derivativeData):
	for mtm in MTMList:
		adjClosePre = stockData['S_DQ_ADJCLOSE'][mtm:].reset_index(drop=True)
		stockData['MTM_' + str(mtm)] = (stockData['S_DQ_ADJCLOSE'] - adjClosePre) / adjClosePre
		
		derivativeData['MTM_' + str(mtm)] = stockData['MTM_' + str(mtm)]

def ComputePSY(stockData, derivativeData):
	stockData.sort_values('TRADE_DT', inplace = True)
	for psy in PSYList:
		stockData['PSY_' + str(psy)] = pd.Series.rolling(stockData[stockData > 0]['MTM_1'], window = psy).count() / psy
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for psy in PSYList:
		derivativeData['PSY_' + str(psy)] = stockData['PSY_' + str(psy)][:-psy]

def ComputeRSI(stockData, derivativeData):
	stockData.sort_values('TRADE_DT', inplace = True)
	for rsi in RSIList:
		stockData['RSI_' + str(rsi)] = 1 - 1 / (1 + pd.Series.rolling(stockData[stockData > 0]['MTM_1'].fillna(0), window = rsi).sum() / -pd.Series.rolling(stockData[stockData < 0]['MTM_1'].fillna(0), window = rsi).sum())
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for rsi in RSIList:
		derivativeData['RSI_' + str(rsi)] = stockData['RSI_' + str(rsi)][:-rsi]

def ComputeVR(stockData, derivativeData):
	stockData['VOLUME_PREV'] = stockData['S_DQ_VOLUME'][1:].reset_index(drop=True)

	stockData.sort_values('TRADE_DT', inplace = True)
	for vr in VRList:
		stockData['VR_' + str(vr)] = (stockData['S_DQ_VOLUME'] / pd.Series.rolling(stockData['VOLUME_PREV'].replace(0, np.nan), window = vr).mean())
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
	stockData.sort_values('TRADE_DT', inplace = True)
	for tstd in TSTDList:
		stockData['TURNOVER_STD_' + str(tstd)] = pd.Series.rolling(stockData['S_DQ_TURN'], window = tstd).std()
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for tstd in TSTDList:
		derivativeData['TURNOVER_STD_' + str(tstd)] = stockData['TURNOVER_STD_' + str(tstd)]

def ComputeTopOverCurrent(stockData, derivativeData):
	stockData.sort_values('TRADE_DT', inplace = True)
	for toc in TopOverCurrentList:
		stockData['TopOverCurrent_' + str(toc)] = pd.Series.rolling(stockData['S_DQ_ADJHIGH'], window = toc).max() / stockData['S_DQ_ADJCLOSE']
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for toc in TopOverCurrentList:
		derivativeData['TopOverCurrent_' + str(toc)] = stockData['TopOverCurrent_' + str(toc)]	

def ComputeTopDistance(stockData, derivativeData):
	stockData.sort_values('TRADE_DT', inplace = True)
	for td in TopDistanceList:
		stockData['TopDistance_' + str(td)] = pd.Series.rolling(stockData['S_DQ_ADJHIGH'], window=td).apply(np.argmax) / td
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for td in TopDistanceList:
		derivativeData['TopDistance_' + str(td)] = stockData['TopDistance_' + str(td)]

def ComputeMA5_GT_MA20(stockData, derivativeData):
	stockData['MA_5_minus_MA_20'] = stockData['MA_5'] - stockData['MA_20']

	stockData.sort_values('TRADE_DT', inplace = True)
	for gt in MA5_GT_MA20List:
		stockData['MA5_GT_MA20_' + str(gt)] = pd.Series.rolling(stockData[stockData > 0]['MA_5_minus_MA_20'], window = gt).count() / gt
	stockData.sort_values('TRADE_DT', ascending=False, inplace=True)

	for gt in MA5_GT_MA20List:
		derivativeData['MA5_GT_MA20_' + str(gt)] = stockData['MA5_GT_MA20_' + str(gt)][:-gt]	

def HandleData(fileName):
	date = pd.read_csv(os.path.join(stockDataPathList[0], fileName), parse_dates=[1])['TRADE_DT']
	stockData = pd.DataFrame({'TRADE_DT': date})

	for stockDataPath in stockDataPathList:
		oneFileData = pd.read_csv(os.path.join(stockDataPath, fileName), parse_dates=[1]).drop('Unnamed: 0', axis = 1)
		stockData = pd.merge(stockData, oneFileData, on = 'TRADE_DT')

	# without halt
	stockData = stockData[stockData['S_DQ_VOLUME'] > 0].reset_index(drop=True)
	derivativeData = pd.DataFrame({'TRADE_DT': stockData['TRADE_DT']})	
	if len(stockData) == 0:
		return

	ComputeMA(stockData, derivativeData)
	ComputeEMA(stockData, derivativeData)
	ComputeBIAS(stockData, derivativeData)
	ComputeMTM(stockData, derivativeData)
	ComputePSY(stockData, derivativeData)
	ComputeRSI(stockData, derivativeData)
	ComputeVR(stockData, derivativeData) 
	ComputeOCDELTA(stockData, derivativeData)
	ComputeAADELTA(stockData, derivativeData)
	ComputeOODELTA(stockData, derivativeData)
	ComputeTSTD(stockData, derivativeData)
	ComputeTopOverCurrent(stockData, derivativeData)
	ComputeTopDistance(stockData, derivativeData)
	ComputeMA5_GT_MA20(stockData, derivativeData)

	if len(derivativeData['TRADE_DT']) > 0:
		# date to int format
		derivativeData['TRADE_DT'] = derivativeData['TRADE_DT'].dt.strftime('%Y%m%d')
	
	derivativeData.to_csv(os.path.join(derivativeDataPath, fileName))

if __name__ == '__main__':
	start_time = time.time()
	for fileName in os.listdir(stockDataPathList[0]):
		print fileName

		HandleData(fileName)

		duration = time.time() - start_time
		print 'done. {}s used.\n'.format(duration)