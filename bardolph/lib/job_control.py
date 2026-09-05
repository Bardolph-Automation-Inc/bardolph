import collections
import threading
from collections.abc import Iterator
from functools import partial


class Job:
    """
    A Job runs in a single thread. A call to execute() blocks until the job
    finishes.
    """

    def execute(self) -> None: pass
    def request_stop(self) -> None: pass


class Agent:
    """
    When the job finishes, the callback is invoked with self (this Agent) as
    the only parameter.
    """

    def __init__(self, job: Job, callback=None):
        self._job = job
        self._callback = callback
        self._thread = None
        self._stop_requested = False

    @property
    def job(self) -> Job:
        return self._job

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def launch(self) -> None:
        """
        Run the job inside a new Thread. This function returns immediately.
        """
        if not self._stop_requested:
            self._thread = threading.Thread(target=self.run)
            self._thread.start()

    def run(self) -> None:
        """
        Run the job. This function blocks until the job finishes executing.
        """
        if not self._stop_requested:
            self._job.execute()
        if self._callback:
            self._callback(self)

    def request_stop(self) -> None:
        self._stop_requested = True
        self._job.request_stop()


class JobControl:
    """
    Each running Job is contained by an Agent. There is one foreground Agent
    and a dictionary of background Agents. The foreground Agents typically come
    from the queue.

    Jobs are pulled out from the left (front of the queue). add_job() appends
    one to the end (right side).
    """

    def __init__(self):
        self._bg_agents = set()
        self._fg_agent = None
        self._fg_queue = collections.deque()

    def clear_queue(self) -> None:
        self._fg_queue.clear()

    def append_job(self, job: Job) -> Agent:
        """
        Add a Job to the end of the foreground queue. This function returns
        without waiting.
        """
        return self._enqueue_job(job, self._fg_queue.append)

    def run_job(self, job: Job, callback=None) -> Agent:
        """
        Clear out the foreground queue and stop the foreground job if one is
        running. Run the incoming job immediately. This function returns without
        waiting.
        """
        if callback is not None:
            fn = partial(self._callback_chain, callback, self._on_fg_done)
        else:
            fn = self._on_fg_done
        agent = Agent(job, fn)
        self.clear_foreground()
        self._fg_agent = agent
        agent.launch()
        return agent

    def run_iterated(self, producer: Iterator[Job]) -> bool:
        """
        Run jobs one after another. Rather than putting them all into the
        queue, get each job when the current one finishes. This function
        blocks until all of the Jobs have been processed.
        """
        for job in producer:
            self._fg_agent = Agent(job)
            self._fg_agent.run()
            self._fg_agent = None
        return True

    def spawn(self, job: Job) -> Agent:
        """
        Run a job in the background. This function returns without waiting.
        """
        agent = Agent(job, self._on_bg_done)
        self._bg_agents.add(agent)
        agent.launch()
        return agent

    def get_queued(self) -> list[Agent]:
        return list(self._fg_queue)

    def get_background(self) -> list[Agent]:
        return list(self._bg_agents)

    def get_foreground(self) -> Agent | None:
        return self._fg_agent

    def stop_foreground(self) -> None:
        if self._fg_agent is not None:
            self._fg_agent.request_stop()

    def clear_foreground(self) -> None:
        """
        Clear the queue and stop the foreground job.
        """
        self._fg_queue.clear()
        fg_agent = self._fg_agent
        if fg_agent is not None:
            fg_agent.request_stop()

    def clear_background(self) -> None:
        """
        Stop and clear out all background jobs.
        """
        any_change = False
        agents = list(self._bg_agents)
        if len(agents) > 0:
            any_change = True
            list_copy = list(agents).copy()
            agents.clear()
        if any_change:
            for agent in list_copy:
                agent.request_stop()

    def has_any_jobs(self) -> bool:
        return (len(self._fg_queue) > 0
                or len(self._bg_agents) > 0
                or self._fg_agent is not None)

    def _run_next_job(self) -> None:
        """
        If necessary, get the next Job from the queue and run it. If a
        foreground Job is already present, do nothing.
        """
        if self._fg_agent is None and len(self._fg_queue) > 0:
            self._fg_agent = self._fg_queue.popleft()
            if self._fg_agent is not None:
                self._fg_agent.launch()

    def _enqueue_job(self, job, append_fn) -> Agent:
        """
        append_fn is deque.append() or deque.appendleft().
        """
        agent = Agent(job, self._on_fg_done)
        append_fn(agent)
        self._run_next_job()
        return agent

    def _on_fg_done(self, agent: Agent) -> None:
        if agent is self._fg_agent:
            self._fg_agent = None
        self._run_next_job()

    def _on_bg_done(self, agent: Agent) -> None:
        self._bg_agents.discard(agent)
