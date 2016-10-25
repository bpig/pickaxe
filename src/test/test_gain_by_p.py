# -*- coding:utf-8 -*-
from unittest import TestCase
import src.gain_by_p as gain

class TestProcess(TestCase):
    def test_process(self):
        gain.process("2016.ans", "2016.ft", 50, 90, "20160104", "2016_gb")
