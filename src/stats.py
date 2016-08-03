# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/3"

from common import *

class Stats:
    def __init__(self, pkl):
        self.df = pd.read_pickle(pkl)
    
    def allPrice(self):
        '''total price of market, total trade of market'''
        dt = {}
        values = sorted(list(set(self.df.index.get_level_values("date"))))
        for key in values:
            one_day = self.df.xs(key, level="date")
            price0 = (one_day["open"] * one_day["shares"]).sum() / 1e12
            price1 = (one_day["open"] * one_day["vol"]).sum() / 1e11
            dt[key] = (price0, price1)
        self.allPrice = pd.DataFrame(data=dt.values(), index=dt.keys(), columns=['all', 'trade'])
        self.allPrice.to_pickle("../data/sh14_price.pkl")
    
    def oneStock(self, key):
        '''one stock trend'''
        s = self.df.xs(key, level="id").copy()
        s['trade'] = (s["open"] * s["vol"]) / 1e8
        s[['trade', 'open']].plot(title=key)

if __name__ == '__main__':
    st = Stats("../data/sh14.pkl")
    for s in ['sh4', 'sh5', 'sh6']:
        st.oneStock(s)
    plt.show()
