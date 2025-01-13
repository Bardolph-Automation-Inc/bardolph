import logging

functional = {
    'default_num_lights': None,
    'sleep_time': 0.01, # seconds

    'generated_path': 'generated',
    'log_date_format': '%D %H:%M:%S',
    'log_format':
        '%(asctime)s %(filename)s(%(lineno)d) %(funcName)s(): %(message)s',
    'log_level': logging.ERROR,
    'log_to_console': True,

    # Ignored unless log_to_console is False.
    'log_file_name': '/var/log/lights/lights.log',

    # How long to wait before attempting the next discovery.
    'refresh_sleep_time': 60, # seconds, used when there was no problem.
    'failure_sleep_time': 20, # seconds, used when the last one failed.

    # How long to wait before pruning lights that seem to have disappeared.
    'light_gc_time': 300, # seconds

    'script_path': 'scripts',
    'single_light_discover': False,
    'use_fakes': False
}
