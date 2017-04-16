# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/3"

from src.common import *

class Stats:
    def __init__(self, pkl):
        self.df = pd.read_pickle(pkl)
        self.nameCoder = NameCoder()
    
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
        self.allPrice.to_pickle("sh_price.pkl")
    
    def oneStock(self, key, c):
        '''one stock trend'''
        ax = c / 3, c % 3
        s = self.df.xs(key, level="id").copy()
        s['trade'] = np.log(s["close"] * s["vol"])
        s['close'] = np.log(s["close"] * 1e7)
        # s['trade'] = (s['trade'] - s['trade'].min()) / (s['trade'].max() - s['trade'].min())
        # s['close'] = (s['close'] - s['close'].min()) / (s['close'].max() - s['trade'].min())
        
        corr = s['trade'].corr(s['close'])
        cov = s['trade'].cov(s['close'])
        corr2 = (s['trade'] - s['close']).abs().sum()
        
        # s['trade'] = (s['trade'] - s['trade'].mean()) / s['trade'].std()
        # s['close'] = (s['close'] - s['close'].mean()) / s['close'].std()
        s[['trade', 'close']].plot(title=key + " p-%.2f corr-%.2f corr2-%.2f cov-%.2f"
                                               % (s['trade'].sum(), corr, corr2, cov),
                                   ax=axes[ax])
    
    def oneTarget(self, key, c):
        '''one stock trend'''
        ax = c / 3, c % 3
        s = self.df.xs(key, level="id").copy()
        
        i = s.index
        o1 = pd.Series(s['open'][1:].get_values(), index=i[1:])
        dst = 'close'
        # s[dst] = o1
        s['trade'] = s["close"] * s["vol"] / 1e8
        # s[dst] = np.log(s["o1"] * 1e7)
        s = s[1:]
        
        # s['trade'] = (s['trade'] - s['trade'].mean()) / s['trade'].std()
        # s[dst] = (s[dst] - s[dst].mean()) / s[dst].std()
        
        corr = s['trade'].corr(s[dst])
        cov = s['trade'].cov(s[dst])
        
        s[[dst]]['20150501':'20150731'].plot(title=key + " p-%.2f corr-%.2f cov-%.2f"
                                                         % (s['trade'].sum(), corr, cov),
                                             ax=axes[ax])

def normal(df, vol):
    df[vol] = (df[vol] - df[vol].mean()) / df[vol].std()

if __name__ == '__main__':
    os.chdir("../macro")
    # st = Stats("sh.pkl")
    
    sh = pd.read_pickle("sh.pkl")
    s4 = sh.xs('sh4', level="id")
    s4 = s4[-30:]
    normal(s4, 'close')
    normal(s4, 'vol')
    s4[['close', 'vol']].plot()
    plt.show()
    
    # fig, axes = plt.subplots(nrows=2, ncols=3)
    # for c, s in enumerate(st.nameCoder.name(4, 10)):
    #     # st.oneStock(s, c)
    #     st.oneTarget(s, c)
    # plt.show()
    # exit(1)
    # price = pd.read_pickle("sh_price.pkl")
    # price['all'] = (price['all'] - price['all'].mean()) / price['all'].std()
    # price['trade'] = (price['trade'] - price['trade'].mean()) / price['trade'].std()
    #
    # corr = price['all'].corr(price['trade'])
    # cov = price['all'].cov(price['trade'])
    # price.plot(title="corr-%.2f, cov-%.2f" % (corr, cov))
    # plt.show()
