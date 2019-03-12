"""
Specific tests for the plain functionality of each ThreadHandler function

Khai, 27.02.2019
"""
import datetime
import json
import requests
from unittest import TestCase

from ..handlers import ThreadHandler


class ThreadHandlerTestCase(TestCase):
    """
    TestCases include:
        * Testing the initialization of the ThreadHandler
        *

    Khai, 27.02.2019
    """

    def test_initialization_of_thread_handler(self):
        """Testing the initialization of the ThreadHandler"""
        def dummy_func(x):
            return x + x
        dummy_list = [x for x in range(10)]

        # TheadHandler requires a function and iterable input
        with self.assertRaises(TypeError) as e:
            threadhandler = ThreadHandler()

        # Object needs to be an Iterable
        with self.assertRaises(TypeError) as e:
            theadhandler = ThreadHandler(dummy_func, dummy_func)

        # Function needs to be a Callable
        with self.assertRaises(TypeError) as e:
            theadhandler = ThreadHandler(dummy_list, dummy_list)

        # This counts as a proper initialization
        threadhandler = ThreadHandler(dummy_func, dummy_list)

    def test_run_with_simple_function(self):
        """Test .run() of handler with a simple function"""

        def call_httpbin(data, url="https://httpbin.org/post"):
            """
            Calls https://httpbin.org/post with a data payload

            Khai, 11.03.2019
            """
            response = requests.post(url, data=json.dumps(data))
            return response.json()

        # Initiate payloads to be tested with
        payloads = []
        for i in range(10):
            payloads.append({
                'no': i
            })

        start_1 = datetime.datetime.now()
        results_1 = []
        for data in payloads:
            results_1.append(call_httpbin(data))
        end_1 = datetime.datetime.now()
        time_taken_1 = end_1 - start_1

        # This counts as a proper initialization
        start_2 = datetime.datetime.now()
        threadhandler = ThreadHandler(call_httpbin, payloads, threads=2)
        results_2 = threadhandler.run()
        end_2 = datetime.datetime.now()
        time_taken_2 = end_2 - start_2

        # The threaded handler should have the same results as the 
        # non threaded function
        self.assertEqual(results_1, results_2)
        self.assertGreater(time_taken_1, time_taken_2)
        # Check that it has no errors:
        self.assertFalse(threadhandler.worker_exceptions)

    def test_run_with_error_handling(self):
        """Test .run() of handler with an errornous function"""

        def mod_function(data):
            """
            Checks if the payload contains an even number

            Khai, 11.03.2019
            """
            if data['no'] % 2 != 0:
                raise ValueError(f'{data} does not contain an Even number!')
            return True

        # Initiate payloads to be tested with
        payloads = []
        for i in range(10):
            payloads.append({
                'no': i
            })

        # Check for error handling for this threaded function wrapper
        with self.assertRaises(ValueError):
            threadhandler = ThreadHandler(mod_function, payloads, threads=2)
            results = threadhandler.run()

        results = threadhandler.run(fail_silently=True)
        # Check that every 2nd result is a True statement
        for i, r in enumerate(results):
            if i % 2 != 0:
                self.assertEqual(r, {})
            else:
                self.assertEqual(r, True)

        print(threadhandler.worker_exceptions)
