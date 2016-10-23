# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/10"
from common import *
import wget

def yesterday(dt, days=-1):
    return dt + datetime.timedelta(days=days)

def download():
    tmpl = "http://60.191.48.94:8000/download/%s_2016-10-%02d.csv"
    for i in range(12, 13):
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

def transform():
    fbig = open("big.sql", "w")
    fprice = open("price.sql", "w")
    fbig.write("use st;\n")
    fprice.write("use st;\n")
    
    for f in os.listdir("."):
        if "derivativeindicator_" in f:
            ans = transformOne(f, "big", 39)
            fbig.write(ans + "\n")
        elif "price_" in f:
            ans = transformOne(f, "price", 23)
            fprice.write(ans + "\n")

def transformOne(filename, table, ct):
    keys = set()
    for l in open(filename).read().replace('"', '').split("\n"):
        if not l:
            continue
        if "OBJECT" in l:
            ans = "INSERT INTO `%s`(%s) VALUES " % (table, l)
            continue
        items = l.split(",")
        items = map(lambda s: s.strip(), items)
        if items[0] in keys:
            print "dup", l
            continue
        keys.add(items[0])
        assert len(items) == ct, str(len(items)) + ":" + l
        idx = [0, 1, 2, 3, -2, -1]
        for i in idx:
            items[i] = "'" + items[i] + "'"
        for i in range(len(items)):
            if not items[i]:
                items[i] = "NULL"
        if table == "price":
            items[-3] = "NULL"
        ans += "(%s)," % ",".join(items)
    ans = ans[:-1] + ";"
    return ans

if __name__ == '__main__':
    os.chdir("../data/inc")
    # now = datetime.datetime.now()
    # print now.year, now.month, now.day
    # yesterday = yesterday(now)
    # print yesterday.year, yesterday.month, yesterday.day
    # download()
    # wc()
    transform()
