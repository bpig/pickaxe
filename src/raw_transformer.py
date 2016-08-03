# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

from common import *

class RawTransformer:
    @staticmethod
    def parseNormal(normal_file):
        normal = pd.read_pickle(normal_file)
        normal = normal.set_index("date")
        ans = None
        bound = len(normal.columns)
        for i in range(0, bound, 6):
            stock = normal.ix[:, i:i + 6].copy()
            stock["id"] = stock.columns[0]
            stock.columns = ["open", "high", "low", "close", "vol", "tun", "id"]
            stock = stock.set_index(["id"], append=True)
            if ans is None:
                ans = stock
            else:
                ans = ans.add(stock, fill_value=0)
        return ans
    
    @staticmethod
    def parseEx(ex_file):
        ex = pd.read_pickle(ex_file)
        bound = len(ex.columns)
        print "trim", bound % 7
        bound = bound / 7 * 7
        ans = None
        print bound
        for i in range(0, bound, 7):
            print i
            stock = ex.ix[:, i:i + 5].copy()
            stock["id"] = stock.columns[0]
            stock.columns = ["ex0", "ex1", "ex2", "ex3", "ex4", "id"]
            stock = stock.set_index(["id"], append=True)
            if ans is None:
                ans = stock
            else:
                ans = ans.add(stock, fill_value=0)
        return ans
        
        # df.index = pd.MultiIndex.from_tuples(index, names = names)
        # df.index.set_levels([u'Total', u'x2'],level=1,inplace=True)
        # df.index.set_labels([0, 1],level=1,inplace=True)
        # s.add(v, fill_value=0)

if __name__ == '__main__':
    rt = RawTransformer()
    # s = rt.parseNormal("../data/sh14_normal.pkl")
    # s.to_pickle("../data/
    print time.ctime()
    s = rt.parseEx("../data/sh14_ex.pkl")
    s.to_pickle("../data/sh14_ex_multindex.pkl")
    print time.ctime()
