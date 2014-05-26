import os
import time
import unittest
import threading

from pebble import process, TaskCancelled, TimeoutError


event = threading.Event()
initarg = 0
results = 0
exception = None


def callback(task):
    global results
    global exception

    try:
        results = task.get()
    except Exception as error:
        exception = error

    event.set()


def function(argument, keyword_argument=0):
    """A docstring."""
    return argument + keyword_argument


def error_function():
    raise Exception("BOOM!")


def long_function():
    time.sleep(1)


def pid_function():
    time.sleep(0.1)
    return os.getpid()


# class TestProcessTaskObj(object):
#     a = 0

#     def __init__(self):
#         self.b = 1

#     @classmethod
#     @process.task
#     def clsmethod(cls):
#         return cls.a

#     @process.task
#     def instmethod(self):
#         return self.b

#     @staticmethod
#     @process.task
#     def stcmethod():
#         return 2


class TestProcessPool(unittest.TestCase):
    def setUp(self):
        self.event = threading.Event()
        self.event.clear()
        self.results = None
        self.exception = None

    def callback(self, task):
        try:
            self.results = task.get()
        except Exception as error:
            self.exception = error
        finally:
            self.event.set()

    def test_process_pool_single_task(self):
        """Process Pool single task."""
        with process.Pool() as pool:
            task = pool.schedule(function, args=[1],
                                 kwargs={'keyword_argument': 1})
        self.assertEqual(task.get(), 2)

    def test_process_pool_multiple_tasks(self):
        """Process Pool multiple tasks."""
        tasks = []
        with process.Pool() as pool:
            for index in range(5):
                tasks.append(pool.schedule(function, args=[1]))
        self.assertEqual(sum([t.get() for t in tasks]), 5)

    def test_process_pool_callback(self):
        """Process Pool results are forwarded to the callback."""
        with process.Pool() as pool:
            pool.schedule(function, args=[1], callback=self.callback,
                          kwargs={'keyword_argument': 1})
        self.event.wait()
        self.assertEqual(self.results, 2)

    def test_process_pool_error(self):
        """Process Pool errors are raised by task get."""
        with process.Pool() as pool:
            task = pool.schedule(error_function)
        self.assertRaises(Exception, task.get)

    def test_process_pool_error_callback(self):
        """Process Pool errors are forwarded to callback."""
        with process.Pool() as pool:
            pool.schedule(error_function, callback=self.callback)
        self.event.wait()
        self.assertTrue(isinstance(self.exception, Exception))

    def test_process_pool_timeout(self):
        """Process Pool task raises TimeoutError if so."""
        with process.Pool() as pool:
            task = pool.schedule(long_function, timeout=0.1)
        self.assertRaises(TimeoutError, task.get)

    def test_process_pool_timeout_callback(self):
        """Process Task TimeoutError is forwarded to callback."""
        with process.Pool() as pool:
            pool.schedule(long_function, callback=self.callback, timeout=0.1)
        self.event.wait()
        self.assertTrue(isinstance(self.exception, TimeoutError))

    def test_process_pool_different_processs(self):
        """Process Pool multiple tasks are handled by different processes."""
        tasks = []
        with process.Pool(workers=2) as pool:
            for i in range(0, 5):
                tasks.append(pool.schedule(pid_function))
        self.assertEqual(len(set([t.get() for t in tasks])), 2)

    def test_process_pool_schedule_id(self):
        """Process Pool task ID is forwarded to it."""
        with process.Pool() as pool:
            task = pool.schedule(function, args=[1], identifier='foo')
        self.assertEqual(task.id, 'foo')