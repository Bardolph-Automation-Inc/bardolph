#!/usr/bin/env python

import argparse
import logging
import os

from ..lib import injection
from ..lib import job_control
from ..lib import settings

from . import arg_helper
from . import light_module
from . import config_values
from .script_job import ScriptJob

_epilog = """The -n parameter is optional, but if you don't specify it,
discovery of the lights will take several seconds, and there will
be a noticeable pause before the script actually runs. If specified, this
parameter overrides any values in any configuration files."""


def init_args():
    parser = argparse.ArgumentParser(epilog=_epilog)
    parser.add_argument('file', help='name of the script file', nargs='*')
    parser.add_argument(
        '-c', '--config-file', help='customized configuration file')
    parser.add_argument(
        '-f', '--fakes', help='use fake lights', action='store_true')
    arg_helper.add_n_argument(parser)
    parser.add_argument(
        '-s', '--script', help='run script from command line', action='store')
    parser.add_argument(
        '-v', '--verbose', help='verbose output', action='store_true')
    return parser.parse_args()


def init_settings(args):
    overrides = {
        'log_date_format': "%I:%M:%S %p",
        'log_format': '%(asctime)s %(filename)s(%(lineno)d): %(message)s',
        'log_level': logging.DEBUG if args.verbose else logging.INFO,
        'log_to_console': True,
        'sleep_time': 0.1
    }
    if args.fakes:
        overrides['use_fakes'] = True

    settings_init = settings.using(
        config_values.functional).add_overrides(overrides)

    if args.config_file:
        settings_init.apply_file(args.config_file)

    overrides = arg_helper.get_overrides(args)
    if overrides is not None:
        settings_init.add_overrides(overrides)
    settings_init.apply_env().configure()


def main():
    args = init_args()
    injection.configure()
    init_settings(args)
    light_module.configure()

    jobs = job_control.JobControl()
    if args.script is not None:
        jobs.add_job(ScriptJob.from_string(args.script))
    for file_name in args.file:
        jobs.add_job(ScriptJob.from_file(file_name))


if __name__ == "__main__":
    main()
