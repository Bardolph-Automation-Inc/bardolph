#!/usr/bin/env python

import unittest

from tests import print_driven_test, test_module


class ArrayLoopTest(print_driven_test.PrintDrivenTest):
    def setUp(self):
        test_module.configure()
        self.post_setup()

    def test_min_in(self):
        script = """
            array a[3]
            assign a[0] 10
            assign a[1] 20
            assign a[2] 30

            repeat in a[] as i
            begin
                print i
                print a[i]
            end
        """
        self.run_and_check(script, [0, 10, 1, 20, 2, 30])

    def test_assign_in(self):
        script = """
            array a[10]
            repeat in a[] as i
                assign a[i] (i * 10)

            repeat in a as i
            begin
                print a[i]
            end
        """
        self.run_and_check(script, [0, 10, 20, 30, 40, 50, 60, 70, 80, 90])

    def test_1d_iteration(self):
        script = """
            array a[3]
            assign a[0] 10
            assign a[1] 11
            assign a[2] 12

            repeat in a[] as i
                print a[i]
        """
        self.run_and_check(script, [10, 11, 12])

    def test_2d_iteration(self):
        script = """
            array arr[3 3]
            repeat in arr[] as i
                repeat in arr[i] as j
                    assign arr[i j] (i * 10 + j)

             repeat in arr[] as i
                repeat in arr[i] as j
                    print arr[i j]
        """
        self.run_and_check(script, [0, 1, 2, 10, 11, 12, 20, 21, 22])

    def test_in_partial(self):
        script = """
            array arr[3 3]

            repeat in arr[] as i
                repeat in arr[i] as j
                    assign arr[i j] (i * 10 + j)

            define f with a[]
            begin
                repeat in a[] as i
                    print a[i]
            end

            f arr[2]
        """
        self.run_and_check(script, [20, 21, 22])

    def test_return_mid_loop(self):
        script = """
            array a[4]
            assign a[0] 10
            assign a[1] 11
            assign a[2] 12
            assign a[3] 13

            define has_return
            begin
                repeat in a[] as i
                begin
                    print a[i]
                    if i == 2
                        return a[i + 1] * 10
                end
            end

            print [has_return]
        """
        self.run_and_check(script, [10, 11, 12, 130])

    def test_break(self):
        script = """
            array a[4]
            assign a[0] 10
            assign a[1] 11
            assign a[2] 12
            assign a[3] 13

            repeat in a[] as i
            begin
                print a[i]
                if i == 2
                    break
            end
        """
        self.run_and_check(script, [10, 11, 12])

    def test_break_in_routine(self):
        script = """
            array a[4]
            assign a[0] 10
            assign a[1] 11
            assign a[2] 12
            assign a[3] 13

            define has_break
            begin
                repeat in a[] as i
                begin
                    print a[i]
                    if i == 1
                        break
                end
            end

            has_break
        """
        self.run_and_check(script, [10, 11])


if __name__ == '__main__':
    unittest.main()
