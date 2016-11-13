# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/13/16"

from common import *

if __name__ == '__main__':
    rd = csv.reader(open(sys.argv[1]))
    t3 = defaultdict(list)
    t50 = defaultdict(list)
    for r in rd:
        if not r:
            continue
        key = r[0]
        name = key + "_" + r[1]
        
