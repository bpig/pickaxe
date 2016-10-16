# -*- coding:utf-8 -*-
from unittest import TestCase
import src.cmvn as cmvn

__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

class TestCmvn(TestCase):
    def test_loadData(self):
        cmvn.process("small.fe", "small.fe.cmvn")
