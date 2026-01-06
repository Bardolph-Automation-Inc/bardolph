#!/usr/bin/env python

import unittest

from tests.script_runner import ScriptRunner
from tests import test_module


class ArrayTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._output = test_module.replace_print()
        self._runner = ScriptRunner(self)

    def _assert_output(self, expected):
        try:
            self.assertEqual(self._output.get_object(), expected)
        except IndexError:
            self.fail("No output was generated.")

    def _run_and_check(self, script, expected):
        self._runner.run_script(script)
        if isinstance(expected, list):
            self.assertListEqual(self._output.get_objects(), expected)
        else:
            self._assert_output(expected)

    def test_min_declaration(self):
        script = """
            array a[10]
            array b[10 20]
            array c[10 20 30]
        """
        self._runner.run_script(script)

    def test_min_assign(self):
        script = """
            array a[10]
            assign a[5] 100
            print a[5]
        """
        self._run_and_check(script, 100)

    def test_string_assign(self):
        script = """
            array a[10]
            assign a[5] "hello"
            print a[5]
        """
        self._run_and_check(script, 'hello')

    def test_min_assign_2d(self):
        script = """
            array x[5 10]
            assign x[3 2] 4
            print x[3 2]
        """
        self._run_and_check(script, 4)

    def test_assign_partial(self):
        script = """
            array x[5 10]
            assign x[3 2] 30

            array y[4]
            assign y[] x[3]

            print y[2]
        """
        self._run_and_check(script, 30)

    def test_assign_empty(self):
        script = """
            array a[10]
            assign a[5] 200
            array b[]
            assign b[] a[]
            print b[5]
        """
        self._run_and_check(script, 200)

    def test_overwrite_with_empty(self):
        script = """
            array a[10]
            assign a[5] 200
            array b[20]
            assign b[5] 300
            assign b[] a[]
            print b[5]
        """
        self._run_and_check(script, 200)

    def test_lvalue_error(self):
        script = """
            array a[10]
            array b[20]
            assign b a[]
        """
        self._runner.parse_erroneous_script(script, 4)

    def test_rvalue_error(self):
        script = """
            array a[10]
            array b[20]
            assign b[] a
        """
        self._runner.parse_erroneous_script(script, 5)

    def test_as_param(self):
        script = """
            define f with arr[] index begin
                return arr[index]
            end

            array v[10]
            repeat with i from 0 to 9
                assign v[i] (i* 50)
            print [f v[] 5]
        """
        self._run_and_check(script, 250)

    def test_nested(self):
        script = """
            array outer[10]
            array inner[5]

            repeat with i from 0 to 9
                assign outer[i] i
            assign inner[3] 5
            assign inner[0] 3
            print outer[inner[inner[0]]]
        """
        self._run_and_check(script, 5)

    def test_partial_deref(self):
        script = """
            array a[10 20]
            assign a[5 10] 300
            array b[]
            assign b[] a[5]
            print b[10]
        """
        self._run_and_check(script, 300)

    def test_partial_param(self):
        script = """
            define f with a[] i
                begin
                    return a[i]
                end

            array y[10 20]
            assign y[5 10] 200

            print [f y[5] 10]
        """
        self._run_and_check(script, 200)

    def test_no_deref(self):
        script = """
            array a[10]
            assign a[5] 400
            array b[]
            assign b[] a[]
            assign c b[5]
            print c
        """
        self._run_and_check(script, 400)

    def test_as_return(self):
        script = """
            array a[20]
            assign a[10] 415
            define ret_arr[]
                return a[]
            print [ret_arr][10]
        """
        self._run_and_check(script, 415)

    def test_as_unindexed_return(self):
        script = """
            array a[20]
            assign a[10] 415

            define ret_arr[]
                return a[]

            array b[]
            assign b[] [ret_arr][]

            print b[10]
        """
        self._run_and_check(script, 415)

    def test_return_partial(self):
        script = """
            define return_partial[] with arr[] n
                begin
                    return arr[n]
                end

            array mat[3 3]
            assign mat[1 2] 2000

            array vec[]
            assign vec[] [return_partial mat[] 1][]
            print vec[2]
        """
        self._run_and_check(script, 2000)

    def test_as_param(self):
        script = """
            define ret_elem with arr[]
                return arr[10]

            array a[20]
            assign a[10] 500
            print [ret_elem a[]]
        """
        self._run_and_check(script, 500)

    def test_return_as_param(self):
        script = """
            define return_arr[] with a b
                begin
                    array arr[2]
                    assign arr[0] a
                    assign arr[1] b
                    return arr[]
                end

            define use_arr with arr[]
                begin
                    print arr[0]
                    print arr[1]
                end

            use_arr [return_arr 100 200][]
        """
        self._run_and_check(script, [100, 200])

    def test_poke_param(self):
        script = """
            define set_arr with arr[]
                assign arr[10] 50

            array a[20]
            assign a[10] 500
            set_arr a[]

            print a[10]
        """
        self._run_and_check(script, 50)

    def test_as_param_and_return(self):
        script = """
            array a[20]
            assign a[10] 415
            assign a[15] 510

            define ret_arr[] with arr[]
                return arr[]

            print [ret_arr a[]][10]
            print [ret_arr a[]][15]
        """
        self._run_and_check(script, [415, 510])

    def test_return_partial_deref(self):
        script = """
            array a[10 20]
            assign a[0 1] 415
            assign a[0 2] 510

            define ret_arr[] with arr[] i
                return arr[i]

            print [ret_arr a[] 0][1]
            print [ret_arr a[] 0][2]
        """
        self._run_and_check(script, [415, 510])

    def test_internally_created(self):
        script = """
            define create[]
            begin
                array arr[5]
                assign arr[3] 4500
                return arr[]
            end

            print [create][3]
        """
        self._run_and_check(script, 4500)


if __name__ == '__main__':
    unittest.main()
