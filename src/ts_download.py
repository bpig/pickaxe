# -*- coding: utf-8 -*-
from common import *
from tqdm import tqdm

start_date = '2014-01-01'
end_date = '2017-12-31'

# start_date = '2016-12-19'
# end_date = '2017-12-31'

def getShare():
    df = ts.get_stock_basics()
    for code in tqdm(df.index):
        df = ts.get_k_data(code, start=start_date, end=end_date, 
                           index=False, retry_count=5, pause=0.005)
        df.to_csv("share/%s.csv" % code)

# name = ['000905', '000001']

def getIndex():
    df = ts.get_index()
    for code in tqdm(df['code']):
        df = ts.get_k_data(code, start=start_date, end=end_date, 
                           index=True, retry_count=5, pause=0.005)
        df.to_csv("share/index/%s.csv" % code)

def getK(ktype):
    df = ts.get_stock_basics()
    for code in tqdm(df.index):
        df = ts.get_k_data(code, ktype=ktype, retry_count=5, pause=0.005)
        df.to_csv("share/%s/%s.csv" % (ktype, code))

def getCat():
    os.system("mkdir share/cat")

    df = ts.get_sme_classified()
    df.to_csv("share/cat/zx.csv", encoding='utf-8')

    df = ts.get_gem_classified()
    df.to_csv("share/cat/cy.csv", encoding='utf-8')

    df = ts.get_st_classified()
    df.to_csv("share/cat/st.csv", encoding='utf-8')

    df = ts.get_industry_classified()
    df.to_csv("share/cat/industry.csv", encoding='utf-8')

    df = ts.get_concept_classified()
    df.to_csv("share/cat/concept.csv", encoding='utf-8')

    df = ts.get_area_classified()
    df.to_csv("share/cat/area.csv", encoding='utf-8')

    df = ts.get_hs300s()
    df.to_csv("share/cat/hs300.csv", encoding='utf-8')

    df = ts.get_sz50s()
    df.to_csv("share/cat/sz50.csv", encoding='utf-8')

    df = ts.get_zz500s()
    df.to_csv("share/cat/zz500.csv", encoding='utf-8')

if __name__ == "__main__"    :
    getIndex()
    # getCat()
