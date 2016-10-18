# -*- coding:utf-8 -*-
from unittest import TestCase
import src.wide_n_deep_tutorial as wide

__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/17/16"

class TestWide(TestCase):
    def test_main(self):
        wide.train_and_eval()
