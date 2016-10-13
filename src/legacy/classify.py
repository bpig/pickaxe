# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/23"

# min 1.84e9 sh3909
# max 1.5e12 sh1398
from src.common import *

class Classify:
    def __init__(self):
        sh = pd.read_pickle("sh.pkl")
        self.sh = sh
        sh = sh.xs('20160630', level='date')
        
        value = sh['close'] * sh['shares']
        value.dropna(inplace=True)
        value = value[value != 0]
        value.sort_values(inplace=True)
        level = math.log(value[-1] / 1e9, 3)
        level = int(math.ceil(level))
        self.split_by_level(level, value)
    
    def split_by_level(self, level, value):
        keys = {}
        floor = [1e9 * 3.0 ** _ for _ in range(level)]
        for i in range(level - 1):
            keys[i] = value[(floor[i] <= value) & (value < floor[i + 1])].index
        keys[level - 1] = value[floor[-1] <= value].index
        self.floor = floor
        self.keys = keys
    
    def get_by_level(self, level):
        df = None
        for key in self.keys[level]:
            print key
            tp = self.sh.loc[self.sh.index.get_level_values('id') == key, :].copy()
            if df is None:
                df = tp
            else:
                df = pd.concat([df, tp])
            print len(df)
        df.to_pickle("../data/1.pkl")
        return df

if __name__ == '__main__':
    os.chdir("../data")
    cl = Classify()
    cl.get_by_level(1)
