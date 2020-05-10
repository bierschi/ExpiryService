import logging
import heapq
import functools
import threading
from datetime import datetime


class Scheduler:
    """ class Scheduler to schedule threaded tasks

    USAGE:
            scheduler = Scheduler()
            scheduler.schedule(func, startts, *args)
            scheduler.periodic(5, test, 'test_message')
    """

    @functools.total_ordering
    class _Task:
        """A scheduled task"""

        def __init__(self, func, startts, *args):
            """Create task that will run fn at or after the datetime start."""
            self.func = func
            self.start = startts
            self.args = args
            self.cancelled = False

        def __le__(self, other):
            # Tasks compare according to their start time.
            return self.start <= other.start

        @property
        def timeout(self):
            """Return time remaining in seconds before task should start."""
            return (self.start - datetime.now()).total_seconds()

        def cancel(self):
            """Cancel task if it has not already started running."""
            self.cancelled = True

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class Scheduler')

        cv = self._cv = threading.Condition(threading.Lock())
        tasks = self._tasks = []

        self._lock = threading.Lock()
        self._timer = None
        self.function = None
        self.interval = None
        self.args = None
        self.kwargs = None
        self._stopped = True

        def run():
            while True:
                with cv:
                    while True:
                        timeout = None
                        while tasks and tasks[0].cancelled:
                            heapq.heappop(tasks)
                        if tasks:
                            timeout = tasks[0].timeout
                            if timeout <= 0:
                                task = heapq.heappop(tasks)
                                break

                        cv.wait(timeout=timeout)
                # self.logger.info("Starting new task thread")
                threading.Thread(target=task.func, args=task.args).start()

        threading.Thread(target=run, name='Scheduler').start()

    def schedule(self, func, startts, *args):
        """Schedule a task that will run fn at or after start (which must be a datetime object) and return an
        object representing that task.

        """

        task = self._Task(functools.partial(func), startts, *args)
        with self._cv:
            heapq.heappush(self._tasks, task)
            self._cv.notify()
        return task

    def get_tasks(self):
        """ get the tasks list

        :return: list with all open tasks
        """
        return self._tasks

    def is_tasks_empty(self):
        """ checks if the tasks list is empty

        :return: True if tasks list is empty, else False
        """
        if len(self._tasks) == 0:
            return True
        else:
            return False

    def periodic(self, interval, function, *args, **kwargs):
        """ schedules a periodic task

        :param interval: interval
        :param function: function handler
        :param args: args
        :param kwargs: kwargs
        """

        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs

        # start the periodic task
        self._start_periodic()

    def _start_periodic(self, from_run=False):
        """ starts the periodic task through the Timer object

        :param from_run: from run boolean
        """
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        """ runs the function handler

        """
        self._start_periodic(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop_periodic(self):
        """ stops the periodic task

        """
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


