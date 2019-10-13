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
        self.keep_going = False
        self.event = threading.Event()
        self.start_time = 0.0
        self.cue_time = 0.0
        self.keep_going = True

    def start(self):
        self.reset()
        threading.Thread(target=self.run, args=(), daemon=True).start()

    @injection.inject(i_lib.Settings)
    def run(self, settings):
        self.keep_going = True
        sleep_time = float(settings.get_value('sleep_time'))
        while self.keep_going:
            if sleep_time > 0.0:
                time.sleep(sleep_time)
            self.fire()

    def stop(self):
        self.keep_going = False

    def reset(self):
        self.cue_time = 0.0
        self.start_time = now()

    def et(self):
        return time.time() - self.start_time

    def fire(self):
        if self.keep_going:
            self.event.set()
            self.event.clear()

    def wait(self):
        if self.keep_going:
            self.event.wait()
        return self.keep_going

    def pause_for(self, delay):
        self.cue_time += delay
        while self.et() < self.cue_time:
            self.wait()
