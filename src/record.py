# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/23"

from common import *

class Record:
    def __init__(self):
        df = pd.read_pickle("1.pkl")
        del df['tun'], df['pb_lf'], df['pe_ttm'], df['shares'], df['ma']
        del df['open'], df['low'], df['high']
        self.df = df
        
        self.get_daily_cap()
        
        self.ans = []
        keys = set(df.index.get_level_values('id'))
        for key in keys:
            self.parse_st(key)
            return
    
    def get_daily_cap(self):
        self.cap = {}
        df = self.df
        keys = set(df.index.get_level_values('date'))
        for key in keys:
            dt = df.xs(key, level='date')
            cap = (dt['close'] * dt['vol']).sum()
            self.cap[key] = cap
    
    @staticmethod
    def parse_target(ary):
        p = (ary[1:] / ary[:-1] - 1) * 100 + 10
        p = np.concatenate([[0], p])
        p[p < 0] = 0
        p = np.floor(p / 4)
        p = p.astype(int)
        p[p == 5] = 4
        return p
    
    @staticmethod
    def get_stats(ary):
        ary = (ary - ary.mean()) / ary.std()
        # s0 = scipy.stats.skew(ary)
        # s1 = scipy.stats.kurtosis(ary)
        return ary
    
    def parse_st(self, key):
        df = self.df
        st = df.xs(key, level='id')
        st = st.dropna()
        st['capital'] = st['close'] * st['vol']
        st['target'] = self.parse_target(st['close'].get_values())
        del st['close'], st['vol']
        step = 10
        print len(st)
        for i in range(0, len(st) - step):
            swing = np.array([st.iloc[i + _, 0] for _ in range(step)])
            swing_ex = self.get_stats(swing)
            cap = np.array([st.iloc[i + _, 1] for _ in range(step)])
            cap_ex = self.get_stats(cap)
            cap2 = np.array([st.iloc[i + _, 1] / self.cap[st.index[i + _]] for _ in range(step)])
            cap2_ex = self.get_stats(cap2)
            self.ans += [np.concatenate([swing_ex, cap_ex, cap2_ex, [st.iloc[i + step - 1, 2]]])]

if __name__ == '__main__':
    os.chdir("../data")
    rd = Record()
    print len(rd.ans)
    print rd.ans[0]
    print rd.ans[10]
    print rd.ans[100]
    print rd.ans[400]
