# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/23"

from src.common import *

class Record:
    def __init__(self):
        df = pd.read_pickle("sh.pkl")
        del df['tun'], df['open'], df['low'], df['high']
        self.df = df
        
        self.get_daily_cap()
        self.ans = []
        keys = set(df.index.get_level_values('id'))
        for c, key in enumerate(keys):
            self.parse_st(key)
            if c % 10 == 0:
                print time.ctime(), c
    
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
        p = np.concatenate([p, [0]])
        p[p < 0] = 0
        p = np.floor(p / 4)
        p = p.astype(int)
        p[p >= 5] = 4
        return p
    
    def dump(self):
        fout = open("test.dump." + str(self.step), "w")
        for r in self.ans:
            r = [str(_) for _ in r]
            fout.write(",".join(r) + "\n")
    
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
        # del st['close'], st['vol']
        
        step = 50
        self.step = step
        
        for i in range(0, len(st) - step - 1):
            ma = np.array([st['ma'][i + _] for _ in range(step)])
            ma_ex = self.get_stats(ma)
            pb_lf = np.array([st['pb_lf'][i + _] for _ in range(step)])
            pe_ttm = np.array([st['pe_ttm'][i + _] for _ in range(step)])
            swing = np.array([st['swing'][i + _] for _ in range(step)])
            swing_ex = self.get_stats(swing)
            cap = np.array([st['capital'][i + _] for _ in range(step)])
            cap_ex = self.get_stats(cap)
            cap2 = np.array([st['capital'][i + _] / self.cap[st.index[i + _]] for _ in range(step)])
            cap2_ex = self.get_stats(cap2)
            vol = np.array([st['vol'][i + _] for _ in range(step)])
            vol_ex = self.get_stats(vol)
            clo = np.array([st['close'][i + _] for _ in range(step)])
            clo_ex = self.get_stats(clo)
            self.ans += [np.concatenate([ma_ex, pb_lf, pe_ttm, swing_ex, cap_ex, cap2_ex, vol_ex, clo_ex,
                                         [st['target'][i + step - 1]]])]

if __name__ == '__main__':
    os.chdir("../data")
    rd = Record()
    print len(rd.ans)
    rd.dump()
