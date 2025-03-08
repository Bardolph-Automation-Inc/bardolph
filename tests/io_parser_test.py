#!/usr/bin/env python

import logging
import unittest

from bardolph.parser.parse import Parser
from tests import test_module


class IoParserTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        logging.getLogger().addHandler(logging.NullHandler())
        self.parser = Parser()

    def test_print(self):
        input_string = "print 1 print 2"
        self.assertTrue(self.parser.parse(input_string))

    def test_println(self):
        input_string = 'println 10'
        self.assertTrue(self.parser.parse(input_string))

    def test_printf(self):
        input_string = """
            assign y 60 define z "hello"
            printf "{} {brightness} {} {} {y} {}" 500 saturation "there" z
        """
        self.assertTrue(self.parser.parse(input_string))


if __name__ == '__main__':
    unittest.main()
