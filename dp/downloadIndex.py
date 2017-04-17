import numpy as np
import os
import datetime
import csv
from pylab import *
import tushare as ts

def strtodatetime(datestr,format):
    return datetime.datetime.strptime(datestr,format)

def datediff(beginDate,endDate):
    format="%Y-%m-%d";
    bd=strtodatetime(beginDate,format)
    ed=strtodatetime(endDate,format)
    delta = ed - bd
    return delta.days

start_date = '2015-04-01'
end_date = '2017-10-12'

current_dir = os.path.dirname(os.path.realpath(__file__))
dest_path = 'index/'

header_list = ['open', 'high', 'close', 'low', 'volume', 'amount']

name = 'zh500'
df = ts.get_hist_data(name, start=start_date, end=end_date, retry_count=5, pause=0.005)
df.to_csv(os.path.join(current_dir, dest_path) + name+'.csv')

name = 'hs300'
df = ts.get_hist_data(name, start=start_date, end=end_date, retry_count=5, pause=0.005)
df.to_csv(os.path.join(current_dir, dest_path) + name+'.csv')
