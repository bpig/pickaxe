# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

from common import *

class RawTransformer:
    @staticmethod
    def parseNormal(normal_file):
        """normal raw to multiindex df"""
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
        """ex raw to multiindex df"""
        ex = pd.read_pickle(ex_file)
        bound = len(ex.columns)
        print "trim", bound % 7
        bound = bound / 7 * 7
        ans = None
        for i in range(0, bound, 7):
            stock = ex.ix[:, i:i + 5].copy()
            stock["id"] = stock.columns[0]
            stock.columns = ["swing", "ma", "shares", "pe_ttm", "pb_lf", "id"]
            stock = stock.set_index(["id"], append=True)
            if ans is None:
                ans = stock
            else:
                ans = ans.add(stock, fill_value=0)
        ans.index.names = ["date", "id"]
        return ans
        
        # df.index = pd.MultiIndex.from_tuples(index, names = names)
        # df.index.set_levels([u'Total', u'x2'],level=1,inplace=True)
        # df.index.set_labels([0, 1],level=1,inplace=True)
        # s.add(v, fill_value=0)
    
    @staticmethod
    def merge(normal_file, ex_file):
        """merge multiindex normal && ex"""
        normal = pd.read_pickle(normal_file)
        ex = pd.read_pickle(ex_file)
        return normal.add(ex, fill_value=0)

if __name__ == '__main__':
    rt = RawTransformer()
    print time.ctime()
    # s = rt.parseNormal("../data/sh14_normal.pkl")
    # s.to_pickle("../data/sh14_normal_multindex.pkl")
    # print time.ctime()
    # s = rt.parseEx("../data/sh14_ex.pkl")
    # s.to_pickle("../data/sh14_ex_multindex.pkl")
    m = rt.merge("../data/sh14_normal_multindex.pkl", "../data/sh14_ex_multindex.pkl")
    m.to_pickle("../data/sh14.pkl")
    print time.ctime()
