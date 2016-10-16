# -*- coding:utf-8 -*-
from unittest import TestCase
import src.fea as fea

__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

class TestFea(TestCase):
    def test_main(self):
        fea.process("small.ft", "small", "20160306", 2)
