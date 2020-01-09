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
    def __init__(self):
        super().__init__()
        self._call_count = 0
        self._stop_requested = False

    def execute(self):
        self._call_count += 1
        time.sleep(0.1)

    def request_stop(self):
        self._stop_requested = True
        
    @property
    def call_count(self):
        return self._call_count

    @property
    def stop_requested(self):
        return self._stop_requested

class TrackedJob(StoppableJob):
    def __init__(self, job_id, call_list):
        super().__init__()
        self._id = job_id
        self._call_list = call_list
        
    def execute(self):
        self._call_list.append(self._id)
        super().execute()

class JobControlTest(unittest.TestCase):
    def setUp(self):
        self.failed = False
        self.job_stopped = False

    def wait_for_threads(self, j_control):
        max_wait = 10
        while j_control.has_jobs():
            time.sleep(0.2)
            max_wait -= 1
            if max_wait <= 0:
                self.fail("jobs still running")

    def test_add_one(self):
        j_control = job_control.JobControl()
        job = TestJob()
        j_control.add_job(job)
        self.wait_for_threads(j_control)
        job.execute.assert_called_once()

    def test_add_multiple(self):
        j_control = job_control.JobControl()
        call_list = []
        num_jobs = 5
        for job_num in range(0, num_jobs):
            name = 'tj {}'.format(job_num)
            j_control.add_job(TrackedJob(name, call_list))
        self.wait_for_threads(j_control)
        expected = ['tj 0', 'tj 1', 'tj 2', 'tj 3', 'tj 4']
        self.assertListEqual(call_list, expected)

    def test_request_stop(self):
        j_control = job_control.JobControl()
        for _ in range(0, 20):
            j_control.add_job(StoppableJob())
        unwanted = UnwantedJob()
        j_control.add_job(unwanted)
        time.sleep(0.1)
        j_control.request_stop()
        self.wait_for_threads(j_control)
        self.assertFalse(
            unwanted.failed, "Failure: job should not have been run.")

    def test_repeat(self):
        call_list = []
        job1 = TrackedJob(1, call_list)
        job2 = TrackedJob(2, call_list)
        j_control = job_control.JobControl()
        j_control.add_job(job1, True)
        j_control.add_job(job2, True)
        time.sleep(1)
        j_control.request_stop()
        self.wait_for_threads(j_control)
        self.assertListEqual(call_list[0:4], [1, 2, 1, 2])
        
    def test_background_jobs(self):
        job1 = StoppableJob()
        job2 = StoppableJob()
        j_control = job_control.JobControl()
        j_control.spawn_job(job1)
        j_control.spawn_job(job2, True)
        time.sleep(1)
        j_control.request_stop(True)
        self.wait_for_threads(j_control)
        self.assertEqual(job1.call_count, 1)
        self.assertGreater(job2.call_count, 1)               

if __name__ == "__main__":
    unittest.main()
