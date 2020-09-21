#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from tests.script_runner import ScriptRunner
from tests import test_module

class PrintTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)

    @patch('builtins.print')
    def test_script(self, print_fn):
        script = """
            units raw
            hue 1 saturation 2 brightness 3 kelvin 4
            set all
            hue 10 saturation 20 brightness 30 kelvin 40
            assign label "Light"

            define print_light with the_light begin
                print label the_light {time + 5}
                get the_light
                print "hue:" hue "saturation:" saturation
                print "brightness:"
                println brightness "kelvin:" kelvin
            end

            print_light "Table"
        """
        self._runner.run_script(script)
        print_fn.assert_called_with(
            'Light Table 5.0 hue: 1 saturation: 2 brightness: 3 kelvin: 4')

if __name__ == '__main__':
    unittest.main()
