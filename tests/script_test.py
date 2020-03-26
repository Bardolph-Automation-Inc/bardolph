#!/usr/bin/env python3

import unittest

from bardolph.controller import i_controller
from bardolph.lib.injection import provide
from tests.script_runner import ScriptRunner
from tests import test_module

class ScriptTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._runner = ScriptRunner(self)

    def test_script(self):
        script = """
            saturation 80 brightness 40
            define delay 1.20
            define dur 1.20

            define set_pole with base_hue begin
                hue base_hue set "Top"
                time 0
                hue {hue + 36} set "Middle"
                hue {hue + 72} set "Bottom"
                time delay
            end

            duration 3
            set_pole 36

            duration dur
            repeat
                repeat 10 with _hue cycle 72
                    set_pole _hue
        """
        self._runner.run_script(script)
        lifx = provide(i_controller.Lifx)
        for light in lifx.get_lights():
            print(light.get_label(), light.call_list())

if __name__ == '__main__':
    unittest.main()
