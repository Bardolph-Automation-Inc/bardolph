#!/usr/bin/env python

import unittest

from tests.script_runner import ScriptRunner
from tests import test_module


class FunctionTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._output = test_module.replace_print()
        self._runner = ScriptRunner(self)

    def test_minimal(self):
        script = """
            define f with a begin
                return a
            end

            define g with b return b

            print [f 0]
            print [g 1]
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [0, 1])

    def test_recursion(self):
        script = """
            define f with a begin
                if a > 9
                    return a
                return [f a + 1]
            end

            # 10
            print [f 0]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), 10)

    def test_calls_as_params(self):
        script = """
            define f with a b return a + b
            define g with y return y + 1

            # 17
            print [f [g 5] [g 10]]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), 17)

    def test_global(self):
        script = """
            assign x 100

            define f with y begin
                assign x x * y
                return x * 2
            end

            print [f 2]
            print x
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [400, 200])

    def test_global_as_param(self):
        script = """
            assign x 100

            # Using x as a parameter hides the global.
            #
            define g with x begin
                assign x x * 2
                return x * 2
            end

            print [g 5]
            print x
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [20, 100])

    def test_no_return(self):
        script = """
            define no_return begin
                assign x 25
                return
            end

            print [no_return]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), None)

    def test_multiple_returns(self):
        script = """
            define m_returns with val begin
                if val > 100 && val < 200
                    return val * 2

                if val >= 200 && val < 1000 begin
                    return val * 7
                end

                if val > 1000 return val * 11

                if val < 0 begin
                    return
                end

                return val
            end

            print [m_returns 10]
            print [m_returns 120]
            print [m_returns 200]
            print [m_returns 2000]
            print [m_returns -1]
        """
        self._runner.run_script(script)
        self.assertListEqual(
            self._output.get_objects(), [10, 240, 1400, 22000, None])

    def test_standalone(self):
        script = """
            assign x 10

            define set_x with val begin
                assign x val
                return 30
            end

            # Don't use the return value, but do execute it.
            [set_x 50]
            print x

            print [set_x 100]
            print x
        """
        self._runner.run_script(script)
        self.assertListEqual(self._output.get_objects(), [50, 30, 100])

    def test_mixed_params(self):
        script = """
            define plus with i j begin
                return i + j
            end

            define multi_params with a b c begin
                return a + b * 100 + c * 1000
            end

            print [multi_params 5 5+2 [plus 5 4]]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), 9705)

if __name__ == '__main__':
    unittest.main()
