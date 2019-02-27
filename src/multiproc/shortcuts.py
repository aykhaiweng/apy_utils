"""
Shortcut helpers for creating Threads and Multiprocess functions

Khai, 27.02.2019
"""
from collections.abc import Iterable
from threading import Thread
from queue import Queue


class ThreadHandler:
    """
    Thread handler that accepts a list of variables as well
    as the function to be iterated on.

    Khai, 27.02.2019
    """

    def __init__(self, func, objs, threads=1, *args, **kwargs):
        # Checking func
        if callable(func) is False:
            raise TypeError("func input has to be a callable.")

        # Checking objs
        if isinstance(objs, Iterable) is False:
            raise TypeError("obs input has to be iterable.")

        # Assigning class variables
        self.func = func
        self.objs = objs
        self.threads = threads
        self.kwargs = kwargs
        self.args = args

    @classmethod
    def count(cls, objs):
        """
        Count the object, hook inspired for using with Django's QuerySets.

        Khai, 27.02.2019
        """
        return len(objs)

    @classmethod
    def run(cls, func=None, objs=None, threads=None):
        """
        Starting point.

        Khai, 27.02.2019
        """
        func = func or cls.func
        objs = objs or cls.objs
        threads = threads or cls.threads

        # Create a data store for the objects
        results = [{} for x in objs]
        # Create a Queue to be used by the threads
        queue = Queue(maxsize=0)

        # Count the number of objects available
        count = self.count(objs)

        # Determine the number of threads to be used as the minimum
        # between the number of objects available and the minimum number
        # of threads we are willing to deploy
        threads = min(count, threads)
