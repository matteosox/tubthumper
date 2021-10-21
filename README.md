# **Tubthumper**: Helping you get up ... again!

[![CI/CD: n/a](https://github.com/matteosox/tubthumper/actions/workflows/cicd.yaml/badge.svg)](https://github.com/matteosox/tubthumper/actions/workflows/cicd.yaml)
[![Docs: n/a](https://readthedocs.org/projects/tubthumper/badge/?version=stable)](https://tubthumper.mattefay.com)
[![Downloads: n/a](https://static.pepy.tech/personalized-badge/tubthumper?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/tubthumper)
[![PyPI: n/a](https://img.shields.io/badge/dynamic/json?color=blueviolet&label=PyPI&query=%24.info.version&url=https%3A%2F%2Fpypi.org%2Fpypi%2Ftubthumper%2Fjson)](https://pypi.org/project/tubthumper/)
[![codecov: n/a](https://codecov.io/gh/matteosox/tubthumper/branch/main/graph/badge.svg?token=8VKKDG9SMZ)](https://codecov.io/gh/matteosox/tubthumper)
[![MyPY: n/a](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fmatteosox%2Fbd79bbd912687bf44fac6b7887d18f14%2Fraw%2Fmypy.json)](https://tubthumper.mattefay.com/en/stable/mypy.html)
[![Pylint: n/a](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fmatteosox%2Fbd79bbd912687bf44fac6b7887d18f14%2Fraw%2Fpylint.json)](https://tubthumper.mattefay.com/en/stable/pylint.html)

----

## What's in a name?

**Tubthumper** is a Python package of retry utilities named after the English anarcho-communist rock band Chumbawamba's 1997 hit [Tubthumping](https://www.youtube.com/watch?v=2H5uWRjFsGc). Yes, really.

> I get knocked down, but I get up again. 🎶\
> You're never gonna keep me down. 🎶\
> I get knocked down, but I get up again. 🎶\
> You're never gonna keep me down... 🎶

## Getting Started

### Installation

`tubthumper` is a pip-installable package [hosted on PyPI](https://pypi.org/project/tubthumper/). Getting started is as easy as:

```console
$ pip install tubthumper
```

`tubthumper` requires Python 3.6 or greater. For Python 3.8 or greater, it has no external dependencies, i.e. standard library only, but earlier versions require the [`dataclasses`](https://pypi.org/project/dataclasses/) backport and [`typing-extensions`](https://pypi.org/project/typing-extensions/).

### Usage

Import `tubthumper`'s useful bits:
```python
>>> from tubthumper import retry, retry_decorator, retry_factory
```

Call a function with retry and jittered exponential backoff:
```python
>>> retry(get_ip, exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 0.844422 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

Call that same function with positional and keyword arguments, e.g. retry `get_ip(42, "test", dev=True)`:
```python
>>> retry(get_ip,
...     args=(42, "test"), kwargs={"dev": True},
...     exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 0.420572 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

Bake retry behavior into your function with a decorator:
```python
>>> @retry_decorator(exceptions=ConnectionError)
... def get_ip_retry():
...     return requests.get("http://ip.jsontest.com").json()
>>> get_ip_retry()
WARNING: Function threw exception below on try 1, retrying in 0.511275 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

Create a new function with retry behavior from an existing one:
```python
>>> get_ip_retry = retry_factory(get_ip, exceptions=ConnectionError)
>>> get_ip_retry()
WARNING: Function threw exception below on try 1, retrying in 0.783799 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

## Customization

While `tubthumper` ships with a set of sensible defaults, its retry behavior is fully customizable.

### Exceptions

Because overbroad except clauses are [the most diabolical Python antipattern](https://realpython.com/the-most-diabolical-python-antipattern/), there is no sensible default for what exception or exceptions to catch and retry. Thus, every `tubthumper` interface has a required `exceptions` keyword-only argument, which takes an exception or tuple of exceptions to catch and retry on, i.e. a sensible lack of a default.

```python
>>> retry(get_ip, exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 0.476597 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
>>> retry(get_ip, exceptions=(KeyError, ConnectionError))
WARNING: Function threw exception below on try 1, retrying in 0.908113 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

By default, `tubthumper` raises a `tubthumper.RetryError` exception when all retries have been exhausted:

```python
>>> retry(lambda: 1/0, retry_limit=0, exceptions=ZeroDivisionError)
Traceback (most recent call last):
  ...
tubthumper._retry_factory.RetryError: Retry limit 0 reached
```

You can override this behavior using the `reraise` flag to reraise the original exception in place of `RetryError`:

```python
>>> retry(lambda: 1/0, retry_limit=0, reraise=True, exceptions=ZeroDivisionError)
Traceback (most recent call last):
  ...
ZeroDivisionError: division by zero
```

### Retry Limits

By default, `tubthumper` will retry endlessly, but you have two means of limiting retry behavior. As shown previously, to limit the number of retries attempted, use the `retry_limit` keyword-only argument:

```python
>>> retry(lambda: 1/0, retry_limit=10, exceptions=ZeroDivisionError)
...  # Warning logs for each failed call
Traceback (most recent call last):
  ...
tubthumper._retry_factory.RetryError: Retry limit 10 reached
```

Alternatively, you can use the `time_limit` keyword-only argument to prevent retry attempts after a certain duration:

```python
>>> retry(lambda: 1/0, time_limit=60, exceptions=ZeroDivisionError)
...  # Warning logs for each failed call
Traceback (most recent call last):
  ...
tubthumper._retry_factory.RetryError: Time limit 60 exceeded
```

### Backoff timing

By default, the backoff duration doubles with each retry, starting off at one second. As well, each backoff period is jittered, i.e. scaled by a uniformly distributed random number on the [0.0, 1.0) interval. You can disable jittering using the `jitter` keyword-only argument:

```python
>>> retry(get_ip, jitter=False, exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 1 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

You can set the initial backoff duration using the `init_backoff` keyword-only argument:

```python
>>> retry(get_ip, jitter=False, init_backoff=10, exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 10 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

Finally, you can set the factor by which each successive backoff duration is scaled using the `exponential` keyword-only argument:

```python
>>> retry(get_ip, jitter=False, exponential=3, exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 1 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
WARNING: Function threw exception below on try 2, retrying in 3 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

### Logging

By default, `tubthumper` logs each caught exception at the `logging.WARNING` level using a logger named `tubthumper`, i.e. `logging.getLogger("tubthumper")`. As described in the [Python logging tutorial](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library), for this default logger, "events of severity WARNING and greater will be printed to sys.stderr" if no further logging is configured.

You can set the logging level using the `log_level` keyword-only argument:

```python
>>> retry(get_ip, log_level=logging.DEBUG, exceptions=ConnectionError) # No warnings
{'ip': '8.8.8.8'}
```

You can provide your own logger using the `logger` keyword-only argument. This logger's `log` method will be called like so:

```python
logger.log(log_level, "Function threw...", exc_info=True)
```

## Features

### Compatible with methods

`tubthumper`'s various interfaces are compatible with methods, including classmethods and staticmethods:

```python
>>> class Class:
...     @retry_decorator(exceptions=ConnectionError)
...     def get_ip(self):
...         return requests.get("http://ip.jsontest.com").json()
...
>>> Class().get_ip()
WARNING: Function threw exception below on try 1, retrying in 0.719705 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

### Signature preserving

`tubthumper`'s various interfaces preserve the relevant [dunder](https://wiki.python.org/moin/DunderAlias) attributes of your function:

```python
>>> @retry_decorator(exceptions=ConnectionError)
... def func(one: bool, two: float = 3.0) -> complex:
...     """This is a docstring"""
...
>>> func.__name__
'func'
>>> func.__qualname__
'func'
>>> func.__module__
'__main__'
>>> func.__doc__
'This is a docstring'
>>> func.__annotations__
{'one': <class 'bool'>, 'two': <class 'float'>, 'return': <class 'complex'>}
```

`tubthumper` also preserves the inspect module's function signature, and `is*` functions:

```python
>>> import inspect
>>> inspect.signature(func)
<Signature (one: bool, two: float = 3.0) -> complex>
>>> inspect.isfunction(func)
True
>>> inspect.isroutine(func)
True
>>> inspect.ismethod(Class().get_ip)
True
```

### Async support

`tubthumper`'s various interfaces support coroutine functions, including [generator-based coroutines](https://docs.python.org/3/library/asyncio-task.html#generator-based-coroutines), awaiting them while using `async.sleep` between awaits:

```python
>>> @retry_decorator(exceptions=ConnectionError)
... async def get_ip():
...     return requests.get("http://ip.jsontest.com").json()
...
>>> inspect.iscoroutinefunction(get_ip)
True
```

### Fully type annotated

`tubthumper`'s various interfaces are fully type annotated, passing [Mypy](https://mypy.readthedocs.io/en/stable/)'s static type checker. You can find Mypy's [Type Check Coverage Summary](https://tubthumper.mattefay.com/en/stable/mypy.html) at that link.

### 100% Test Coverage

`tubthumper` achieves 100% test coverage across three supported operating systems (Windows, MacOS, & Linux). You can find the [Linux coverage report](https://tubthumper.mattefay.com/en/stable/coverage.html) at that link, or the full coverage report on [Codecov](https://codecov.io/gh/matteosox/tubthumper).
