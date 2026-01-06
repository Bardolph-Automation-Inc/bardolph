#!/usr/bin/env python

import logging
import unittest

from bardolph.lib import injection
from bardolph.parser.parse import Parser
from bardolph.runtime import runtime_module


class ParserTest(unittest.TestCase):
    def setUp(self):
        injection.configure()
        runtime_module.configure()
        logging.getLogger().addHandler(logging.NullHandler())
        self.parser = Parser()
        self.parser.set_testing_errors()

    def good_input(self, input_string):
        self.assertTrue(self.parser.parse(input_string))

    def test_good_strings(self):
        input_strings = [
            '#abcde \n hue 5 \n #efghi \n ',
            '',
            'set "name with spaces"',
            'define table "Table" set table',
            'hue 5 saturation 10 set "Table"',
            'hue 5 set all',
            'get "Table"',
            'get "Table" zone 0'
        ]
        for string in input_strings:
            self.assertIsNotNone(self.parser.parse(string), string)

    def test_bad_keyword(self):
        script = """
            on "Top" on "Bottom" on
            "Middle" Frank'
        """
        self.assertFalse(self.parser.parse(script))
        self.assertEqual('3', self.parser.get_errors())

    def test_bad_number(self):
        script = "hue 5 saturation x"
        self.assertFalse(self.parser.parse(script))
        self.assertEquals('1', self.parser.get_errors())

    def test_overwrite_constant(self):
        script = 'define x 5 assign x 6'
        self.assertFalse(self.parser.parse(script))
        self.assertEquals('1', self.parser.get_errors())


if __name__ == '__main__':
    unittest.main()
