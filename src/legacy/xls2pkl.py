# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/4"
from src.common import *

def trans(filebase):
    os.chdir("../macro")
    
    filename = filebase + ".xlsx"
    xls_file = pd.ExcelFile(filename)
    
    normal_pkl = filebase + "_normal.pkl"
    normal = xls_file.parse("sheet3")
    normal.to_pickle(normal_pkl)
    
    ex_pkl = filebase + "_ex.pkl"
    ex = xls_file.parse("Sheet2")
    ex.to_pickle(ex_pkl)
    
    os.chdir("../src")

if __name__ == '__main__':
    trans("sh15")
