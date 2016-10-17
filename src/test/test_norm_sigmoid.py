# -*- coding:utf-8 -*-
from unittest import TestCase
import src.norm_sigmoid as sigmoid

__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

class TestMain(TestCase):
    def test_process(self):
        sigmoid.process("small.fe")
        
