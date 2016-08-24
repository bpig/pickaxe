# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/10"
import wget
import time
import os

if __name__ == '__main__':
    tmpl = "http://sk5.proxy.taobao.org/part-%05d.bz2"
    os.chdir("../data/mfcc")
    for i in range(500, 600):
        print time.ctime(), i
        ret = wget.download(tmpl % i)
        print time.ctime()
