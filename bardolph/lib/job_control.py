import collections
import logging
import threading


class Job:
    def execute(self): pass
    def request_stop(self): pass


class Agent:
    """
    The name serves as the unique identifier. When the job finishes, the
    callback is invoked with self (this Agent) as the only parameter.
    """
    def __init__(self, job, callback, name=None):
        self._job = job
        self._callback = callback
        self._thread = None
        self._name = name or 'job {}'.format(id(self))

    @property
    def name(self):
        return self._name

    @property
    def job(self):
        return self._job

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def execute(self):
        self._thread = threading.Thread(target=self._execute_and_call)
        self._thread.start()
        return self

    def request_stop(self):
        self._job.request_stop()

    def _execute_and_call(self):
        try:
            self._job.execute()
        finally:
            self._callback(self)


def failed_job() -> Agent:
    class FailedJob:
        def execute(self):
            return False
        def request_stop(self):
            return True
    callback = lambda _: None
    return Agent(FailedJob(), callback, "failed job")


class JobControl:
    """
    Jobs are pulled out from the left (front of the queue). add_job() appends
    one to the end (right side), while insert_job() inserts it in front (left
    side).
    """
    def __init__(self):
        self._background = {}
        self._active_agent = None
        self._queue = collections.deque()
        self._lock = threading.RLock()

    def clear_queue(self) -> None:
        self._queue.clear()

    def add_job(self, job, name=None):
        return self._enqueue_job(job, self._queue.append, name)

    def insert_job(self, job, name=None):
        return self._enqueue_job(job, self._queue.appendleft, name)

    def spawn_job(self, job, name):
        agent = None
        if self._acquire_lock():
            try:
                agent = Agent(job, self._on_background_done, name)
                self._background[agent.name] = agent
                agent.execute()
            finally:
                self._release_lock()
        return agent

    def get_queued(self):
        return list(self._queue) if self._queue is not None else None

    def get_background(self):
        if self._background is None:
            return None
        return self._background.values()

    def get_current(self):
        return self._active_agent

    def is_running(self, name) -> bool:
        if self._active_agent is not None and self._active_agent.name == name:
            return True
        return name in self._background

    def stop_background(self) -> bool:
        result = False
        if self._acquire_lock():
            result = True
            try:
                # Get a copy to avoid iterating over a list that's undergoing
                # deletions.
                agents = self.get_background()
                if agents is not None:
                    for agent in list(agents).copy():
                        agent.request_stop()
            finally:
                self._release_lock()
        return result

    def stop_job(self, name) -> bool:
        result = False
        if self._acquire_lock():
            try:
                if (self._active_agent is not None and
                        self._active_agent.name == name):
                    self._active_agent.request_stop()
                    result = True
                elif name in self._background:
                    self._background[name].request_stop()
                    result = True
            finally:
                self._release_lock()
        return result

    def stop_current(self) -> bool:
        if self._active_agent is not None and self._active_agent.is_running():
            if self._acquire_lock():
                try:
                    self._active_agent.request_stop()
                finally:
                    self._release_lock()
                return True
        return False

    def has_jobs(self) -> bool:
        return (len(self._queue) > 0 or len(self._background) > 0 or
                self._active_agent is not None)

    def _run_next_job(self) -> None:
        if self._acquire_lock():
            try:
                if self._active_agent is None and len(self._queue) > 0:
                    self._active_agent = self._queue.popleft()
                    self._active_agent.execute()
            finally:
                self._release_lock()

    def _enqueue_job(self, job, append_fn, name):
        agent = None
        if self._acquire_lock():
            try:
                agent = Agent(job, self._on_execution_done, name)
                append_fn(agent)
                if self._active_agent is None:
                    self._run_next_job()
            finally:
                self._lock.release()
        return agent

    def _on_execution_done(self, _):
        if self._acquire_lock():
            try:
                self._active_agent = None
            finally:
                self._release_lock()
            self._run_next_job()

    def _on_background_done(self, agent):
        if self._acquire_lock():
            try:
                del self._background[agent.name]
            finally:
                self._release_lock()

    def _acquire_lock(self):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
            return False
        return True

    def _release_lock(self):
        self._lock.release()

