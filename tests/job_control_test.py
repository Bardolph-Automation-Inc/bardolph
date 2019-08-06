#!/usr/bin/env python

import threading
import time
import unittest.mock

from bardolph.lib import job_control


class TestJob(job_control.Job):
    def __init__(self):
        self.execute = unittest.mock.Mock()

class FailJob(TestJob):
    def __init__(self, test_case):
        self.test_case = test_case
        
    def execute(self):
        self.test_case.failed = True

class StoppableJob(TestJob):
    def __init__(self, test_case):
        self.test_case = test_case
        
    def execute(self):
        self.test_case.job_stopped = False
        time.sleep(0.1)
        
    def request_stop(self):
        self.test_case.job_stopped = True

class JobControlTest(unittest.TestCase):
    def setUp(self):
        self.failed = False
        self.job_stopped = False
    
    def wait_for_threads(self, jc):
        while jc.has_jobs():
            time.sleep(0.2)
  
    def test_add_one(self):
        jc = job_control.JobControl()
        job = TestJob()
        jc.add_job(job)
        self.wait_for_threads(jc)    
        job.execute.assert_called_once()
      
    def test_add_multiple(self):
        jc = job_control.JobControl()
        job = TestJob()
        num_jobs = 10
        for _ in range(0, num_jobs):
            jc.add_job(job)
        self.wait_for_threads(jc)
        self.assertEqual(job.execute.call_count, num_jobs)

    def test_request_stop(self):
        jc = job_control.JobControl()
        for _ in range(0, 10):
            jc.add_job(StoppableJob(self))
        jc.add_job(FailJob(self))
        time.sleep(0.1)
        jc.request_stop()
        self.wait_for_threads(jc)
        self.assertFalse(self.failed, "Failure jobs should not have been run.")
        self.assertTrue(self.job_stopped, "Job not stopped.")

    def test_repeat(self):
        job1 = TestJob()
        job2 = TestJob()
        jc = job_control.JobControl()
        jc.set_repeat(True)
        jc.add_job(job1)
        jc.add_job(job2)
        time.sleep(0.1)
        jc.request_stop()
        self.wait_for_threads(jc)
        self.assertTrue(job1.execute.call_count > 1)
        self.assertTrue(job2.execute.call_count > 1)

if __name__ == "__main__":
    unittest.main()
