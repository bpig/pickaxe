# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

from common import *

class RawTransformer:
    def __init__(self, normal, ex=None):
        self.normal = pd.read_pickle(normal)
        # self.ex = pd.read_pickle(ex)
    
    def ParseNormal(self):
        self.normal = self.normal.set_index("date")
        ans = None
        # for i in range(0, len(self.normal.columns), 6):
        for i in range(0, 12, 6):
            stock = self.normal.ix[:, i:i + 6].copy()
            stock["id"] = stock.columns[0]
            stock.columns = ["open", "high", "low", "close", "vol", "tun", "id"]
            stock = stock.set_index(["id"], append=True)
            if ans is None:
                ans = stock
            else:
                ans = ans.add(stock, fill_value=0)
        return ans[:4]
        # df.index = pd.MultiIndex.from_tuples(index, names = names)
        # df.index.set_levels([u'Total', u'x2'],level=1,inplace=True)
        # df.index.set_labels([0, 1],level=1,inplace=True)
        # s.add(v, fill_value=0)

if __name__ == '__main__':
    rt = RawTransformer("../data/sh14_normal.pkl")
    s = rt.ParseNormal()
    print s
