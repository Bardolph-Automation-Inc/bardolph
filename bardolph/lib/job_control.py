import collections
import logging
import threading


class Job:
    def execute(self): pass
    def request_stop(self): pass


class Promise:
    def __init__(self, job, callback, repeat=False):
        self._job = job
        self._callback = callback
        self._repeat = repeat

    @property
    def job(self):
        return self._job

    def execute(self):
        threading.Thread(target=self._execute_and_call).start()
        return self

    def request_stop(self):
        self._repeat = False
        self._job.request_stop()

    def _execute_and_call(self):
        if self._repeat:
            while self._repeat:
                self._job.execute()
        else:
            self._job.execute()    
        return self._callback(self)


class JobControl:
    def __init__(self, repeat=False):
        self._background = set()
        self._promise = None
        self._queue = collections.deque()
        self._repeat = repeat
        self._lock = threading.RLock()

    def set_repeat(self, repeat):
        self._repeat = repeat

    def add_job(self, job):
        return self._enqueue_job(job, self._queue.append)

    def insert_job(self, job):
        return self._enqueue_job(job, self._queue.appendleft)
    
    def spawn_job(self, job, repeat=False):           
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                promise = Promise(job, self._remove_background_job, repeat)
                self._background.add(promise)
                promise.execute()
            finally:
                self._lock.release()

    def has_jobs(self):
        return len(self._queue) > 0 or len(self._background) > 0

    def run_next_job(self):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                if self._promise is None and len(self._queue) > 0:
                    next_job = self._queue.popleft()
                    if self._repeat:
                        self._queue.append(next_job)
                    self._promise = Promise(next_job, self._on_execution_done)
                    self._promise.execute()
            finally:
                self._lock.release()

    def request_stop(self, stop_background=False):
        logging.debug("Stopping jobs.")
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                self._repeat = False
                if stop_background:
                    self._stop_background_jobs()
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

    def _on_execution_done(self, _):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                self._promise = None
            finally:
                self._lock.release()
            self.run_next_job()

    def _remove_background_job(self, promise):
        self._background.discard(promise)
        
    def _stop_background_jobs(self):
        logging.debug("Stopping background jobs.")
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                promise_list = list(self._background)
                for promise in promise_list:
                    promise.request_stop()
            finally:
                self._lock.release()

    def _enqueue_job(self, job, append_fn):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                append_fn(job)
                if self._promise is None:
                    self.run_next_job()
            finally:
                self._lock.release()
