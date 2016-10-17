# -*- coding:utf-8 -*-
from unittest import TestCase
import src.gainByPredict as gain

class TestProcess(TestCase):
    def test_process(self):
        gain.process("small.predict", "small.ft", 1, 1)
