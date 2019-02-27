"""
Specific tests for the plain functionality of each ThreadHandler function

Khai, 27.02.2019
"""
from unittest import TestCase

from ..shortcuts import ThreadHandler


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
