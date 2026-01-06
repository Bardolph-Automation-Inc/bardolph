#!/usr/bin/env python


from bardolph.parser import parse
import unittest

from tests import print_driven_test, test_module


class LoopTest(print_driven_test.PrintDrivenTest):
    def setUp(self):
        test_module.using_medium_set().configure()
        self.post_setup()

    def test_count(self):
        script = """
            repeat 3 print "x"
        """
        self.run_and_check(script, ['x', 'x', 'x'])

    def test_count_with_range(self):
        script = """
            repeat 3 with x from 5 to 15
            begin
                print x
            end
        """
        self.run_and_check(script, [5, 10, 15])

    def test_nested_count_with_range(self):
        script = """
            repeat 3 with x from 5 to 7
            begin
                print x
                repeat 3 with y from 1000 to 1002
                begin
                    print y
                end
            end
        """
        self.run_and_check(
            script,
            [5, 1000, 1001, 1002, 6, 1000, 1001, 1002, 7, 1000, 1001, 1002])

    def test_count_with_cycle(self):
        script = """
            repeat 5 with x cycle print x
        """
        self.run_and_check(script, [0, 72, 144, 216, 288])

    def test_count_with_cycle_offset(self):
        script = """
            repeat 5 with x cycle 10
            begin
                print x
            end
        """
        self.run_and_check(script, [10, 82, 154, 226, 298])

    def test_count_with_nested_cycle(self):
        script = """
            repeat 4 with a cycle
            begin
                print a
                repeat in group "Table" as the_light with b cycle
                begin
                    print the_light
                    print b
                end
            end
        """
        self.run_and_check(script,
                            [0, 'table-0', 0, 'table-1', 180,
                             90, 'table-0', 0, 'table-1', 180,
                             180, 'table-0', 0, 'table-1', 180,
                             270, 'table-0', 0, 'table-1', 180])

    def test_count_with_expressions(self):
        script = """
            assign x 16
            define y 5
            assign z 10
            assign thou 1000

            repeat 16 / (y - 1) with brt from -z + z to thou / 10
                print brt
        """
        self.run_and_check_rounded(script, [0, 33.33, 66.67, 100])

    def test_all(self):
        script = """
            repeat all as the_light
            begin
                print the_light
            end
        """
        self.run_and_check(script, [
            'Balcony', 'Bottom', 'Candle', 'Lamp', 'Middle', 'Top',
            'White Candle', 'table-0', 'table-1'
        ])

    def test_all_with_range(self):
        script = """
            repeat all as the_light with x from 10 to 90
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, [
            'Balcony', 10, 'Bottom', 20, 'Candle', 30, 'Lamp', 40, 'Middle', 50,
            'Top', 60, 'White Candle', 70, 'table-0', 80, 'table-1', 90
        ])

    def test_all_with_range_expressions(self):
        script = """
            assign a 5
            assign b 45

            repeat all as the_light with x from a * 2 to 2 * b
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, [
            'Balcony', 10, 'Bottom', 20, 'Candle', 30, 'Lamp', 40, 'Middle', 50,
            'Top', 60, 'White Candle', 70, 'table-0', 80, 'table-1', 90
        ])

    def test_all_with_cycle(self):
        script = """
            repeat all as the_light with x cycle
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, [
            'Balcony', 0, 'Bottom', 40, 'Candle', 80, 'Lamp', 120,
            'Middle', 160, 'Top', 200, 'White Candle', 240, 'table-0', 280,
            'table-1', 320
        ])

    def test_all_with_cycle_offset(self):
        script = """
            assign y 50

            repeat all as the_light with x cycle y * 2
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, [
            'Balcony', 100, 'Bottom', 140, 'Candle', 180, 'Lamp', 220,
            'Middle', 260, 'Top', 300, 'White Candle', 340, 'table-0', 380,
            'table-1', 420
        ])

    def test_all_with_cycle(self):
        script = """
            repeat all as the_light with x cycle
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, [
            'Balcony', 0, 'Bottom', 40, 'Candle', 80, 'Lamp', 120,
            'Middle', 160, 'Top', 200, 'White Candle', 240, 'table-0', 280,
            'table-1', 320
        ])

    def test_all_with_cycle_offset(self):
        script = """
            repeat all as the_light with x cycle 20
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, [
            'Balcony', 20, 'Bottom', 60, 'Candle', 100, 'Lamp', 140,
            'Middle', 180, 'Top', 220, 'White Candle', 260, 'table-0', 300,
            'table-1', 340
        ])

    def test_locations(self):
        script = """
            repeat location as the_loc print the_loc
        """
        self.run_and_check(script, ['Home', 'Living Room', 'Outside'])

    def test_locations_with_range(self):
        script = """
            repeat location as the_loc with a from 100 to 300
            begin
                print the_loc
                print a
            end
        """
        self.run_and_check(
            script,
            ['Home', 100, 'Living Room', 200, 'Outside', 300])

    def test_locations_with_cycle(self):
        script = """
            repeat location as the_loc with a cycle
            begin
                print the_loc
                print a
            end
        """
        self.run_and_check(
            script,
            ['Home', 0, 'Living Room', 120, 'Outside', 240])

    def test_locations_with_cycle_offset(self):
        script = """
            repeat location as the_loc with a cycle 50
            begin
                print the_loc
                print a
            end
        """
        self.run_and_check(
            script,
            ['Home', 50, 'Living Room', 170, 'Outside', 290])

    def test_groups(self):
        script = """
            repeat group as the_group print the_group
        """
        self.run_and_check(script, ['Furniture', 'Pole', 'Table', 'Windows'])

    def test_groups_with_range(self):
        script = """
            repeat group as the_group with a from 100 to 400
            begin
                print the_group
                print a
            end
        """
        self.run_and_check(
            script,
            ['Furniture', 100, 'Pole', 200, 'Table', 300, 'Windows', 400])

    def test_groups_with_cycle(self):
        script = """
            repeat group as the_group with a cycle
            begin
                print the_group
                print a
            end
        """
        self.run_and_check(
            script,
            ['Furniture', 0, 'Pole', 90, 'Table', 180, 'Windows', 270])

    def test_groups_with_cycle_offset(self):
        script = """
            repeat group as the_group with a cycle 45
            begin
                print the_group
                print a
            end
        """
        self.run_and_check(
            script,
            ['Furniture', 45, 'Pole', 135, 'Table', 225, 'Windows', 315])

    def test_in_location(self):
        script = """
            repeat in location "Home" as the_light print the_light
        """
        self.run_and_check(script, ['Bottom', 'Middle', 'Top'])

    def test_in_location_with_range(self):
        script = """
            repeat in location "Home" as the_light with x from 100 to 300
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, ['Bottom', 100, 'Middle', 200, 'Top', 300])

    def test_in_location_and_light_with_range(self):
        script = """
            repeat in location "Home" and "Candle"
                as the_light
                with x from 100 to 400
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(
            script,
            ['Bottom', 100, 'Middle', 200, 'Top', 300, 'Candle', 400])

    def test_location_members_nested(self):
        script = """
            repeat location as the_loc
            begin
                print the_loc
                repeat in location the_loc as the_light
                begin
                    print the_light
                end
            end
        """
        self.run_and_check(script, [
            'Home', 'Bottom', 'Middle', 'Top',
            'Living Room', 'Lamp', 'table-0', 'table-1',
            'Outside', 'Balcony', 'Candle', 'White Candle',
        ])

    def test_multiple_locations_with_range(self):
        script = """
            repeat in location "Outside" and location "Home" as the_light
                with x from 1000 to 6000
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(
            script,
            ['Balcony', 1000, 'Candle', 2000, 'White Candle', 3000,
             'Bottom', 4000, 'Middle', 5000, 'Top', 6000])

    def test_in_group(self):
        script = """
            repeat in group "Windows" as the_light print the_light
        """
        self.run_and_check(script, ['Balcony', 'Lamp'])

    def test_in_group_with_range(self):
        script = """
            repeat in group "Pole" as the_light with x from 1000 to 3000
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(
            script,
            ['Bottom', 1000, 'Middle', 2000, 'Top', 3000])

    def test_in_group_with_cycle(self):
        script = """
            repeat in group "Pole" as the_light with x cycle
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(
            script,
            ['Bottom', 0, 'Middle', 120, 'Top', 240])

    def test_group_members_nested(self):
        script = """
            repeat group as the_group
            begin
                print the_group
                repeat in group the_group as the_light
                    begin
                        print the_light
                    end
            end
        """
        self.run_and_check(script, [
            'Furniture', 'Candle', 'White Candle',
            'Pole', 'Bottom', 'Middle', 'Top',
            'Table', 'table-0', 'table-1',
            'Windows', 'Balcony', 'Lamp'
        ])

    def test_multiple_groups_with_range(self):
        script = """
            repeat in group "Table" and group "Pole" as the_light
                    with x from 100 to 500
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(
            script,
            ['table-0', 100, 'table-1', 200,
             'Bottom', 300, 'Middle', 400, 'Top', 500])

    def test_literal_list(self):
        script = """
            repeat in "Top" and "Middle" and "Bottom" as the_light
                print the_light
        """
        self.run_and_check(script, ['Top', 'Middle', 'Bottom'])

    def test_literal_list_with_range(self):
        script = """
            repeat in "Top" and "Middle" and "Bottom"
                as the_light
                with x from 25 to 75
            begin
                print the_light
                print x
            end
        """
        self.run_and_check(script, ['Top', 25, 'Middle', 50, 'Bottom', 75])

    def test_var_list(self):
        script = """
            assign top "Top"
            assign middle "Middle"
            assign bottom "Bottom"

            repeat in top and middle and bottom as the_light
                print the_light
        """
        self.run_and_check(script, ['Top', 'Middle', 'Bottom'])

    def test_var_list_with_range(self):
        script = """
            assign bottom "Bottom"
            assign middle "Middle"
            assign top "Top"

            repeat in bottom and top and middle
                as the_light
                with var from 20000 to 30000
            begin
                print the_light
                print var
            end
        """
        self.run_and_check(script,
                            ['Bottom', 20000, 'Top', 25000, 'Middle', 30000])

    def test_var_list_with_cycle(self):
        script = """
            assign bottom "Bottom"
            assign middle "Middle"
            assign top "Top"

            repeat in bottom and top and middle as the_light with var cycle
            begin
                print the_light
                print var
            end
        """
        self.run_and_check(script, ['Bottom', 0, 'Top', 120, 'Middle', 240])

    def test_var_and_literal_list(self):
        script = """
            assign top "Top"
            assign middle "Middle"
            assign bottom "Bottom"

            repeat in
                    top
                    and "Balcony"
                    and middle
                    and bottom
                    and bottom
                    and "Candle"
                as the_light
                    print the_light
        """
        self.run_and_check(script, [
            'Top',
            'Balcony',
            'Middle',
            'Bottom',
            'Bottom',
            'Candle'
            ])

    def test_var_and_literal_list_with_range(self):
        script = """
            assign top "Top"
            assign middle "Middle"
            assign bottom "Bottom"

            repeat in top
                    and "Balcony"
                    and middle
                    and bottom
                    and bottom
                    and "Candle"
                as the_light
                with the_hue from 1 to 10
            begin
                print the_light
                print the_hue
            end
        """
        self.run_and_check_rounded(
            script,
            ['Top', 1, 'Balcony', 2.8, 'Middle', 4.6, 'Bottom', 6.4,
             'Bottom', 8.2, 'Candle', 10])

    def test_var_and_literal_list_with_cycle(self):
        script = """
            assign top "Top"
            assign middle "Middle"
            assign bottom "Bottom"

            repeat in top
                    and middle
                    and "Balcony"
                    and bottom
                    and "Candle"
                    and bottom
                as the_light
                with the_hue cycle
            begin
                print the_light
                print the_hue
            end
        """
        self.run_and_check_rounded(
            script,
            ['Top', 0, 'Middle', 60, 'Balcony', 120, 'Bottom', 180,
             'Candle', 240, 'Bottom', 300])

    def test_range(self):
        script = """
            repeat with a from 5 to 7 print a
        """
        self.run_and_check(script, [5, 6, 7])

    def test_reverse_range(self):
        script = """
            repeat with b from 20 to 15 print b
        """
        self.run_and_check(script, [20, 19, 18, 17, 16, 15])

    def test_while(self):
        script = """
            assign y 0
            repeat while y < 3
            begin
                print y
                assign y y + 1
            end
        """
        self.run_and_check(script, [0, 1, 2])

    def test_break(self):
        script = """
            assign i 0
            repeat
            begin
                if i >= 2
                    break
                print i
                assign i i + 1
            end
        """
        self.run_and_check(script, [0, 1])

    def test_nested_break(self):
        script = """
            assign i 0
            repeat
            begin
                if i >= 2
                    break
                print i
                assign i i + 1

                assign j 1000
                repeat
                begin
                    if j > 1002
                        break
                    print j
                    assign j j + 1
                end
            end
        """
        self.run_and_check(script, [0, 1000, 1001, 1002, 1, 1000, 1001, 1002])

    def test_while_break(self):
        script = """
            assign y 0
            repeat while y < 4
            begin
                print y
                if y == 2
                    break
                assign y y + 1
            end
        """
        self.run_and_check(script, [0, 1, 2])

    def test_nested_return(self):
        script = """
            define has_return
            begin
                repeat with i from 5 to 10
                begin
                    if i == 6
                        return 1000
                end
                return 0
            end

            print [has_return]
        """
        self.run_and_check(script, 1000)

    def test_erroneous_break(self):
        script = "hue 5 saturation 6 break set all"
        parser = parse.Parser()
        parser.set_testing_errors()
        self.assertFalse(parser.parse(script))
        self.assertEqual(parser.get_errors(), '1')


if __name__ == '__main__':
    unittest.main()
