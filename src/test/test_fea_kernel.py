# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/11/11"
from unittest import TestCase
from src.fea_kernel import *
from src.data_loader import Ft

class TestRsi(TestCase):
    def test_rsi(self):
        price = np.array([44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
                          45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00])[::-1]
        pre_price = np.concatenate((price[1:], [0]))
        ds = np.arange(1, len(price) + 1)[::-1]
        aa = [[] for _ in range(20)]
        aa[0] = ds
        aa[4] = pre_price
        aa[8] = price
        ft = Ft(*aa)
        ans = rsi("test", ft, 14)
        expect = np.array([66.32, 70.53])
        value = np.array(zip(*ans)[1])
        delta = np.abs(value - expect)
        self.assertTrue(np.all(delta < 0.1))
