"""Unit tests for the function retry_decorator"""
# pylint: disable=too-many-public-methods

import inspect
import logging
import random
import unittest

from mock import AsyncMock, Mock

from tubthumper import RetryError, retry_decorator

from . import constants, util

tubthumper_logger = logging.getLogger("tubthumper")
tubthumper_logger.setLevel(logging.ERROR)  # silence warnings from retries


class TestRetryDecoratorAsync(util.IsolatedAsyncioTestCase):
    """Test case for retry decorator with coroutines"""

    async def test_coroutine_success(self):
        """Test success of a simple coroutine passed into decorated function"""
        return_value = 1
        func = AsyncMock(return_value=return_value)
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        result = await dec_func()
        self.assertEqual(result, return_value)
        func.assert_awaited_once_with()

    @staticmethod
    async def test_coroutine_call():
        """Test coroutine is called with appropriate arguments with decorated function"""
        func = AsyncMock()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        await dec_func(*constants.ARGS, **constants.KWARGS)
        func.assert_awaited_once_with(*constants.ARGS, **constants.KWARGS)

    async def test_single_exception(self):
        """Test providing a single exception to catch is caught and retried by decorated function"""
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )(func)
        with self.assertRaises(RetryError):
            await dec_func()
        self.assertEqual(func.await_count, 2)

    async def test_diff_single_exception(self):
        """Test providing a single exception and throwing a different one is not caught and retried by decorated function"""
        side_effect = TypeError
        func = AsyncMock(side_effect=side_effect)
        dec_func = retry_decorator(exceptions=constants.TestException, retry_limit=1)(
            func
        )
        with self.assertRaises(side_effect):
            await dec_func()
        func.assert_awaited_once_with()

    async def test_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing one of them is caught and retried by decorated function"""
        exceptions = (constants.TestException, TypeError)
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=exceptions, retry_limit=1, init_backoff=0
        )(func)
        with self.assertRaises(RetryError):
            await dec_func()
        self.assertEqual(func.await_count, 2)

    async def test_diff_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing a different one is not caught and retried by decorated function"""
        exceptions = (ValueError, TypeError)
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(exceptions=exceptions, retry_limit=1)(func)
        with self.assertRaises(constants.TestException):
            await dec_func()
        func.assert_awaited_once_with()

    async def test_reraise(self):
        """Test that setting reraise to True results in raising the caught exception, not RetryError by decorated function"""
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            reraise=True,
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(constants.TestException):
            await dec_func()
        self.assertEqual(func.await_count, 2)

    async def test_reraise_with_time_limit(self):
        """Test that setting reraise to True with a time limit results in raising the caught exception, not RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            reraise=True,
            time_limit=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(constants.TestException):
            await dec_func()
        self.assertEqual(func.await_count, 1)

    async def test_retry_limit_0(self):
        """Test retry_limit set to 0 calls function once and raises RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(retry_limit=0, exceptions=constants.TestException)(
            func
        )
        with self.assertRaises(RetryError):
            await dec_func()
        func.assert_awaited_once_with()

    async def test_time_limit(self):
        """Test that setting a time_limit results in a RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(time_limit=0, exceptions=constants.TestException)(
            func
        )
        with self.assertRaises(RetryError):
            await dec_func()
        func.assert_awaited_once_with()

    async def test_jitter(self):
        """Test jitter results in random variation in backoff time, predictable thanks to setting the random seed"""
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        dec_func = retry_decorator(retry_limit=1, exceptions=constants.TestException)(
            func
        )
        random.seed(constants.RANDOM_SEED)
        with self.assertRaises(RetryError):
            await dec_func()
        self.assertEqual(func.await_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, constants.RANDOM_QUANTITY)

    async def test_init_backoff(self):
        """Test init_backoff results in appropriate backoff time"""
        init_backoff = 0.01
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        dec_func = retry_decorator(
            init_backoff=init_backoff,
            retry_limit=1,
            jitter=False,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func()
        self.assertEqual(func.await_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, init_backoff)

    async def test_exponential_backoff(self):
        """Test default exponential backoff time"""
        init_backoff = 0.01
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        dec_func = retry_decorator(
            init_backoff=init_backoff,
            retry_limit=2,
            jitter=False,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func()
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
        dec_func = retry_decorator(
            init_backoff=init_backoff,
            exponential=exponential,
            retry_limit=2,
            jitter=False,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func()
        self.assertEqual(func.await_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], exponential * init_backoff
        )

    async def test_logging(self):
        """Test retrying a function results in a warning log statement"""
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )(func)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=logging.WARNING):
                await dec_func()
        self.assertEqual(func.await_count, 2)

    async def test_custom_logging_level(self):
        """Test that setting a custom log level works"""
        level = logging.INFO
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException,
            retry_limit=1,
            init_backoff=0,
            log_level=level,
        )(func)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=level):
                await dec_func()
        self.assertEqual(func.await_count, 2)

    async def test_custom_logger(self):
        """Test that supplying a custom logger works"""
        logger = logging.getLogger(__name__)
        func = AsyncMock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )(func)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=logger, level=logging.WARNING):
                await dec_func()
        self.assertEqual(func.await_count, 2)

    async def test_method_of_object(self):
        """Test retry and correct call structure for wrapping an object's async method"""

        class _Class:
            method = util.create_method_mock(
                async_mock=True, side_effect=constants.TestException
            )

        obj = _Class()
        func = obj.method
        dec_func = retry_decorator(
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(obj, *constants.ARGS, **constants.KWARGS)

    async def test_method_of_class(self):
        """Test retry and correct call structure for wrapping a class's async method"""

        class _Class:
            method = util.create_method_mock(
                async_mock=True, side_effect=constants.TestException
            )

        func = _Class.method
        dec_func = retry_decorator(
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func(*constants.ARGS, **constants.KWARGS)
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
        dec_func = retry_decorator(
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func(*constants.ARGS, **constants.KWARGS)
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
        dec_func = retry_decorator(
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func(*constants.ARGS, **constants.KWARGS)
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
        dec_func = retry_decorator(
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func(*constants.ARGS, **constants.KWARGS)
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
        dec_func = retry_decorator(
            retry_limit=1,
            init_backoff=0,
            exceptions=constants.TestException,
        )(func)
        with self.assertRaises(RetryError):
            await dec_func(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)


class TestRetryDecorator(unittest.TestCase):
    """Test case for retry decorator"""

    def test_success(self):
        """Test success of a simple function decorated with retry_decorator"""
        return_value = 1
        func = Mock(return_value=return_value)
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        result = dec_func()
        self.assertEqual(result, return_value)
        func.assert_called_once_with()

    def test_only_keyword_args(self):
        """Test that the retry decorator only allows keyword arguments"""
        with self.assertRaises(TypeError):
            retry_decorator(  # pylint: disable=missing-kwoa,too-many-function-args
                constants.TestException
            )

    @staticmethod
    def test_func_call():
        """Test function is called with appropriate arguments"""
        func = Mock()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        dec_func(*constants.ARGS, **constants.KWARGS)
        func.assert_called_once_with(*constants.ARGS, **constants.KWARGS)

    def test_single_exception(self):
        """Test providing a single exception to catch is caught and retried"""
        func = Mock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )(func)
        with self.assertRaises(RetryError):
            dec_func()
        self.assertEqual(func.call_count, 2)

    def test_diff_single_exception(self):
        """Test providing a single exception and throwing a different one is not caught and retried"""
        side_effect = TypeError
        func = Mock(side_effect=side_effect)
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        with self.assertRaises(side_effect):
            dec_func()
        func.assert_called_once_with()

    def test_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing one of them is caught and retried"""
        exceptions = (constants.TestException, TypeError)
        func = Mock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=exceptions,
            retry_limit=1,
            init_backoff=0,
        )(func)
        with self.assertRaises(RetryError):
            dec_func()
        self.assertEqual(func.call_count, 2)

    def test_diff_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing a different one is not caught and retried"""
        exceptions = (ValueError, TypeError)
        side_effect = constants.TestException
        func = Mock(side_effect=side_effect)
        dec_func = retry_decorator(exceptions=exceptions)(func)
        with self.assertRaises(constants.TestException):
            dec_func()
        func.assert_called_once_with()

    def test_reraise(self):
        """Test that setting reraise to True results in raising the caught exception, not RetryError"""
        func = Mock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException,
            reraise=True,
            retry_limit=1,
            init_backoff=0,
        )(func)
        with self.assertRaises(constants.TestException):
            dec_func()
        self.assertEqual(func.call_count, 2)

    def test_reraise_with_time_limit(self):
        """Test that setting reraise to True with a time limit results in raising the caught exception, not RetryError"""
        func = Mock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException,
            reraise=True,
            time_limit=0,
        )(func)
        with self.assertRaises(constants.TestException):
            dec_func()
        self.assertEqual(func.call_count, 1)

    def test_retry_limit_0(self):
        """Test retry_limit set to 0 calls function once and raises RetryError"""
        func = Mock(side_effect=constants.TestException)
        dec_func = retry_decorator(exceptions=constants.TestException, retry_limit=0)(
            func
        )
        with self.assertRaises(RetryError):
            dec_func()
        func.assert_called_once_with()

    def test_time_limit(self):
        """Test that setting a time_limit results in a RetryError"""
        func = Mock(side_effect=constants.TestException)
        dec_func = retry_decorator(exceptions=constants.TestException, time_limit=0)(
            func
        )
        with self.assertRaises(RetryError):
            dec_func()
        func.assert_called_once_with()

    def test_jitter(self):
        """Test jitter results in random variation in backoff time, predictable thanks to setting the random seed"""
        func = util.timed_mock(side_effect=constants.TestException)
        dec_func = retry_decorator(exceptions=constants.TestException, retry_limit=1)(
            func
        )
        random.seed(constants.RANDOM_SEED)
        with self.assertRaises(RetryError):
            dec_func()
        self.assertEqual(func.call_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, constants.RANDOM_QUANTITY)

    def test_init_backoff(self):
        """Test init_backoff results in appropriate backoff time"""
        func = util.timed_mock(side_effect=constants.TestException)
        init_backoff = 0.01
        dec_func = retry_decorator(
            exceptions=constants.TestException,
            init_backoff=init_backoff,
            retry_limit=1,
            jitter=False,
        )(func)
        with self.assertRaises(RetryError):
            dec_func()
        self.assertEqual(func.call_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, init_backoff)

    def test_exponential_backoff(self):
        """Test default exponential backoff time"""
        func = util.timed_mock(side_effect=constants.TestException)
        init_backoff = 0.01
        dec_func = retry_decorator(
            exceptions=constants.TestException,
            init_backoff=init_backoff,
            retry_limit=2,
            jitter=False,
        )(func)
        with self.assertRaises(RetryError):
            dec_func()
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
        dec_func = retry_decorator(
            exceptions=constants.TestException,
            init_backoff=init_backoff,
            exponential=exponential,
            retry_limit=2,
            jitter=False,
        )(func)
        with self.assertRaises(RetryError):
            dec_func()
        self.assertEqual(func.call_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], exponential * init_backoff
        )

    def test_logging(self):
        """Test retrying results in a warning log statement"""
        func = Mock(side_effect=constants.TestException)
        dec_func = retry_decorator(
            exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )(func)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=logging.WARNING):
                dec_func()
        self.assertEqual(func.call_count, 2)

    def test_custom_logging_level(self):
        """Test that setting a custom log level works"""
        func = Mock(side_effect=constants.TestException)
        level = logging.INFO
        dec_func = retry_decorator(
            exceptions=constants.TestException,
            retry_limit=1,
            init_backoff=0,
            log_level=level,
        )(func)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=level):
                dec_func()
        self.assertEqual(func.call_count, 2)

    def test_custom_logger(self):
        """Test that supplying a custom logger works"""
        func = Mock(side_effect=constants.TestException)
        logger = logging.getLogger(__name__)
        dec_func = retry_decorator(
            exceptions=constants.TestException, retry_limit=1, init_backoff=0
        )(func)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=logger, level=logging.WARNING):
                dec_func()
        self.assertEqual(func.call_count, 2)

    def test_method_of_object(self):
        """Test retry and correct call structure for decorating an object's method"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = retry_decorator(
                exceptions=constants.TestException, retry_limit=1, init_backoff=0
            )(method_mock)

        obj = _Class()
        with self.assertRaises(RetryError):
            obj.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(obj, *constants.ARGS, **constants.KWARGS)

    def test_method_of_class(self):
        """Test retry and correct call structure for decorating a class's method"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = retry_decorator(
                exceptions=constants.TestException, retry_limit=1, init_backoff=0
            )(method_mock)

        with self.assertRaises(RetryError):
            _Class.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(*constants.ARGS, **constants.KWARGS)

    def test_classmethod_of_object(self):
        """Test retry and correct call structure for decorating an object's classmethod"""
        method_mock = util.create_method_mock(side_effect=constants.TestException)

        class _Class:
            method = classmethod(
                retry_decorator(
                    exceptions=constants.TestException, retry_limit=1, init_backoff=0
                )(method_mock)
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
                retry_decorator(
                    exceptions=constants.TestException, retry_limit=1, init_backoff=0
                )(method_mock)
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
                retry_decorator(
                    exceptions=constants.TestException, retry_limit=1, init_backoff=0
                )(method_mock)
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
                retry_decorator(
                    exceptions=constants.TestException, retry_limit=1, init_backoff=0
                )(method_mock)
            )

        with self.assertRaises(RetryError):
            _Class.method(*constants.ARGS, **constants.KWARGS)
        self.assertEqual(method_mock.call_count, 2)
        method_mock.assert_called_with(*constants.ARGS, **constants.KWARGS)

    def test_function_signature(self):
        """Test that the decorated function has the same signature as the original"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        func_sig = inspect.signature(func)
        dec_func_sig = inspect.signature(dec_func)
        self.assertEqual(func_sig, dec_func_sig)

    def test_function_name(self):
        """Test that the decorated function has the same __name__ as the original"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        func_name = func.__name__
        dec_func_name = dec_func.__name__
        self.assertEqual(func_name, dec_func_name)

    def test_function_qualname(self):
        """Test that the decorated function has the same __qualname__ as the original"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        func_qualname = func.__qualname__
        dec_func_qualname = dec_func.__qualname__
        self.assertEqual(func_qualname, dec_func_qualname)

    def test_function_module(self):
        """Test that the decorated function has the same __module__ as the original"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        func_module = func.__module__
        dec_func_module = dec_func.__module__
        self.assertEqual(func_module, dec_func_module)

    def test_function_docstr(self):
        """Test that the decorated function has the same __doc__ as the original"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        func_docstr = func.__doc__
        dec_func_docstr = dec_func.__doc__
        self.assertEqual(func_docstr, dec_func_docstr)

    def test_function_annotations(self):
        """Test that the decorated function has the same __annotations__ as the original"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        func_annotations = func.__annotations__
        dec_func_annotations = dec_func.__annotations__
        self.assertEqual(func_annotations, dec_func_annotations)

    def test_function_attrs(self):
        """Test that the decorated function has the same attributes as the original"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        for key in func.__dict__:
            func_val = getattr(func, key)
            dec_func_val = getattr(dec_func, key)
            self.assertEqual(func_val, dec_func_val)

    def test_isfunction(self):
        """Test the the decorated function is recognized as a function"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        self.assertTrue(inspect.isfunction(dec_func))

    def test_isroutine(self):
        """Test the the decorated function is recognized as a routine"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        self.assertTrue(inspect.isroutine(dec_func))

    def test_ismethod(self):
        """Test the the decorated function is recognized as a method"""
        func = util.get_a_func()

        class _Class:
            method = retry_decorator(exceptions=constants.TestException)(func)

        obj = _Class()
        self.assertTrue(inspect.ismethod(obj.method))

    def test_iscoroutinefunction(self):
        """Test the the decorated function is recognized as a coroutine function"""
        async_func = util.get_an_async_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(async_func)
        self.assertTrue(inspect.iscoroutinefunction(dec_func))

    def test_repr(self):
        """Test that the decorated function has the proper repr"""
        func = util.get_a_func()
        dec_func = retry_decorator(exceptions=constants.TestException)(func)
        dec_func_repr = repr(dec_func)
        self.assertRegex(dec_func_repr, constants.REPR_REGEX)


if __name__ == "__main__":
    unittest.main()
