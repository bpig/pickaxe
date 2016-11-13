# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/11/11"
from unittest import TestCase
from src.fea_kernel import *
from src.data_loader import Ft

class TestFeaKernel(TestCase):
    @staticmethod
    def gen_ft(price):
        pre_price = np.concatenate((price[1:], [0]))
        aa = [[] for _ in range(20)]
        aa[4] = pre_price
        aa[8] = price
        return Ft(*aa)
    
    def test_rsi(self):
        price = np.array([44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
                          45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00])[::-1]
        ft = self.gen_ft(price)
        rsi_value = rsi(ft, 14)
        expect = np.array([66.32, 70.53])
        np.testing.assert_array_almost_equal(expect, rsi_value, decimal=1)
    
    def test_sma(self):
        price = np.array([22.27, 22.19, 22.08, 22.17, 22.18, 22.13,
                          22.23, 22.43, 22.24, 22.29, 22.15, 22.39])[::-1]
        ft = self.gen_ft(price)
        
        sma_value = sma(ft.e, 10)
        sma_expect = np.array([22.23, 22.21, 22.22])
        np.testing.assert_array_almost_equal(sma_expect, sma_value, decimal=2)
        
        ema_value = ema(ft.e, sma_value, 10)
        ema_expect = np.array([22.24, 22.21, 22.22])
        np.testing.assert_array_almost_equal(ema_expect, ema_value, decimal=2)
