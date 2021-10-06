"""Unit tests for the function retry_decorator"""
# pylint: disable=too-many-public-methods

import inspect
import logging
import random
import unittest

import asynctest
from mock import AsyncMock, Mock

from tubthumper import RetryError, retry_factory

from . import constants, util

tubthumper_logger = logging.getLogger("tubthumper")
tubthumper_logger.setLevel(logging.ERROR)  # silence warnings from retries


class TestRetryFactoryAsync(asynctest.TestCase):
    """Test case for retry factory with coroutines"""

    async def test_coroutine_success(self):
        """Test success of a simple coroutine passed into retry"""
        return_value = 1
        func = AsyncMock(return_value=return_value)
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        result = await wrapped_func()
        self.assertEqual(result, return_value)
        func.assert_awaited_once_with()

    @staticmethod
    async def test_coroutine_call():
        """Test coroutine is called with appropriate arguments"""
        func = AsyncMock()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        await wrapped_func(*constants.ARGS, **constants.KWARGS)
        func.assert_awaited_once_with(*constants.ARGS, **constants.KWARGS)

    async def test_single_exception(self):
        """Test providing a single exception to catch is caught and retried"""
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )
        with self.assertRaises(RetryError):
            await wrapped_func()
        self.assertEqual(func.await_count, 2)

    async def test_diff_single_exception(self):
        """Test providing a single exception and throwing a different one is not caught and retried"""
        side_effect = TypeError
        func = AsyncMock(side_effect=side_effect)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1
        )
        with self.assertRaises(side_effect):
            await wrapped_func()
        func.assert_awaited_once_with()

    async def test_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing one of them is caught and retried"""
        exceptions = (constants.TestException, TypeError)
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=exceptions, retry_limit=1, init_backoff=0
        )
        with self.assertRaises(RetryError):
            await wrapped_func()
        self.assertEqual(func.await_count, 2)

    async def test_diff_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing a different one is not caught and retried"""
        exceptions = (ValueError, TypeError)
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(func, exceptions=exceptions, retry_limit=1)
        with self.assertRaises(constants.TestException):
            await wrapped_func()
        func.assert_awaited_once_with()

    async def test_reraise(self):
        """Test that setting reraise to True results in raising the caught exception, not RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            reraise=True,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(constants.TestException):
            await wrapped_func()
        self.assertEqual(func.await_count, 2)

    async def test_reraise_with_time_limit(self):
        """Test that setting reraise to True with a time limit results in raising the caught exception, not RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            reraise=True,
            time_limit=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(constants.TestException):
            await wrapped_func()
        self.assertEqual(func.await_count, 1)

    async def test_retry_limit_0(self):
        """Test retry_limit set to 0 calls function once and raises RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, retry_limit=0, exceptions=constants.TestException
        )
        with self.assertRaises(RetryError):
            await wrapped_func()
        func.assert_awaited_once_with()

    async def test_time_limit(self):
        """Test that setting a time_limit results in a RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, time_limit=0, exceptions=constants.TestException
        )
        with self.assertRaises(RetryError):
            await wrapped_func()
        func.assert_awaited_once_with()

    async def test_jitter(self):
        """Test jitter results in random variation in backoff time, predictable thanks to setting the random seed"""
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, retry_limit=1, exceptions=constants.TestException
        )
        random.seed(constants.RANDOM_SEED)
        with self.assertRaises(RetryError):
            await wrapped_func()
        self.assertEqual(func.await_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, constants.RANDOM_QUANTITY)

    async def test_init_backoff(self):
        """Test init_backoff results in appropriate backoff time"""
        init_backoff = 0.01
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            init_backoff=init_backoff,
            retry_limit=1,
            jitter=False,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func()
        self.assertEqual(func.await_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, init_backoff)

    async def test_exponential_backoff(self):
        """Test default exponential backoff time"""
        init_backoff = 0.01
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            init_backoff=init_backoff,
            retry_limit=2,
            jitter=False,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func()
        self.assertEqual(func.await_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], 2 * init_backoff
        )

    async def test_custom_exponential_backoff(self):
        """Test custom exponential backoff time"""
        init_backoff = 0.01
        exponential = 1.5
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            init_backoff=init_backoff,
            exponential=exponential,
            retry_limit=2,
            jitter=False,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func()
        self.assertEqual(func.await_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], exponential * init_backoff
        )

    async def test_logging(self):
        """Test retrying a function results in a warning log statement"""
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=logging.WARNING):
                await wrapped_func()
        self.assertEqual(func.await_count, 2)

    async def test_custom_logging_level(self):
        """Test that setting a custom log level works"""
        level = logging.INFO
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            exceptions=constants.TestException,
            retry_limit=1,
            init_backoff=0,
            log_level=level,
        )
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=level):
                await wrapped_func()
        self.assertEqual(func.await_count, 2)

    async def test_custom_logger(self):
        """Test that supplying a custom logger works"""
        logger = logging.getLogger(__name__)
        func = AsyncMock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=logger, level=logging.WARNING):
                await wrapped_func()
        self.assertEqual(func.await_count, 2)

    async def test_method_of_object(self):
        """Test retry and correct call structure for wrapping an object's async method"""

        class _Class:
            method = util.create_method_mock(
                async_mock=True, side_effect=constants.TestException
            )

        obj = _Class()
        func = obj.method
        wrapped_func = retry_factory(
            func,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(obj, *constants.ARGS, **constants.KWARGS)

    async def test_method_of_class(self):
        """Test retry and correct call structure for wrapping a class's async method"""

        class _Class:
            method = util.create_method_mock(
                async_mock=True, side_effect=constants.TestException
            )

        func = _Class.method
        wrapped_func = retry_factory(
            func,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)

    async def test_classmethod_of_object(self):
        """Test retry and correct call structure for wrapping an object's async classmethod"""

        class _Class:
            method = classmethod(
                util.create_method_mock(
                    async_mock=True, side_effect=constants.TestException
                )
            )

        obj = _Class()
        func = obj.method
        wrapped_func = retry_factory(
            func,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(_Class, *constants.ARGS, **constants.KWARGS)

    async def test_classmethod_of_class(self):
        """Test retry and correct call structure for wrapping a class's async classmethod"""

        class _Class:
            method = classmethod(
                util.create_method_mock(
                    async_mock=True, side_effect=constants.TestException
                )
            )

        func = _Class.method
        wrapped_func = retry_factory(
            func,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(_Class, *constants.ARGS, **constants.KWARGS)

    async def test_staticmethod_of_object(self):
        """Test retry and correct call structure for wrapping a object's async staticmethod"""

        class _Class:
            method = staticmethod(
                util.create_method_mock(
                    async_mock=True, side_effect=constants.TestException
                )
            )

        obj = _Class()
        func = obj.method
        wrapped_func = retry_factory(
            func,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)

    async def test_staticmethod_of_class(self):
        """Test retry and correct call structure for wrapping a class's async staticmethod"""

        class _Class:
            method = staticmethod(
                util.create_method_mock(
                    async_mock=True, side_effect=constants.TestException
                )
            )

        func = _Class.method
        wrapped_func = retry_factory(
            func,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(RetryError):
            await wrapped_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)


class TestRetryFactory(unittest.TestCase):
    """Test case for retry factory"""

    def test_success(self):
        """Test success of a simple function decorated with retry_decorator"""
        return_value = 1
        func = Mock(return_value=return_value)
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        result = wrapped_func()
        self.assertEqual(result, return_value)
        func.assert_called_once_with()

    def test_only_keyword_args(self):
        """Test that the retry decorator only allows keyword arguments"""
        func = Mock()
        with self.assertRaises(TypeError):
            retry_factory(  # pylint: disable=missing-kwoa,too-many-function-args
                func,
                constants.TestException,
            )

    @staticmethod
    def test_func_call():
        """Test function is called with appropriate arguments"""
        func = Mock()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        wrapped_func(*constants.ARGS, **constants.KWARGS)
        func.assert_called_once_with(*constants.ARGS, **constants.KWARGS)

    def test_single_exception(self):
        """Test providing a single exception to catch is caught and retried"""
        func = Mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )
        with self.assertRaises(RetryError):
            wrapped_func()
        self.assertEqual(func.call_count, 2)

    def test_diff_single_exception(self):
        """Test providing a single exception and throwing a different one is not caught and retried"""
        side_effect = TypeError
        func = Mock(side_effect=side_effect)
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        with self.assertRaises(side_effect):
            wrapped_func()
        func.assert_called_once_with()

    def test_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing one of them is caught and retried"""
        exceptions = (constants.TestException, TypeError)
        func = Mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            exceptions=exceptions,
            retry_limit=1,
            init_backoff=0,
        )
        with self.assertRaises(RetryError):
            wrapped_func()
        self.assertEqual(func.call_count, 2)

    def test_diff_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing a different one is not caught and retried"""
        exceptions = (ValueError, TypeError)
        side_effect = constants.TestException
        func = Mock(side_effect=side_effect)
        wrapped_func = retry_factory(func, exceptions=exceptions)
        with self.assertRaises(constants.TestException):
            wrapped_func()
        func.assert_called_once_with()

    def test_reraise(self):
        """Test that setting reraise to True results in raising the caught exception, not RetryError"""
        func = Mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            exceptions=constants.TestException,
            reraise=True,
            retry_limit=1,
            init_backoff=0,
        )
        with self.assertRaises(constants.TestException):
            wrapped_func()
        self.assertEqual(func.call_count, 2)

    def test_reraise_with_time_limit(self):
        """Test that setting reraise to True with a time limit results in raising the caught exception, not RetryError"""
        func = Mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func,
            reraise=True,
            time_limit=0,
            exceptions=constants.TestException,
        )
        with self.assertRaises(constants.TestException):
            wrapped_func()
        self.assertEqual(func.call_count, 1)

    def test_retry_limit_0(self):
        """Test retry_limit set to 0 calls function once and raises RetryError"""
        func = Mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=0
        )
        with self.assertRaises(RetryError):
            wrapped_func()
        func.assert_called_once_with()

    def test_time_limit(self):
        """Test that setting a time_limit results in a RetryError"""
        func = Mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, time_limit=0
        )
        with self.assertRaises(RetryError):
            wrapped_func()
        func.assert_called_once_with()

    def test_jitter(self):
        """Test jitter results in random variation in backoff time, predictable thanks to setting the random seed"""
        func = util.timed_mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1
        )
        random.seed(constants.RANDOM_SEED)
        with self.assertRaises(RetryError):
            wrapped_func()
        self.assertEqual(func.call_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, constants.RANDOM_QUANTITY)

    def test_init_backoff(self):
        """Test init_backoff results in appropriate backoff time"""
        func = util.timed_mock(side_effect=constants.TestException)
        init_backoff = 0.01
        wrapped_func = retry_factory(
            func,
            exceptions=constants.TestException,
            init_backoff=init_backoff,
            retry_limit=1,
            jitter=False,
        )
        with self.assertRaises(RetryError):
            wrapped_func()
        self.assertEqual(func.call_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, init_backoff)

    def test_exponential_backoff(self):
        """Test default exponential backoff time"""
        func = util.timed_mock(side_effect=constants.TestException)
        init_backoff = 0.01
        wrapped_func = retry_factory(
            func,
            exceptions=constants.TestException,
            init_backoff=init_backoff,
            retry_limit=2,
            jitter=False,
        )
        with self.assertRaises(RetryError):
            wrapped_func()
        self.assertEqual(func.call_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], 2 * init_backoff
        )

    def test_custom_exponential_backoff(self):
        """Test custom exponential backoff time"""
        func = util.timed_mock(side_effect=constants.TestException)
        init_backoff = 0.01
        exponential = 1.5
        wrapped_func = retry_factory(
            func,
            exceptions=constants.TestException,
            init_backoff=init_backoff,
            exponential=exponential,
            retry_limit=2,
            jitter=False,
        )
        with self.assertRaises(RetryError):
            wrapped_func()
        self.assertEqual(func.call_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], exponential * init_backoff
        )

    def test_logging(self):
        """Test retrying results in a warning log statement"""
        func = Mock(side_effect=constants.TestException)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=logging.WARNING):
                wrapped_func()
        self.assertEqual(func.call_count, 2)

    def test_custom_logging_level(self):
        """Test that setting a custom log level works"""
        func = Mock(side_effect=constants.TestException)
        level = logging.INFO
        wrapped_func = retry_factory(
            func,
            exceptions=constants.TestException,
            retry_limit=1,
            init_backoff=0,
            log_level=level,
        )
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=level):
                wrapped_func()
        self.assertEqual(func.call_count, 2)

    def test_custom_logger(self):
        """Test that supplying a custom logger works"""
        func = Mock(side_effect=constants.TestException)
        logger = logging.getLogger(__name__)
        wrapped_func = retry_factory(
            func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=logger, level=logging.WARNING):
                wrapped_func()
        self.assertEqual(func.call_count, 2)

    def test_method_of_object(self):
        """Test retry and correct call structure for decorating an object's method"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = retry_factory(
                method_mock,
                exceptions=constants.TestException,
                retry_limit=1,
                init_backoff=0,
            )

        obj = _Class()
        with self.assertRaises(RetryError):
            obj.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(obj, *constants.ARGS, **constants.KWARGS)

    def test_method_of_class(self):
        """Test retry and correct call structure for decorating a class's method"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = retry_factory(
                method_mock,
                exceptions=constants.TestException,
                retry_limit=1,
                init_backoff=0,
            )

        with self.assertRaises(RetryError):
            _Class.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(*constants.ARGS, **constants.KWARGS)

    def test_classmethod_of_object(self):
        """Test retry and correct call structure for decorating an object's classmethod"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = classmethod(
                retry_factory(
                    method_mock,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
            )

        obj = _Class()
        with self.assertRaises(RetryError):
            obj.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(_Class, *constants.ARGS, **constants.KWARGS)

    def test_classmethod_of_class(self):
        """Test retry and correct call structure for decorating a class's classmethod"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = classmethod(
                retry_factory(
                    method_mock,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
            )

        with self.assertRaises(RetryError):
            _Class.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(_Class, *constants.ARGS, **constants.KWARGS)

    def test_staticmethod_of_object(self):
        """Test retry and correct call structure for decorating a object's staticmethod"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = staticmethod(
                retry_factory(
                    method_mock,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
            )

        obj = _Class()
        with self.assertRaises(RetryError):
            obj.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(*constants.ARGS, **constants.KWARGS)

    def test_staticmethod_of_class(self):
        """Test retry and correct call structure for decorating a class's staticmethod"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = staticmethod(
                retry_factory(
                    method_mock,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
            )

        with self.assertRaises(RetryError):
            _Class.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(*constants.ARGS, **constants.KWARGS)

    def test_function_signature(self):
        """Test that the decorated function has the same signature as the original"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        func_sig = inspect.signature(func)
        dec_func_sig = inspect.signature(wrapped_func)
        self.assertEqual(func_sig, dec_func_sig)

    def test_function_name(self):
        """Test that the decorated function has the same __name__ as the original"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        func_name = func.__name__
        dec_func_name = wrapped_func.__name__
        self.assertEqual(func_name, dec_func_name)

    def test_function_qualname(self):
        """Test that the decorated function has the same __qualname__ as the original"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        func_qualname = func.__qualname__
        dec_func_qualname = wrapped_func.__qualname__
        self.assertEqual(func_qualname, dec_func_qualname)

    def test_function_module(self):
        """Test that the decorated function has the same __module__ as the original"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        func_module = func.__module__
        dec_func_module = wrapped_func.__module__
        self.assertEqual(func_module, dec_func_module)

    def test_function_docstr(self):
        """Test that the decorated function has the same __doc__ as the original"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        func_docstr = func.__doc__
        dec_func_docstr = wrapped_func.__doc__
        self.assertEqual(func_docstr, dec_func_docstr)

    def test_function_annotations(self):
        """Test that the decorated function has the same __annotations__ as the original"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        func_annotations = func.__annotations__
        dec_func_annotations = wrapped_func.__annotations__
        self.assertEqual(func_annotations, dec_func_annotations)

    def test_function_attrs(self):
        """Test that the decorated function has the same attribbutes as the original"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        for key in func.__dict__:
            func_val = getattr(func, key)
            dec_func_val = getattr(wrapped_func, key)
            self.assertEqual(func_val, dec_func_val)

    def test_isfunction(self):
        """Test the the decorated function is recognized as a function"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        self.assertTrue(inspect.isfunction(wrapped_func))

    def test_isroutine(self):
        """Test the the decorated function is recognized as a routine"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        self.assertTrue(inspect.isroutine(wrapped_func))

    def test_ismethod(self):
        """Test the the decorated function is recognized as a method"""
        func = util.get_a_func()

        class _Class:
            method = retry_factory(func, exceptions=constants.TestException)

        obj = _Class()
        self.assertTrue(inspect.ismethod(obj.method))

    def test_iscoroutinefunction(self):
        """Test the the decorated function is recognized as a coroutine function"""
        async_func = util.get_an_async_func()
        wrapped_func = retry_factory(async_func, exceptions=constants.TestException)
        self.assertTrue(inspect.iscoroutinefunction(wrapped_func))

    def test_repr(self):
        """Test that the decorated function has the proper repr"""
        func = util.get_a_func()
        wrapped_func = retry_factory(func, exceptions=constants.TestException)
        dec_func_repr = repr(wrapped_func)
        self.assertRegex(dec_func_repr, constants.REPR_REGEX)


if __name__ == "__main__":
    unittest.main()
