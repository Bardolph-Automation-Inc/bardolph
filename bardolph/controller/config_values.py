import logging

functional = {
    'default_num_lights': None,
    'light_gc_time': 20 * 60, # seconds (20 minutes)
    'sleep_time': 0.01, # seconds

    'generated_path': 'generated',
    'log_date_format': '%D %H:%M:%S',
    'log_format':
        '%(asctime)s %(filename)s(%(lineno)d) %(funcName)s(): %(message)s',
    'log_level': logging.ERROR,
    'log_to_console': True,

    # Ignored unless log_to_console is False.
    'log_file_name': '/var/log/lights/lights.log',

    'refresh_sleep_time': 600, # seconds
    'failure_sleep_time': 120, # seconds
    'script_path': 'scripts',
    'single_light_discover': False,
    'use_fakes': False
}
