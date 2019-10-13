#!/usr/bin/env python

import argparse
import logging

from ..lib import injection
from ..lib import job_control
from ..lib import settings

from . import light_module
from . import config_values
from .script_runner import ScriptRunner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='name of the script file', nargs='*')
    parser.add_argument(
        '-f', '--fakes', help='use fake lights', action='store_true')
    parser.add_argument(
        '-r', '--repeat', help='repeat until key pressed', action='store_true')
    parser.add_argument(
        '-s', '--script', help='run script from command line', action='store')
    parser.add_argument(
        '-v', '--verbose', help='verbose output', action='store_true')
    args = parser.parse_args()

    injection.configure()
    settings.using_base(config_values.functional).configure()
    overrides = {
        'log_date_format': "%I:%M:%S %p",
        'log_format': '%(asctime)s %(filename)s(%(lineno)d): %(message)s',
        'log_level': logging.DEBUG if args.verbose else logging.INFO,
        'log_to_console': True,
        'sleep_time': 0.1
    }
    if args.fakes:
        overrides['use_fakes'] = True

    settings.specialize(overrides)
    light_module.configure()

    jobs = job_control.JobControl(args.repeat)
    if args.script is not None:
        jobs.add_job(ScriptRunner.from_string(args.script))
    for file_name in args.file:
        jobs.add_job(ScriptRunner.from_file(file_name))


if __name__ == "__main__":
    main()
