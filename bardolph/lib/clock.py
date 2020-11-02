from datetime import datetime
import threading
import time

from . import injection
from . import i_lib

def now():
    # seconds
    return time.time()


def configure():
    injection.bind(Clock).to(i_lib.Clock)


# All time quantities are in seconds.
class Clock(i_lib.Clock):
    def __init__(self):
        self._event = threading.Event()
        self._start_time = 0.0
        self._cue_time = 0.0
        self._keep_going = True

    def start(self):
        self.reset()
        threading.Thread(target=self.run, args=(), daemon=True).start()

    @injection.inject(i_lib.Settings)
    def run(self, settings):
        self._keep_going = True
        sleep_time = float(settings.get_value('sleep_time'))
        while self._keep_going:
            if sleep_time > 0.0:
                time.sleep(sleep_time)
            self.fire()

    def stop(self):
        self._keep_going = False

    def reset(self):
        self._cue_time = 0.0
        self._start_time = now()

    def et(self):
        return time.time() - self._start_time

    def fire(self):
        self._event.set()
        self._event.clear()

    def wait(self):
        if self._keep_going:
            self._event.wait()
        return self._keep_going

    def pause_for(self, delay):
        self._cue_time += delay
        while self.et() < self._cue_time:
            if not self.wait():
                break

    def wait_until(self, time_pattern):
        hour, minute = Clock._hour_minute()
        while not time_pattern.match(hour, minute):
            self.wait()
            hour, minute = Clock._hour_minute()
        self.reset()

    @staticmethod
    def _hour_minute():
        now = datetime.now()
        return (now.hour, now.minute)
