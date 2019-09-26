import collections
import logging
import threading


class Job:
    def execute(self): pass
    def request_stop(self): pass


class Promise:
    def __init__(self, job, callback):
        self.job = job
        self.callback = callback

    def execute(self):
        threading.Thread(
            target=self.execute_and_call).start()
        return self
              
    def execute_and_call(self):
        self.job.execute()
        return self.callback()

    def request_stop(self):
        self.job.request_stop()
    

class JobControl:
    def __init__(self, repeat=False):
        self.promise = None
        self.queue = collections.deque()
        self.repeat = repeat
        self.lock = threading.RLock()
    
    def set_repeat(self, repeat):
        self.repeat = repeat
    
    def add_job(self, job):
        return self.enqueue_job(job, self.queue.append)
    
    def insert_job(self, job):
        return self.enqueue_job(job, self.queue.appendleft)
                
    def enqueue_job(self, job, fn): 
        if not self.lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                fn(job)
                if self.promise is None:
                    self.run_next_job()
            finally:
                self.lock.release()
    
    def has_jobs(self):
        return len(self.queue) > 0
                
    def run_next_job(self):
        if not self.lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                if self.promise is None and len(self.queue) > 0:
                    next_job = self.queue.popleft()
                    if self.repeat:
                        self.queue.append(next_job) 
                    self.promise = Promise(next_job, self.on_execution_done)
                    self.promise.execute()
            finally:        
                self.lock.release()

    def on_execution_done(self):
        if not self.lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                self.promise = None
                logging.debug("Script jobs finished.")
            finally:
                self.lock.release()        
            self.run_next_job()

    def request_stop(self):
        if not self.lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                logging.debug("Stop requested.")
                self.repeat = False
                self.queue.clear()
                p = self.promise
                if p != None:
                    self.promise = None
                    p.request_stop()
            finally:
                self.lock.release()

    def request_finish(self):
        """ Clear out the queue but let the running job finish. """
        if not self.lock.acquire(True, 1.0):
            logging.error("Unable to acquire lock.")
        else:
            try:
                logging.debug("Finish requested.")
                self.repeat = False
                self.queue.clear()
            finally:
                self.lock.release()
