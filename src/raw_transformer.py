# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/2"

from common import *

class RawTransformer:
    def __init__(self, normal, ex):
        self.normal = pd.read_pickle(normal)
        self.ex = pd.read_pickle(ex)
    
    def ParseNormal(self):
        self.normal = self.normal.set_index("date")
        # v.columns = ["open", "high", "low", "close", "vol", "tun", "id"]
        # v.set_index(["id"], append=True)
        # df.index = pd.MultiIndex.from_tuples(index, names = names)
        # df.index.set_levels([u'Total', u'x2'],level=1,inplace=True)
        # df.index.set_labels([0, 1],level=1,inplace=True)
        # s.add(v, fill_value=0)

if __name__ == '__main__':
    print np.arange(3)
