"""Unit tests for the function retry"""
# pylint: disable=too-many-public-methods

import logging
import random
import unittest

import asynctest
from mock import AsyncMock, Mock

from tubthumper import RetryError, retry

from . import constants, util

tubthumper_logger = logging.getLogger("tubthumper")
tubthumper_logger.setLevel(logging.ERROR)  # silence warnings from retries


class TestRetryAsync(asynctest.TestCase):
    """Test case for retry function with coroutines"""

    async def test_coroutine_success(self):
        """Test success of a simple coroutine passed into retry"""
        return_value = 1
        func = AsyncMock(return_value=return_value)
        result = await retry(func, exceptions=constants.TestException)
        self.assertEqual(result, return_value)
        func.assert_awaited_once_with()

    @staticmethod
    async def test_coroutine_call():
        """Test coroutine is called with appropriate arguments"""
        func = AsyncMock()
        await retry(
            func,
            args=constants.ARGS,
            kwargs=constants.KWARGS,
            exceptions=constants.TestException,
        )
        func.assert_awaited_once_with(*constants.ARGS, **constants.KWARGS)

    async def test_single_exception(self):
        """Test providing a single exception to catch is caught and retried"""
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            await retry(
                func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
            )
        self.assertEqual(func.await_count, 2)

    async def test_diff_single_exception(self):
        """Test providing a single exception and throwing a different one is not caught and retried"""
        side_effect = TypeError
        func = AsyncMock(side_effect=side_effect)
        with self.assertRaises(side_effect):
            await retry(func, exceptions=constants.TestException, retry_limit=1)
        func.assert_awaited_once_with()

    async def test_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing one of them is caught and retried"""
        exceptions = (constants.TestException, TypeError)
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            await retry(func, exceptions=exceptions, retry_limit=1, init_backoff=0)
        self.assertEqual(func.await_count, 2)

    async def test_diff_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing a different one is not caught and retried"""
        exceptions = (ValueError, TypeError)
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(constants.TestException):
            await retry(func, exceptions=exceptions, retry_limit=1)
        func.assert_awaited_once_with()

    async def test_reraise(self):
        """Test that setting reraise to True results in raising the caught exception, not RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(constants.TestException):
            await retry(
                func,
                reraise=True,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.await_count, 2)

    async def test_reraise_with_time_limit(self):
        """Test that setting reraise to True with a time limit results in raising the caught exception, not RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(constants.TestException):
            await retry(
                func,
                reraise=True,
                time_limit=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.await_count, 1)

    async def test_retry_limit_0(self):
        """Test retry_limit set to 0 calls function once and raises RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            await retry(func, retry_limit=0, exceptions=constants.TestException)
        func.assert_awaited_once_with()

    async def test_time_limit(self):
        """Test that setting a time_limit results in a RetryError"""
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            await retry(func, time_limit=0, exceptions=constants.TestException)
        func.assert_awaited_once_with()

    async def test_jitter(self):
        """Test jitter results in random variation in backoff time, predictable thanks to setting the random seed"""
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        random.seed(constants.RANDOM_SEED)
        with self.assertRaises(RetryError):
            await retry(func, retry_limit=1, exceptions=constants.TestException)
        self.assertEqual(func.await_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, constants.RANDOM_QUANTITY)

    async def test_init_backoff(self):
        """Test init_backoff results in appropriate backoff time"""
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        init_backoff = 0.01
        with self.assertRaises(RetryError):
            await retry(
                func,
                init_backoff=init_backoff,
                retry_limit=1,
                jitter=False,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.await_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, init_backoff)

    async def test_exponential_backoff(self):
        """Test default exponential backoff time"""
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        init_backoff = 0.01
        with self.assertRaises(RetryError):
            await retry(
                func,
                init_backoff=init_backoff,
                retry_limit=2,
                jitter=False,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.await_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], 2 * init_backoff
        )

    async def test_custom_exponential_backoff(self):
        """Test custom exponential backoff time"""
        func = util.timed_mock(async_mock=True, side_effect=constants.TestException)
        init_backoff = 0.01
        exponential = 1.5
        with self.assertRaises(RetryError):
            await retry(
                func,
                init_backoff=init_backoff,
                exponential=exponential,
                retry_limit=2,
                jitter=False,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.await_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], exponential * init_backoff
        )

    async def test_logging(self):
        """Test retrying a function results in a warning log statement"""
        func = AsyncMock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=logging.WARNING):
                await retry(
                    func,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
        self.assertEqual(func.await_count, 2)

    async def test_custom_logging_level(self):
        """Test that setting a custom log level works"""
        func = AsyncMock(side_effect=constants.TestException)
        level = logging.INFO
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=level):
                await retry(
                    func,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                    log_level=level,
                )
        self.assertEqual(func.await_count, 2)

    async def test_custom_logger(self):
        """Test that supplying a custom logger works"""
        func = AsyncMock(side_effect=constants.TestException)
        logger = logging.getLogger(__name__)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=logger, level=logging.WARNING):
                await retry(
                    func,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
        self.assertEqual(func.await_count, 2)

    async def test_method_of_object(self):
        """Test retry and correct call structure for wrapping an object's async method"""

        class _Class:
            method = util.create_method_mock(
                async_mock=True, side_effect=constants.TestException
            )

        obj = _Class()
        func = obj.method
        with self.assertRaises(RetryError):
            await retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(obj, *constants.ARGS, **constants.KWARGS)

    async def test_method_of_class(self):
        """Test retry and correct call structure for wrapping a class's async method"""

        class _Class:
            method = util.create_method_mock(
                async_mock=True, side_effect=constants.TestException
            )

        func = _Class.method
        with self.assertRaises(RetryError):
            await retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
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
        with self.assertRaises(RetryError):
            await retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
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
        with self.assertRaises(RetryError):
            await retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
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
        with self.assertRaises(RetryError):
            await retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
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
        with self.assertRaises(RetryError):
            await retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.await_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)


