#!/usr/bin/env python

import unittest

from tests.activity_log_test import ActivityLogTest
from tests.call_context_test import CallContextTest
from tests.call_stack_test import CallStackTest
from tests.clock_test import ClockTest
from tests.code_gen_test import CodeGenTest
from tests.define_test import DefineTest
from tests.end_to_end_test import EndToEndTest
from tests.example_test import ExampleTest
from tests.expr_test import ExprTest
from tests.injection_test import InjectionTest
from tests.job_control_test import JobControlTest
from tests.lex_test import LexTest
from tests.light_set_test import LightSetTest
from tests.log_config_test import LogConfigTest
from tests.loop_test import LoopTest
from tests.machine_test import MachineTest
from tests.parser_test import ParserTest
from tests.print_test import PrintTest
from tests.settings_test import SettingsTest
from tests.sorted_list_test import SortedListTest
from tests.time_pattern_test import TimePatternTest
from tests.units_test import UnitsTest
from tests.vm_math_test import VmMathTest
from tests.web_app_test import WebAppTest

tests = unittest.TestSuite()

for test_class in (
    ActivityLogTest,
    CallContextTest,
    CallStackTest,
    ClockTest,
    CodeGenTest,
    DefineTest,
    EndToEndTest,
    ExampleTest,
    ExprTest,
    InjectionTest,
    JobControlTest,
    LexTest,
    LightSetTest,
    LogConfigTest,
    LoopTest,
    MachineTest,
    ParserTest,
    SettingsTest,
    SortedListTest,
    TimePatternTest,
    UnitsTest,
    VmMathTest,
    WebAppTest
): tests.addTest(unittest.makeSuite(test_class))

unittest.TextTestRunner(verbosity=2).run(tests)
