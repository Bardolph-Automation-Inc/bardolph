#!/usr/bin/env python

import unittest

from tests.activity_log_test import ActivityLogTest
from tests.clock_test import ClockTest
from tests.end_to_end_test import EndToEndTest
from tests.injection_test import InjectionTest
from tests.job_control_test import JobControlTest
from tests.lex_test import LexTest
from tests.light_set_test import LightSetTest
from tests.log_config_test import LogConfigTest
from tests.machine_test import MachineTest
from tests.parser_test import ParserTest
from tests.settings_test import SettingsTest
from tests.time_pattern_test import TimePatternTest
from tests.units_test import UnitsTest
from tests.web_app_test import WebAppTest

tests = unittest.TestSuite()

for test_class in (
    ActivityLogTest,
    ClockTest,
    EndToEndTest,
    InjectionTest,
    JobControlTest,
    LexTest,
    LightSetTest,
    LogConfigTest,
    MachineTest,
    ParserTest,
    SettingsTest,
    TimePatternTest,
    UnitsTest,
    WebAppTest
): tests.addTest(unittest.makeSuite(test_class))
    
unittest.TextTestRunner(verbosity=2).run(tests)
