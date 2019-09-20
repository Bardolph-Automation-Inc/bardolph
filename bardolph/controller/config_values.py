import logging

functional = {
    'default_num_lights': 5,
    'sleep_time': 0.01, # seconds
    
    'script_path': 'scripts',
    'generated_path': 'generated',
    'log_date_format': '%D %H:%M:%S',
    'log_format':
        '%(asctime)s %(filename)s(%(lineno)d) %(funcName)s(): %(message)s',
    'log_level': logging.WARNING,
    'log_to_console': True,
    'refresh_sleep_time': 600, # seconds
    'failure_sleep_time': 120, # seconds
    'single_light_discover': False,
    'use_fakes': False,

    # Ignored unless log_to_console gets overridden to False.
    'log_file_name': '/var/log/lights/lights.log'
}

