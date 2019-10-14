import collections
import logging
import threading


class Job:
    def execute(self): pass
    def request_stop(self): pass


class Promise:
    def __init__(self, job, callback):
        self._job = job
        self._callback = callback

    def execute(self):
        threading.Thread(
            target=self.execute_and_call).start()
        return self

    def execute_and_call(self):
        self._job.execute()
        return self._callback()

    def request_stop(self):
        self._job.request_stop()


class JobControl:
    def __init__(self, repeat=False):
        self._promise = None
        self._queue = collections.deque()
        self._repeat = repeat
        self._lock = threading.RLock()

    def set_repeat(self, repeat):
        self._repeat = repeat

    def add_job(self, job):
        return self.enqueue_job(job, self._queue.append)

    def insert_job(self, job):
        return self.enqueue_job(job, self._queue.appendleft)

    def enqueue_job(self, job, append_fn):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                append_fn(job)
                if self._promise is None:
                    self.run_next_job()
            finally:
                self._lock.release()

    def has_jobs(self):
        return len(self._queue) > 0

    def run_next_job(self):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                if self._promise is None and len(self._queue) > 0:
                    next_job = self._queue.popleft()
                    if self._repeat:
                        self._queue.append(next_job)
                    self._promise = Promise(next_job, self.on_execution_done)
                    self._promise.execute()
            finally:
                self._lock.release()

    def on_execution_done(self):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                self._promise = None
            finally:
                self._lock.release()
            self.run_next_job()

    def request_stop(self):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                self._repeat = False
                self._queue.clear()
                promise = self._promise
                if promise is not None:
                    self._promise = None
                    promise.request_stop()
            finally:
                self._lock.release()

    def request_finish(self):
        """ Clear out the _queue but let the running job finish. """
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                self._repeat = False
                self._queue.clear()
            finally:
                self._lock.release()
