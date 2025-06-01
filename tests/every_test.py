#!/usr/bin/env python

import importlib
import unittest

module_names = (
    'activity_log_test',
    ### 'array_test',
    ### 'array_vm_test',
    'block_candle_test',
    'call_stack_test',
    'candle_test',
    'clock_test',
    'code_gen_test',
    'color_matrix_test',
    'context_test',
    'define_test',
    'end_to_end_test',
    'example_test',
    'expr_test',
    'fake_light_builder_test',
    'function_test',
    'injection_test',
    'io_parser_test',
    'job_control_test',
    'lex_test',
    'light_set_test',
    'log_config_test',
    'loop_test',
    'ls_module_test',
    'math_runtime_test',
    'noneable_test',
    'param_helper_test',
    'parser_test',
    'print_test',
    'query_test',
    'retry_test',
    'settings_test',
    'sorted_list_test',
    'time_pattern_test',
    'units_test',
    'vm_discover_test',
    'vm_math_test',
    'web_app_test'
)

modules = (importlib.import_module('tests.' + module_name)
            for module_name in module_names)

loader = unittest.TestLoader()
suite = unittest.TestSuite()

for module in modules:
    suite.addTests(loader.loadTestsFromModule(module))

unittest.TextTestRunner(verbosity=2).run(suite)
