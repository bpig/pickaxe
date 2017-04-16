# coding:utf-8

from src.common import *
import tushare as ts


def dump():
    # dump in 20170415
    # http://tushare.org/macro.html
    with TimeLog("hah"):
        apis = [
            "get_rrr",  # 存款准备金
            "get_money_supply",  # 货币供应量
            "get_loan_rate",  # 贷款利率
            "get_deposit_rate",  # 存款利率
            "get_money_supply_bal",  # 货币供应量，年底余额
            "get_gdp_year",  # 国内gdp
            "get_gdp_quarter",  # 国内gdp，季度
            "get_gdp_for",  # 三大需求对gdp贡献
            "get_gdp_pull",  # 三大产业
            "get_gdp_contrib",
            "get_cpi",
            "get_ppi",
        ]
        idx = -1
        expr = "ts.%s(), '%s'[4:]" % (apis[idx], apis[idx])
        print expr
        df, tgt = eval(expr)
        df.to_csv("macro/" + tgt + ".csv", encoding="gbk")
    return df


if __name__ == '__main__':
    print dump()
