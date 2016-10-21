# -*- coding:utf-8 -*-
from unittest import TestCase
import src.gain_by_p as gain

class TestProcess(TestCase):
    def test_process(self):
        gain.process("small.predict", "small.ft", 1, 1)
