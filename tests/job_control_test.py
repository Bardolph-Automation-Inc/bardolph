#!/usr/bin/env python

import time
import unittest.mock

from bardolph.lib import job_control


class TestJob(job_control.Job):
    def __init__(self):
        super().__init__()
        self.execute = unittest.mock.Mock()


class UnwantedJob(job_control.Job):
    def __init__(self):
        super().__init__()
        self.failed = False

    def execute(self):
        self.failed = True


class StoppableJob(job_control.Job):
    def __init__(self, test_case):
        super().__init__()
        self._test_case = test_case

    def execute(self):
        self._test_case.job_stopped = False
        time.sleep(0.1)

    def request_stop(self):
        self._test_case.job_stopped = True


class JobControlTest(unittest.TestCase):
    def setUp(self):
        self.failed = False
        self.job_stopped = False

    @classmethod
    def wait_for_threads(cls, j_control):
        while j_control.has_jobs():
            time.sleep(0.2)

    def test_add_one(self):
        j_control = job_control.JobControl()
        job = TestJob()
        j_control.add_job(job)
        JobControlTest.wait_for_threads(j_control)
        job.execute.assert_called_once()

    def test_add_multiple(self):
        j_control = job_control.JobControl()
        job = TestJob()
        num_jobs = 10
        for _ in range(0, num_jobs):
            j_control.add_job(job)
        JobControlTest.wait_for_threads(j_control)
        self.assertEqual(job.execute.call_count, num_jobs)

    def test_request_stop(self):
        j_control = job_control.JobControl()
        for _ in range(0, 20):
            j_control.add_job(StoppableJob(self))
        unwanted = UnwantedJob()
        j_control.add_job(unwanted)
        time.sleep(0.1)
        j_control.request_stop()
        JobControlTest.wait_for_threads(j_control)
        self.assertFalse(unwanted.failed, "Failure j_control should not have been run.")
        self.assertTrue(self.job_stopped, "Job not stopped.")

    def test_repeat(self):
        job1 = TestJob()
        job2 = TestJob()
        j_control = job_control.JobControl()
        j_control.set_repeat(True)
        j_control.add_job(job1)
        j_control.add_job(job2)
        time.sleep(0.1)
        j_control.request_stop()
        JobControlTest.wait_for_threads(j_control)
        self.assertTrue(job1.execute.call_count > 1)
        self.assertTrue(job2.execute.call_count > 1)

if __name__ == "__main__":
    unittest.main()
