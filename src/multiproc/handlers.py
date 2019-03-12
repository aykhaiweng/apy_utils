"""
Shortcut helpers for creating Threads and Multiprocess functions

Khai, 27.02.2019
"""
import traceback
import logging
import threading
from collections.abc import Iterable
from queue import Queue

logger = logging.getLogger(__name__)


def thread_wrapper(queue, results, func):
    """
    Default Thread Wrapper to work on items in the queue

    Khai, 11.03.2019
    """
    while not queue.empty():
        position, obj = queue.get()

        # Function invocation
        result = func(obj)

        results[position] = result
        queue.task_done()

    return True


class CustomThread(threading.Thread):
    """
    Worker Thread that does work from a Queue with Exception handling

    Khai, 11.03.2019
    """

    def __init__(self, target, queue, results, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = kwargs.get('args')
        self.target = target
        self.queue = queue
        self.results = results

        self.exceptions = []
        self.has_exceptions = False

    def run(self):
        """
        Run the function via the Thread.

        Khai, 11.03.2019
        """
        queue = self.queue
        results = self.results
        target = self.target

        while not queue.empty():
            position, obj = queue.get()

            try:
                # Function invocation
                result = target(obj)
                results[position] = result
            except Exception as e:
                message = (
                    f"Error when processing object `{obj}` with function "
                    f"`{target}`"
                )
                exception = {
                    'position': position,
                    'exception': e,
                    'func': target,
                    'obj': obj,
                    'traceback': traceback.format_exc()
                }
                self.exceptions.append(exception)
                self.has_exceptions = True

            queue.task_done()


class ThreadHandler:
    """
    Thread handler that accepts a list of variables as well
    as the function to work on each item in the list.

    Example of a func argument that is acceptable:

        >>>
        > def thread_wrapper(q, results, handler):
        >     while not q.empty():
        >         obj = q.get()
        >
        >         # Actual function start
        >         updated_transaction = handler.handle_payment(
        >             quotation=obj[1], no_of_units=1
        >         )
        >         if updated_transaction.status == 0:
        >             style = self.style.SUCCESS
        >         else:
        >             style = self.style.WARNING
        >         self.stdout.write(style(
        >             "\t[T] {transaction} | {transaction.amount_received} | "
        >             "{transaction.status}".format(
        >                 transaction=updated_transaction
        >             )
        >         ))
        >         # Actual function end
        >
        >         results[obj[0]] = updated_transaction
        >         q.task_done()
        >     return True 

    Khai, 27.02.2019
    """

    def __init__(self, func, objs, threads=1, wrapper=thread_wrapper,
                 thread_class=CustomThread, fail_silently=False,
                 *args, **kwargs):
        # Checking func
        if callable(func) is False:
            raise TypeError("func input has to be a callable.")

        # Checking wrapper
        if callable(wrapper) is False:
            raise TypeError("wrapper input has to be a callable.")

        # Checking objs
        if isinstance(objs, Iterable) is False:
            raise TypeError("obs input has to be iterable.")

        # Options
        self.fail_silently = fail_silently

        # Assigning class variables
        self.func = func
        self.wrapper = wrapper
        self.objs = objs
        self.threads = threads
        self.thread_class = thread_class
        self.kwargs = kwargs
        self.args = args

        # Count the objects being worked on
        self.count = self.count_objects(self.objs)

        # Store the exceptions
        self.worker_exceptions = []

    @classmethod
    def count_objects(cls, objs):
        """
        Count the object, hook inspired for using with Django's QuerySets.

        Khai, 27.02.2019
        """
        return len(objs)

    @classmethod
    def create_queue(cls, maxsize=0):
        """
        Establish a Queue

        Khai, 11.03.2019
        """
        # Create a Queue to be used by the threads
        queue = Queue(maxsize=maxsize)
        # Chuck the objects into the queue

        return queue

    def populate_queue(self, queue, objs):
        """
        Creates a Queue based on objects

        Khai, 11.03.2019
        """
        for i in range(self.count):
            queue.put((i, objs[i]))

        return queue

    def run(self, func=None, objs=None, threads=None,
            wrapper=None, thread_class=None, fail_silently=None):
        """
        Starting point.

        Khai, 27.02.2019
        """
        func = func or self.func
        wrapper = wrapper or self.wrapper
        objs = objs or self.objs
        threads = threads or self.threads
        thread_class = thread_class or self.thread_class
        count = self.count or self.count_objects(objs)
        fail_silently = fail_silently or self.fail_silently

        # Create a data store for the objects
        errors = []
        results = [{} for x in objs]

        # Determine the number of threads to be used as the minimum
        # between the number of objects available and the minimum number
        # of threads we are willing to deploy
        threads = min(count, threads)

        # Create a Queue
        queue = self.create_queue()

        # Populate the Queue with objects
        queue = self.populate_queue(queue, objs)

        workers = []
        for i in range(threads):
            worker = thread_class(
                target=func, queue=queue, results=results
            )
            # worker.setDaemon(True)
            worker.start()
            workers.append(worker)

        queue.join()
        for i in range(threads):
            queue.put(None)
        for w in workers:
            w.join(timeout=30)

        # Check for Exceptions:
        for w in workers:
            if w.has_exceptions:
                self.worker_exceptions.extend(w.exceptions)

        pprint.pprint(self.worker_exceptions)

        if self.worker_exceptions:
            if fail_silently is False:
                exception = self.worker_exceptions[0]['exception']
                raise exception

        return results

