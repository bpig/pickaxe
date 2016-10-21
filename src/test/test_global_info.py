# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/21"
from unittest import TestCase
from src.global_info import process

class TestGlobalInfo(TestCase):
    def test_process(self):
        process("small.ft", "small.gb")
