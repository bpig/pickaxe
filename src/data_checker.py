# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/4"

from common import *

class DataChecker:
    def __init__(self, pkl):
        self.sh = pd.read_pickle(pkl)
    
    def checkShares(self):
        sh = self.sh
        c = 0
        for sid in set(sh.index.get_level_values('id')):
            mean = sh['shares'].xs(sid, level='id').mean()
            head, tail = sh['shares'].xs(sid, level='id')[0], sh['shares'].xs(sid, level='id')[-1]
            if tail != mean:
                print sid, mean, tail
                c += 1
        print c

if __name__ == '__main__':
    os.chdir("../data")
    dc = DataChecker("sh.pkl")
    dc.checkShares()
