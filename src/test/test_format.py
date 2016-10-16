# -*- coding:utf-8 -*-
from unittest import TestCase
import src.format as ft

__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/16/16"

class TestFormat(TestCase):
    def test_main(self):
        ft.process("small.csv", "small.ft")
