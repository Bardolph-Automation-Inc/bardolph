#!/usr/bin/env python

import time
import unittest

from bardolph.lib import job_control
from tests.threaded_test import ThreadedTest


class _TestJob(job_control.Job):
    # 50 ms.
    _sleep_time = 0.05

    def __init__(self, run_until_stopped: bool = True):
        super().__init__()
        self._running = False
        self._executed = False
        self._stop_requested = False
        self._loop_count = 0

        # If run_until_stopped is False, execute() exits immediately. Otherwise,
        # it will run in a loop containing a sleep() call until request_stop()
        # is called.
        self._run_until_stopped = run_until_stopped

    @property
    def running(self) -> bool:
        return self._running

    @property
    def executed(self) -> bool:
        return self._executed

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    @property
    def loop_count(self) -> int:
        return self._loop_count

    def allow_stop(self, sleep_time: float | None = None) -> None:
        while self._running:
            self.pause_for_thread(sleep_time)

    @staticmethod
    def pause_for_thread(sleep_time: float | None = None) -> None:
        if sleep_time is None:
            time.sleep(_TestJob._sleep_time * 2.0)
        else:
            time.sleep(sleep_time)

    def execute(self) -> None:
        self._running = True
        self._executed = True
        if self._run_until_stopped:
            while not self._stop_requested:
                self._loop_count += 1
                time.sleep(self._sleep_time)
        self._running = False

    def request_stop(self) -> None:
        self._stop_requested = True


class _ReportingJob(_TestJob):
    def __init__(self, name: str, report_to: list):
        super().__init__()
        self._name = name
        self._report_to = report_to

    @property
    def name(self) -> str:
        return self._name

    def execute(self) -> None:
        self._report_to.append(self._name)
        super().execute()


class _Sequence:
    def __init__(self):
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    def advance(self) -> None:
        self._value += 1


class _SequentialJob(_TestJob):
    def __init__(self, sequence: _Sequence):
        super().__init__(False)
        self._sequence = sequence
        self._sequence_val = 0

    @property
    def sequence_val(self) -> int:
        return self._sequence_val

    def execute(self) -> None:
        super().execute()
        self._sequence_val = self._sequence.value
        self._sequence.advance()


