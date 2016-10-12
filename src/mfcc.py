# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/10"
import wget
import time
import os

def download():
    tmpl = "http://60.191.48.94:8000/download/%s_2016-10-%02d.csv"
    for i in range(11, 12):
        print time.ctime(), i
        url = tmpl % ("derivativeindicator", i)
        wget.download(url)
        url = tmpl % ("price", i)
        wget.download(url)
        print time.ctime()

def wc():
    files = os.listdir(".")
    for f in files:
        if not os.path.isfile(f):
            continue
        lf = len(open(f).readlines())
        if lf <= 7:
            os.remove(f)

if __name__ == '__main__':
    os.chdir("../data/mfcc")
    for l in open("price_2016-08-22.csv").readlines()[:3]:
        print l
