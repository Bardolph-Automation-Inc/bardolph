#!/usr/bin/env python

import unittest

from tests.clock_test import ClockTest
from tests.injection_test import InjectionTest
from tests.job_control_test import JobControlTest
from tests.lex_test import LexTest
from tests.light_set_test import LightSetTest
from tests.log_config_test import LogConfigTest
from tests.parser_test import ParserTest
from tests.units_test import UnitsTest
from tests.web_app_test import WebAppTest

tests = unittest.TestSuite()

def add_test(test_class):
    global tests
    tests.addTest(unittest.makeSuite(test_class))

if __name__ == '__main__':
    add_test(ClockTest)
    add_test(InjectionTest)
    add_test(JobControlTest)
    add_test(LexTest) 
    add_test(LightSetTest)
    add_test(LogConfigTest)
    add_test(ParserTest)   
    add_test(UnitsTest)
    add_test(WebAppTest) 
    unittest.TextTestRunner(verbosity=2).run(tests)