class JobControlTest(ThreadedTest):
    def setUp(self) -> None:
        self._job_control = job_control.JobControl()

    def test_add_one(self) -> None:
        job = _TestJob()
        agent = self._job_control.append_job(job)
        agent.request_stop()
        job.allow_stop()
        self.assertTrue(job.executed)
        self.assertFalse(job.running)
        self.assertGreater(job.loop_count, 0)

    def test_add_multiple(self) -> None:
        jobs = (_TestJob() for _ in range(3))
        agents: list[job_control.Agent] = []
        for job in jobs:
            agents.append(self._job_control.append_job(job))
        for agent in agents:
            agent.request_stop()
        for job in jobs:
            job.allow_stop()
        for job in jobs:
            self.assertTrue(job.executed)
            self.assertFalse(job.running)
            self.assertGreater(job.loop_count, 0)

    def test_run_job(self) -> None:
        job1 = _TestJob()
        job2 = _TestJob()
        job3 = _TestJob()

        self._job_control.append_job(job1)
        self._job_control.append_job(job2)

        # Clears queue and runs job3 immediately. job2 should never run.
        self._job_control.run_job(job3)
        job3.request_stop()
        for job in (job1, job2, job3):
            job.allow_stop()

        self.assertTrue(job1.executed)
        self.assertFalse(job2.executed)
        self.assertTrue(job3.executed)

    def test_run_iterated(self) -> None:
        sequence = _Sequence()
        job_list = [_SequentialJob(sequence) for _ in range(3)]
        self._job_control.run_iterated(iter(job_list))
        for job in job_list:
            job.allow_stop()
        self.assertFalse(self._job_control.has_any_jobs())
        self.assertEqual(job_list[0].sequence_val, 0)
        self.assertEqual(job_list[1].sequence_val, 1)
        self.assertEqual(job_list[2].sequence_val, 2)

    def test_spawn(self) -> None:
        fg_job = _TestJob()
        self._job_control.append_job(fg_job)
        bg_job_0 = _TestJob()
        self._job_control.spawn(bg_job_0)
        bg_job_1 = _TestJob()
        self._job_control.spawn(bg_job_1)

        self.assertTrue(fg_job.running)
        self.assertTrue(bg_job_0.running)
        self.assertTrue(bg_job_1.running)

        fg_job.request_stop()
        fg_job.allow_stop()
        bg_job_0.request_stop()
        bg_job_0.allow_stop()
        bg_job_1.request_stop()
        bg_job_1.allow_stop()

        self.assertTrue(fg_job.executed)
        self.assertTrue(bg_job_0.executed)
        self.assertTrue(bg_job_1.executed)

    def test_get_queued(self) -> None:
        jobs = [_TestJob() for _ in range(5)]
        for job in jobs:
            self._job_control.append_job(job)
        jobs_list = [agent.job for agent in self._job_control.get_queued()]
        for job in jobs:
            job.request_stop()
        self.assertListEqual(jobs[1:], jobs_list)

    def test_get_background(self) -> None:
        jobs = [_TestJob() for _ in range(5)]
        for job in jobs:
            self._job_control.spawn(job)
        job_list = [agent.job for agent in self._job_control.get_background()]
        for job in jobs:
            job.request_stop()

        # Order not guaranteed, so put them into sets.
        self.assertSetEqual(set(jobs), set(job_list))

    def test_get_foreground(self) -> None:
        self.assertIsNone(self._job_control.get_foreground())
        job = _TestJob()
        self._job_control.append_job(job)
        self.assertEqual(self._job_control.get_foreground().job, job)
        job.request_stop()
        job.allow_stop()
        self.assertIsNone(self._job_control.get_foreground())

    def test_stop_foreground(self) -> None:
        job0, job1 = _TestJob(), _TestJob()

        self._job_control.append_job(job0)
        self._job_control.append_job(job1)

        self.assertEqual(self._job_control.get_foreground().job, job0)
        self._job_control.stop_foreground()
        self.assertTrue(job0.stop_requested)
        job0.allow_stop()

        self.assertEqual(self._job_control.get_foreground().job, job1)
        job1.request_stop()
        job1.allow_stop()

        self.assertIsNone(self._job_control.get_foreground())
        self.assertFalse(self._job_control.has_any_jobs())

    def test_clear_foreground(self) -> None:
        job0, job1, job2 = _TestJob(), _TestJob(), _TestJob()
        for job in (job0, job1, job2):
            self._job_control.append_job(job)

        self.assertTrue(job0.running)
        job0.request_stop()
        job0.allow_stop()

        self.assertTrue(job1.running)
        self._job_control.clear_foreground()
        job1.allow_stop()
        job2.allow_stop()

        self.assertIsNone(self._job_control.get_foreground())
        self.assertFalse(self._job_control.has_any_jobs())

    def test_clear_background(self) -> None:
        self.assertFalse(self._job_control.clear_background())
        jobs = [_TestJob() for _ in range(5)]
        for job in jobs:
            self._job_control.spawn(job)
        self.assertTrue(self._job_control.has_any_jobs())
        self._job_control.clear_background()
        for job in jobs:
            job.allow_stop()
        self.assertFalse(self._job_control.has_any_jobs())

    def test_has_any_jobs(self) -> None:
        self.assertFalse(self._job_control.has_any_jobs())
        job0 = _TestJob()
        self._job_control.append_job(job0)
        self.assertTrue(self._job_control.has_any_jobs())
        job1 = _TestJob()
        self._job_control.spawn(job1)
        self.assertTrue(self._job_control.has_any_jobs())
        job0.request_stop()
        job0.allow_stop()
        self.assertTrue(self._job_control.has_any_jobs())
        job1.request_stop()
        job1.allow_stop()
        self.assertFalse(self._job_control.has_any_jobs())


if __name__ == "__main__":
    unittest.main()
