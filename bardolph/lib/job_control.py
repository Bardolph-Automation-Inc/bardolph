import collections
import logging
import threading


class Job:
    def __init__(self, name=None):
        if name is not None:
            self._name = name 
        else:
            self._name = 'job {}'.format(self.__hash__())
    
    @property
    def name(self):
        return self._name 
        
    def execute(self): pass
    def request_stop(self): pass


class Agent:
    def __init__(self, job, callback, repeat=False):
        self._job = job
        self._callback = callback
        self._repeat = repeat

    @property
    def job(self):
        return self._job
    
    @property
    def repeat(self):
        return self._repeat

    def execute(self):
        threading.Thread(target=self._execute_and_call).start()
        return self

    def request_stop(self):
        self._repeat = False
        self._job.request_stop()

    def _execute_and_call(self):
        self._job.execute()    
        return self._callback(self)


class JobControl:
    # By default, jobs are added to the right and pulled out from the left.
    
    def __init__(self):
        self._background = set()
        self._active_agent = None
        self._queue = collections.deque()
        self._lock = threading.RLock()

    def add_job(self, job, repeat=False):
        return self._enqueue_job(job, self._queue.append, repeat)

    def insert_job(self, job, repeat=False):
        return self._enqueue_job(job, self._queue.appendleft, repeat)
    
    def _enqueue_job(self, job, append_fn, repeat):
        if self._acquire_lock():
            try:
                append_fn(Agent(job, self._on_execution_done, repeat))
                if self._active_agent is None:
                    self.run_next_job()
            finally:
                self._lock.release()

    def has_jobs(self):
        return (len(self._queue) > 0 or len(self._background) > 0 or
            self._active_agent is not None)

    def run_next_job(self):
        if self._acquire_lock():
            try:
                if self._active_agent is None and len(self._queue) > 0:
                    self._active_agent = self._queue.popleft()
                    self._active_agent.execute()
            finally:
                self._release_lock()

    def request_stop(self, stop_background=False):
        logging.debug("Stopping jobs.")
        if self._acquire_lock():
            try:
                if stop_background:
                    self._stop_background_jobs()
                self._queue.clear()
                agent = self._active_agent
                if agent is not None:
                    self._active_agent = None
                    agent.request_stop()
            finally:
                self._release_lock()

    def _on_execution_done(self, agent):
        if self._acquire_lock():
            try:
                self._active_agent = None
                if agent.repeat:
                    self._queue.append(agent)
            finally:
                self._release_lock()
            self.run_next_job()

    def spawn_job(self, job, repeat=False):           
        if self._acquire_lock():
            try:
                agent = Agent(job, self._on_background_done, repeat)
                self._background.add(agent)
                agent.execute()
            finally:
                self._release_lock()

    def _on_background_done(self, agent):
        if self._acquire_lock():
            try:
                if agent.repeat:
                    agent.execute()
                else:
                    self._background.discard(agent)
            finally:
                self._release_lock()

    def _stop_background_jobs(self):
        logging.debug("Stopping background jobs.")
        if self._acquire_lock():
            try:
                agent_list = list(self._background)
                for agent in agent_list:
                    agent.request_stop()
            finally:
                self._release_lock()

    def _acquire_lock(self):
        if not self._lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
            return False
        return True
    
    def _release_lock(self):
        self._lock.release()
    