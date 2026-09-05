import threading
import time
from datetime import datetime

from bardolph.lib import i_lib, injection


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

    def start(self) -> None:
        self._reset()
        threading.Thread(target=self._run, args=(), daemon=True).start()

    def stop(self) -> None:
        self._keep_going = False

    def wait_until(self, time_pattern) -> None:
        hour, minute = Clock._hour_minute()
        while not time_pattern.match(hour, minute):
            self._wait()
            hour, minute = Clock._hour_minute()
        self._reset()

    def pause_for(self, delay) -> None:
        self._cue_time += delay
        while self._et() < self._cue_time:
            if not self._wait():
                break

    @injection.inject(i_lib.Settings)
    def _run(self, settings):
        self._keep_going = True
        sleep_time = float(settings.get_value('sleep_time'))
        while self._keep_going:
            if sleep_time > 0.0:
                time.sleep(sleep_time)
            self._fire()

    def _reset(self):
        self._cue_time = 0.0
        self._start_time = now()

    def _et(self):
        return time.time() - self._start_time

    def _fire(self):
        self._event.set()
        self._event.clear()

    def _wait(self):
        if self._keep_going:
            self._event.wait()
        return self._keep_going

    @staticmethod
    def _hour_minute():
        now = datetime.now()
        return (now.hour, now.minute)
