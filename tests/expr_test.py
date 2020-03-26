#!/usr/bin/env python

import unittest

from bardolph.parser.code_gen import CodeGen
from bardolph.parser.expr_parser import ExprParser

class ExprTest(unittest.TestCase):
    def setUp(self):
        self._parser = ExprParser("1")

    def test_ast(self):
        code_gen = CodeGen()
        self._parser.generate_code(code_gen)
        self.assertIsNotNone(code_gen.program)

if __name__ == '__main__':
    unittest.main()
