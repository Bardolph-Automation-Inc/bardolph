import datetime
import logging

from .i_lib import Settings
from .injection import inject


logging_defaults = {
    'log_date_format': '%D %H:%M:%S',
    'log_file_name': '/tmp/python_log',
    'log_format':
        '%(asctime)s %(filename)s(%(lineno)d) %(funcName)s(): %(message)s',
    'log_level': logging.INFO,
    'log_to_console': False
}

class LogConfig():
    def _extract_level(self):
        level = self.get_value('log_level')
        if isinstance(level, str):
            level = getattr(logging, level.strip(), logging.ERROR)
        return level

    @inject(Settings)
    def get_value(self, name, settings):
        return settings.get_value(name, logging_defaults.get(name, None))

    def configure(self):
        if self.get_value('log_to_console'):
            logging.basicConfig(
                level=self._extract_level(),
                format=self.get_value('log_format'),
                datefmt=self.get_value('log_date_format'))
        else:
            logging.basicConfig(
                filename=self.get_value('log_file_name'),
                level=self._extract_level(),
                format=self.get_value('log_format'),
                datefmt=self.get_value('log_date_format'))
            logging.info(
                "\n\n\nLogging started {}"
                .format(datetime.datetime.now().strftime("%I:%M:%S %p")))

def configure():
    LogConfig().configure()