class TestRetry(unittest.TestCase):
    """Test case for retry function"""

    def test_success(self):
        """Test success of a simple function passed into retry"""
        return_value = 1
        func = Mock(return_value=return_value)
        result = retry(func, exceptions=constants.TestException)
        self.assertEqual(result, return_value)
        func.assert_called_once_with()

    def test_only_one_positional_arg(self):
        """Test that the retry function only allows one positional argument"""
        func = Mock()
        with self.assertRaises(TypeError):
            retry(  # pylint: disable=too-many-function-args
                func, None, exceptions=constants.TestException
            )

    @staticmethod
    def test_func_call():
        """Test args & kwargs are passed into func properly"""
        func = Mock()
        retry(
            func,
            args=constants.ARGS,
            kwargs=constants.KWARGS,
            exceptions=constants.TestException,
        )
        func.assert_called_once_with(*constants.ARGS, **constants.KWARGS)

    def test_single_exception(self):
        """Test providing a single exception to catch is caught and retried"""
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            retry(
                func, exceptions=constants.TestException, retry_limit=1, init_backoff=0
            )
        self.assertEqual(func.call_count, 2)

    def test_diff_single_exception(self):
        """Test providing a single exception and throwing a different one is not caught and retried"""
        side_effect = TypeError
        func = Mock(side_effect=side_effect)
        with self.assertRaises(side_effect):
            retry(func, exceptions=constants.TestException, retry_limit=1)
        func.assert_called_once_with()

    def test_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing one of them is caught and retried"""
        exceptions = (constants.TestException, TypeError)
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            retry(func, exceptions=exceptions, retry_limit=1, init_backoff=0)
        self.assertEqual(func.call_count, 2)

    def test_diff_multiple_exceptions(self):
        """Test providing a tuple of exceptions and throwing a different one is not caught and retried"""
        exceptions = (ValueError, TypeError)
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(constants.TestException):
            retry(func, exceptions=exceptions, retry_limit=1)
        func.assert_called_once_with()

    def test_reraise(self):
        """Test that setting reraise to True results in raising the caught exception, not RetryError"""
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(constants.TestException):
            retry(
                func,
                reraise=True,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)

    def test_reraise_with_time_limit(self):
        """Test that setting reraise to True with a time limit results in raising the caught exception, not RetryError"""
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(constants.TestException):
            retry(
                func,
                reraise=True,
                time_limit=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 1)

    def test_retry_limit_0(self):
        """Test retry_limit set to 0 calls function once and raises RetryError"""
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            retry(func, retry_limit=0, exceptions=constants.TestException)
        func.assert_called_once_with()

    def test_time_limit(self):
        """Test that setting a time_limit results in a RetryError"""
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            retry(func, time_limit=0, exceptions=constants.TestException)
        func.assert_called_once_with()

    def test_jitter(self):
        """Test jitter results in random variation in backoff time, predictable thanks to setting the random seed"""
        func = util.timed_mock(side_effect=constants.TestException)
        random.seed(constants.RANDOM_SEED)
        with self.assertRaises(RetryError):
            retry(func, retry_limit=1, exceptions=constants.TestException)
        self.assertEqual(func.call_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, constants.RANDOM_QUANTITY)

    def test_init_backoff(self):
        """Test init_backoff results in appropriate backoff time"""
        func = util.timed_mock(side_effect=constants.TestException)
        init_backoff = 0.01
        with self.assertRaises(RetryError):
            retry(
                func,
                init_backoff=init_backoff,
                retry_limit=1,
                jitter=False,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)
        duration = func.call_times[1] - func.call_times[0]
        util.assert_time(self, duration, init_backoff)

    def test_exponential_backoff(self):
        """Test default exponential backoff time"""
        func = util.timed_mock(side_effect=constants.TestException)
        init_backoff = 0.01
        with self.assertRaises(RetryError):
            retry(
                func,
                init_backoff=init_backoff,
                retry_limit=2,
                jitter=False,
                exceptions=constants.TestException,
            )
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
        with self.assertRaises(RetryError):
            retry(
                func,
                init_backoff=init_backoff,
                exponential=exponential,
                retry_limit=2,
                jitter=False,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 3)
        util.assert_time(self, func.call_times[1] - func.call_times[0], init_backoff)
        util.assert_time(
            self, func.call_times[2] - func.call_times[1], exponential * init_backoff
        )

    def test_logging(self):
        """Test retrying a function results in a warning log statement"""
        func = Mock(side_effect=constants.TestException)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=logging.WARNING):
                retry(
                    func,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
        self.assertEqual(func.call_count, 2)

    def test_custom_logging_level(self):
        """Test that setting a custom log level works"""
        func = Mock(side_effect=constants.TestException)
        level = logging.INFO
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=tubthumper_logger, level=level):
                retry(
                    func,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                    log_level=level,
                )
        self.assertEqual(func.call_count, 2)

    def test_custom_logger(self):
        """Test that supplying a custom logger works"""
        func = Mock(side_effect=constants.TestException)
        logger = logging.getLogger(__name__)
        with self.assertRaises(RetryError):
            with self.assertLogs(logger=logger, level=logging.WARNING):
                retry(
                    func,
                    exceptions=constants.TestException,
                    retry_limit=1,
                    init_backoff=0,
                )
        self.assertEqual(func.call_count, 2)

    def test_method_of_object(self):
        """Test retry and correct call structure for wrapping an object's method"""

        class _Class:
            method = util.create_method_mock(side_effect=constants.TestException)

        obj = _Class()
        func = obj.method
        with self.assertRaises(RetryError):
            retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)
        func.assert_called_with(obj, *constants.ARGS, **constants.KWARGS)

    def test_method_of_class(self):
        """Test retry and correct call structure for wrapping a class's method"""

        class _Class:
            method = util.create_method_mock(side_effect=constants.TestException)

        func = _Class.method
        with self.assertRaises(RetryError):
            retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)

    def test_classmethod_of_object(self):
        """Test retry and correct call structure for wrapping an object's classmethod"""

        class _Class:
            method = classmethod(
                util.create_method_mock(side_effect=constants.TestException)
            )

        obj = _Class()
        func = obj.method
        with self.assertRaises(RetryError):
            retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)
        func.assert_called_with(_Class, *constants.ARGS, **constants.KWARGS)

    def test_classmethod_of_class(self):
        """Test retry and correct call structure for wrapping a class's classmethod"""

        class _Class:
            method = classmethod(
                util.create_method_mock(side_effect=constants.TestException)
            )

        func = _Class.method
        with self.assertRaises(RetryError):
            retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)
        func.assert_called_with(_Class, *constants.ARGS, **constants.KWARGS)

    def test_staticmethod_of_object(self):
        """Test retry and correct call structure for wrapping a object's staticmethod"""

        class _Class:
            method = staticmethod(
                util.create_method_mock(side_effect=constants.TestException)
            )

        obj = _Class()
        func = obj.method
        with self.assertRaises(RetryError):
            retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)

    def test_staticmethod_of_class(self):
        """Test retry and correct call structure for wrapping a class's staticmethod"""

        class _Class:
            method = staticmethod(
                util.create_method_mock(side_effect=constants.TestException)
            )

        func = _Class.method
        with self.assertRaises(RetryError):
            retry(
                func,
                args=constants.ARGS,
                kwargs=constants.KWARGS,
                retry_limit=1,
                init_backoff=0,
                exceptions=constants.TestException,
            )
        self.assertEqual(func.call_count, 2)
        func.assert_called_with(*constants.ARGS, **constants.KWARGS)


if __name__ == "__main__":
    unittest.main()
