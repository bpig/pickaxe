from common import *
from tqdm import tqdm

start_date = '2015-01-01'
end_date = '2017-12-31'

# start_date = '2016-12-19'
# end_date = '2017-12-31'

# df = ts.get_stock_basics()
# for code in tqdm(df.index):
#     df = ts.get_k_data(code, start=start_date, end=end_date, index=False, retry_count=5, pause=0.005)
#     df.to_csv("share/%s.csv" % code)

# name = ['000905', '000001']

# df = ts.get_index()
# for code in tqdm(df['code']):
#     df = ts.get_k_data(code, start=start_date, end=end_date, index=True, retry_count=5, pause=0.005)
#     df.to_csv("share/index/%s.csv" % code)

df = ts.get_stock_basics()
for code in tqdm(df.index):
    df = ts.get_k_data(code, ktype='30', retry_count=5, pause=0.005)
    df.to_csv("share/30/%s.csv" % code)
