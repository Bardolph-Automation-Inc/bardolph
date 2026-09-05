#!/usr/bin/env python

import unittest

from bardolph.lib.i_lib import Output
from bardolph.lib.injection import inject
from tests.script_runner import ScriptRunner
from tests import test_module


class ArrayTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        test_module.replace_print()
        self._runner = ScriptRunner(self)

    @inject(Output)
    def _assert_output(self, expected, output):
        try:
            self.assertEqual(output.get_object(), expected)
        except IndexError:
            self.fail("No output was generated.")

    @inject(Output)
    def _run_and_check(self, script, expected, output):
        self._runner.run_script(script)
        if isinstance(expected, list):
            self.assertListEqual(output.get_objects(), expected)
        else:
            self._assert_output(expected)

    @inject(Output)
    def test_min_declaration(self, output):
        script = """
            array a[10]
            array b[10 20]
            array c[10 20 30]
        """
        self._runner.run_script(script)

    @inject(Output)
    def test_min_assign(self, output):
        script = """
            array a[10]
            assign a[5] 100
            print a[5]
        """
        self._run_and_check(script, 100)

    @inject(Output)
    def test_string_assign(self, output):
        script = """
            array a[10]
            assign a[5] "hello"
            print a[5]
        """
        self._run_and_check(script, 'hello')

    @inject(Output)
    def test_min_assign_2d(self, output):
        script = """
            array x[5 10]
            assign x[3 2] 4
            print x[3 2]
        """
        self._run_and_check(script, 4)

    @inject(Output)
    def test_assign_partial(self, output):
        script = """
            array x[5 10]
            assign x[3 2] 30

            array y[4]
            assign y[] x[3]

            print y[2]
        """
        self._run_and_check(script, 30)

    @inject(Output)
    def test_assign_empty(self, output):
        script = """
            array a[10]
            assign a[5] 200
            array b[]
            assign b[] a[]
            print b[5]
        """
        self._run_and_check(script, 200)

    @inject(Output)
    def test_overwrite_with_empty(self, output):
        script = """
            array a[10]
            assign a[5] 200
            array b[20]
            assign b[5] 300
            assign b[] a[]
            print b[5]
        """
        self._run_and_check(script, 200)

    @inject(Output)
    def test_lvalue_error(self, output):
        script = """
            array a[10]
            array b[20]
            assign b a[]
        """
        self._runner.parse_erroneous_script(script, 4)

    @inject(Output)
    def test_rvalue_error(self, output):
        script = """
            array a[10]
            array b[20]
            assign b[] a
        """
        self._runner.parse_erroneous_script(script, 5)

    @inject(Output)
    def test_as_param(self, output):
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

    @inject(Output)
    def test_nested(self, output):
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

    @inject(Output)
    def test_partial_deref(self, output):
        script = """
            array a[10 20]
            assign a[5 10] 300
            array b[]
            assign b[] a[5]
            print b[10]
        """
        self._run_and_check(script, 300)

    @inject(Output)
    def test_partial_param(self, output):
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

    @inject(Output)
    def test_no_deref(self, output):
        script = """
            array a[10]
            assign a[5] 400
            array b[]
            assign b[] a[]
            assign c b[5]
            print c
        """
        self._run_and_check(script, 400)

    @inject(Output)
    def test_as_return(self, output):
        script = """
            array a[20]
            assign a[10] 415
            define ret_arr[]
                return a[]
            print [ret_arr][10]
        """
        self._run_and_check(script, 415)

    @inject(Output)
    def test_as_unindexed_return(self, output):
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

    @inject(Output)
    def test_return_partial(self, output):
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

    @inject(Output)
    def test_as_param2(self, output): ###
        script = """
            define ret_elem with arr[]
                return arr[10]

            array a[20]
            assign a[10] 500
            print [ret_elem a[]]
        """
        self._run_and_check(script, 500)

    @inject(Output)
    def test_return_as_param(self, output):
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

    @inject(Output)
    def test_poke_param(self, output):
        script = """
            define set_arr with arr[]
                assign arr[10] 50

            array a[20]
            assign a[10] 500
            set_arr a[]

            print a[10]
        """
        self._run_and_check(script, 50)

    @inject(Output)
    def test_as_param_and_return(self, output):
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

    @inject(Output)
    def test_return_partial_deref(self, output):
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

    @inject(Output)
    def test_internally_created(self, output):
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
